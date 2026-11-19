#!/usr/bin/env python3
"""Пересчёт оптических и энергетических оценок для концепции «Фотохимический разум грибницы».

Печатает таблицы, приведённые в docs/09-istochniki-i-velichiny.md.
Зависимостей нет — только стандартная библиотека.

Использование:
    python3 tools/fotogify_calc.py
"""

from __future__ import annotations

import math

# --------------------------------------------------------------------------
# Рабочий профиль. Меняйте здесь — все таблицы пересчитаются.
# --------------------------------------------------------------------------
N_CORE = 1.375          # сердцевина (осветлённая цитоплазма)
N_CLAD = 1.335          # оболочка / низкоплотная стенка
N_WALL = 1.530          # хитиновая стенка (для ARROW)
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
QY = 0.05               # квантовый выход биолюминесценции (допущение)
ATP_PER_PHOTON = 3.0    # молекул АТФ на один излучаемый фотон (минимум)
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


def photon_energy_j(lam_nm: float = LAMBDA_NM) -> float:
    return H * C / (lam_nm * 1e-9)


def symbol_cost_pj(n_detector: int = N_DETECTOR, budget_db: float = 20.0,
                   qy: float = QY) -> tuple[float, float, float]:
    """Возвращает (фотонов на выходе, молекул АТФ, энергия в пДж)."""
    emitted = n_detector * 10 ** (budget_db / 10)
    photochemical = emitted / qy
    atp = photochemical * ATP_PER_PHOTON
    energy_pj = atp * J_PER_ATP * 1e12
    return emitted, atp, energy_pj


def hr(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Рабочий профиль")
    print(f"  n_core={N_CORE}  n_clad={N_CLAD}  n_wall={N_WALL}")
    print(f"  NA={na():.3f}  delta={(N_CORE - N_CLAD) / N_CORE:.4f}  "
          f"aperture={math.degrees(math.asin(na())):.1f} deg")
    print(f"  lambda={LAMBDA_NM:.0f} nm  E_photon={photon_energy_j():.3e} J")

    hr("Диаметр, моды, изгиб (таблица 16.3)")
    print(f"{'a,um':>6} {'d,um':>6} {'V':>7} {'мод':>7} "
          f"{'Lc,um':>7} {'Rc,um':>8} {'роль':>22}")
    roles = {0.5: "одиночная мода", 1: "локальные петли", 2: "межместные связи",
             4: "магистраль округа", 8: "ствол, много полос"}
    for a in (0.5, 1, 2, 4, 8):
        print(f"{a:6.1f} {2*a:6.1f} {v_number(a):7.2f} {n_modes(a):7.1f} "
              f"{beat_length_um(a):7.3f} {critical_radius_um(a):8.1f} {roles[a]:>22}")

    hr("Бюджет звена (таблица 16.4)")
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

    hr("ARROW: толщина стенки (таблица 16.1)")
    for m in range(3):
        print(f"  m={m}: t={arrow_wall_nm(m):.0f} нм")

    hr("Стыковка и границы")
    print(f"  потери на стыковке 1->4 мкм: {splice_loss_db(1, 4):.2f} дБ")
    print(f"  потери на стыковке 2->4 мкм: {splice_loss_db(2, 4):.2f} дБ")
    print(f"  френель 1.375->1.335: {fresnel_db(1.375, 1.335):.3f} дБ")
    print(f"  френель 1.375->1.000: {fresnel_db(1.375, 1.000):.3f} дБ")
    print(f"  дисперсия: {(N_CORE / C) * ((N_CORE - N_CLAD) / N_CORE) * 1e9:.4f} нс/м")
    print(f"  рэлей 480->590 нм: x{(590 / 480) ** 4:.3f}")

    hr("Стоимость символа (раздел 13.7)")
    print(f"{'порог дБ':>9} {'фотонов':>12} {'АТФ':>12} {'пДж':>9}")
    for budget in (15, 20, 25, 30):
        emitted, atp, energy = symbol_cost_pj(budget_db=budget)
        print(f"{budget:9d} {emitted:12.2e} {atp:12.2e} {energy:9.2f}")

    hr("Задержка узла (раздел 13.6)")
    print(f"  свет, 1 м в цитоплазме: {1.0 / (C / N_CORE) * 1e9:.1f} нс")
    for lo, hi, label in ((0.2, 2.0, "один узел"),
                          (2.0, 60.0, "местная петля 1 см"),
                          (20.0, 100.0, "округ 10 см"),
                          (20.0, 200.0, "организм 1 м"),
                          (300.0, 600.0, "3 м, кончик-ствол-кончик")):
        print(f"  {label:<26} {lo:6.1f}-{hi:6.1f} мс")


if __name__ == "__main__":
    main()
