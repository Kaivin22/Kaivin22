"""Build a terminal profile from a local avatar. Python 3.9+ and Pillow.

Layout inspired by https://github.com/ganji759/asciifetch.
This is an original SVG renderer, not the upstream portrait converter.
"""

import argparse
import html
import json
from pathlib import Path
import re
import sys
import textwrap

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
FONT = "'SFMono-Regular',Consolas,'Liberation Mono',monospace"
ASCII_RAMP = ".,:;irsXA253hMHGS#9B&@"


def load_portrait(profile):
    """Read the actual avatar and map its light and color to ASCII cells."""
    config = profile["portrait"]
    source = (ROOT / config["src"]).resolve()
    if ROOT.resolve() not in source.parents:
        raise ValueError("portrait.src must point to a file inside the repository")
    if not source.is_file():
        raise ValueError(f"Avatar not found: {config['src']}. Add your image before building.")
    columns = config.get("columns", 80)
    if not isinstance(columns, int) or not 40 <= columns <= 120:
        raise ValueError("portrait.columns must be an integer between 40 and 120")
    # A monospace cell is roughly twice as tall as it is wide.
    row_count = columns // 2
    with Image.open(source) as original:
        avatar = ImageOps.exif_transpose(original).convert("RGBA")
        background = Image.new("RGBA", avatar.size, profile["palette"]["background"])
        background.alpha_composite(avatar)
        square = ImageOps.fit(background.convert("RGB"), (columns, columns),
                              method=Image.Resampling.LANCZOS)
        pixels = square.resize((columns, row_count), Image.Resampling.LANCZOS)
    luminance = ImageOps.autocontrast(ImageOps.grayscale(pixels), cutoff=1)
    rows = []
    for y in range(row_count):
        cells = []
        for x in range(columns):
            level = (luminance.getpixel((x, y)) / 255) ** 0.7
            glyph = ASCII_RAMP[round(level * (len(ASCII_RAMP) - 1))]
            # Lift the ink brightness for a dark terminal while retaining
            # the orange fur, blue background, and other source-image colors.
            rgb = pixels.getpixel((x, y))
            ink = [min(255, round((48 + 207 * (channel / 255) ** 0.8) / 8) * 8)
                   for channel in rgb]
            color = "#" + "".join(f"{channel:02x}" for channel in ink)
            cells.append((glyph, color))
        rows.append(cells)
    return rows


def render_portrait(rows, x, y, width):
    """Draw real colored text, with no embedded raster or remote image."""
    columns = len(rows[0])
    line_height = width / len(rows)
    font_size = width / columns / 0.6
    out = [f'<g font-size="{font_size:.3f}" font-weight="600" xml:space="preserve">']
    for index, row in enumerate(rows):
        spans = []
        previous_color = None
        run = ""
        for glyph, color in row:
            if color != previous_color and run:
                spans.append(f'<tspan fill="{previous_color}">{html.escape(run)}</tspan>')
                run = ""
            run += glyph
            previous_color = color
        spans.append(f'<tspan fill="{previous_color}">{html.escape(run)}</tspan>')
        baseline = y + (index + 0.8) * line_height
        out.append(f'<text x="{x}" y="{baseline:.3f}" textLength="{width}" '
                   f'lengthAdjust="spacingAndGlyphs">' + "".join(spans) + '</text>')
    out.append('</g>')
    return "\n".join(out)


def text(x, y, value, color, size=18, weight=400, extra=""):
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
        f'font-weight="{weight}" {extra}>{html.escape(str(value))}</text>'
    )


def profile_fields(profile):
    return [
        ["Name", profile["name"]],
        ["Role", profile["role"]],
        ["Location", profile["location"]],
        [],
        *profile["fields"],
        [],
        ["GitHub", "github.com/" + profile["username"]],
    ]


def render_svg(profile, portrait, mobile=False):
    p = profile["palette"]
    width = 480 if mobile else 1200
    # Wrap long values before sizing the window, including later profile edits.
    rows = []
    limit = 28 if mobile else 31
    for field in profile_fields(profile):
        if not field:
            rows.append(None)
            continue
        label, value = field
        for index, line in enumerate(textwrap.wrap(value, limit) or [""]):
            rows.append((label if index == 0 else "", line))
    line_height = 33 if mobile else 32
    info_y = 642 if mobile else 221
    height = max(740, info_y + len(rows) * line_height + 145)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
        f'<title id="title">{html.escape(profile["name"])} | {html.escape(profile["role"])}</title>',
        '<desc id="description">' + html.escape(profile["portrait"]["description"]) + ' '
        + html.escape(". ".join(f"{field[0]}: {field[1]}" for field in profile_fields(profile) if field))
        + '</desc>',
        f'<rect width="{width}" height="{height}" rx="16" fill="{p["canvas"]}"/>',
        f'<rect x="12" y="12" width="{width - 24}" height="{height - 24}" rx="12" '
        f'fill="{p["background"]}" stroke="{p["border"]}"/>',
        f'<path d="M24 12H{width - 24}Q{width - 12} 12 {width - 12} 24V66H12V24Q12 12 24 12Z" '
        f'fill="{p["bar"]}"/>',
        f'<path d="M12 66H{width - 12}" stroke="{p["border"]}"/>',
        f'<g font-family="{FONT}">',
    ]
    for x, color in [(37, "#cc6b63"), (59, "#e0b66e"), (81, "#87ad8a")]:
        out.append(f'<circle cx="{x}" cy="39" r="6" fill="{color}"/>')
    out.append(text(width / 2, 44, profile["username"].lower() + " — ~/profile", p["muted"], 14,
                    extra='text-anchor="middle"'))
    out.append(text(width - 35, 44, "UTF-8", p["muted"], 12,
                    extra='text-anchor="end"'))
    out.append(text(40, 109, profile["username"].lower() + "@github", p["green"], 17, 600))
    out.append(text(40, 139, "$ ./asciifetch --profile", p["text"], 17))

    portrait_width = 360 if mobile else 400
    portrait_x = 60 if mobile else 86
    portrait_y = 176
    out.append(render_portrait(portrait, portrait_x, portrait_y, portrait_width))
    caption_y = portrait_y + portrait_width + 27
    center = 240 if mobile else 286
    out.append(text(center, caption_y, " ".join(profile["username"].upper()), p["text"], 15, 600,
                    'text-anchor="middle"'))
    out.append(text(center, caption_y + 24, profile["role"].upper(), p["muted"], 11,
                    extra='text-anchor="middle"'))

    info_x = 40 if mobile else 600
    if not mobile:
        out.append(f'<path d="M558 183V{height - 140}" stroke="{p["border"]}" stroke-dasharray="3 7"/>')
        out.append(text(info_x, 186, profile["username"].lower() + "@github", p["accent"], 20, 600))
    else:
        out.append(f'<path d="M40 611H{width - 40}" stroke="{p["border"]}"/>')
    for index, row in enumerate(rows):
        if row:
            label, value = row
            y = info_y + index * line_height
            out.append(text(info_x, y, label, p["accent"], 17, 600))
            out.append(text(info_x + (105 if mobile else 119), y, value, p["text"], 17))

    colors = [p["bar"], "#cc6b63", "#87ad8a", "#e0b66e", "#7aa5c4", "#b59ac4", "#7fc4bc", "#e9e6df"]
    palette_y = info_y + len(rows) * line_height + 4
    for index, color in enumerate(colors):
        out.append(f'<rect x="{info_x + index * 27}" y="{palette_y}" width="27" height="16" fill="{color}"/>')
    out.append(f'<path d="M40 {height - 77}H{width - 40}" stroke="{p["border"]}"/>')
    out.append(text(40, height - 43, "$", p["green"], 18, 600))
    out.append(text(64, height - 43, "Thanks for stopping by.", p["muted"], 16))
    out.append(f'<rect x="306" y="{height - 58}" width="9" height="19" fill="{p["accent"]}"/>')
    out.append(text(width - 40, height - 43, "[ exit 0 ]", p["green"], 13,
                    extra='text-anchor="end"'))
    out.extend(["</g>", "</svg>"])
    return "\n".join(out) + "\n"


def render_readme(profile):
    username = profile["username"]
    url = f"https://github.com/{username}"
    stack = "\n".join(f"| `{label}` | {value} |" for label, value in profile["stack"])
    fields = "\n".join(
        f"{field[0]:<10} {field[1]}" if field else ""
        for field in profile_fields(profile)
    )
    return f'''<!-- Generated by scripts/build_profile.py. Edit profile.json, then rebuild. -->

<picture>
  <source media="(max-width: 640px)" srcset="assets/profile-terminal-mobile.svg">
  <img src="assets/profile-terminal.svg" width="100%" alt="{html.escape(profile['name'])} ({username}) — {html.escape(profile['role'])} in {html.escape(profile['location'])}. {html.escape(profile['portrait']['description'])} Skills and links below.">
</picture>

<p align="center">
  <a href="{url}?tab=repositories"><code>./repositories</code></a>
  &nbsp;·&nbsp;
  <a href="{url}?tab=stars"><code>./stars</code></a>
  &nbsp;·&nbsp;
  <a href="{url}?tab=overview"><code>./activity</code></a>
</p>

### `~ $ whoami`

{profile['intro']}

### `~ $ cat stack.conf`

| Module | Toolkit |
| :--- | :--- |
{stack}

### `~ $ ls github/`

- [Repositories]({url}?tab=repositories) — Browse my code and projects.
- [Starred projects]({url}?tab=stars) — Explore the projects I follow.
- [Contributions]({url}?tab=overview) — See my latest public activity.

<details>
<summary><code>cat profile.txt</code> — plain-text version</summary>

```text
{username.lower()}@github
------------------------------
{fields}
```

</details>

---

<p align="center">
  <sub>Terminal design inspired by <a href="https://github.com/ganji759/asciifetch">asciifetch</a> · Built with text, kept simple.</sub>
</p>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated files are out of date.")
    args = parser.parse_args()
    profile = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"[A-Za-z0-9-]+", profile["username"]):
        parser.error("username must be a GitHub handle")
    if not all(re.fullmatch(r"#[0-9a-fA-F]{6}", color) for color in profile["palette"].values()):
        parser.error("palette colors must use #rrggbb")
    try:
        portrait = load_portrait(profile)
    except (KeyError, ValueError, OSError) as error:
        parser.error(str(error))
    outputs = {
        "assets/profile-terminal.svg": render_svg(profile, portrait),
        "assets/profile-terminal-mobile.svg": render_svg(profile, portrait, mobile=True),
        "README.md": render_readme(profile),
    }
    stale = []
    for name, content in outputs.items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_bytes() != content.encode("utf-8"):
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8"))
            print(f"Built {name}")
    if stale:
        print("Rebuild required: " + ", ".join(stale), file=sys.stderr)
        return 1
    if args.check:
        print("All profile assets are up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
