# Red loops for React Native apps

Read the project first: its test command and scripts in `package.json`, whether Detox or Maestro is
installed, and how it captures crashes. Use what the project has; name a tool here only after
confirming it is installed.

| Situation | Loop |
|---|---|
| Pure logic (selectors, formatters, reducers) | a test with the project's runner, or a `node` script that imports the module and asserts the symptom with the captured input |
| A hook or component | a test at the component's public seam with the project's Testing Library setup; switch props in place when the bug follows an identity change |
| Wrong data from the backend | save the real response (redacted) to a file and replay it through the mapping code |
| Only reproducible on a device | a scripted trigger plus a filtered log: a deep link (`xcrun simctl openurl booted <url>`, `adb shell am start -W -a android.intent.action.VIEW -d <url>`) and the log stream (`xcrun simctl spawn booted log stream --predicate '<filter>'`, `adb logcat -s <tag>`) |
| A crash from production | the crash frame from the crash reporter, symbolicated (native symbols, or the release source map for a JavaScript frame); the loop drives the input that reaches that frame |
| Appeared between two versions | `git bisect run <loop command>` when the loop runs unattended |
| Slow or janky since a change | a timing harness around the suspect code on a realistic data size, then a release build on the slowest supported device with the profiler the project uses; record the before number |

## Flaky tests

Run the single test many times with a fixed seed or fake timers, and record the failure rate. Make
the suspected race deterministic: control the order in which promises resolve, or inject a delay at
the point you suspect, until the failure is reliable.

## Native and JavaScript boundaries

A symptom on one platform only usually lives in native code, configuration or a library's native
module: compare the platform builds before reading shared JavaScript.
