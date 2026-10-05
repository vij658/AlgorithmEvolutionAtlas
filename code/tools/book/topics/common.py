"""Shared pieces for topic modules: SVG helpers, drawn placeholders for objects, and small parsing helpers."""
import html
import re

import era01
import page


def svg_doc(w, h, body, label, theme, standalone, min_scale=0.72, max_w=None):
    label = html.escape(label)
    if standalone:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
                f'aria-label="{label}" style="font-family:{theme["font"]}"><title>{label}</title>{body}</svg>\n')
    mw = max_w if max_w else w * 1.05
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" style="font-family:{theme["font"]};'
            f'min-width:{int(w * min_scale)}px;max-width:{mw:.0f}px;margin:0 auto">{body}</svg>')


def text(x, y, s, fill, size=13, anchor="start", weight=400, italic=False):
    st = f"fill:{fill};font-size:{size}px;font-weight:{weight}" + (";font-style:italic" if italic else "")
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" style="{st}">{html.escape(str(s))}</text>'


def rect(x, y, w, h, fill, stroke=None, sw=1.5, rx=0, extra=""):
    st = f"fill:{fill}" + (f";stroke:{stroke};stroke-width:{sw}" if stroke else "") + extra
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" style="{st}"/>'


def line(x1, y1, x2, y2, stroke, sw=1.5, extra=""):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" style="stroke:{stroke};stroke-width:{sw}{extra}"/>'


def path(d, stroke=None, fill="none", sw=1.5, extra=""):
    st = f"fill:{fill}" + (f";stroke:{stroke};stroke-width:{sw}" if stroke else "") + extra
    return f'<path d="{d}" style="{st}"/>'


def circle(cx, cy, r, fill, stroke=None, sw=1.5):
    st = f"fill:{fill}" + (f";stroke:{stroke};stroke-width:{sw}" if stroke else "")
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" style="{st}"/>'


# ----------------------------------------------------------------------------------------------------------------------
# drawn placeholders for the "objects" section: simple, clearly drawn, never passed off as photographs
# ----------------------------------------------------------------------------------------------------------------------
def draw_book(theme, standalone=False):
    c = theme
    b = [path("M100,20 C80,12 40,12 20,18 V108 C40,102 80,102 100,110 Z", c["ink2"], c["paper"], 1.2),
         path("M100,20 C120,12 160,12 180,18 V108 C160,102 120,102 100,110 Z", c["ink2"], c["paper"], 1.2)]
    b += [line(32, 32 + i * 9, 88, 32 + i * 9, c["axis"], 2) for i in range(6)]
    b += [circle(140, 60, 24, "none", c["red"], 2), path("M116,60 L164,60 M140,36 L140,84", c["blue"], "none", 2)]
    return svg_doc(200, 120, "".join(b), "Drawn placeholder of an open printed book", theme, standalone, 0.3, 220)


def draw_manuscript(theme, standalone=False, note="888"):
    c = theme
    b = [rect(50, 10, 100, 130, c["paper"], c["ink2"], 1.2)]
    b += [line(60, 22 + i * 7, 118 if i % 3 == 2 else 140, 22 + i * 7, c["axis"], 2) for i in range(9)]
    b += [rect(72, 90, 36, 36, "none", c["red"], 2), line(72, 126, 108, 90, c["blue"], 2), text(118, 120, note, c["muted"], 9)]
    return svg_doc(200, 150, "".join(b), "Drawn placeholder of a manuscript page", theme, standalone, 0.3, 220)


def draw_papyrus(theme, standalone=False):
    c = theme
    b = [path("M40,22 L150,14 L162,60 L150,128 L60,136 L36,96 Z", c["ink2"], c["paper"], 1.2)]
    b += [line(52, 32 + i * 8, 146 - i * 6, 30 + i * 8, c["axis"], 2) for i in range(5)]
    b += [rect(66, 76, 44, 44, "none", c["yellow"], 2), rect(110, 76, 22, 44, "none", c["red"], 2), line(66, 120, 110, 76, c["blue"], 2)]
    return svg_doc(200, 150, "".join(b), "Drawn placeholder of a papyrus fragment", theme, standalone, 0.3, 220)


def draw_tablet(theme, standalone=False, round_=False):
    """A clay tablet with a few wedge marks."""
    c = theme
    b = [f'<ellipse cx="100" cy="75" rx="62" ry="58" style="fill:{c["paper"]};stroke:{c["ink2"]};stroke-width:1.2"/>' if round_
         else rect(40, 18, 120, 114, c["paper"], c["ink2"], 1.2, rx=14)]
    def wedge(x, y, s=1.0, color=None):
        col = color or c["ink"]
        return path(f"M{x},{y} l{8 * s},{-4 * s} l0,{8 * s} Z", None, col) + line(x + 8 * s, y, x + 20 * s, y, col, 1.6)
    for row in range(3):
        for k in range(3 - row % 2):
            b.append(wedge(62 + k * 26, 50 + row * 24, 1.0, c["ink"] if row != 1 else c["red"]))
    return svg_doc(200, 150, "".join(b), "Drawn placeholder of a clay tablet", theme, standalone, 0.3, 220)


def draw_bone(theme, standalone=False):
    """A bone handle with groups of notches."""
    c = theme
    b = [path("M24,70 C24,56 40,52 52,58 L150,58 C162,52 178,56 178,70 C178,84 162,88 150,82 L52,82 C40,88 24,84 24,70 Z", c["ink2"], c["paper"], 1.2)]
    x = 58
    for g, n in enumerate([5, 3, 6, 4]):
        for k in range(n):
            b.append(line(x, 61, x, 79, c["red"] if g % 2 == 0 else c["blue"], 2))
            x += 5
        x += 9
    b.append(path("M178,70 L194,64 L196,76 Z", c["ink2"], c["wash"], 1))
    return svg_doc(200, 140, "".join(b), "Drawn placeholder of a notched bone", theme, standalone, 0.3, 220)


def draw_board(theme, standalone=False):
    """A counting board: lines with pebbles."""
    c = theme
    b = [rect(24, 20, 152, 110, c["paper"], c["ink2"], 1.2)]
    for i in range(5):
        y = 36 + i * 20
        b.append(line(34, y, 166, y, c["axis"], 1.5))
    import random
    rnd = random.Random(7)
    for i, n in enumerate([3, 1, 4, 2, 2]):
        for k in range(n):
            b.append(circle(50 + k * 16 + (i % 2) * 6, 36 + i * 20, 5, [c["red"], c["blue"], c["yellow"]][i % 3]))
    return svg_doc(200, 150, "".join(b), "Drawn placeholder of a counting board", theme, standalone, 0.3, 220)


# ----------------------------------------------------------------------------------------------------------------------
def era_timeline_block(index, era=era01):
    return dict(type="timeline", name="era-timeline", events=era.timeline_events(), current=index,
                label=f"Era {era.ERA['num']}: {era.ERA['title']}, from {era.ERA['span']}")


def tagged(out: str, tag: str):
    """Lines of the program output that start with `tag ` (the tag removed)."""
    return [ln[len(tag) + 1:] for ln in out.splitlines() if ln.startswith(tag + " ")]


def checks(out: str) -> int:
    m = re.search(r": (\d+) checks passed\s*$", out)
    return int(m.group(1))


def java_member(src: str, signature: str) -> str:
    """A method copied verbatim from the program, with the comment directly above it, de-indented by one level."""
    lines = src.split("\n")
    i = next(k for k, l in enumerate(lines) if signature in l)
    start = i
    while start > 0 and lines[start - 1].strip().startswith(("/**", "*", "//")):
        start -= 1
    depth, end = 0, i
    for k in range(i, len(lines)):
        depth += lines[k].count("{") - lines[k].count("}")
        if depth == 0 and "{" in "".join(lines[i:k + 1]):
            end = k
            break
    return "\n".join(l[4:] if l.startswith("    ") else l for l in lines[start:end + 1])


def prove_it_section(ctx, cls, checks_n, what, members, run_dir_note=None):
    snippet = "\n\n".join(java_member(ctx["java"], m) for m in members)
    rel = f"code/{ctx['era'].ERA['folder']}/{ctx['topic'][0]:02d}-{ctx['topic'][1]}/{cls}.java"
    return dict(id="prove", eyebrow="Prove it", title="The program behind every number here", toc="Prove it", blocks=[
        dict(type="p", text=f"[{cls}.java]({ctx['repo_url']}{rel}) makes **{checks_n:,} checks**: {what} "
                            f"Run it with `java {cls}.java` (JDK 17 or newer). The heart of it:"),
        dict(type="code", code=snippet),
    ])


def links_section(ctx, extra=()):
    rows = page.catalog_links(ctx["catalog"], ctx["topic"][0]) + list(extra)
    return dict(id="read", eyebrow="Watch and read", title="Every link was opened before it was listed", toc="Watch and read",
                blocks=[dict(type="links", items=rows),
                        dict(type="p", text=f"More, with certainty labels and the gaps we could not fill: [Era 1 reference catalog]({ctx['repo_url']}book/{ctx['era'].ERA['folder']}/reference-catalog.md).")])
