"""Makes the v8 3D art: scene.svg (isometric Claude Code workspace) and cards/*.svg. Run: python make_3d.py <out_dir>"""
import sys
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape

# Theme "dusk": plum-black ground; each colour means one kind of thing.
BG, BG2, SLAB, INK, MUTED = "#161220", "#211a2e", "#2a2238", "#F3EEF8", "#A79DB8"
CLAUDE, MCP, AGENT, OSS, TOOL = "#FF8A65", "#5EEAD4", "#B9A6FF", "#FFD166", "#8FB8FF"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Consolas,Menlo,monospace"
C30, S30 = 0.866, 0.5


def shade(hex_color, f):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


class Iso:
    def __init__(self, ox, oy, u):
        self.ox, self.oy, self.u = ox, oy, u

    def p(self, x, y, z=0):
        return (self.ox + (x - y) * C30 * self.u, self.oy + (x + y) * S30 * self.u - z * self.u)

    def poly(self, pts, fill, extra=""):
        return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in (self.p(*q) for q in pts))}" fill="{fill}" {extra}/>'

    def box(self, x, y, z, w, d, h, color, edge=True):
        top = [(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)]
        right = [(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)]
        left = [(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)]
        stroke = f'stroke="{color}" stroke-opacity=".9" stroke-width="1"' if edge else ""
        return (self.poly(left, shade(color, .55)) + self.poly(right, shade(color, .38)) + self.poly(top, color, stroke)
                + self.poly(top, "url(#sheen)"))

    def path(self, pts, cls, delay=0):
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.p(*q) for q in pts))
        return f'<polyline points="{d}" class="{cls}" style="animation-delay:{delay}s"/>'


def defs():
    return f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="halo"><stop offset="0" stop-color="{CLAUDE}" stop-opacity=".35"/><stop offset="1" stop-color="{CLAUDE}" stop-opacity="0"/></radialGradient>
</defs>
<style>
.pipe{{fill:none;stroke:#4a3f5e;stroke-width:4;stroke-linecap:round;stroke-linejoin:round}}
.flow{{fill:none;stroke-width:4;stroke-linecap:round;stroke-dasharray:8 400;animation:flow 3.2s linear infinite}}
@keyframes flow{{from{{stroke-dashoffset:408}}to{{stroke-dashoffset:0}}}}
.bob{{animation:bob 5s ease-in-out infinite}}@keyframes bob{{50%{{transform:translateY(-6px)}}}}
.spin{{animation:spin 14s linear infinite;transform-box:fill-box;transform-origin:center}}@keyframes spin{{to{{transform:rotate(360deg)}}}}
.name{{font:700 40px {SANS};fill:{INK};letter-spacing:-.5px}}
.role{{font:500 17px {SANS};fill:{INK}}}
.body{{font:400 15px {SANS};fill:{MUTED}}}
.tag{{font:600 12px {MONO}}}
@media (prefers-reduced-motion:reduce){{.flow,.bob,.spin{{animation:none}}}}
</style>"""


def label(iso, x, y, z, text, color, dx=0, dy=-10, anchor="middle"):
    a, b = iso.p(x, y, z)
    return f'<text x="{a + dx:.1f}" y="{b + dy:.1f}" text-anchor="{anchor}" class="tag" fill="{color}">{escape(text)}</text>'


def scene():
    W, H = 900, 440
    iso = Iso(610, 78, 27)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', defs(),
         f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>']
    # who
    o += ['<text x="44" y="118" class="name">Prafulla Purohit</text>',
          '<text x="44" y="150" class="role">AI/ML developer at Satva Solutions</text>',
          '<text x="44" y="194" class="body">I build AI agents, and the MCP servers</text>',
          '<text x="44" y="216" class="body">that let them work inside real business tools.</text>']
    legend = [(CLAUDE, "Claude Code"), (MCP, "MCP servers I built"), (AGENT, "agents and evals"), (TOOL, "tools the agent drives")]
    for i, (c, t) in enumerate(legend):
        y = 266 + i * 26
        o.append(f'<rect x="44" y="{y - 11}" width="13" height="13" rx="2" fill="{c}"/><text x="66" y="{y}" class="body" style="font-size:14px">{t}</text>')

    # ground slab + glow under the tower
    o.append(iso.box(0, 0, -0.5, 11, 11, 0.5, SLAB, edge=False))
    hx, hy = iso.p(5.5, 5.5, 0)
    o.append(f'<ellipse cx="{hx:.0f}" cy="{hy:.0f}" rx="120" ry="60" fill="url(#halo)"/>')

    # pipes from every block into the Claude tower (centre 5.5,5.5)
    mcp = [(0.6, 0.8, "ledger-mcp"), (0.6, 3.4, "books-mcp"), (0.6, 6.0, "store-mcp"), (0.6, 8.6, "orders-mcp")]
    agents = [(8.6, 0.8, "agent runtime"), (8.6, 3.4, "evals")]
    tools = [(5.0, 9.4, "github"), (8.4, 8.0, "browser")]
    routes = []
    for x, y, _ in mcp:
        routes.append(([(x + 1.6, y + 0.8, 0), (3.2, y + 0.8, 0), (3.2, 5.5, 0), (4.5, 5.5, 0)], MCP))
    for x, y, _ in agents:
        routes.append(([(x, y + 0.8, 0), (7.8, y + 0.8, 0), (7.8, 5.2, 0), (6.5, 5.2, 0)], AGENT))
    routes.append(([(5.8, 9.4, 0), (5.8, 6.5, 0)], TOOL))
    routes.append(([(8.4, 8.8, 0), (6.6, 8.8, 0), (6.6, 6.5, 0)], TOOL))
    for i, (pts, c) in enumerate(routes):
        o.append(iso.path(pts, "pipe"))
        o.append(iso.path(pts, "flow", i * 0.4).replace('class="flow"', f'class="flow" stroke="{c}"'))

    # blocks, back to front
    blocks = [(x, y, 1.6, 1.6, 1.1, MCP, n) for x, y, n in mcp] + [(x, y, 1.6, 1.6, 1.6, AGENT, n) for x, y, n in agents] \
        + [(x, y, 1.6, 1.2, 0.8, TOOL, n) for x, y, n in tools]
    tower = (4.5, 4.5, 2, 2, 4.2, CLAUDE, "Claude Code")
    labels = []
    for x, y, w, d, h, c, n in sorted(blocks + [tower], key=lambda b: b[0] + b[1] + b[2] + b[3]):
        if n == "Claude Code":
            o.append('<g class="bob">' + iso.box(x, y, 0, w, d, h, c))
            # spark on the tower's top face, drawn in the iso plane
            cx, cy, z = x + w / 2, y + d / 2, h
            rays = "".join(f'<line x1="{iso.p(cx, cy, z)[0]:.1f}" y1="{iso.p(cx, cy, z)[1]:.1f}" '
                           f'x2="{iso.p(cx + .75 * dx, cy + .75 * dy, z)[0]:.1f}" y2="{iso.p(cx + .75 * dx, cy + .75 * dy, z)[1]:.1f}"/>'
                           for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, -.7), (.7, -.7), (-.7, .7)])
            o.append(f'<g stroke="#fff" stroke-width="3.5" stroke-linecap="round">{rays}</g>')
            o.append("</g>")
            labels.append(label(iso, x + w, y, h, n, CLAUDE, dx=12, dy=4, anchor="start"))
        else:
            o.append(iso.box(x, y, 0, w, d, h, c))
            labels.append(label(iso, x + w / 2, y + d / 2, h, n, c, dy=-22))
    o += labels
    o.append(f'<text x="{W - 24}" y="{H - 18}" text-anchor="end" class="tag" fill="{MUTED}">prafulla2121</text></svg>')
    return "".join(o)


CARDS = [
    ("agentflow", "AgentFlow", ["A supervisor agent hands work", "to research, summary and code agents."], ["LangGraph", "Claude", "FastAPI", "GCP"], AGENT, [1.4, 1.0, 1.8]),
    ("documind-rag", "DocuMind", ["Ask questions across many PDFs;", "every answer cites its source."], ["LangChain", "FAISS", "AWS"], MCP, [0.6, 1.2, 1.8]),
    ("mcp-servers", "MCP Servers", ["Let agents read accounting, store", "and order data, safely read-only."], ["MCP", "Python", "Docker"], CLAUDE, [1.8, 1.1, 0.7]),
    ("beets-oss", "beets #7139", ["Merged into a 15k-star", "open source music manager."], ["Python", "pytest", "OSS"], OSS, [0.8, 1.6, 1.0]),
    ("careerwise-ai", "CareerWise AI", ["Resume review, cover letters", "and interview practice."], ["Next.js", "Claude", "Postgres"], TOOL, [1.2, 0.7, 1.5]),
    ("whatsapp-analyzer", "Chat Analyzer", ["Sentiment, word use and activity", "heatmaps from chat exports."], ["NLP", "sklearn", "Streamlit"], "#F49AC2", [0.5, 1.3, 0.9]),
]


def card(title, lines, chips, accent, heights):
    W, H = 440, 220
    iso = Iso(92, 92, 17)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', defs(),
         f'<rect width="{W}" height="{H}" rx="16" fill="url(#bg)"/>',
         iso.box(0, 0, -0.3, 4.6, 4.6, 0.3, SLAB, edge=False), '<g class="bob">']
    spots = [(0.4, 0.4), (2.5, 0.4), (0.4, 2.5)]
    for (x, y), h in sorted(zip(spots, heights), key=lambda s: s[0][0] + s[0][1]):
        o.append(iso.box(x, y, 0, 1.7, 1.7, h * 1.6, accent))
    o.append(iso.box(2.5, 2.5, 0, 1.7, 1.7, 0.5, shade(accent, .8)) + "</g>")
    o += [f'<text x="190" y="62" style="font:700 24px {SANS};fill:{INK};letter-spacing:-.3px">{escape(title)}</text>',
          f'<text x="190" y="96" class="body" style="font-size:14px">{escape(lines[0])}</text>',
          f'<text x="190" y="116" class="body" style="font-size:14px">{escape(lines[1])}</text>']
    x = 190
    for c in chips:
        w = len(c) * 7.4 + 18
        o.append(f'<rect x="{x}" y="150" width="{w}" height="24" rx="12" fill="{accent}" fill-opacity=".13" stroke="{accent}" stroke-opacity=".55"/>'
                 f'<text x="{x + w / 2}" y="166" text-anchor="middle" class="tag" fill="{accent}">{escape(c)}</text>')
        x += w + 6
    o.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{accent}" stroke-opacity=".3"/></svg>')
    return "".join(o)


out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent)
files = {out / "assets" / "scene.svg": scene()}
for slug, *data in CARDS:
    files[out / "assets" / "cards" / f"{slug}.svg"] = card(*data)
for path, svg in files.items():
    ElementTree.fromstring(svg)  # self-check: invalid XML shows as a broken image on GitHub
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
print(f"wrote {len(files)} files to {out / 'assets'}")
