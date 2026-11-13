#!/usr/bin/env python3
"""Git's core idea, from scratch: store files by the hash of their contents. A from-scratch worked example.

  python hashstore.py --step 1..4      run one step of the lesson (each prints something you can check by eye)
  python hashstore.py --compare-git    hash a few strings here and with the real `git hash-object`, and compare

The one mechanism: an object's name IS the SHA-1 of "blob <size>\\0<content>". Same content, same name, stored once.
Left out on purpose: trees, commits, packfiles, compression details beyond zlib, refs, and SHA-256 repositories.
"""
import hashlib, shutil, subprocess, sys, tempfile, zlib
from pathlib import Path


def blob_id(data: bytes) -> str:
    # Step 1: the header is part of what gets hashed, so "hello" as a blob is not sha1("hello").
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


class Store:
    def __init__(self, root: Path):
        self.root = root

    def put(self, data: bytes) -> str:
        # Step 2: write under objects/<first 2 hex>/<rest>, zlib-compressed, exactly like .git/objects
        oid = blob_id(data)
        p = self.root / oid[:2] / oid[2:]
        if not p.exists():  # Step 3: identical content is stored once
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(zlib.compress(b"blob %d\0" % len(data) + data))
        return oid

    def get(self, oid: str) -> bytes:
        raw = zlib.decompress((self.root / oid[:2] / oid[2:]).read_bytes())
        header, _, body = raw.partition(b"\0")
        assert header == b"blob %d" % len(body), "corrupt object"
        assert blob_id(body) == oid, "content does not match its name"  # Step 4: integrity for free
        return body


def step(n):
    tmp = Path(tempfile.mkdtemp())
    s = Store(tmp / "objects")
    if n == 1:
        print("sha1('hello\\n')        =", hashlib.sha1(b"hello\n").hexdigest())
        print("blob_id('hello\\n')     =", blob_id(b"hello\n"), " <- what git calls it")
    if n >= 2:
        a = s.put(b"hello\n"); print("put hello ->", a, "stored at", f"objects/{a[:2]}/{a[2:]}")
    if n >= 3:
        b = s.put(b"hello\n"); files = [p for p in (tmp / "objects").rglob("*") if p.is_file()]
        print("put hello again ->", b, "| objects on disk:", len(files))
    if n >= 4:
        print("get ->", s.get(a))
        p = tmp / "objects" / a[:2] / a[2:]
        raw = zlib.decompress(p.read_bytes()).replace(b"hello", b"jello"); p.write_bytes(zlib.compress(raw))
        try:
            s.get(a)
        except AssertionError as e:
            print("after tampering, get ->", "error:", e)
    shutil.rmtree(tmp)


def compare_git():
    git = shutil.which("git")
    if not git:
        sys.exit("git not found: the comparison needs the real tool")
    ok = True
    for data in [b"", b"hello\n", "naïve café ☕\n".encode(), b"\x00\x01binary"]:
        real = subprocess.run([git, "hash-object", "--stdin"], input=data, capture_output=True).stdout.decode().strip()
        mine = blob_id(data)
        ok &= real == mine
        print(f"{'match' if real == mine else 'DIFF '}  {mine}  {data[:20]!r}")
    print("all match" if ok else "mismatch"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if "--compare-git" in sys.argv:
        compare_git()
    else:
        step(int(sys.argv[sys.argv.index("--step") + 1]) if "--step" in sys.argv else 4)
