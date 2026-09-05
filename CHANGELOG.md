# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-09-05

No database migrations. Image remains `ghcr.io/brendenwalker/stillroom`.

### Fixed

- One volume↔weight food conversion (e.g. ¼ cup = 40g) applies to the rest of that system (tbsp, tsp, ml, oz, …) (#46)

## [0.1.3] - 2026-09-05

No database migrations. Image remains `ghcr.io/brendenwalker/stillroom`.

### Added

- Recipe ingredient editor shows live line kcal as amount and measure change (#44)

### Fixed

- Count units (Each, pcs, …) convert to grams via food Per Each grams when no explicit conversion exists (#44)

## [0.1.2] - 2026-09-05

No database migrations. Nested recipe ingredients gain a read-only `kcal` (line total). Image remains `ghcr.io/brendenwalker/stillroom`.

### Added

- Recipe view shows kcal per serving with working time, waiting time, and servings (#42)
- Ingredient lines show that ingredient’s kcal contribution per serving (#42)
- Read-only `kcal` on nested recipe ingredient API responses (#42)

## [0.1.1] - 2026-09-04

No database migrations. Image remains `ghcr.io/brendenwalker/stillroom`.

### Security

- Ingredient parser: bound regexes that CodeQL flagged as ReDoS / overly broad `[A-z]` ranges (#39)
- AI food/recipe property and step-sort 500s no longer include exception text in the response; traceback stays in server logs (#39)

### Changed

- CodeQL scan ignores pdfjs vendor files and test fixtures; drop deprecated `HEAD^2` checkout (#39)

## [0.1.0] - 2026-09-04

Back up before upgrading. Apply migrations **0244–0248**. Pack-size fields and shopping `amount_grams` are additive; **0246** backfills grams when conversion is possible and clears `count_per_pack` below 1; unconverted shopping entries stay unchanged. Rolling back does not restore converted shopping `amount`/`unit`. **0247** adds food `kcal` / `kcal_grams`; **0248** copies from existing calorie/grams properties only when those food fields are null. After upgrade, check foods’ Details tab (pack sizes and kcal). Mark non-food supermarket categories (soap, bags) with Food items unchecked. Integrations may see new optional fields on Food, ShoppingListEntry, SupermarketCategory, Recipe, and MealPlan (`kcal_per_serving` is read-only). Image remains `ghcr.io/brendenwalker/stillroom`.

### Added

- Meal Planner (`/this-week`): week/day cards, recipe picker, keyword filter, copy-yesterday, per-plan and per-day kcal; calendar planner stays at `/mealplan` (#35)
- Per-serving kcal from food calorie density and ingredient grams (read-only `kcal_per_serving` on recipe and meal plan APIs) (#35)
- Food calorie fields (`kcal`, `kcal_grams`) on the Details tab; migrations 0247–0248 (#29)
- Shopping pack sizes (`shopping_measure`, grams per pack, count per pack, shopping `amount_grams`) with pack counts on the list; migrations 0244–0246 (#17)
- Generic / non-food catalog items via supermarket category “Food items”; those foods stay on shopping lists but are excluded from recipe ingredients, pantry auto-fill, and on-hand updates; `?is_food=` food API filter (#17)
- Native recipe export/import includes pack and kcal food fields; import fills empty Details only and still accepts Tandoor Default zips (#33)
- Default Breakfast/Lunch/Dinner meal types for spaces that have none (#31)
- Field help popovers on the food Details tab (#29)
- Public GitHub Releases workflow and `CHANGELOG.md`

### Changed

- Nav: Calendar for the existing meal-plan calendar; Meal Planner for the weekly view (#36)
- User-facing help, docs, and English copy from Tandoor to Stillroom; Docker image name unchanged (#36)
- Food editor: pack and calorie fields on a Details tab (#29)
- Shopping list shows buy-count + measure + grams when pack metadata exists; recipe-to-list and Telegram paths set `amount_grams` (#17)
- Leaving first-run welcome or household setup marks it completed so the wizard does not return (#29)
- Frontend Vuetify 3 to 4 (select/date/file upload paths)
- Dependency updates (Python, Vue, GitHub Actions)

### Fixed

- Meal plan editor: recipes and meal types selectable under Vuetify 4; seed meal types when missing (#31)
- Native recipe export dropping Details-tab food values on import (#33)
- Debug frontend serving stale cached assets (#29, #31)

[Unreleased]: https://github.com/BrendenWalker/Stillroom/compare/0.1.4...develop
[0.1.4]: https://github.com/BrendenWalker/Stillroom/releases/tag/0.1.4
[0.1.3]: https://github.com/BrendenWalker/Stillroom/releases/tag/0.1.3
[0.1.2]: https://github.com/BrendenWalker/Stillroom/releases/tag/0.1.2
[0.1.1]: https://github.com/BrendenWalker/Stillroom/releases/tag/0.1.1
[0.1.0]: https://github.com/BrendenWalker/Stillroom/releases/tag/0.1.0
