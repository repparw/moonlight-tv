# Bookworm ABI verification

The Raspberry Pi workflow runs its cross compiler inside Debian Bookworm.
GCC's cross installation supplies implicit headers, CRT objects, and libc even
with `--sysroot`. Keep that compiler distribution aligned with the Bookworm
sysroot. Changing only the Ubuntu runner version can produce packages that link
successfully but require newer glibc symbols.

The workflow logs a C23 `strtol` probe with `-v -H -Wl,-t`, builds verbosely, and
checks every ELF in each resulting package before uploading the package.
The separate ABI artifact retains compiler paths, raw readelf output, package
hashes, target package metadata, and missing symbol/version pairs.

Run the same gate with Python 3, binutils, and dpkg installed:

```sh
python3 scripts/raspi/check-abi.py --arch armhf --package build/moonlight-tv_VERSION_armhf.deb --output build/abi-armhf
python3 scripts/raspi/check-abi.py --arch arm64 --package build/moonlight-tv_VERSION_arm64.deb --output build/abi-arm64
```

The gate downloads official Debian Bookworm libc6, libgcc-s1, and libstdc++6,
verifies their SHA256 values against the downloaded package index, and compares
versioned undefined symbols against their exports. It also checks ELF machine
architecture and rejects packages without ELF files. It checks symbol names as
well as versions. A maximum-version comparison alone would miss absent symbols
within an otherwise available version.

This is a partial ABI check, not a target runtime test. It does not resolve all
transitive dependencies, validate package dependency declarations, or prove
compatibility with every Raspberry Pi OS image. In particular, external SDL,
font, multimedia, and crypto library availability still needs target validation.
The workflow needs privileged container access for the existing sysroot action's
binfmt registration and chroot setup.
