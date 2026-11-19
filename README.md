# Mush

Спекулятивный биологический проект: грибница с оптической (фотогифной) сигнальной сетью, распределённой обработкой сигналов, обучением и предсказанием.

## Концепция

- [docs/README.md](docs/README.md) — оглавление и статус концепции

**Исходная концепция**

- [docs/00-status-i-obshiy-princip.md](docs/00-status-i-obshiy-princip.md) — § 1. Общий принцип
- [docs/01-osnova-fotogify-i-uf.md](docs/01-osnova-fotogify-i-uf.md) — § 2–3. Фотогифы, световая связь, УФ-регуляция
- [docs/02-organizaciya-i-kamery.md](docs/02-organizaciya-i-kamery.md) — § 4–5. Организация грибницы, ассоциативные камеры
- [docs/03-obuchenie-predskazanie-seysmika.md](docs/03-obuchenie-predskazanie-seysmika.md) — § 6–8. Обучение, предсказание, сейсмочувствительность
- [docs/04-ustoychivost-opyt-ogranicheniya.md](docs/04-ustoychivost-opyt-ogranicheniya.md) — § 9–12. Устойчивость, передача опыта, ограничения, источники

**Углубление физики и биологии**

- [docs/05-fizika-fotogifov.md](docs/05-fizika-fotogifov.md) — § 13. Бюджет звена, хроматика, диаметры, топология, скорость, энергетика
- [docs/06-uzly-topologiya-marshrutizaciya.md](docs/06-uzly-topologiya-marshrutizaciya.md) — § 14. Чем узел отличается от гифы, топология как вычисление
- [docs/07-biologiya-uzlov.md](docs/07-biologiya-uzlov.md) — § 15. Стенка как ARROW, вакуоль, тельца Воронина, Spitzenkörper, рецепторы
- [docs/08-kritika-i-ispravleniya.md](docs/08-kritika-i-ispravleniya.md) — сводка: 4 критические проблемы и порядок правки
- [docs/09-istochniki-i-velichiny.md](docs/09-istochniki-i-velichiny.md) — § 16. Формулы, бюджет, допущения, источники

## Инструменты

- [tools/fotogify_calc.py](tools/fotogify_calc.py) — пересчёт оптических и энергетических оценок (`python3 tools/fotogify_calc.py`)
