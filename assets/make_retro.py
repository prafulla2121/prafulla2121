"""Makes the v9 art: grainy hero, pink retro-desktop panel, big statement, retro-window project cards. Run: python make_retro.py"""
from math import sqrt
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape

INK, PAPER, PINK, GREY, SKY, ROSE = "#1d1d1f", "#ffffff", "#F48BA0", "#e7e7e7", "#79B8E8", "#F25FC2"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'Courier New',Courier,ui-monospace,monospace"
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def svg(w, h, body, defs=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>'


def t(x, y, s, size, font=SANS, fill=INK, weight=400, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>'


def dither_sphere(cx, cy, r, step=5, color=INK):
    """Ordered-dither shading of a lit sphere: a dot wherever the surface is darker than the Bayer threshold."""
    lx, ly, lz = -0.5, -0.6, 0.62
    out = []
    for gy in range(int(cy - r), int(cy + r), step):
        for gx in range(int(cx - r), int(cx + r), step):
            nx, ny = (gx - cx) / r, (gy - cy) / r
            if nx * nx + ny * ny >= 1:
                continue
            nz = sqrt(1 - nx * nx - ny * ny)
            light = max(0.0, nx * lx + ny * ly + nz * lz)
            if light < BAYER[(gy // step) % 4][(gx // step) % 4] / 16:
                out.append(f'<rect x="{gx}" y="{gy}" width="2.4" height="2.4"/>')
    return f'<g fill="{color}">{"".join(out)}</g>'


def window(x, y, w, h, title, body, fill=PAPER):
    """1-bit desktop window: hard shadow, black border, black title bar."""
    return (f'<rect x="{x + 5}" y="{y + 5}" width="{w}" height="{h}" fill="{INK}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{INK}" stroke-width="2"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="22" fill="{INK}"/>'
            + t(x + 8, y + 16, title, 13, MONO, PAPER, 700) + f'<g transform="translate({x},{y + 22})">{body}</g>')


GRAIN = ('<filter id="grain" x="0" y="0" width="1" height="1"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>'
         '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 0"/></filter>'
         '<filter id="cloud" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="38"/></filter>'
         '<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset=".25" stop-color="#fff" stop-opacity="0"/><stop offset=".62" stop-color="#fff"/></linearGradient>'
         '<pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="1.6" height="1.6" fill="#1d1d1f" opacity=".25"/></pattern>')


def hero():
    W, H = 900, 680
    clouds = (f'<g filter="url(#cloud)"><ellipse cx="110" cy="70" rx="230" ry="130" fill="{ROSE}"/>'
              f'<ellipse cx="460" cy="30" rx="280" ry="120" fill="{SKY}"/><ellipse cx="800" cy="100" rx="210" ry="140" fill="{ROSE}"/>'
              f'<ellipse cx="320" cy="170" rx="170" ry="70" fill="#B48CF2"/><ellipse cx="640" cy="200" rx="160" ry="60" fill="{SKY}"/></g>')
    news = window(300, 70, 300, 104, "Nov 2026 ▪ Prafulla News",
                  t(150, 30, "Got a fix merged into beets,", 14, MONO, INK, 400, "middle")
                  + t(150, 50, "a 15k-star open source project", 14, MONO, INK, 400, "middle")
                  + t(150, 72, "View the pull request", 14, MONO, INK, 400, "middle", 'text-decoration="underline"'), "#eeeeee")
    lines = ["I Build AI Agents", "That Do Real Work", "Inside Business", "Software."]
    head = "".join(t(450, 400 + i * 74, s, 80, SANS, INK, 500, "middle", 'letter-spacing="-3.5"') for i, s in enumerate(lines))
    body = (f'<rect width="{W}" height="{H}" fill="{PAPER}"/>{clouds}<rect width="{W}" height="360" filter="url(#grain)" opacity=".5"/>'
            f'<rect width="{W}" height="380" fill="url(#fade)"/>{news}'
            + t(450, 300, "Prafulla Purohit ......................... AI/ML developer, Ahmedabad", 16, SANS, INK, 400, "middle") + head)
    return svg(W, H, body, GRAIN)


MCP_ROWS = [("ledger-mcp", "cloud accounting"), ("books-mcp", "second ledger"), ("store-mcp", "online store"), ("orders-mcp", "orders + stock")]


def desktop():
    W, H = 900, 560
    tree = "".join(t(14, 28 + i * 24, s, 14, MONO) for i, s in enumerate(
        ["├ skills/    140", "├ agents/     69", "├ hooks/      19", "├ plugins/     6", "└ mcp/   my servers"]))
    rows = ""
    for i, (name, what) in enumerate(MCP_ROWS):
        y = 20 + i * 40
        rows += (f'<rect x="14" y="{y}" width="112" height="22" fill="{INK}"/>' + t(70, y + 16, name, 13, MONO, PAPER, 700, "middle")
                 + t(140, y + 16, what, 14, MONO) + f'<line x1="300" y1="{y + 11}" x2="388" y2="{y + 11}" stroke="{INK}" stroke-dasharray="2 3"/>'
                 + t(400, y + 16, "read-only", 13, MONO, INK, 700))
    steps = "".join(f'<rect x="14" y="{14 + i * 21}" width="11" height="11" fill="{INK if i < 3 else PAPER}" stroke="{INK}"/>'
                    + t(34, 24 + i * 21, s, 13, MONO) for i, s in enumerate(["research", "plan", "human sign-off", "build", "review", "QA"]))
    place = t(12, 26, "Ahmedabad, IN", 14, MONO, INK, 700) + t(12, 46, "UTC+05:30", 14, MONO)
    sig = (f'<rect x="28" y="470" width="230" height="62" fill="{PAPER}" stroke="{INK}" stroke-width="2"/><rect x="28" y="470" width="230" height="18" fill="{INK}"/>'
           + t(36, 483, "prafulla2121", 12, MONO, PAPER, 700) + t(36, 506, "v2026.11", 12, MONO) + t(36, 524, "Made in Ahmedabad. With chai.", 12, MONO))
    body = (f'<rect width="{W}" height="{H}" fill="{PINK}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>'
            + dither_sphere(140, 560, 190) + dither_sphere(800, 300, 130)
            + f'<rect x="20" y="14" width="210" height="22" fill="{INK}"/>' + t(28, 30, "TOOLS.CLAUDE.CODE", 13, MONO, PAPER, 700)
            + window(56, 66, 260, 160, "~/.claude", tree)
            + window(640, 56, 210, 170, "how a feature ships", steps)
            + window(220, 236, 500, 196, "MCP servers I built", rows)
            + window(740, 456, 140, 76, "Location 1.0", place) + sig)
    return svg(W, H, body, GRAIN)


def statement():
    W, H = 900, 380
    lines = ["1 Merged PR,", "4 MCP Servers,", "69 Agents On Call."]
    body = (f'<rect width="{W}" height="{H}" fill="{PINK}"/>'
            + "".join(t(40, 110 + i * 92, s, 92, SANS, "#3a3a3c", 500, "start", 'letter-spacing="-4"') for i, s in enumerate(lines))
            + t(42, 352, "*Agents = Claude Code subagents in my daily setup. PR = beetbox/beets #7139.", 12, MONO, INK))
    return svg(W, H, body)


CARDS = [("agentflow", "agentflow", ["A supervisor agent hands work", "to research, summary and", "code agents."], "LangGraph / Claude / FastAPI"),
         ("documind-rag", "documind", ["Ask questions across many", "PDFs; every answer cites", "its source."], "LangChain / FAISS / AWS"),
         ("careerwise-ai", "careerwise", ["Resume review, cover letters", "and interview practice."], "Next.js / Claude / Postgres"),
         ("whatsapp-analyzer", "chat-analyzer", ["Sentiment, word use and", "activity heatmaps from", "chat exports."], "Python / sklearn / Streamlit")]


def card(title, lines, stack):
    W, H = 440, 250
    inner = (dither_sphere(70, 92, 52, 4) + "".join(t(140, 44 + i * 22, s, 15, SANS) for i, s in enumerate(lines))
             + f'<line x1="140" y1="132" x2="410" y2="132" stroke="{INK}" stroke-dasharray="2 3"/>' + t(140, 156, stack, 13, MONO, INK, 700)
             + t(140, 190, "Open repo", 13, MONO, INK, 400, "start", 'text-decoration="underline"'))
    return svg(W, H, f'<rect width="{W}" height="{H}" fill="{GREY}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>'
               + window(14, 12, 408, 222, f"{title}.app", inner), GRAIN)


here = Path(__file__).parent
files = {here / "hero.svg": hero(), here / "desktop.svg": desktop(), here / "statement.svg": statement()}
for slug, *data in CARDS:
    files[here / "cards" / f"{slug}.svg"] = card(*data)
for path, s in files.items():
    ElementTree.fromstring(s)  # self-check: invalid XML shows as a broken image on GitHub
    path.parent.mkdir(exist_ok=True)
    path.write_text(s, encoding="utf-8")
print(f"wrote {len(files)} files")
