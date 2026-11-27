# Coding Standards (Review Checklist)

Deterministic checks (desktop tests, ASan/UBSan sanitizer runs, Raspberry Pi ELF
ABI gates, shellcheck) belong in CI. Apply these judgement rules during review:

- **Explicit submodule provenance:** Performance and bugfix PRs touching
  `moonlight-common-c` or `ss4s` must record exact baseline and candidate
  commit SHAs and keep instrumentation isolated from functional changes.
- **No silent assertion stripping:** Test harnesses must keep `assert()` active
  in CI and local verification runs (reject builds where dependency headers or
  flags disable assertions).
- **Separate client, server, and submodule PRs:** Keep `moonlight-common-c`,
  `ss4s`, `moonlight-tv`, and `moonshine` changes in independent PRs unless
  strictly coupled.
- **Explicit operator handoff:** End verification reports with the exact
  operator action (`merge`, `recover`, or `none`) and never claim physical TV
  presentation from launch exit codes or submitted-frame counts alone.
