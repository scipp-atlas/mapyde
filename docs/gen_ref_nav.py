"""Generate the code reference pages and navigation.
From: https://github.com/mkdocstrings/python/blob/32030df6a98b527a3f5167e1836a36efae6530d4/docs/gen_ref_nav.py
"""

from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in sorted(Path("src").rglob("*.py")):
    module_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    if parts[-1] in ["__main__", "_version"]:
        continue
    elif len(parts) > 1 and parts[1] == "cli":
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(full_doc_path, ".." / path)

with mkdocs_gen_files.open("reference/SUMMARY.txt", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
