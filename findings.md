# Findings

## Design document summary

- Required flow: birth info input -> Bazi chart -> AI/lite prelude -> yearly life simulation -> D100 checks -> annual summary -> ending around 60.
- Required backend modules include `bazi_engine.py`, `fate_mapper.py`, `game_logic.py`, `state_manager.py`, `openai_client.py`, `websocket_manager.py`, and role prompts.
- Required frontend pages include birth info, chart display, prelude, and life simulation state/narrative/action UI.
- MVP attributes: health, mind, emotion, knowledge, career, wealth, family, romance, social, reputation, merit, pressure.

## Current project snapshot

- Project has `backend/app` with FastAPI app, game logic, Bazi/fate mapping, state manager, text OpenAI client, auth/security, live observer system, and WebSocket manager.
- Frontend has `index.html/css/js` and live page assets.
- Existing files appear to be adapted from `TenCyclesofFate` and need thematic/game-flow replacement.

## Current backend/frontend flow

- `backend/app/main.py` exposes `/api/game/init` behind `auth.get_current_active_user`, then WebSocket `/api/ws` also requires a `token` cookie.
- Original `backend/app/game_logic.py` was a daily-trial loop; it has now been replaced by the life-simulation phase flow.
- Existing D100 roll support is reusable: `_handle_roll_request`, `roll_event` state, and frontend roll overlay already render rolls.
- `backend/app/state_manager.py` stores session metadata and histories separately under `game_data/sessions` and can be reused.
- `frontend/index.*` has been converted to the birth form, chart page, prelude page, and annual action simulator.

## Auth and reference notes

- `backend/app/auth.py` only supports JWT cookie from Linux.do OAuth today; local MVP will benefit from a guest-session path so the birth form is reachable without external OAuth.
- `README.md` now describes the YiMingQianTu MVP and local guest flow.
- `ichingshifa` contains `src/ichingshifa/jieqi.py` and `d.py`; initial search did not reveal a direct Bazi module, matching the design doc note that an independent `bazi_engine.py` is needed.

## Implementation notes

- Added a self-contained MVP Bazi engine with approximate solar-term month boundaries, four/three-pillar mode, element counts, useful elements, ten-god labels, luck cycles, and annual cycles.
- Added a deterministic fate mapper so the game can run without an OpenAI key: prelude generation, initial life state, annual D100 target calculation, and annual state changes.
- Replaced old daily trial logic with `birth_input -> chart_ready -> prelude_ready -> life_simulation -> ending` phases.
- Added guest login support and a development default `SECRET_KEY`, so local play is possible without Linux.do OAuth configuration.
- Windows `apply_patch` argument handling strips double quotes and treats percent-formats badly; code patches should prefer single-quoted literals and avoid percent format strings.
- Added chart UX improvements: calendar selector, start-age presets, five-element distribution board, ten-god summary, chart tags, luck-cycle timeline, and a return-to-birth reset button.
- Rebranded the live spectator page as a YiMingQianTu life observer page and removed CDN dependencies from `live.html`; `live.js` now renders escaped lightweight text locally.
- Updated the image-generation prompt in `openai_client.py` from the old fantasy/combat aesthetic to realistic life-stage scenes matching family, school, work, health, travel, and relationship events.
- Removed the unused old-named `start_trial_prompt.txt` prompt file after confirming no code references it.

## Completion audit 2026-06-07

- File structure now contains the requested core modules: `main.py`, `bazi_engine.py`, `fate_mapper.py`, `game_logic.py`, `state_manager.py`, `openai_client.py`, `websocket_manager.py`, and the four main role prompt files.
- Source/assets scan no longer finds legacy project-theme terms in `backend/app` or `frontend`; only the placeholder API-key sentinel remains in `openai_client.py`, which is intentional configuration handling.
- `prompts/` still includes extra compatibility prompts (`game_master.txt`, `start_game_prompt.txt`, `cheat_check.txt`) beyond the design doc; they are not old-themed and do not block MVP completion.
- Key gap found during audit: life prelude and annual narration are deterministic fallback logic today; the prompt files exist, but `game_logic.py` does not yet call `openai_client.get_ai_response` for Bazi analyst, prelude, GM, or annual-summary roles.
- Core logic smoke passes without filesystem writes: sample birth info reaches `life_simulation`, annual actions advance to age 60, ending is created, all required state keys exist, and MVP life-state attributes are present.
- Three-pillar mode smoke passes: unknown time produces `mode=三柱模式`, `hour_pillar=None`, and annual cycles cover start age through 60.
- Noted UX/backend mismatch: frontend allows free-text yearly action input, but backend `_normalize_focuses` currently discards actions not in the fixed option list and falls back to `随缘而行`.
- `state.schema.json` is intentionally loose and only requires a small subset of state keys; it does not yet validate chart/prelude/luck-cycle shape or all MVP fields.
- `run.sh` was still pointing at `/mydata/python/ElysiaGameImmortal`; this was corrected to start `backend.app.main:app` from the current project directory.
- `pytest` was added to `backend/requirements.txt` so the checked-in backend tests can run in a fresh dependency install.
- Inherited `redemption.py`/`db.py` were removed after confirming no active app references. Related database settings and unused SQL/MySQL dependencies were removed as well.
- Optional image storage/generation infrastructure was removed to match the design document's MVP scope. The frontend can still passively display images if narrative text contains `<img>` tags, but the backend no longer generates, stores, or mounts generated images.

## Follow-up implementation 2026-06-07

- Free-text yearly actions now map into the closest fixed action profile through keyword inference in `fate_mapper.infer_action_from_text`, so typed actions affect the D100 roll category instead of always falling back to `随缘而行`.
- `game_logic.py` now attempts optional AI enhancement for life prelude and latest annual summary when `openai_client.is_text_ai_enabled()` is true. It always creates deterministic fallback content first, so missing keys or invalid AI JSON do not break the game loop.
- Annual summaries now retain richer metadata: `year`, `focuses`, `roll_event`, and `annual_cycle`, which helps AI summarization and future archive/export features.
- New backend tests cover custom text mapping, no-AI prelude fallback, and custom text annual action behavior.
- `state.schema.json` now documents all top-level session fields, MVP life-state attributes, Bazi chart fields, luck/annual cycle shape, and annual-summary metadata.
- Added tests for AI JSON override behavior and state schema coverage.
- Added a WebSocket smoke test that logs in as guest, initializes a session, connects to `/api/ws`, sends `generate_chart`, and verifies the pushed state reaches `chart_ready`.

## Completion re-audit 2026-06-07

- Current file structure matches the MVP backend structure in the design document, with extra but harmless support modules for auth/security/live observer and tests.
- Old project theme, old path, database/redemption, and backend image-generation/storage scans return no source hits.
- Core flow smoke still passes: chart generation -> prelude -> start simulation -> yearly actions -> age-60 ending, with the required 12 life-state fields.
- Three-pillar mode still passes: unknown time gives `hour_pillar=None` and annual cycles cover start age through 60.
- Optional text AI is wired for prelude and annual summary; `bazi_analyst.txt` and `life_game_master.txt` remain prompt assets but are not yet active runtime roles.
- Frontend flow coverage remains aligned: birth form, chart, prelude, yearly action input, status panel, D100 roll overlay, ending display, and live observer page.

## Repeat completion audit 2026-06-07

- Design document MVP checklist remains covered: birth input, simplified four/three-pillar chart, luck cycles, annual cycles, prelude, yearly player action, D100 roll, persistent life-state panel, annual summary, and 60-year/health-zero ending.
- Validation passed again: backend tests, frontend JS syntax checks, static layout regression, no-cache/cache-dir check, and direct core-flow smoke.
- `run.sh` starts `backend.app.main:app` from the current project directory and no longer references the inherited path.
- Legacy-theme/reference scan only reports the expected negative assertion inside `tests/frontend_layout_check.mjs`; no active source hit was found for the old project path/theme, database/redemption, or backend image-generation/storage.
- Current non-blocking gaps are feature depth rather than MVP blockers: `bazi_analyst.txt` and `life_game_master.txt` are still prompt assets only, annual WebSocket E2E coverage stops at chart generation, and the frontend retains passive `<img>` background handling even though backend image generation was removed.

## AI Bazi analyst integration 2026-06-07

- `bazi_analyst.txt` is now active through `_handle_generate_chart_async`: chart generation first creates deterministic analysis, then optionally asks text AI for structured analysis when configured.
- New state fields: `bazi_analysis`, `chart_tags`, `life_topics`, `suitable_directions`, and `high_risk_fields`. The AI response can enrich these fields without mutating the authoritative computed pillars, five-element counts, luck cycles, or annual cycles.
- Deterministic fallback covers the same shape as the AI role: five-element balance, day-master status, useful/unfavorable elements, ten-god focus, luck-cycle themes, life topics, suitable directions, risk fields, and chart tags.
- Frontend chart view now renders life topics, suitable directions, and high-risk fields alongside the core chart cards.
- New tests cover no-AI chart-analysis fallback, AI chart-analysis override, schema documentation for `baziAnalysis`, and WebSocket chart generation with AI explicitly disabled to avoid accidental external calls in test environments.

## AI life GM integration 2026-06-07

- `life_game_master.txt` is now active after backend annual D100 resolution. It receives the authoritative roll event, state effect, before/after life state, Bazi analysis, annual cycle, luck cycle, and recent memory.
- The AI GM can add `gm_narrative`, `gm_scene_title`, `gm_memory_tags`, and `gm_state_update_suggestion` to the latest annual record. `gm_state_update_suggestion` is explicitly non-authoritative and does not mutate `life_state`.
- `display_history` now gets a separate `【年度叙事】` entry inserted before `【年度总结】`, so the yearly UI can show richer scene narration without interfering with the annual summarizer.
- Annual records now retain more replay/debug metadata: `main_focus`, `roll_modifiers`, `state_before`, `state_after`, and `luck_cycle`.
- New tests verify AI GM narrative insertion, state-update non-authority, annual metadata schema coverage, and that existing annual-summary AI behavior still works.

## WebSocket E2E expansion 2026-06-07

- `backend/tests/test_api_websocket.py` now drives the real `/api/ws` flow from guest login through `generate_chart`, `generate_prelude`, `accept_prelude`, two annual actions, and `ending`.
- The test handles both server message formats: `full_state` and JSON Patch `patch`, so it remains stable when payload-size diffing changes the WebSocket response shape.
- The E2E starts at age 59 to verify annual progression to age 60, then sends one more annual action to trigger the configured 60-year ending condition.
- The test verifies deterministic chart analysis, prelude creation, annual free-text action mapping, D100 roll metadata, final ending state, and annual summary count through the same WebSocket path the frontend uses.

## Completion check after AI/WebSocket work 2026-06-07

- MVP coverage is now high: birth input, simplified Bazi, three-pillar mode, chart analysis, luck/annual cycles, prelude, yearly choices, D100, state panel, optional AI Bazi/prelude/GM/summary roles, WebSocket state sync, live observer, and ending are all implemented and covered by tests or smoke checks.
- Validation passed again: backend tests, frontend JS syntax, static UI/layout assertions, app import, direct core-flow smoke, legacy/reference scan, cache-dir checks, and dependency-list review.
- Dependency list includes the runtime/test packages now used by the app and tests, including `jsonpatch` for WebSocket diffing and E2E patch application.
- Remaining gaps are polish rather than blockers: `start_game_prompt.txt` and `game_master.txt` are extra unused compatibility prompts; `cheat_check.py` and `cheat_check.txt` are present but not part of the current MVP flow; frontend still passively supports narrative `<img>` backgrounds although backend image generation was removed.
- Resolved semantic gap: README says the ending appears "到 60 岁"; annual progression now checks for ending again after age/year advancement, so a 59-year action that advances the player to 60 immediately produces the ending.

## Age-60 ending alignment 2026-06-07

- `_handle_annual_action` now calls `_finish_if_needed` after incrementing `current_age` and `current_year`, aligning runtime behavior with the documented "到 60 岁" ending condition.
- The WebSocket E2E now verifies that starting at 59 and submitting one annual action reaches `phase=ending`, `current_age=60`, and exactly one annual summary.
- A dedicated backend unit test covers the same age-60 immediate-ending condition without WebSocket transport.

## Docker deployment 2026-06-07

- Added `Dockerfile`, `.dockerignore`, and `docker-compose.yml`.
- Docker deployment uses port `7650` internally and externally: `0.0.0.0:7650->7650/tcp`.
- `docker-compose.yml` bind-mounts `./game_data` to `/app/game_data`, so deployed session data persists on the host.
- Container build and startup succeeded with the local HTTP/HTTPS proxy set to `http://127.0.0.1:10808`.
- Runtime checks passed against `http://127.0.0.1:7650`: homepage HTTP 200, guest login, game init, and full WebSocket flow through chart, prelude, life simulation, annual action, and ending.
- Container status after deployment: `Up ... (healthy)`.

## Login cleanup 2026-06-07

- Removed the Linux.do login link from `frontend/index.html`; the login page now exposes only guest play.
- Removed backend OAuth routes `/api/login/linuxdo` and `/callback`, OAuth client registration, Linux.do settings, `SessionMiddleware`, and unused OAuth dependencies (`Authlib`, `itsdangerous`).
- Source scan across active app/test/docs files now only finds Linux.do text in the negative frontend layout assertion.
- Docker deployment was rebuilt after cleanup; `http://127.0.0.1:7650` serves HTML without Linux.do/login references, guest API still works, and WebSocket gameplay flow still reaches ending.

## Custom AI API settings 2026-06-07

- Added an in-game `AI API` button and settings panel after entering the game. The panel accepts API Key, Base URL, and model name for OpenAI Chat Completions compatible providers.
- Added authenticated settings endpoints: `GET /api/settings/ai`, `POST /api/settings/ai`, and `DELETE /api/settings/ai`.
- Custom settings are stored per current guest/player under `game_data/ai_settings/<player_id>.json`. API keys are masked in API responses and are not included in WebSocket game state.
- Text AI calls now prefer the current player's custom API config when present, while preserving the deterministic local fallback when no global or custom key is configured.
- Validation passed locally: `python -B -m pytest -p no:cacheprovider backend/tests` (15 passed), `node --check frontend/index.js`, `node --check frontend/live.js`, and `node tests/frontend_layout_check.mjs`.
- Docker deployment on `http://127.0.0.1:7650` serves the new panel, contains no Linux.do login references, the custom settings API can save, mask, read, and clear a sample config, and the deployed WebSocket gameplay flow still reaches the age-60 ending.

## API test button and prelude event display 2026-06-07

- Added `POST /api/settings/ai/test`, which tests the current form input first, then saved player config, then server environment config if available.
- The in-game AI API panel now has a `测试连接` button and reports success/failure inline without saving secrets first.
- AI prelude `early_events` now normalizes structured objects such as `{age, year, event, impact}` into readable text, preventing raw Python dict strings from entering `display_history`.
- The frontend now renders early-life events as card rows with age/year metadata and impact text. It also recognizes legacy saved strings like `{'age': 1, ...}` and displays them as cards.
- Validation passed locally with 16 backend tests plus frontend JS/layout checks, then Docker was rebuilt and verified on port `7650`.

## Planned flowing-month / half-year loop 2026-06-07

- Current simulation advances one whole year per `annual_action`; `current_annual_cycle` is the only active short-cycle context.
- `bazi_engine.py` already has month-pillar helpers, so flowing-month analysis can reuse the existing approximate solar-term month boundary model instead of adding a new dependency.
- Recommended model: generate 12 `monthly_cycles` for each active year, group them into `current_half_year_months` for `上半年` and `下半年`, and let the player choose once per half-year.
- To preserve balance, state deltas from one half-year action should be scaled down from current yearly deltas, while a full-year aggregate summary can still be written after the second half.
- Current loading is a generic spinner and current roll reveal appears only after backend processing completes. A better UX is an immediate decision-pending overlay on submit, followed by a staged D100 reveal when `roll_event` arrives.

## Flowing-month / half-year loop implementation 2026-06-07

- `bazi_engine.py` now generates `monthly_cycles` for each age/year, with month name, pillar, half marker, theme, risk, opportunity, and roll modifiers.
- Session state now tracks `current_half`, `current_half_label`, `current_monthly_cycles`, and `half_year_summaries`.
- The existing WebSocket action name `annual_action` remains accepted for compatibility, but runtime now treats it as a half-year action: first action moves from `上半年` to `下半年`; second action advances age/year.
- D100 target calculation now includes a capped `流月` modifier derived from the current half-year's six flowing months.
- State changes from the old yearly resolution are scaled down for half-year cadence to avoid runaway attributes.
- Frontend simulation now renders a six-card `本半年流月` board, changes action wording to `本半年`, and shows a pending divination overlay immediately after the player submits.
- Roll reveal now has a staged `命书推演中 -> D100 已落定` flow with a shaking cup animation and themed loader.
- README and AI prompt wording were updated from annual-only phrasing to stage/half-year phrasing so custom AI receives flowing-month context consistently.
- Validation passed locally with 17 backend tests, frontend JS checks, and layout assertions. Docker deployment on port 7650 was rebuilt and verified through a real WebSocket flow: 59 岁上半年 -> 59 岁下半年 -> 60 岁结局.

## AI API modal UI 2026-06-07

- The AI API settings UI now uses a centered modal dialog instead of an inline card in the main content flow.
- Added a dimmed `modal-backdrop`, `role="dialog"`, `aria-modal="true"`, close button, Escape close behavior, and backdrop-click close behavior.
- The modal is mounted directly under `#app-container` rather than inside `#main-content`, avoiding `backdrop-filter` / grid containment side effects that shifted fixed positioning.
- Browser verification on `http://127.0.0.1:7650/?v=modal-final` confirmed the panel is fixed-position, visible with backdrop, and exactly centered (`centerDeltaX=0`, `centerDeltaY=0`); Escape closes it and resets `aria-expanded=false`.

## Multi-profile custom AI API settings 2026-06-07

- Custom AI settings now use a versioned profile store: each player can save multiple named API profiles with masked API Key, Base URL, model, enabled state, timestamps, and one active default profile.
- Old single-key settings are normalized in memory to the new v2 shape, so existing saved configs continue to work through the active default profile.
- Added profile endpoints: `POST /api/settings/ai/profiles`, `DELETE /api/settings/ai/profiles/{profile_id}`, `POST /api/settings/ai/profiles/{profile_id}/activate`, and `POST /api/settings/ai/profiles/{profile_id}/test`.
- `openai_client.py` still uses only the active profile for game AI generation, but profile testing can target a specific saved profile without accidentally falling back to another saved/default key.
- The AI API modal now has a left profile list and right editor. Users can add profiles, save/overwrite keys, clear a single key, test connection, set a default profile, and delete a profile.
- API responses never return raw API Keys; frontend displays only masked keys such as `sk-t...mary`.
- Validation passed locally with 18 backend tests, frontend syntax checks, layout assertions, deployed API CRUD smoke, and browser modal verification on Docker port `7650`.

## Full functional/UI/content test 2026-06-07

- Full automated checks passed: frontend syntax, frontend layout assertions, backend unit/WebSocket/API tests, Docker health, deployed WebSocket flow, desktop browser UI, and mobile browser UI.
- Content detail issue fixed: half-year summaries no longer render Python dict strings for state effects. They now display readable text such as `状态变化：学识 +4、心智 +2、压力 -2`.
- UI detail issue fixed: JSON Patch array removals and sparse arrays could make flowing-month cards show lone punctuation such as `、` or `忌：、体力透支`. Frontend patch handling now uses array `splice`, and month-card rendering cleans sparse/empty list values before joining.
- Old persisted session histories may still contain prior `状态变化：{'属性': 数值}` text. `index.js` and `live.js` now prettify those legacy lines at render time so old saves and the live observer page do not show raw dict syntax.
- Fresh-browser deployed validation on `http://127.0.0.1:7650` confirmed: birth form -> chart -> prelude -> life simulation -> half-year action works, the year banner switches to `下半年`, six month cards render, `badCards=[]`, and the summary text remains readable.
- Mobile viewport validation at `390x844` confirmed the status panel collapses into an off-canvas drawer, the main content remains single-column, and the AI API modal switches to a scrollable single-column layout.

## Continued full regression with AI mock 2026-06-07

- Added a focused deployed-browser validation using a temporary OpenAI-compatible mock endpoint reachable from Docker at `http://host.docker.internal:8765/v1`.
- Confirmed custom AI settings can drive actual game generation: deployed backend called `/v1/chat/completions` for chart analysis, life prelude, AI GM narration, and AI half-year summaries.
- Found and fixed a content detail issue: when AI half-year summary replaced the deterministic summary, the rendered `???????` could lose the explicit player action phrase such as `???????` / `???????`, even though backend classification and D100 roll type were correct.
- Fix: `backend/app/game_logic.py` now prepends an authoritative focus context line (`?? + ?? + ???...`) to AI summary display text when the AI text does not already contain it.
- Post-fix browser verification confirmed AI summaries now render lines like `59?????????????` and `59?????????????`, while state effects remain readable (`??????? +4??? +2??? +2`).
- Fresh mobile validation at `390x844` confirmed no horizontal overflow, status panel defaults collapsed, the AI API modal stays inside the viewport and scrolls, and the status panel can expand/collapse from the header button.
- Live observer verification confirmed `/live.html` loads, lists recent players, can select a player, and does not display raw legacy dict/object text.

## Page design/accessibility audit 2026-06-07

- Reviewed the page design against the current Web Interface Guidelines audit focus: responsive layout, touch target size, focus visibility, motion reduction, status announcements, and modal behavior.
- Issues found: mobile header/quick-age/action controls could fall below the 44px touch target threshold; there was no project-level `:focus-visible` rule; motion-heavy roll/loader animations did not honor `prefers-reduced-motion`; status/error text did not announce changes with `aria-live`; and the centered AI API modal did not trap Tab focus inside the dialog.
- Fixes applied: `frontend/index.css` now sets consistent 44px targets, visible focus rings, 16px input text, styled action submit button, checkbox accent color, and a reduced-motion override.
- Fixes applied: `frontend/index.html` now adds `aria-live` for phase/login/API status, useful `name`/`autocomplete` attributes, and versioned CSS/JS URLs to prevent stale browser cache from hiding design fixes.
- Fixes applied: `frontend/index.js` now traps Tab focus inside the AI API modal while it is open and still closes with Escape.
- Deployed browser verification at `390x844` confirmed `smallTargets=[]`, no horizontal overflow, `prefers-reduced-motion` and `:focus-visible` rules are loaded, live regions are present, action button min-height is `44px`, and modal focus remains inside the dialog.

## Luck-cycle start-age correction 2026-06-07

- User-reported design issue: ???? was effectively treated as a gameplay-stage value instead of an independent birth-chart ?? value.
- Root cause: `backend/app/bazi_engine.py` generated ?? with a simple fixed age band and did not calculate ?? from the birth datetime relative to solar-term boundaries. The sexagenary index used to advance from the month pillar was also corrected to match the actual ?? index.
- Fix: ?? now calculates `age_start_months` from birth to the next/previous approximate solar-term boundary according to ??/??, using the traditional `3 days ? 1 year` conversion. Each cycle stores `age_start_label` / `age_end_label`, e.g. `9?11??-19?10??`.
- Fix: `fate_mapper.find_luck_cycle()` now uses month-based boundaries when available, so the current ?? at game start is selected from real ?? ranges rather than from the chosen simulation start age.
- UI fix: the chart cards now show `??`, and the ????? prefers the month-aware labels instead of plain integer age ranges.
- Deployed verification: with birth `2000-02-05 08:30`, male, game start age `30`, the chart shows `??9?11??` and the timeline begins `9?11??-19?10??`; formal start at age `30` shows current ?? `??`, matching the `29?11??-39?10??` cycle.

## Start-age 6 and narrative-detail follow-up 2026-06-07

- Frontend and backend now clamp/play from start_age 6 (`frontend/index.html`, `backend/app/game_logic.py`, `backend/app/bazi_engine.py`, `backend/app/state.schema.json`).
- Deterministic prelude now keeps at least 4 early-life events even at age 6 and adds more family/body/learning/inner-topic context.
- Deterministic stage narrative now includes action landing, concrete scene, Bazi/timing context, D100 result, and state aftereffects.
- Half-year summary now expands roll details, modifier sources, state trajectory, and long-term narrative hooks; short AI GM/summary/prelude outputs are supplemented with deterministic detail instead of replacing detail with sparse text.
- Deployed age-6 WebSocket smoke on port 7650 verified: prelude_len=375, early_events=4, stage_len=515, summary_len=574, and scene/roll/state markers present.

## Gameplay depth optimization 2026-06-07

- Added current age-stage metadata (`current_stage`) with labels/goals/summaries and dynamic action options for childhood, adolescence, early adult, building, midlife, and late-life phases.
- Childhood no longer exposes adult-heavy actions such as `????` or `????`; free-text adult actions at age 6 are safely redirected to age-appropriate actions such as `????`.
- Added deterministic stage-event hooks to each half-year record, so summaries and stage narratives now have a concrete age-appropriate event source.
- Added long-term systems in `life_systems`: relationship network, study/career, and assets. These update from life state after each action and are shown in the status panel with relationship snapshots.
- Enhanced endings now include 7 dimension grades, achievements, regrets, key turning points, final life systems, and relationship snapshots; frontend renders these as an `ending-archive`.
- Deployed smoke on port 7650 verified age-6 stage/options/system/event behavior and age-59-to-ending archive fields.

## Life-goal system optimization 2026-06-07

- Added five selectable life goals: stable abundance, recognized work, warm bonds, inner peace, and free explorer.
- Backend now tracks `life_goals`, `active_life_goal_id`, and `goal_progress`; half-year records store goal progress before/after, and AI prompts receive goal context.
- Prelude UI now renders selectable life-goal cards before starting life; status panel shows active goal progress; ending archive shows final goal completion.
- Deployed WebSocket smoke verified selecting `warm_bonds`, active goal title `????`, 5 goals, and half-year `goal_progress_after`.

## Player-experience helper optimization 2026-06-07

- Added a beginner guide on the birth page with a short play loop checklist and a compact glossary for 大运、流年、流月、D100.
- Added a current-turn decision guide above the simulation board. It summarizes the current age stage, active life-goal progress, current 大运/流年, aggregated flowing-month opportunities, and risk reminders before the player chooses the half-year action.
- Added a narrative toolbar that classifies history entries into 判定、阶段、总结、成就、结局、系统, supports quick filtering, and collapses long histories to the latest 12 entries by default.
- Added a frontend-only Markdown life-archive export. After chart generation, the header “导出档案” button can save birth/chart summary, current state, goal progress, achievements, milestones, ending summary, and full display history.
- Browser deployment smoke found a subtle reset-to-age-6 patch artifact: action chips could render as blank buttons even though the server state had valid `action_options`. The frontend now cleans action options and falls back to `current_stage.action_options`, preventing sparse/blank chip rendering.
- Static checks passed for the new UI/JS wiring: `node --check frontend/index.js`, `node --check frontend/live.js`, and `node tests/frontend_layout_check.mjs`.
- Backend regression still passes with 29 tests; the first sandboxed pytest attempt failed only because Windows temp directory writes were denied, then passed after running pytest with approved elevated permissions.
- Docker was rebuilt on port `7650`; deployed desktop smoke verified guide, turn guide, filter chips, archive button, age-6 action chips, half-year progression, achievement/summary history typing, and readable state effects. Mobile smoke at `390x844` verified no horizontal overflow, collapsed status panel, single-column guide/history layout, and no visible interactive target below 44px.

## Raw choice / Bazi event / Life memory follow-up 2026-06-09

- Design decision: 玩家自由输入是叙事事实，后台行动归类只是判定工具；因此半年度记录同时保存 `raw_choice_text` 和 `normalized_focuses`，确定性总结与 AI prompt 都必须优先使用原句。
- Design decision: 八字不再只用于结算解释，`event_pool.pick_stage_event()` 使用命盘喜忌、十神、命盘标签和大运/流年主题为事件模板加权；评分使用模板专属标签，避免所有同类行动因继承行动 meta 而同分。
- Design decision: 每个半年都会生成一条 `life_memory`，并按年龄门槛在 18/22/35 岁等节点产生 `memory_echoes`，让童年习惯、关系遗憾或迁移经验在后续人生重新出现。
- Follow-up: 玩家需要在提交前知道系统如何理解自由输入，因此行动预览承担“预归类 + 命盘事件倾向”职责；真正写入半年度记录时仍以后端 `choice_intent` 和权威事件抽取为准。
