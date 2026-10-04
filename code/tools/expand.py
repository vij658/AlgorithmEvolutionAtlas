#!/usr/bin/env python3
"""Expand source directives in a Markdown file into fenced Java blocks copied verbatim from the tested programs.

Directive (one per line, must start the line):
    @@ Part3a.java: name1 name2 ...      members of the top-level class, in the order given
    @@ Part3a.java: first..last          everything from the start of `first` to the end of `last`, as it is in the file

A member is a method, a nested class/record/enum, or a field declaration; its name is the method name, the type name, or any
name declared by the field. A Javadoc or // comment that sits directly above a member (no blank line) belongs to it.
Members are de-indented by four spaces. Members that touch in the source stay together; others are separated by a blank line.

Usage: expand.py IN.md OUT.md [--report]
"""
import pathlib
import re
import sys


def scan(text):
    """Yield (index, char, depth_before, paren_before) for every character that is real code (not in a string, char literal or comment)."""
    i, n = 0, len(text)
    depth = paren = 0
    while i < n:
        c = text[i]
        if text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c == '"':
            j = i + 1
            while text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            i = j + 1
            continue
        if c == "'":
            j = i + 1
            while text[j] != "'":
                j += 2 if text[j] == "\\" else 1
            i = j + 1
            continue
        yield i, c, depth, paren
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == "(":
            paren += 1
        elif c == ")":
            paren -= 1
        i += 1


class Member:
    def __init__(self, names, start_line, end_line, header):
        self.names, self.start, self.end, self.header = names, start_line, end_line, header  # lines are 0-based, end exclusive


def members_of(text):
    lines = text.split("\n")
    starts = [0]
    for ln in lines[:-1]:
        starts.append(starts[-1] + len(ln) + 1)

    def line_of(pos):
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo

    code = list(scan(text))
    # find the opening brace of the top-level class
    k = next(idx for idx, (p, c, d, pa) in enumerate(code) if c == "{" and d == 0)
    out = []
    idx = k + 1
    while idx < len(code):
        while idx < len(code) and code[idx][1].isspace():
            idx += 1                                        # a member starts at its first real character, not at the blank line before it
        if idx >= len(code):
            break
        p, c, d, pa = code[idx]
        if d == 1 and c == "}":
            break                                           # the closing brace of the top-level class
        # a member starts at its first real code character at depth 1
        first = p
        header_end = None
        j = idx
        saw_eq = False
        while True:
            p2, c2, d2, pa2 = code[j]
            if d2 == 1 and pa2 == 0 and c2 == "=":
                saw_eq = True
            if d2 == 1 and pa2 == 0 and c2 in "{;":
                if c2 == ";" or not saw_eq:
                    header_end = j
                    break
                # '= {' array initialiser or similar: the member continues to the next ';' at depth 1
                while not (code[j][2] == 1 and code[j][1] == ";" and code[j][3] == 0):
                    j += 1
                header_end = j
                break
            j += 1
        c_end = code[header_end][1]
        if c_end == "{" and not saw_eq:
            depth_target = 1
            j = header_end + 1
            while not (code[j][1] == "}" and code[j][2] == 2):
                j += 1
            last = j
        else:
            last = header_end
        header = text[first:code[header_end][0]]
        # names
        m = re.search(r"\b(class|record|enum|interface)\s+([A-Za-z_]\w*)", header)
        if m:
            names = [m.group(2)]
        elif c_end == "{" and not saw_eq:
            mm = re.search(r"([A-Za-z_]\w*)\s*\(", header)
            names = [mm.group(1)]
        else:
            names = []
            depth_here = 0
            for q in range(idx, header_end + 1):
                pq, cq, dq, paq = code[q]
                if dq == 1 and paq == 0 and cq == "=":
                    mm = re.search(r"([A-Za-z_]\w*)\s*$", text[:pq])
                    if mm:
                        names.append(mm.group(1))
            if not names:
                mm = re.search(r"([A-Za-z_]\w*)\s*;", text[first:code[header_end][0] + 1])
                names = [mm.group(1)] if mm else ["?"]
        start_line = line_of(first)
        end_line = line_of(code[last][0]) + 1
        # attach comments directly above (no blank line in between)
        s = start_line
        while (s > 0 and lines[s - 1].strip()
               and (lines[s - 1].lstrip().startswith(("//", "/*", "*")) or lines[s - 1].rstrip().endswith("*/"))
               and not re.match(r"\s*//\s*={5,}", lines[s - 1])):      # the "// ==== 43. title ====" banners are not part of a member
            s -= 1
        out.append(Member(names, s, end_line, header.strip()))
        idx = last + 1
    return lines, out


def dedent(block):
    return [ln[4:] if ln.startswith("    ") else ln for ln in block]


def expand_directive(spec, base, report):
    fname, _, rest = spec.partition(":")
    fname = fname.strip()
    text = (base / fname).read_text()
    lines, members = members_of(text)
    byname = {}
    for mem in members:
        for nm in mem.names:
            if nm in byname:
                raise SystemExit(f"{fname}: name {nm!r} is declared twice at top level")
            byname[nm] = mem
    chunks = []          # list of (start, end)
    for tok in rest.split():
        if ".." in tok:
            a, b = tok.split("..")
            chunks.append((byname[a].start, byname[b].end))
        else:
            if tok not in byname:
                raise SystemExit(f"{fname}: no member named {tok!r}")
            chunks.append((byname[tok].start, byname[tok].end))
    out = []
    prev_end = None
    for s, e in chunks:
        if out and not (prev_end == s):
            out.append("")
        out.extend(dedent(lines[s:e]))
        prev_end = e
    report.append((fname, rest.split(), out))
    return "```java\n" + "\n".join(out) + "\n```"


def main():
    src = pathlib.Path(sys.argv[1])
    dest = pathlib.Path(sys.argv[2])
    verbose = "--report" in sys.argv
    base = src.parent
    report = []
    result = []
    for line in src.read_text().split("\n"):
        if line.startswith("@@ "):
            result.append(expand_directive(line[3:], base, report))
        else:
            result.append(line)
    dest.write_text("\n".join(result))
    total = sum(len(r[2]) for r in report)
    longest = max((len(ln) for r in report for ln in r[2]), default=0)
    print(f"expanded {len(report)} directives, {total} code lines, longest line {longest} characters")
    if verbose:
        for fname, names, code in report:
            width = max((len(x) for x in code), default=0)
            print(f"  {fname}: {' '.join(names)} -> {len(code)} lines, widest {width}")


if __name__ == "__main__":
    main()
