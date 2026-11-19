#!/usr/bin/env python3
"""Пересчёт оптических и энергетических оценок грибницы с фотогифами.

Меняйте константы профиля ниже — таблицы пересчитаются.
Зависимостей нет, только стандартная библиотека.

Использование:
    python3 tools/fotogify_calc.py
"""

from __future__ import annotations

import math

# --------------------------------------------------------------------------
# Профиль. Меняйте здесь — все таблицы пересчитаются.
# --------------------------------------------------------------------------
N_CORE = 1.348          # сердцевина: вакуоль с полифосфатом и аминокислотами
N_CLAD = 1.337          # кортикальный гель, 98% воды (dn/dc 0.15)
N_WALL = 1.530          # хитиновая стенка (для ARROW); литература 1.5-1.6
LAMBDA_NM = 530.0       # рабочая длина волны, нм
LAMBDA_UM = LAMBDA_NM / 1000.0
V_CUTOFF = 2.405        # первая нулевая точка J0

# бюджет звена, дБ
BUDGET_SECTION_DB = 12.0
LOSS_INPUT_DB = 3.0
LOSS_PROP_MM_DB = 0.1
LOSS_BEND_DB = 0.5
LOSS_SPLIT_DB = 3.5
LOSS_EXIT_DB = 0.1
LOSS_DETECT_DB = 3.0

# фотонные оценки
# Светлячковая люцифераза: 1 фотон на 1 молекулу АТФ, квантовый выход 0,41.
QY = 0.2                # эффективный выход грибной системы in vivo (оценка по обзорам)
ATP_PER_PHOTON = 1.0    # сопряжение реакции с АТФ
ATP_REGEN = 2.0         # регенерация люциферина, молекул АТФ на цикл
J_PER_ATP = 8.3e-20     # ≈ 50 кДж/моль
N_DETECTOR = 300        # фотонов на детектор для надёжного различения

H = 6.62607015e-34
C = 299_792_458.0


def na(n_core: float = N_CORE, n_clad: float = N_CLAD) -> float:
    return math.sqrt(n_core**2 - n_clad**2)


def v_number(a_um: float, lam_um: float = LAMBDA_UM) -> float:
    return 2 * math.pi * a_um * na() / lam_um


def n_modes(a_um: float) -> float:
    v = v_number(a_um)
    return 1.0 if v <= V_CUTOFF else v**2 / 2


def critical_radius_um(a_um: float) -> float:
    delta = (N_CORE - N_CLAD) / N_CORE
    return a_um / delta


def beat_length_um(a_um: float) -> float:
    return 2 * math.pi * a_um * na() / V_CUTOFF


def splice_loss_db(a1: float, a2: float) -> float:
    eta = (2 * a1 * a2 / (a1**2 + a2**2)) ** 2
    return -10 * math.log10(eta)


def fresnel_db(n1: float, n2: float) -> float:
    r = ((n1 - n2) / (n1 + n2)) ** 2
    return -10 * math.log10(1 - r)


def arrow_wall_nm(m: int, lam_nm: float = LAMBDA_NM) -> float:
    s = math.sqrt(N_WALL**2 - N_CORE**2)
    return (2 * m + 1) * lam_nm / (4 * s)


def arrow_resonance_nm(t_nm: float) -> float:
    """Длина волны, на которую резонирует стенка заданной толщины."""
    return 4 * math.sqrt(N_WALL**2 - N_CORE**2) * t_nm


def photon_energy_j(lam_nm: float = LAMBDA_NM) -> float:
    return H * C / (lam_nm * 1e-9)


def symbol_cost_fj(n_detector: int = N_DETECTOR, budget_db: float = 20.0,
                   qy: float = QY) -> tuple[float, float, float]:
    """Возвращает (фотонов на выходе, молекул АТФ, энергия в фДж).

    Светлячковый тип: событие сопряжено с АТФ напрямую, поэтому число
    молекул АТФ равно числу реакционных циклов, а не делится на выход.
    """
    emitted = n_detector * 10 ** (budget_db / 10)
    cycles = emitted / qy
    atp = cycles * ATP_PER_PHOTON + cycles * ATP_REGEN
    energy_fj = atp * J_PER_ATP * 1e15
    return emitted, atp, energy_fj


def hr(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Профиль")
    print(f"  n_core={N_CORE}  n_clad={N_CLAD}  n_wall={N_WALL}")
    print(f"  NA={na():.3f}  delta={(N_CORE - N_CLAD) / N_CORE:.4f}  "
          f"aperture={math.degrees(math.asin(na())):.1f} deg")
    print(f"  lambda={LAMBDA_NM:.0f} nm  E_photon={photon_energy_j():.3e} J")

    hr("Диаметр, моды, изгиб")
    print(f"{'a,um':>6} {'d,um':>6} {'V':>7} {'мод':>7} "
          f"{'Lc,um':>7} {'Rc,um':>8} {'роль':>22}")
    roles = {0.5: "одиночная мода", 1: "локальные петли", 2: "межместные связи",
             4: "магистраль округа", 8: "ствол, много полос"}
    for a in (0.5, 1, 2, 4, 8):
        print(f"{a:6.1f} {2*a:6.1f} {v_number(a):7.2f} {n_modes(a):7.1f} "
              f"{beat_length_um(a):7.3f} {critical_radius_um(a):8.1f} {roles[a]:>22}")

    hr("Бюджет звена")
    total = (LOSS_INPUT_DB + LOSS_PROP_MM_DB + LOSS_BEND_DB +
             LOSS_SPLIT_DB + LOSS_EXIT_DB + LOSS_DETECT_DB)
    for label, val in (("ввод в моду", LOSS_INPUT_DB),
                       ("распространение 1 мм", LOSS_PROP_MM_DB),
                       ("один изгиб", LOSS_BEND_DB),
                       ("ответвление 1x2", LOSS_SPLIT_DB),
                       ("выход из сердцевины", LOSS_EXIT_DB),
                       ("вывод на детектор", LOSS_DETECT_DB)):
        print(f"  {label:<24} {val:5.2f} дБ")
    print(f"  {'ИТОГО':<24} {total:5.2f} дБ")
    print(f"  {'бюджет звена':<24} {BUDGET_SECTION_DB:5.2f} дБ "
          f"(запас {BUDGET_SECTION_DB - total:.2f} дБ)")

    hr("Гель: показатель от концентрации (dn/dc=0.15)")
    for conc in (1, 2, 5, 10, 20):
        print(f"  {conc:2d}% сухого ({100-conc}% воды) -> n={1.333 + 0.15 * conc / 100:.4f}")
    print(f"  для n=1.375 нужно {((1.375 - 1.333) / 0.15 * 100):.1f}% сухого — не гель")

    hr("Апертура от гидратации геля")
    for conc in (2, 5, 10):
        gel = 1.333 + 0.15 * conc / 100
        na_v = math.sqrt(N_CORE**2 - gel**2)
        print(f"  гель {conc:2d}%: n={gel:.4f}, NA={na_v:.3f}, "
              f"апертура={math.degrees(math.asin(na_v)):.1f} град")

    hr("ARROW: толщина стенки под полосу")
    for lam in (405, 470, 520, 590):
        print(f"  λ={lam} нм -> t={arrow_wall_nm(0, lam):.0f} нм")
    print(f"  обычная стенка 78 нм -> λ={arrow_resonance_nm(78):.0f} нм (жёсткий УФ)")

    hr("Стыковка и границы")
    print(f"  потери на стыковке 1->4 мкм: {splice_loss_db(1, 4):.2f} дБ")
    print(f"  потери на стыковке 2->4 мкм: {splice_loss_db(2, 4):.2f} дБ")
    print(f"  френель 1.375->1.335: {fresnel_db(1.375, 1.335):.3f} дБ")
    print(f"  френель 1.375->1.000: {fresnel_db(1.375, 1.000):.3f} дБ")
    print(f"  дисперсия: {(N_CORE / C) * ((N_CORE - N_CLAD) / N_CORE) * 1e9:.4f} нс/м")
    print(f"  рэлей 480->590 нм: x{(590 / 480) ** 4:.3f}")

    hr("Стоимость символа (QY=0.2, 1+2 АТФ на цикл)")
    print(f"{'порог дБ':>9} {'фотонов':>12} {'АТФ':>12} {'фДж':>10}")
    for budget in (6, 10, 15, 20):
        emitted, atp, energy = symbol_cost_fj(budget_db=budget)
        print(f"{budget:9d} {emitted:12.2e} {atp:12.2e} {energy:10.3f}")

    hr("Сравнение с потенциалом действия")
    for atp in (1e4, 1e5, 1e6):
        print(f"  ПД {atp:9.0e} АТФ = {atp * J_PER_ATP * 1e15:8.3f} фДж")

    hr("Чувствительность химического метода (статья)")
    for label, grams in (("1 фг/клетка", 1e-15), ("0.1 пг/мл", 0.1e-12)):
        mol = grams / 507.2 * 6.02214076e23
        print(f"  {label:<14} = {mol:.2e} молекул АТФ")

    hr("Задержка узла")
    print(f"  свет, 1 м в цитоплазме: {1.0 / (C / N_CORE) * 1e9:.1f} нс")
    for lo, hi, label in ((0.2, 2.0, "один узел"),
                          (2.0, 60.0, "местная петля 1 см"),
                          (20.0, 100.0, "округ 10 см"),
                          (20.0, 200.0, "организм 1 м"),
                          (300.0, 600.0, "3 м, кончик-ствол-кончик")):
        print(f"  {label:<26} {lo:6.1f}-{hi:6.1f} мс")


if __name__ == "__main__":
    main()
