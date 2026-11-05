#!/usr/bin/env python3
"""Check shipped ELF symbol/version pairs against Bookworm runtime libraries.

This checks GLIBC, GCC, GLIBCXX and CXXABI only. It does not resolve the
complete dependency graph or establish runtime correctness.
"""
import argparse
import hashlib
import json
import lzma
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--arch', required=True, choices=['armhf', 'arm64'])
parser.add_argument('--package', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)


def run(*command):
    return subprocess.check_output(command, text=True)


def elfs(root):
    for path in root.rglob('*'):
        if path.is_file() and not path.is_symlink():
            with path.open('rb') as stream:
                if stream.read(4) == b'\x7fELF':
                    yield path


def symbols(dump, undefined):
    return {(symbol, version) for line in dump.splitlines()
            if (' UND ' in line) == undefined
            for symbol, version in re.findall(
                r'(\S+?)@@?((?:GLIBC|GLIBCXX|CXXABI|GCC)_[\w.]+)', line)}


index_url = f'https://deb.debian.org/debian/dists/bookworm/main/binary-{args.arch}/Packages.xz'
index = urllib.request.urlopen(index_url).read()
(args.output / 'Packages.xz').write_bytes(index)
blocks = lzma.decompress(index).decode().split('\n\n')
extraction = tempfile.TemporaryDirectory(dir=args.output)
workspace = Path(extraction.name)
target = workspace / 'target'
metadata = {}
for name in ['libc6', 'libgcc-s1', 'libstdc++6']:
    block = next(block for block in blocks if block.startswith(f'Package: {name}\n'))
    fields = dict(line.split(': ', 1) for line in block.splitlines()
                  if ': ' in line and not line.startswith(' '))
    data = urllib.request.urlopen('https://deb.debian.org/debian/' + fields['Filename']).read()
    if hashlib.sha256(data).hexdigest() != fields['SHA256']:
        raise SystemExit(f'Checksum mismatch for {name}')
    deb = args.output / Path(fields['Filename']).name
    deb.write_bytes(data)
    subprocess.run(['dpkg-deb', '-x', str(deb), str(target)], check=True)
    metadata[name] = fields

exports = set()
for path in elfs(target):
    exports.update(symbols(run('readelf', '-W', '--dyn-syms', str(path)), False))
payload = workspace / 'payload'
subprocess.run(['dpkg-deb', '-x', str(args.package), str(payload)], check=True)
expected_machine = {'armhf': 'ARM', 'arm64': 'AArch64'}[args.arch]
results = []
for path in elfs(payload):
    dump = run('readelf', '-W', '-h', '-l', '-d', '-V', '--dyn-syms', str(path))
    relative = path.relative_to(payload)
    evidence = args.output / 'readelf' / relative
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.with_suffix(evidence.suffix + '.txt').write_text(dump)
    machine = re.search(r'Machine:\s+(.+)', dump).group(1).strip()
    missing = sorted(symbols(dump, True) - exports)
    results.append(dict(path=str(relative), machine=machine, missing=missing,
                        needed=re.findall(r'Shared library: \[(.*?)\]', dump)))
    print(f'{relative}: machine={machine}, missing={missing}')
report = dict(arch=args.arch, package=str(args.package),
              sha256=hashlib.sha256(args.package.read_bytes()).hexdigest(),
              control=run('dpkg-deb', '-f', str(args.package)),
              index=index_url, target_packages=metadata, elf=results)
(args.output / 'abi.json').write_text(json.dumps(report, indent=2) + '\n')
if not results or any(row['missing'] or row['machine'] != expected_machine for row in results):
    raise SystemExit('Bookworm ABI check failed')
print('Bookworm ABI check passed')
