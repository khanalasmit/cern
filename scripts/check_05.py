# -*- coding: utf-8 -*-
import io, re
t = io.open(r"output\05-release-notes.md", encoding="utf-8").read()
print("sections:", re.findall(r"^## .*", t, re.M))
print("snapshots:", len(re.findall(r"^### Snapshot", t, re.M)))
print("has FOO env-syntax note:", "$(FOO)" in t)
print("has BadQueryException:", "BadQueryException" in t)
print("has ConfigPackages text:", "ConfigPackage" in t)
print("size:", len(t))