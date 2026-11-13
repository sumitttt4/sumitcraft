# From scratch: a content-addressed store (git's core)

A worked example of the from-scratch method. The steps, the predictions to ask for, and the real-tool comparison:

| Step | Idea | Ask before running | Run |
|---|---|---|---|
| 1 | An object's name is SHA-1 of a header plus the content | "Will `blob_id('hello\n')` equal `sha1('hello\n')`?" | `python hashstore.py --step 1` |
| 2 | Objects live at `objects/ab/cdef...`, zlib-compressed | "How many folders will one object create?" | `--step 2` |
| 3 | Same content, same name: stored once | "Two puts of the same text: how many files?" | `--step 3` |
| 4 | The name doubles as an integrity check | "What happens if one byte on disk changes?" | `--step 4` |
| Check | Compare with the real tool | "Will an empty file and a Unicode file match git too?" | `--compare-git` |

Left out on purpose: trees, commits, packfiles, refs, SHA-256 repositories. Where real git is more complicated:
packfiles with delta compression, loose-object fan-out limits, and the SHA-1 to SHA-256 transition.
