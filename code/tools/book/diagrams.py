"""A small box-and-arrow diagram renderer shared by the book's GitHub and HTML editions.

One diagram spec renders two ways:
  - GitHub edition: a standalone SVG file per theme, colours written out (light and dark files);
  - HTML edition: inline SVG whose colours are CSS variables, so it follows the page's theme.

Colours are named by role ("ink", "red", "yellow", "blue", ...) and resolved by a theme at render time.
Everything is drawn with native shapes and text; there is no script or external resource inside the SVG.
"""
import html
import math

GITHUB_THEMES = {
    "light": dict(ink="#17171a", ink2="#55545a", muted="#7d7c84", rule="#d9d8d1", paper="#ffffff", wash="#f4f3ee",
                  red="#d5352a", yellow="#c98a0c", blue="#1f5ba8", surface="#ffffff", axis="#c4c3bb", on_red="#ffffff", on_yellow="#17171a", on_blue="#ffffff", font="system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif"),
    "dark": dict(ink="#ecebe6", ink2="#b9b8b2", muted="#8f8e96", rule="#3a3d44", paper="#0d1117", wash="#161b22",
                 red="#f0584d", yellow="#d9a227", blue="#5b8fe0", surface="#0d1117", axis="#41444b", on_red="#14161a", on_yellow="#14161a", on_blue="#14161a", font="system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif"),
}
HTML_THEME = dict(ink="var(--ink)", ink2="var(--ink-2)", muted="var(--muted)", rule="var(--rule)", paper="var(--paper)",
                  wash="var(--wash)", red="var(--red)", yellow="var(--yellow)", blue="var(--blue)", surface="var(--surface)", axis="var(--axis)", on_red="var(--on-red)", on_yellow="var(--on-yellow)", on_blue="var(--on-blue)", font="var(--body)")

# text styles: (font size, weight, colour role)
STYLES = {
    "title": (15, 700, "ink"),
    "big": (22, 700, "ink"),
    "combo": (12.5, 600, "ink"),
    "note": (12.5, 400, "ink2"),
    "tag": (11, 700, "muted"),
    "label": (12.5, 600, "ink"),
    "caption": (12.5, 400, "ink2"),
}


def text_width(s: str, size: float, weight: int) -> float:
    """A rough width estimate for system sans text, enough to size boxes and label backgrounds."""
    per = 0.53 if weight < 600 else 0.59
    narrow = sum(1 for c in s if c in "il.,:;'|!()[] ")
    return (len(s) - narrow * 0.5) * size * per


def wrap(s: str, size: float, weight: int, width: float):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial, size, weight) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Diagram:
    def __init__(self, width: int, height: int, label: str):
        self.w, self.h, self.label = width, height, label
        self.nodes, self.edges, self.texts = {}, [], []
        self.warnings = []

    def node(self, key, x, y, w, h, lines, color="ink", fill="paper", weight=None):
        """lines: list of (text, style). Long lines wrap inside the box."""
        self.nodes[key] = dict(x=x, y=y, w=w, h=h, lines=lines, color=color, fill=fill,
                               weight=weight if weight is not None else (1.5 if color == "ink" else 3))
        return self

    def edge(self, a, b, label=None, dashed=False, at=0.5, dx=0, dy=0, anchor="middle", ports=None):
        """An arrow from node a to node b. ports=(side_a, side_b) pins the ends to box sides; otherwise the line runs
        centre to centre and is clipped at both box edges. The label sits at fraction `at` along the line, moved by dx, dy."""
        self.edges.append(dict(a=a, b=b, label=label, dashed=dashed, at=at, dx=dx, dy=dy, anchor=anchor, ports=ports))
        return self

    def text(self, x, y, s, style="caption", anchor="start"):
        self.texts.append((x, y, s, style, anchor))
        return self

    # ------------------------------------------------------------------------------------------------------------
    def _port(self, n, side):
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]
        return {"top": (x + w / 2, y), "bottom": (x + w / 2, y + h), "left": (x, y + h / 2), "right": (x + w, y + h / 2)}[side]

    def _clip(self, n, x0, y0, dx, dy):
        t = min(abs(n["w"] / 2 / (dx or 1e-9)), abs(n["h"] / 2 / (dy or 1e-9)))
        return x0 + dx * t, y0 + dy * t

    def render(self, theme: dict, standalone: bool) -> str:
        c = lambda role: theme[role]
        out = []
        for e in self.edges:
            A, B = self.nodes[e["a"]], self.nodes[e["b"]]
            if e["ports"]:
                (sx, sy), (ex, ey) = self._port(A, e["ports"][0]), self._port(B, e["ports"][1])
            else:
                ax, ay = A["x"] + A["w"] / 2, A["y"] + A["h"] / 2
                bx, by = B["x"] + B["w"] / 2, B["y"] + B["h"] / 2
                sx, sy = self._clip(A, ax, ay, bx - ax, by - ay)
                ex, ey = self._clip(B, bx, by, ax - bx, ay - by)
            dash = ";stroke-dasharray:5 4" if e["dashed"] else ""
            out.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" style="stroke:{c("ink2")};stroke-width:1.5{dash}"/>')
            ang = math.atan2(ey - sy, ex - sx)
            p1 = (ex - 9 * math.cos(ang - 0.42), ey - 9 * math.sin(ang - 0.42))
            p2 = (ex - 9 * math.cos(ang + 0.42), ey - 9 * math.sin(ang + 0.42))
            out.append(f'<polygon points="{ex:.1f},{ey:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" style="fill:{c("ink2")}"/>')
            if e["label"]:
                lx, ly = sx + (ex - sx) * e["at"] + e["dx"], sy + (ey - sy) * e["at"] + e["dy"]
                size, weight, role = STYLES["label"]
                tw = text_width(e["label"], size, weight)
                x0 = lx - tw / 2 if e["anchor"] == "middle" else (lx if e["anchor"] == "start" else lx - tw)
                out.append(f'<rect x="{x0 - 5:.1f}" y="{ly - 13:.1f}" width="{tw + 10:.1f}" height="19" rx="3" style="fill:{c("surface")}"/>')
                out.append(self._t(lx, ly, e["label"], "label", e["anchor"], c))
        for key, n in self.nodes.items():
            out.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" style="fill:{c(n["fill"])};stroke:{c(n["color"])};stroke-width:{n["weight"]}"/>')
            rows = []
            for s, style in n["lines"]:
                size, weight, role = STYLES[style]
                for part in wrap(s, size, weight, n["w"] - 20):
                    rows.append((part, style, size))
                    if text_width(part, size, weight) > n["w"] - 20:
                        self.warnings.append(f"{self.label}: '{part}' may overflow node {key}")
            total = sum(r[2] * 1.32 for r in rows)
            if total > n["h"] - 10:
                self.warnings.append(f"{self.label}: text in node {key} is taller than the box")
            y = n["y"] + (n["h"] - total) / 2
            for part, style, size in rows:
                y += size * 1.32
                out.append(self._t(n["x"] + 12, y - size * 0.3, part, style, "start", c))
        for x, y, s, style, anchor in self.texts:
            out.append(self._t(x, y, s, style, anchor, c))
        body = "".join(out)
        label = html.escape(self.label)
        if standalone:
            return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                    f'role="img" aria-label="{label}" style="font-family:{theme["font"]}"><title>{label}</title>{body}</svg>\n')
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{label}" '
                f'style="font-family:{theme["font"]};min-width:{int(self.w * 0.72)}px;max-width:{self.w * 1.05:.0f}px;margin:0 auto">{body}</svg>')

    def _t(self, x, y, s, style, anchor, c):
        size, weight, role = STYLES[style]
        ls = ";letter-spacing:.08em" if style == "tag" else ""
        return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" style="fill:{c(role)};font-size:{size}px;'
                f'font-weight:{weight}{ls}">{html.escape(str(s))}</text>')
