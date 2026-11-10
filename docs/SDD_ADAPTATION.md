# Переход на SDD: Product Owner + Spec Kit

Дата: 2026-11-10

## Зачем

Ed строит проект в два промпта: «Please plan X» пишет `docs/PLAN_X.md`, «Please implement the plan»
его выполняет. В этом репозитории вместо этого работает связка `/productowner` (что строим) и
`/speckit.*` (как строим). Требования заказчика по-прежнему лежат в `docs/`, поменялся только процесс.

## Соответствие двух подходов

| У Ed | У нас |
|---|---|
| `docs/SPEC.md`, бриф дня в `docs/` | то же; это вход для `/speckit.specify` |
| «Please plan the pilot» → `docs/PLAN.md` | `/speckit.specify` → `clarify` → `plan` → `tasks` → `analyze`, артефакты в `specs/NNN-<name>/` |
| 5–6 фаз с чекбоксами критериев | фазы в `tasks.md`, у каждой checkpoint с проверяемыми критериями |
| Ревью плана студентом | пауза после `/speckit.analyze` (режим `--controlled`) |
| «Please implement the plan» | `/speckit.implement`, коммит после каждой фазы |
| Галочки в `PLAN.md`, обновление `STATUS.md` | галочки в `tasks.md`; `docs/STATUS.md` обновляется как раньше |
| `PROCESS.md`: правила | `.specify/memory/constitution.md` |
| «Never push» | push только в `origin` (форк), PR только в `main` форка |

Один день сборки соответствует одной фиче Spec Kit. Так каждую сборку можно сравнить с ветками Ed
`upstream/week*-start` и `-end`.

## Что изменено

| Файл | Изменение |
|---|---|
| `docs/PROCESS.md` | Разделы Planning и Implementing переписаны под Spec Kit, добавлена таблица шагов. Проверки, хук и правила сохранены. «Never push» заменено правилом про форк |
| `.specify/memory/constitution.md` | Шаблон заполнен: 5 принципов (требования из `docs/`, простота, тесты со stub-моделью и покрытием 80%, агент не видит `data/evals/`, правило $1,000 в коде), ограничения стека, workflow, governance |
| `.specify/memory/autonomous-constitution.md` | Промпт consensus-ревью говорил о чужом проекте («QR icebreaker bar»). Заменён на UnderCover с запретом трогать `data/evals/`. Пути `.specify/specs/` исправлены на `specs/`, как в скриптах |
| `.specify/memory/e2e-testing-guide.md` | Заполнена App Structure: порты 5173 и 8000, `playwright.config.ts`, авторизации нет до IMPROVE |
| `.specify/memory/feature-roadmap.md` | Новый файл: 9 фич, по одной на день сборки. Пилот в статусе PENDING, остальные LOCKED, пока бриф не скопирован в `docs/` |
| `.specify/memory/po-state.md` | Новый файл: приоритет (пилот, scope L), MVP, журнал решений, риски |
| `.specify/memory/ai-api-cost-research.md`, `infrastructure-cost-research.md` | Короткие заметки по данным курса (~$10, бесплатные пути, AWS или Render). Исследование цен не проводилось, потому что стек зафиксирован |
| `CLAUDE.md` | Новый файл: секция Product Owner, ключевые файлы, workflow. Указывает, что `AGENTS.md` действует целиком, кроме способа планирования |

Без изменений остались `docs/SPEC.md`, `TECH_STACK.md`, `CODE_STANDARDS.md`, `BRAND.md`, `STATUS.md`
(это требования заказчика и текущее состояние) и `AGENTS.md`, чтобы `git pull upstream` не давал
конфликтов.

## Как начать пилот

Пошагово, с ревью:

```
/productowner next --controlled
/speckit.specify Claims pilot per docs/SPEC.md
/speckit.clarify
/speckit.plan
/speckit.tasks
/speckit.analyze
# ревью spec.md, plan.md, tasks.md
/speckit.implement
/speckit.review
/productowner doc
```

Автономно: `/productowner next`. Эта команда запускает `/speckit.pipeline ... --scope L --commit`.

## Открытые вопросы и риски

- `.specify/`, `.claude/commands/`, `CLAUDE.md` и `specs/` пока не в git. При `git checkout` на ветку
  Ed они либо потеряются, либо перемешаются с чужими файлами. Их нужно закоммитить в форк до первой
  сборки.
- После `/speckit.pipeline --commit` выполняются `git push` и `gh pr create`. Репозиторий `gh` по умолчанию
  уже `cityac/undercover` (проверено), так что PR попадёт в форк.
- Если позже переключиться на ветку Ed (`weekNdayN-start`), на ней будет его `docs/PLAN_*.md` и его
  `PROCESS.md`. Адаптацию тогда придётся перенести заново.
