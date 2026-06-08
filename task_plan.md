# YiMingQianTu retrofit plan

## Goal
Retrofit `YiMingQianTu` to match the design document: a birth-info driven Bazi + life simulation text game.

## Phases

1. [complete] Inspect design document and current project structure.
2. [complete] Map current backend/frontend flow and reusable systems.
3. [complete] Add Bazi/luck-cycle engine and life-state mapping.
4. [complete] Update backend API/WebSocket game flow and prompts.
5. [complete] Update frontend pages from trial UI to birth chart/prelude/life simulation UI.
6. [complete] Verify with tests/build or focused smoke checks.
7. [complete] Improve chart/prelude UX: calendar select, start-age presets, five-element board, luck timeline, and return-to-birth flow.
8. [complete] Rebrand live view from legacy cultivation spectator UI to YiMingQianTu life observer UI.
9. [complete] Re-run focused validation and update project notes.
10. [complete] Clean old fantasy-themed image-generation prompt text, remove the unused old `start_trial_prompt.txt`, and re-run focused validation.
11. [complete] Audit project completion against design document; fix stale `run.sh`, add test dependency, update README validation notes, and re-run checks.
12. [complete] Add free-text annual action mapping and optional AI enhancement for prelude/annual summaries with deterministic fallback.
13. [complete] Remove unused redemption/database legacy modules, tighten session schema, and add AI/schema tests.
14. [complete] Remove unused backend image generation/storage infrastructure and add a WebSocket chart-generation smoke test.
15. [complete] Re-audit project completion against MVP scope after cleanup and verify no regressions.
16. [complete] Repeat completion audit against the design document, verify current tests/static checks, and record remaining non-blocking gaps.
17. [complete] Connect the optional AI Bazi analyst role, expose analysis fields in the chart UI, and verify deterministic fallback.
18. [complete] Connect the optional AI life GM role for annual narrative while keeping backend D100 and state changes authoritative.
19. [complete] Expand WebSocket E2E coverage from chart generation to prelude, life start, annual action, and ending.
20. [complete] Re-check project completion after AI role and WebSocket E2E work, including validation, scans, dependency list, and remaining polish gaps.
21. [complete] Align the age-60 ending trigger with README/design semantics so reaching 60 immediately ends the run.
22. [complete] Check current project runnability with dependency import, API/WebSocket smoke, Uvicorn lifecycle smoke, tests, and port availability.
23. [complete] Add Docker deployment on port 7650, build/start the container, and verify HTTP/API/WebSocket flow.
24. [complete] Remove Linux.do OAuth login from frontend/backend/dependencies and redeploy Docker service.
25. [complete] Add in-game custom AI API settings for the current guest/player and verify local plus Docker deployment behavior.
26. [complete] Add an AI API connection test button and render structured prelude events as readable cards instead of raw object strings.
27. [complete] Add flowing-month analysis, change life simulation from annual choices to half-year choices, and redesign processing/roll animations.
28. [complete] Change the AI API settings UI from an inline panel to a centered modal dialog with backdrop and keyboard close behavior.
29. [complete] Add multi-profile custom AI API settings with per-profile keys, activation, testing, deletion, migration, and Docker verification.
30. [complete] Run full functional/UI/content-generation testing, fix sparse JSON Patch month-card artifacts, and improve state-effect display formatting.

31. [complete] Continue full functional/UI/content-generation regression, verify custom AI generation with a local OpenAI-compatible mock, preserve action context in AI half-year summaries, rebuild Docker, and re-check deployed desktop/mobile/live flows.

32. [complete] Audit page design against current web UI guidelines, improve touch targets, keyboard focus, reduced-motion handling, live status announcements, modal focus containment, and static asset cache busting; rebuild and verify Docker deployment.

33. [complete] Fix luck-cycle start-age design: calculate ???? from birth-to-solar-term distance instead of simulation start age, show ?? labels with months, and verify current luck cycle independently from game start age.

34. [complete] Lower playable start age to 6 and expand deterministic/AI-guarded prelude, stage narrative, and half-year summary detail.

35. [complete] Add age-stage action gating, stage event hooks, long-term relationship/career/assets systems, and enhanced ending archive.

36. [complete] Add selectable life-goal system with goal progress, summary integration, status UI, and ending completion feedback.

37. [complete] Add achievements and life milestone process-feedback system with status and ending archive display.

38. [complete] Add player-experience helpers: beginner guide, term glossary, current-turn decision guide, filterable/collapsible narrative history, and Markdown life-archive export.

39. [complete] Add active life retrospection: let players voluntarily end the current run, generate an ending archive with a retrospection reason, and expose the action in the simulation UI.

## Decisions

- Keep changes in `YiMingQianTu` only.
- Use deterministic fallback narrative when no AI key is configured, so the MVP remains runnable locally.
- Preserve useful existing infrastructure such as FastAPI, WebSocket, state persistence, and D100 roll logic where practical.

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
| apply_patch rejected PowerShell pipe encoding | Create planning files | Used underlying Codex apply-patch executable with patch as an argument |
| Windows apply_patch argument stripped double quotes / percent format strings | Added Python/HTML/JSON files | Used single-quoted literals where valid and escaped double quotes for JSON |
| TestClient smoke created guest session files | API smoke test | Removed generated files with apply_patch; empty directories remain harmless |
| `git status` inside `YiMingQianTu` failed because it is not a repo | Resume audit | Treat `YiMingQianTu` as a project folder under the workspace; continue with direct file inspection |
| `python -m pytest backend/tests` failed because pytest was not installed | Validation | Installed `pytest` into the user Python environment after approval, then tests passed |
| Removing `.pytest_cache` with escalated PowerShell failed due ACL owner mismatch | Cleanup | Removed it inside the sandbox after path verification; no cache directories remain |
| `run.sh` still changed directory to `/mydata/python/ElysiaGameImmortal` | Completion audit | Rewrote `run.sh` to resolve its own project directory and run `backend.app.main:app` |
| PowerShell piped Unicode smoke script produced a false assertion on Chinese keys | Repeat audit | Re-ran the same core-flow smoke with ASCII `\u` escapes; chart/prelude/annual/ending and three-pillar checks passed |
| Docker BuildKit repeatedly attempted Docker Hub metadata and failed with timeout/EOF | Rebuild after flowing-month changes | Rebuilt successfully with `DOCKER_BUILDKIT=0`, then redeployed the healthy 7650 container |
| Deployed smoke used raw Chinese literals through a PowerShell here-string and produced false negative text checks | Age-6 deployed content verification | Re-ran smoke using Unicode escape literals for checked markers; deployed age-6 flow verified correctly |
| Browser smoke found blank age-6 action chips after reset/chart/prelude WebSocket patch sequence | Experience-helper deployment validation | Added `cleanActionOptions()` so sparse/blank action option patches fall back to `current_stage.action_options`; redeployed and verified no blank chips |

40. [complete] Add hidden ending system: classify rare/hidden/legendary endings from final-state combinations, display the unlocked ending in the archive, and include it in Markdown export.

41. [complete] Add ending codex collection: persist unlocked endings across reset for the same visitor, show collection progress and locked-ending clues, and include codex progress in archive export.

42. [complete] 将阶段事件池模块化到 `backend/app/event_pool.py`，并加入连续行动反馈：D100 加成、状态惯性、机会成本提醒、前端状态卡、档案导出、schema 与测试覆盖。

43. [complete] 新增行动预览系统：后端生成当前阶段每个行动的愿望同频、预计 D100 目标、属性走向、风险属性与连续投入预判；前端在提交前展示决策卡并标记愿望契合/连续可加成行动。

44. [complete] 修复人生模拟阶段底部行动/聊天区过高遮挡主内容：加入紧凑行动栏、内部滚动、输入栏 sticky 和桌面/移动端高度上限。
