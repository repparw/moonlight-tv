# Agent guidance

- Build and test locally (Desktop with sanitizers):
  `cmake -B build -DCMAKE_BUILD_TYPE=Debug -DTARGET_DESKTOP=ON -DWITH_SANITIZE=address,undefined && cmake --build build && xvfb-run ctest --test-dir build --output-on-failure`
- Keep `submodules` pinned explicitly when comparing baseline vs candidate builds (`moonlight-common-c`, `ss4s`); use `.github/workflows/benchmark-build-pair.yml` for matched webOS IPK pairs.
- Physical LG C3 GUI actions (installing/launching Moonlight, Luna foreground calls) must hold `tv-lock` from `repparw/homelab-devices` (`tv/bin/tv-lock`, lock `$XDG_STATE_HOME/homelab-tv/gui.lock`). Read TV/Wi-Fi/Moonlight state with `tv/bin/tv-snapshot`.
- Settled Alpha + LG C3 measurements and open client leads (120 Hz NDL presentation) live in `repparw/moonshine:docs/alpha-c3-baselines.md`.
- Review standards (judgement calls): [CODING_STANDARDS.md](CODING_STANDARDS.md).
