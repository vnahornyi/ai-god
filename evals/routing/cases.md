# Routing eval — cases (fixed 2026-11-01, before the first run; key for cases 10, 11 and 13 changed
2026-11-02 when the estimation skill was removed, and for cases 14–15 when the worklog skill became a
personal skill rather than a stage; key for cases 10–11 changed 2026-11-09 when a personal estimate
card that only adds up the developer's numbers was added; all are requirement changes, agreed with
the developer)

What a fresh session loads for a request, judged against `skills/ai-workflow`. The runner receives
only the prompts (the `Prompt` column); everything else here is the key. A case passes when the
stage matches (or is one of the accepted stages), every required domain skill is loaded, and no
must-not skill is loaded. "none" = no skill of that kind. Third-party skills (document, browser,
skill-creator and the like) count as must-not wherever a project skill covers the request.

| # | Prompt | Stage | Required domain | Must not |
|---|---|---|---|---|
| 1 | сплануй задачу: додати екран налаштувань сповіщень у мобільному застосунку на React Native, ось макет https://www.figma.com/design/abc/Settings?node-id=1-2 | wf-plan | figma-inspect, frontend-craft | wf-review, wf-worklog, wf-implement |
| 2 | Plan the migration of the auth token storage from AsyncStorage to the keychain | wf-plan | none | wf-implement |
| 3 | реалізуй план .claude/plans/PROJ-12-sale-label.md (це React Native компонент) | wf-implement | frontend-craft | wf-plan, wf-review |
| 4 | fix the typo in the README heading | wf-implement | none | wf-plan, frontend-craft |
| 5 | зроби ревʼю мого PR на цій гілці | wf-review | none | wf-peer-review, wf-implement, wf-plan |
| 6 | review my staged diff before I commit it | wf-review | none | wf-peer-review, wf-implement |
| 7 | пройдись по PR колеги https://github.com/acme/app/pull/7 | wf-peer-review | none | wf-review, wf-implement |
| 8 | Walk me through someone else's pull request that adds a Reanimated bottom sheet | wf-peer-review | react-native-animations | wf-review, wf-implement |
| 9 | глянь коментарі бота на моєму PR і підкажи що відповісти | wf-review | none | wf-peer-review, wf-implement |
| 10 | оціни скільки годин піде на цю задачу | none + estimate-card | none | any wf-* |
| 11 | How many hours would the plan in .claude/plans/PROJ-40-filters.md take? | none + estimate-card | none | any wf-* |
| 12 | створи jira задачу на рефакторинг навігації | wf-jira-task | none | wf-implement |
| 13 | Write a Jira ticket for this crash with an hour estimate | wf-jira-task | none | wf-implement, wf-worklog |
| 14 | залогуй мені години за вчора | none + wf-worklog | none | wf-jira-task |
| 15 | close my week in Tempo | none + wf-worklog | none | none |
| 16 | add a swipe-to-dismiss gesture with a light haptic to the toast component | wf-implement | react-native-animations, frontend-craft | wf-plan |
| 17 | чи вплине client-side рендеринг сторінок категорій на органічний пошук? | none | seo | wf-plan, wf-implement |
| 18 | the pose model runs at 12 fps on iPhone and the log shows unassigned nodes — make it faster | wf-implement or wf-debug | realtime-vision-pipeline, apple-neural-engine | wf-plan |
| 19 | this component has a switch over six payment types that grows every sprint — should we refactor it? | wf-plan or none | design-patterns | wf-implement |
| 20 | запусти реалізацію плану фоном в окремому worktree | wf-implement | worktree | wf-plan |
| 21 | open the feature branch worktree in VS Code | none | worktree | wf-implement, wf-plan |
| 22 | What does `git rebase --onto` do? | none | none | any wf-* skill |
| 23 | Explain the difference between useMemo and useCallback in one paragraph | none | none | any wf-* skill |
| 24 | чому падає екран оплати після повернення з бекграунду? | wf-debug | none | wf-plan |
| 25 | Tests started flaking since yesterday's merge — find out why | wf-debug | none | wf-plan, wf-review |
| 26 | the product list scroll became janky after the last release | wf-debug | frontend-craft | wf-plan |
| 27 | add a new skill to ai-god for writing release notes | wf-implement or none, and reads the root `AGENTS.md` of ai-god (maintenance rules) | none | skill-creator, wf-plan |
| 28 | Implement this Figma frame as a component: https://www.figma.com/design/xyz/Cards?node-id=4-5 | wf-implement | figma-inspect, frontend-craft | figma-design-to-code, design-in-figma, wf-plan |
| 29 | сплануй епік з пʼяти задач для нового модуля оплат | wf-plan | none | wf-implement |
| 30 | після ревʼю свого PR я прийняв дві знахідки з пʼяти — що далі? | wf-retro | none | wf-plan, wf-peer-review |
| 31 | знайди в коді, як рахується сума кошика, і поясни | none | none | any wf-* skill |
| 32 | run the unit tests and tell me which ones fail | none | none | wf-plan, wf-review, wf-implement |
| 33 | закоміть поточні зміни | none or wf-implement | none | wf-plan, wf-review |
| 34 | порівняй цей репозиторій із https://github.com/acme/toolkit і скажи, що нам варто взяти | none | none | any wf-* skill |
| 35 | rename the formatPrice helper to formatMoney everywhere in the repo | wf-implement | none | wf-plan, wf-review |
| 36 | зверстай стилі цього екрана піксель-в-піксель за макетом, логіка вже є: https://www.figma.com/design/abc/Checkout?node-id=7-8 | wf-implement | figma-inspect, frontend-craft | figma-design-to-code, design-in-figma, wf-plan |
| 37 | Add the press and appear animations from the Figma prototype to the Toast component: https://www.figma.com/design/abc/Toast?node-id=9-1 | wf-implement | figma-inspect, react-native-animations | figma-design-to-code, design-in-figma, wf-plan |

Cases 24–26 measure requests that had no route before `wf-debug`; 31–35 measure requests the router
has no row for. 36–37 (added 2026-11-10) measure assigned visual work.

## Runner brief

```text
You are measuring skill routing, not doing the tasks. Read <abs>/global/AGENTS.md (the global
instructions every session gets) and follow its "Task routing" section exactly as a real session
would: load or read whatever skills it tells you to, using the skills you have. Then, for each
prompt in <abs prompt file>, decide which skills a session would load for it. Do not perform any
prompt, do not edit, stage, commit or push anything, and do not spawn agents.
Reply with one markdown table only: | # | stage skill | domain skills | other skills | — use "none"
where nothing applies, skill names exactly as listed.
```
