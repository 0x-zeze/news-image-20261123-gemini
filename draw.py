#!/usr/bin/env python3
"""Generate entry.png: The Global Edition — Monday 23 November 2026 (1024x1024)."""

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
GEOJSON_PATH = Path("/tmp/ne_110m_land.geojson")
OUT_PATH = Path(__file__).resolve().parent / "entry.png"

# Palette — broadsheet newsprint & editorial ink
BG = "#F7F3EA"
INK = "#141412"
MUTED = "#46423A"
RULE_DARK = "#1E1C18"
RULE_LIGHT = "#CBC2AF"
OCEAN = "#E3ECF2"
LAND = "#DED6C3"
COAST = "#7D7564"
GRAT = "#CCD8E1"
CARD_BG = "#EFE8D7"
DATECHECK_HDR = "#8B2C1B"

REGION_COLORS = {
    "Europe": "#1B4F8A",
    "Middle East": "#B83B28",
    "Asia-Pacific": "#0F6B5B",
    "Americas": "#76368A",
    "Africa": "#B86612",
    "Global/Climate/Health/Science": "#286B30",
    "Sport/Culture": "#A8265B",
}

TIMELINE = [
    ("00:49", "UK NHS launches AI breast-cancer trial"),
    ("02:45", "S. Korea vows stability as KOSPI falls 5%"),
    ("06:43", "China sets 2030 elderly & childcare goals"),
    ("11:34", "Kyiv video confirms Benghazi ship strike"),
    ("15:09", "FIFA picks 2031 Americas & 2035 UK"),
    ("15:29", "Nvidia reinstates Huang; shares +31%"),
    ("21:48", "3 tankers hit mines in Strait of Hormuz"),
    ("23:16", "US moves to blacklist AI firm Megaspeed"),
]

# 54 verified stories from Monday 23 November 2026
# Fields: num, region, headline, detail, status, source, city, lat, lon
STORIES = [
    # EUROPE (11)
    (1, "Europe", "Ukraine hits Perm & Novoshakhtinsk refineries",
     "Overnight drone barrage kills 1 in Perm region.", "REPORTED", "Moscow Times", "Perm", 58.01, 56.25),
    (2, "Europe", "EU unveils 22nd Russia sanctions package",
     "Targets Russian sports flags & crypto flows.", "CONFIRMED", "Al Jazeera", "Brussels", 50.85, 4.35),
    (3, "Europe", "Spain Supreme Court shelves Puigdemont case",
     "Removes last hurdle for exiled Catalan leader.", "CONFIRMED", "CNN", "Madrid", 40.42, -3.70),
    (4, "Europe", "Belgium austerity strike grounds flights",
     "Walkout over 2027 cuts halts transit; tear gas.", "CONFIRMED", "France 24", "Brussels", 50.85, 4.35),
    (5, "Europe", "UK sanctions 5 Myanmar junta chiefs",
     "Recognises Rohingya genocide as 14 back ICJ.", "CONFIRMED", "BBC", "London", 51.51, -0.13),
    (6, "Europe", "NATO vows space defence on Russia report",
     "Rutte responds to nuclear anti-satellite claim.", "CONFIRMED", "France 24", "Berlin", 52.52, 13.40),
    (7, "Europe", "Email bomb hoaxes hit German & Danish schools",
     "Hundreds of schools hit; police keep open.", "CONFIRMED", "Reuters", "Copenhagen", 55.68, 12.57),
    (8, "Europe", "Finland summons Russian envoy over breach",
     "Protests suspected helicopter & Baltic acts.", "CONFIRMED", "France 24", "Helsinki", 60.17, 24.94),
    (9, "Europe", "Armenia draft charter drops Karabakh claim",
     "Pashinyan calls reform key to Azerbaijan peace.", "CONFIRMED", "SCMP", "Yerevan", 40.18, 44.51),
    (10, "Europe", "Gisèle Pelicot to sue over nude promo photos",
     "Publisher apologises after abuse photos sent.", "CONFIRMED", "BBC", "Paris", 48.86, 2.35),
    (11, "Europe", "Leaked files show 1,000+ Russian war suicides",
     "Analysis of 11m death records tallies toll.", "REPORTED", "Guardian", "Moscow", 55.76, 37.62),

    # MIDDLE EAST (8)
    (12, "Middle East", "Three tankers explode in Strait of Hormuz",
     "IRGC says vessels hit mines despite air cover.", "REPORTED", "MEE", "Strait of Hormuz", 26.57, 56.25),
    (13, "Middle East", "Iran flogs singer Parastoo Ahmadi 74 times",
     "Lawyers report Qom lashes for hijab-free show.", "REPORTED", "BBC", "Qom", 34.64, 50.88),
    (14, "Middle East", "US sanctions Iranian 'shadow banking' web",
     "Treasury targets 24+ firms in UAE, Turkey, HK.", "CONFIRMED", "Al Jazeera", "Dubai", 25.20, 55.27),
    (15, "Middle East", "Iran courts order US to pay $290bn damages",
     "Judiciary also files suits against Gulf states.", "CONFIRMED", "France 24", "Tehran", 35.69, 51.39),
    (16, "Middle East", "Gaza 'toxic wasteland'; Israeli fire kills 4",
     "Oxfam finds 99% tainted; UN notes 77-yr loss.", "CONFIRMED", "BBC/UN", "Gaza City", 31.50, 34.47),
    (17, "Middle East", "Qatar PM pushes to revive US-Iran talks",
     "Warns Gulf cannot risk war after Rubio meet.", "CONFIRMED", "MEE", "Doha", 25.29, 51.53),
    (18, "Middle East", "Israeli raid in Syria's Koya torches homes",
     "Families flee gunfire; US weighs Syria roles.", "REPORTED", "Al Jazeera", "Koya", 32.73, 35.79),
    (19, "Middle East", "Turkey reports PKK quit 14 more N. Iraq bases",
     "State media cites MIT on disarmament pullout.", "REPORTED", "AFP", "Erbil", 36.19, 44.01),

    # ASIA-PACIFIC (11)
    (20, "Asia-Pacific", "Indonesia confirms 24 dead in factory blaze",
     "Toll jumps from 3; ~30 missing in Cikande.", "CONFIRMED", "Guardian", "Cikande", -6.21, 106.36),
    (21, "Asia-Pacific", "India pledges $1.6bn to Nepal in ties reset",
     "Offers flood aid, port access & rail to Shah.", "CONFIRMED", "BBC", "New Delhi", 28.61, 77.21),
    (22, "Asia-Pacific", "S. Korea vows stability after 5% KOSPI drop",
     "Finance chief flags chip swings in tech rout.", "CONFIRMED", "CNA", "Seoul", 37.57, 126.98),
    (23, "Asia-Pacific", "Tajikistan begins withdrawal from ICC",
     "Fourth state to move to exit after US push.", "CONFIRMED", "Reuters", "Dushanbe", 38.56, 68.77),
    (24, "Asia-Pacific", "Indonesia's Prabowo names 2 VP nominees",
     "Picks Sulaiman & Sugiono ahead of Dec 11 vote.", "CONFIRMED", "CNA", "Jakarta", -6.21, 106.85),
    (25, "Asia-Pacific", "Bangladesh vows Hasina arrest; 45 hurt",
     "Awami League & BNP fights rock 2 districts.", "CONFIRMED", "CNA", "Dhaka", 23.81, 90.41),
    (26, "Asia-Pacific", "N. Korea's Kim stresses sovereignty in ties",
     "Outlines foreign policy after Trump no-show.", "CONFIRMED", "CNA", "Pyongyang", 39.04, 125.76),
    (27, "Asia-Pacific", "China sets 2030 elderly & childcare goals",
     "Expands care homes; agrees trade group w/ Mex.", "CONFIRMED", "CNA", "Beijing", 39.90, 116.41),
    (28, "Asia-Pacific", "India to test all bottled water brands",
     "Sweeping audit after unsafe Bisleri sample.", "CONFIRMED", "CNA", "Mumbai", 19.08, 72.88),
    (29, "Asia-Pacific", "Thai court halves MP's royal-insult term",
     "Appellate judges cut Rukchanok Srinork jail.", "CONFIRMED", "CNA", "Bangkok", 13.76, 100.50),
    (30, "Asia-Pacific", "Australia flags AI as foreign-policy threat",
     "FM Wong warns of overseas election meddling.", "CONFIRMED", "SCMP", "Canberra", -35.28, 149.13),

    # AMERICAS (10)
    (31, "Americas", "Nvidia reinstates Jensen Huang; stock +31%",
     "Board reverses exit after Trump; Dems probe.", "CONFIRMED", "CBS/BBC", "Santa Clara", 37.35, -121.95),
    (32, "Americas", "US to blacklist Asian AI firm Megaspeed",
     "Accused of funneling chips to China in affair.", "REPORTED", "BBC", "Washington", 38.91, -77.04),
    (33, "Americas", "Democrats flip 47+ US House seats",
     "Widest margin in 50 yrs; Green Card bill out.", "CONFIRMED", "NPR", "Washington", 38.91, -77.04),
    (34, "Americas", "Virginia & Oregon sue SpaceX over Grok",
     "Lawsuits target chatbot 'spicy mode' CSAM.", "CONFIRMED", "Al Jazeera", "Richmond", 37.54, -77.44),
    (35, "Americas", "US DoJ admits wrongly deporting citizen",
     "Filing confirms US citizen was sent to Mexico.", "CONFIRMED", "Guardian", "Austin", 30.27, -97.74),
    (36, "Americas", "Outrage over ICE arrest at Seattle airport",
     "Mexican father & daughter held; O'Hare delay.", "CONFIRMED", "BBC", "Seattle", 47.61, -122.33),
    (37, "Americas", "Trump delays toxic Army blast in Iowa",
     "Postpones 5t lead azide disposal after outcry.", "CONFIRMED", "Al Jazeera", "Des Moines", 41.59, -93.62),
    (38, "Americas", "Gunmen ambush Mexican troops; 8 arrested",
     "Attack follows weekend capture of cartel boss.", "CONFIRMED", "BBC", "Mexico City", 19.43, -99.13),
    (39, "Americas", "Drone strike hits Colombian police base",
     "3 hurt incl. infant; Bogotá asks X to ban Petro.", "CONFIRMED", "Al Jazeera", "Bogotá", 4.71, -74.07),
    (40, "Americas", "Pneumonia hits Bolsonaro; Brazil trims GDP",
     "Ex-leader in ICU; 2027 growth cut to 1.8%.", "CONFIRMED", "MercoPress", "Brasília", -15.79, -47.88),

    # AFRICA (6)
    (41, "Africa", "Kyiv confirms Benghazi Russian warship sink",
     "Zelensky/SBU claim strike; Libya & UN seek probe.", "CONFIRMED", "NPR/UN", "Benghazi", 32.12, 20.09),
    (42, "Africa", "Drone strikes hit homes & UN site in Sudan",
     "UN condemns Khartoum hits with staff inside.", "CONFIRMED", "Africanews", "Khartoum", 15.50, 32.56),
    (43, "Africa", "Ituri clashes trap DR Congo Ebola teams",
     "WHO says fighting halted response 24h+.", "CONFIRMED", "UN News", "Bunia", 1.56, 30.25),
    (44, "Africa", "Zambian opposition chief indicted for treason",
     "Prosecutors charge Mundubile over coup plot.", "CONFIRMED", "Africanews", "Lusaka", -15.39, 28.32),
    (45, "Africa", "Rescuers search after Nigeria boat tragedy",
     "Crews hunt survivors; Tinubu notes outages.", "CONFIRMED", "BBC", "Abuja", 9.06, 7.49),
    (46, "Africa", "Zimbabwean preacher Uebert Angel arrested",
     "British-Zimbabwean leader held on assault claim.", "CONFIRMED", "BBC", "Harare", -17.83, 31.05),

    # GLOBAL / CLIMATE / HEALTH / SCIENCE (4)
    (47, "Global/Climate/Health/Science", "Plant-based lunches could cut 15.4m t CO2/yr",
     "Australia study projects $611 household savings.", "CONFIRMED", "Guardian", "Sydney", -33.87, 151.21),
    (48, "Global/Climate/Health/Science", "UN chief urges global AI safety pact in 1 yr",
     "Guterres warns in Barbados of power shift.", "CONFIRMED", "France 24", "Bridgetown", 13.10, -59.61),
    (49, "Global/Climate/Health/Science", "UK NHS launches largest AI cancer trial",
     "Tests artificial intelligence in breast checks.", "CONFIRMED", "BBC", "London", 51.51, -0.13),
    (50, "Global/Climate/Health/Science", "Giant exoplanet HIP 88962 b spotted in Chile",
     "5x Jupiter world around tiny star defies models.", "CONFIRMED", "SCMP", "Atacama", -24.63, -70.40),

    # SPORT / CULTURE (4)
    (51, "Sport/Culture", "FIFA picks 2031 Americas & 2035 UK WWC",
     "US/Mex/Jam/CR host 2031; UK first since 1966.", "CONFIRMED", "AFP/BBC", "Zurich", 47.37, 8.54),
    (52, "Sport/Culture", "Marco Penge wins 4-man PGA Tour play-off",
     "Claims Monday RSM Classic in Georgia & 2027 card.", "CONFIRMED", "BBC Sport", "Sea Island", 31.18, -81.35),
    (53, "Sport/Culture", "Don Toliver delays shows over arena gas",
     "Police probe Manchester irritant sickening 80+.", "CONFIRMED", "BBC", "Manchester", 53.48, -2.24),
    (54, "Sport/Culture", "Barbados town signs reparative pact w/ Bristol",
     "Speightstown 3-yr deal addresses slave-trade ties.", "CONFIRMED", "Guardian", "Bristol", 51.45, -2.59),
]

DATE_CHECK = [
    ("19 Nov", "ICJ rules Myanmar committed Rohingya genocide (BBC)"),
    ("21 Nov", "Three Russian cruise missiles land in Poland (BBC/NPR)"),
    ("21 Nov", "Zanzibar fire engulfs 6 hotels, 180 evacuated (Africanews)"),
    ("22 Nov", "COP31 talks in Antalya collapse with no deal (BBC/AFP)"),
    ("22 Nov", "S. Korea education chief quits over AI exam scandal (AFP)"),
    ("22 Nov", "Alcaraz ATP Finals; Simeone 345th win; Bulgari dies (BBC)"),
]

DAY_IN_NUMBERS = [
    ("+31%", "Nvidia surge (~$1tn)"),
    ("47+", "US House seats flipped"),
    ("24", "Dead in Indonesia blaze"),
    ("99%", "Gaza area contaminated"),
    ("74", "Lashes given in Qom"),
    ("$1.6bn", "India aid pledge to Nepal"),
]


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


class GeometryAuditor:
    """Tracks every drawn string bounding box against its allotted container."""

    def __init__(self):
        self.violations = []
        self.text_boxes = []

    def draw_text(self, draw: ImageDraw.ImageDraw, xy, text: str, font, fill,
                  box, group: str, anchor=None):
        x, y = xy
        if anchor:
            bbox = draw.textbbox((x, y), text, font=font, anchor=anchor)
            draw.text((x, y), text, font=font, fill=fill, anchor=anchor)
        else:
            bbox = draw.textbbox((x, y), text, font=font)
            draw.text((x, y), text, font=font, fill=fill)
        x0, y0, x1, y1 = bbox
        bx0, by0, bx1, by1 = box
        if x0 < bx0 - 1 or y0 < by0 - 1 or x1 > bx1 + 1 or y1 > by1 + 1:
            self.violations.append(
                f"OUT-OF-BOX [{group}] '{text[:36]}': text={bbox} vs box={box}"
            )
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            self.violations.append(
                f"OUT-OF-CANVAS [{group}] '{text[:36]}': text={bbox}"
            )
        self.text_boxes.append((group, x0, y0, x1, y1, text))
        return bbox

    def check_overlaps(self):
        by_group = {}
        for g, x0, y0, x1, y1, txt in self.text_boxes:
            by_group.setdefault(g, []).append((x0, y0, x1, y1, txt))
        for g, items in by_group.items():
            for i in range(len(items)):
                ax0, ay0, ax1, ay1, at = items[i]
                for j in range(i + 1, len(items)):
                    bx0, by0, bx1, by1, bt = items[j]
                    ox = min(ax1, bx1) - max(ax0, bx0)
                    oy = min(ay1, by1) - max(ay0, by0)
                    if ox > 1 and oy > 1:
                        self.violations.append(
                            f"OVERLAP [{g}] '{at[:24]}' & '{bt[:24]}' (ox={ox}, oy={oy})"
                        )


def text_width(font, text: str) -> float:
    b = font.getbbox(text)
    return b[2] - b[0]


def wrap_text(font, text: str, max_w: float) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        cand = f"{cur} {w}".strip() if cur else w
        if text_width(font, cand) <= max_w:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_world_map(map_w: int, map_h: int) -> Image.Image:
    """Render supersampled Natural Earth 110m equirectangular base map."""
    scale = 3
    sw, sh = map_w * scale, map_h * scale
    m = Image.new("RGB", (sw, sh), OCEAN)
    d = ImageDraw.Draw(m)

    for lon in range(-150, 180, 30):
        x = (lon + 180.0) / 360.0 * sw
        d.line([(x, 0), (x, sh)], fill=GRAT, width=1 * scale)
    for lat in range(-60, 90, 30):
        y = (90.0 - lat) / 180.0 * sh
        w = 2 if lat == 0 else 1
        d.line([(0, y), (sw, y)], fill=GRAT, width=w * scale)

    data = json.loads(GEOJSON_PATH.read_text(encoding="utf-8"))
    for feat in data["features"]:
        geom = feat["geometry"]
        gtype = geom["type"]
        polys = [geom["coordinates"]] if gtype == "Polygon" else geom["coordinates"]
        for poly in polys:
            ring = poly[0]
            pts = [
                ((lon + 180.0) / 360.0 * sw, (90.0 - lat) / 180.0 * sh)
                for lon, lat in ring
            ]
            if len(pts) >= 3:
                d.polygon(pts, fill=LAND, outline=COAST)

    return m.resize((map_w, map_h), Image.Resampling.LANCZOS)


def place_badges(anchors: list[tuple[int, float, float]], map_x: int, map_y: int,
                 map_w: int, map_h: int, r: float = 5.4) -> dict[int, tuple[float, float]]:
    """Deterministic force-directed deconfliction keeping all badges inside map frame."""
    # ponytail: O(N^2) repulsion for N=54; switch to spatial grid if N>300.
    min_dist = r * 2.15
    pad = r + 1.5
    xmin, xmax = map_x + pad, map_x + map_w - pad
    ymin, ymax = map_y + pad, map_y + map_h - pad

    pos = {}
    seen = {}
    for num, ax, ay in anchors:
        key = (round(ax, 1), round(ay, 1))
        idx = seen.get(key, 0)
        seen[key] = idx + 1
        ang = idx * 2.399963
        rad = 0.0 if idx == 0 else 4.0 + 2.0 * idx
        bx = min(max(ax + rad * math.cos(ang), xmin), xmax)
        by = min(max(ay + rad * math.sin(ang), ymin), ymax)
        pos[num] = [bx, by, ax, ay]

    nums = [a[0] for a in anchors]
    for step in range(450):
        k_anchor = 0.045 if step < 300 else 0.015
        forces = {n: [0.0, 0.0] for n in nums}
        for i in range(len(nums)):
            ni = nums[i]
            xi, yi, axi, ayi = pos[ni]
            forces[ni][0] += (axi - xi) * k_anchor
            forces[ni][1] += (ayi - yi) * k_anchor
            for j in range(i + 1, len(nums)):
                nj = nums[j]
                xj, yj, _, _ = pos[nj]
                dx = xi - xj
                dy = yi - yj
                d = math.hypot(dx, dy)
                if d < min_dist:
                    if d < 1e-4:
                        dx, dy, d = 1.0, 0.5, math.hypot(1.0, 0.5)
                    push = (min_dist - d) * 0.58
                    ux, uy = dx / d, dy / d
                    forces[ni][0] += ux * push
                    forces[ni][1] += uy * push
                    forces[nj][0] -= ux * push
                    forces[nj][1] -= uy * push
        for n in nums:
            pos[n][0] = min(max(pos[n][0] + forces[n][0], xmin), xmax)
            pos[n][1] = min(max(pos[n][1] + forces[n][1], ymin), ymax)

    return {n: (pos[n][0], pos[n][1]) for n in nums}


def draw_story_block(draw, auditor, story, x0: int, y0: int, col_w: int,
                     max_y: int, f_num, f_hl, f_body, f_meta, group: str,
                     hl_step: int = 12, body_step: int = 11, gap: int = 5) -> int:
    """Draw a story block with atomic non-breaking [STATUS · Source] tag."""
    num, region, hl, detail, status, source, city, lat, lon = story
    col = REGION_COLORS[region]
    y = y0

    pill_w, pill_h = 17, 11
    draw.rounded_rectangle([x0, y, x0 + pill_w, y + pill_h], radius=2, fill=col)
    auditor.draw_text(
        draw, (x0 + pill_w / 2, y + pill_h / 2), str(num),
        font=f_num, fill="#FFFFFF",
        box=(x0, y - 1, x0 + pill_w, y + pill_h + 1), group=f"{group}_pill", anchor="mm"
    )

    hx = x0 + pill_w + 4
    hw = col_w - pill_w - 4
    hl_lines = wrap_text(f_hl, hl, hw)
    for idx, line in enumerate(hl_lines):
        lx = hx if idx == 0 else x0
        lw = hw if idx == 0 else col_w
        auditor.draw_text(
            draw, (lx, y), line, font=f_hl, fill=INK,
            box=(lx, y - 1, lx + lw, max_y), group=group
        )
        y += hl_step

    tag = f"[{status} · {source}]"
    tag_w = text_width(f_meta, tag)
    tag_col = "#1D5B2E" if status == "CONFIRMED" else "#8A4A08"

    detail_lines = wrap_text(f_body, detail, col_w)
    for idx, line in enumerate(detail_lines):
        is_last = (idx == len(detail_lines) - 1)
        if is_last:
            lw = text_width(f_body, line + " ")
            if lw + tag_w <= col_w:
                auditor.draw_text(
                    draw, (x0, y), line, font=f_body, fill=MUTED,
                    box=(x0, y - 1, x0 + col_w, max_y), group=group
                )
                auditor.draw_text(
                    draw, (x0 + lw, y + 0.5), tag, font=f_meta, fill=tag_col,
                    box=(x0, y - 1, x0 + col_w, max_y), group=group
                )
                y += body_step
            else:
                auditor.draw_text(
                    draw, (x0, y), line, font=f_body, fill=MUTED,
                    box=(x0, y - 1, x0 + col_w, max_y), group=group
                )
                y += body_step
                auditor.draw_text(
                    draw, (x0, y), tag, font=f_meta, fill=tag_col,
                    box=(x0, y - 1, x0 + col_w, max_y), group=group
                )
                y += body_step
        else:
            auditor.draw_text(
                draw, (x0, y), line, font=f_body, fill=MUTED,
                box=(x0, y - 1, x0 + col_w, max_y), group=group
            )
            y += body_step

    return y + gap


def draw_section_header(draw, auditor, title: str, count: int, color: str,
                        x0: int, y0: int, col_w: int, group: str) -> int:
    hdr_h = 15
    draw.rectangle([x0, y0, x0 + col_w, y0 + hdr_h], fill=color)
    f_hdr = load_font("DejaVuSans-Bold.ttf", 9)
    label = f"{title.upper()} ({count})"
    auditor.draw_text(
        draw, (x0 + 5, y0 + hdr_h / 2), label, font=f_hdr, fill="#FFFFFF",
        box=(x0, y0, x0 + col_w, y0 + hdr_h), group=group, anchor="lm"
    )
    return y0 + hdr_h + 4


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    auditor = GeometryAuditor()

    # Fonts (maximised within 1024x1024 budget for 54 stories + map + timeline + DATE CHECK)
    f_title = load_font("DejaVuSerif-Bold.ttf", 23)
    f_date = load_font("DejaVuSerif-Bold.ttf", 12)
    f_sub = load_font("DejaVuSans.ttf", 8)
    f_ear = load_font("DejaVuSans-Bold.ttf", 7)
    f_tl_t = load_font("DejaVuSansMono-Bold.ttf", 8)
    f_tl_b = load_font("DejaVuSans.ttf", 7)
    f_pin = load_font("DejaVuSans-Bold.ttf", 7)
    f_num = load_font("DejaVuSans-Bold.ttf", 7)
    f_hl = load_font("DejaVuSans-Bold.ttf", 9)
    f_body = load_font("DejaVuSans.ttf", 9)
    f_meta = load_font("DejaVuSans-Bold.ttf", 8)
    f_dc = load_font("DejaVuSans.ttf", 8)
    f_leg = load_font("DejaVuSans.ttf", 7)
    f_foot = load_font("DejaVuSans-Bold.ttf", 8)
    f_stat_n = load_font("DejaVuSerif-Bold.ttf", 13)
    f_stat_l = load_font("DejaVuSans.ttf", 7)

    # 1. MASTHEAD (y=6..46)
    draw.line([(12, 6), (W - 12, 6)], fill=RULE_DARK, width=2)
    draw.line([(12, 10), (W - 12, 10)], fill=RULE_DARK, width=1)
    auditor.draw_text(
        draw, (14, 15), "WORLD NEWS DISPATCH", font=f_ear, fill=MUTED,
        box=(12, 11, 200, 45), group="masthead"
    )
    auditor.draw_text(
        draw, (14, 27), "54 VERIFIED STORIES · 7 REGIONS", font=f_ear, fill=INK,
        box=(12, 11, 220, 45), group="masthead"
    )
    auditor.draw_text(
        draw, (W / 2, 28), "THE GLOBAL EDITION", font=f_title, fill=INK,
        box=(220, 11, 760, 46), group="masthead", anchor="mm"
    )
    auditor.draw_text(
        draw, (W - 14, 14), "Monday 23 November 2026", font=f_date, fill=INK,
        box=(760, 11, W - 12, 45), group="masthead", anchor="rt"
    )
    auditor.draw_text(
        draw, (W - 14, 30), "00:00–23:59 UTC · Fresh Multi-Source Wire", font=f_sub, fill=MUTED,
        box=(760, 11, W - 12, 45), group="masthead", anchor="rt"
    )
    draw.line([(12, 46), (W - 12, 46)], fill=RULE_DARK, width=2)

    # 2. UTC TIMELINE STRIP (y=49..89)
    draw.rectangle([12, 50, 56, 87], fill=INK)
    auditor.draw_text(
        draw, (34, 62), "UTC", font=f_ear, fill="#FFFFFF",
        box=(12, 50, 56, 87), group="tl_hdr", anchor="mm"
    )
    auditor.draw_text(
        draw, (34, 74), "TIMELINE", font=f_ear, fill="#E0D9C8",
        box=(12, 50, 56, 87), group="tl_hdr", anchor="mm"
    )
    tl_x0, tl_x1 = 62, W - 12
    slot_w = (tl_x1 - tl_x0) / len(TIMELINE)
    axis_y = 63
    draw.line([(tl_x0 + 8, axis_y), (tl_x1 - 8, axis_y)], fill=RULE_DARK, width=1)
    for i, (ts, lbl) in enumerate(TIMELINE):
        sx0 = int(tl_x0 + i * slot_w)
        sx1 = int(tl_x0 + (i + 1) * slot_w)
        cx = (sx0 + sx1) / 2
        draw.ellipse([cx - 2.5, axis_y - 2.5, cx + 2.5, axis_y + 2.5], fill=DATECHECK_HDR)
        auditor.draw_text(
            draw, (cx, 54), f"{ts}Z", font=f_tl_t, fill=INK,
            box=(sx0, 49, sx1, 61), group=f"tl_{i}", anchor="mm"
        )
        lines = wrap_text(f_tl_b, lbl, slot_w - 6)[:2]
        for li, ln in enumerate(lines):
            auditor.draw_text(
                draw, (cx, 67 + li * 9), ln, font=f_tl_b, fill=MUTED,
                box=(sx0, 64, sx1, 88), group=f"tl_{i}", anchor="mt"
            )
    draw.line([(12, 89), (W - 12, 89)], fill=RULE_LIGHT, width=1)

    # 3. WORLD MAP (left, 600x300 exact 2:1 equirectangular) + RIGHT PANEL (x=622..1012)
    map_x, map_y, map_w, map_h = 12, 93, 600, 300
    base_map = render_world_map(map_w, map_h)
    img.paste(base_map, (map_x, map_y))
    draw.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], outline=RULE_DARK, width=1)

    anchors = []
    story_by_num = {}
    for s in STORIES:
        num, region, hl, detail, status, source, city, lat, lon = s
        ax = map_x + (lon + 180.0) / 360.0 * map_w
        ay = map_y + (90.0 - lat) / 180.0 * map_h
        anchors.append((num, ax, ay))
        story_by_num[num] = (s, ax, ay)

    assert set(story_by_num.keys()) == set(range(1, len(STORIES) + 1)), "Pin numbers mismatch"
    badge_r = 5.4
    badge_pos = place_badges(anchors, map_x, map_y, map_w, map_h, r=badge_r)

    badge_list = list(badge_pos.items())
    for i in range(len(badge_list)):
        ni, (xi, yi) = badge_list[i]
        if not (map_x + badge_r <= xi <= map_x + map_w - badge_r and
                map_y + badge_r <= yi <= map_y + map_h - badge_r):
            auditor.violations.append(f"BADGE-OUT-OF-MAP #{ni}: ({xi:.1f},{yi:.1f})")
        for j in range(i + 1, len(badge_list)):
            nj, (xj, yj) = badge_list[j]
            d = math.hypot(xi - xj, yi - yj)
            if d < badge_r * 2.0:
                auditor.violations.append(f"BADGE-OVERLAP #{ni} & #{nj}: d={d:.2f}")

    for num, ax, ay in anchors:
        bx, by = badge_pos[num]
        col = REGION_COLORS[story_by_num[num][0][1]]
        if math.hypot(bx - ax, by - ay) > badge_r:
            draw.line([(ax, ay), (bx, by)], fill="#33302A", width=1)
        draw.ellipse([ax - 2, ay - 2, ax + 2, ay + 2], fill=col, outline="#FFFFFF", width=1)

    for num, ax, ay in anchors:
        bx, by = badge_pos[num]
        col = REGION_COLORS[story_by_num[num][0][1]]
        draw.ellipse(
            [bx - badge_r, by - badge_r, bx + badge_r, by + badge_r],
            fill=col, outline="#FFFFFF", width=1
        )
        auditor.draw_text(
            draw, (bx, by), str(num), font=f_pin, fill="#FFFFFF",
            box=(bx - badge_r - 1, by - badge_r - 1, bx + badge_r + 1, by + badge_r + 1),
            group=f"pin_{num}", anchor="mm"
        )

    draw.rectangle([map_x + 3, map_y + map_h - 13, map_x + 224, map_y + map_h - 2], fill="#F7F3EA")
    auditor.draw_text(
        draw, (map_x + 6, map_y + map_h - 7.5),
        "Equirectangular · 54 Story Pins · Natural Earth 110m (PD)",
        font=f_leg, fill=MUTED,
        box=(map_x + 3, map_y + map_h - 14, map_x + 226, map_y + map_h),
        group="map_credit", anchor="lm"
    )

    # RIGHT PANEL (x=622..1012, width 390, y=93..393)
    rp_x, rp_w = 622, 390
    y = 93
    rendered_nums = set()

    global_stories = [s for s in STORIES if s[1] == "Global/Climate/Health/Science"]
    y = draw_section_header(
        draw, auditor, "Global · Climate · Health · Science",
        len(global_stories), REGION_COLORS["Global/Climate/Health/Science"],
        rp_x, y, rp_w, "rp_hdr_gl"
    )
    for s in global_stories:
        y = draw_story_block(
            draw, auditor, s, rp_x, y, rp_w, 233,
            f_num, f_hl, f_body, f_meta, "rp_global",
            hl_step=12, body_step=11, gap=5
        )
        rendered_nums.add(s[0])

    # DATE CHECK BOX (y=235..371)
    dc_y0, dc_y1 = 235, 371
    draw.rectangle([rp_x, dc_y0, rp_x + rp_w, dc_y1], fill=CARD_BG, outline=DATECHECK_HDR, width=1)
    draw.rectangle([rp_x, dc_y0, rp_x + rp_w, dc_y0 + 15], fill=DATECHECK_HDR)
    auditor.draw_text(
        draw, (rp_x + 5, dc_y0 + 7.5),
        "DATE CHECK — LEFT OUT AS OLDER NEWS (BEFORE 23 NOV)",
        font=f_meta, fill="#FFFFFF",
        box=(rp_x, dc_y0, rp_x + rp_w, dc_y0 + 15), group="dc_hdr", anchor="lm"
    )
    dy = dc_y0 + 20
    for dt, desc in DATE_CHECK:
        draw.rounded_rectangle([rp_x + 5, dy, rp_x + 40, dy + 11], radius=2, fill="#6F2B1D")
        auditor.draw_text(
            draw, (rp_x + 22.5, dy + 5.5), dt, font=f_num, fill="#FFFFFF",
            box=(rp_x + 5, dy - 1, rp_x + 40, dy + 12), group="dc_badge", anchor="mm"
        )
        lines = wrap_text(f_dc, desc, rp_w - 48)
        for ln in lines:
            auditor.draw_text(
                draw, (rp_x + 44, dy + 1), ln, font=f_dc, fill=INK,
                box=(rp_x + 43, dy - 1, rp_x + rp_w - 4, dc_y1 - 2), group="dc_body"
            )
            dy += 10
        dy += 9 if len(lines) == 1 else 3

    # Compact Color Key Strip (y=375..393)
    draw.rectangle([rp_x, 375, rp_x + rp_w, 393], fill="#EDE7D8", outline=RULE_LIGHT, width=1)
    kx = rp_x + 5
    key_items = [
        ("Europe", "Europe 11"),
        ("Middle East", "M.East 8"),
        ("Asia-Pacific", "Asia-Pac 11"),
        ("Americas", "Americas 10"),
        ("Africa", "Africa 6"),
        ("Global/Climate/Health/Science", "Global 4"),
        ("Sport/Culture", "Sport 4"),
    ]
    for reg, lbl in key_items:
        draw.ellipse([kx, 381, kx + 6, 387], fill=REGION_COLORS[reg])
        auditor.draw_text(
            draw, (kx + 8, 384), lbl, font=f_leg, fill=INK,
            box=(rp_x + 2, 375, rp_x + rp_w - 2, 393), group="legend", anchor="lm"
        )
        kx += int(text_width(f_leg, lbl)) + 13

    draw.line([(12, 398), (W - 12, 398)], fill=RULE_DARK, width=1)

    # 4. MAIN 3-COLUMN GRID (y=402..991, height 589px)
    col_xs = [12, 349, 686]
    col_w = 326
    grid_top, grid_bot = 402, 991

    draw.line([(343, grid_top), (343, grid_bot)], fill=RULE_LIGHT, width=1)
    draw.line([(680, grid_top), (680, grid_bot)], fill=RULE_LIGHT, width=1)

    col_plan = [
        [("Europe", "Europe"), ("Africa", "Africa")],
        [("Asia-Pacific", "Asia-Pacific"), ("Sport/Culture", "Sport · Culture")],
        [("Americas", "Americas"), ("Middle East", "Middle East")],
    ]

    col_ends = []
    for ci, sections in enumerate(col_plan):
        cx = col_xs[ci]
        cy = grid_top
        for si, (reg_key, reg_title) in enumerate(sections):
            reg_stories = [s for s in STORIES if s[1] == reg_key]
            if si > 0:
                cy += 5
            cy = draw_section_header(
                draw, auditor, reg_title, len(reg_stories), REGION_COLORS[reg_key],
                cx, cy, col_w, f"col{ci}_hdr_{si}"
            )
            for s in reg_stories:
                cy = draw_story_block(
                    draw, auditor, s, cx, cy, col_w, grid_bot,
                    f_num, f_hl, f_body, f_meta, f"col{ci}",
                    hl_step=12, body_step=11, gap=5
                )
                rendered_nums.add(s[0])
        col_ends.append(cy)
        if cy > grid_bot:
            auditor.violations.append(f"COL{ci}-OVERFLOW: cy={cy} > {grid_bot}")

    # DAY IN NUMBERS editorial box at bottom of Col 2 (balances the 3 columns cleanly)
    box_y0 = col_ends[1] + 5
    box_y1 = grid_bot - 2
    cx = col_xs[1]
    if box_y1 - box_y0 >= 76:
        draw.rectangle([cx, box_y0, cx + col_w, box_y1], fill=CARD_BG, outline=RULE_DARK, width=1)
        draw.rectangle([cx, box_y0, cx + col_w, box_y0 + 15], fill=RULE_DARK)
        auditor.draw_text(
            draw, (cx + 5, box_y0 + 7.5),
            "DAY IN NUMBERS · MONDAY 23 NOVEMBER 2026",
            font=f_meta, fill="#F7F3EA",
            box=(cx, box_y0, cx + col_w, box_y0 + 15), group="nums_hdr", anchor="lm"
        )
        inner_top = box_y0 + 19
        cell_w = col_w / 3
        cell_h = (box_y1 - inner_top - 4) / 2
        for idx, (val, lbl) in enumerate(DAY_IN_NUMBERS):
            r_i, c_i = divmod(idx, 3)
            x_c = cx + c_i * cell_w
            y_c = inner_top + r_i * cell_h
            if c_i > 0:
                draw.line([(x_c, y_c + 2), (x_c, y_c + cell_h - 4)], fill=RULE_LIGHT, width=1)
            if r_i > 0:
                draw.line([(x_c + 4, y_c - 1), (x_c + cell_w - 4, y_c - 1)], fill=RULE_LIGHT, width=1)
            auditor.draw_text(
                draw, (x_c + cell_w / 2, y_c + cell_h * 0.34), val,
                font=f_stat_n, fill=DATECHECK_HDR,
                box=(x_c + 2, y_c, x_c + cell_w - 2, y_c + cell_h),
                group=f"stat_{idx}", anchor="mm"
            )
            auditor.draw_text(
                draw, (x_c + cell_w / 2, y_c + cell_h * 0.74), lbl,
                font=f_stat_l, fill=INK,
                box=(x_c + 2, y_c, x_c + cell_w - 2, y_c + cell_h),
                group=f"stat_{idx}", anchor="mm"
            )

    # 5. FOOTER (y=996..1020)
    region_order = [
        ("Europe", "Europe"),
        ("Middle East", "Middle East"),
        ("Asia-Pacific", "Asia-Pacific"),
        ("Americas", "Americas"),
        ("Africa", "Africa"),
        ("Global/Climate/Health/Science", "Global/Climate/Health/Science"),
        ("Sport/Culture", "Sport/Culture"),
    ]
    counts = {k: sum(1 for s in STORIES if s[1] == k) for k, _ in region_order}
    total_stories = sum(counts.values())
    assert total_stories == len(STORIES) == len(rendered_nums), (
        f"Story count mismatch: sum={total_stories}, total={len(STORIES)}, rendered={len(rendered_nums)}"
    )

    draw.rectangle([12, 996, W - 12, 1019], fill=RULE_DARK)
    parts = " · ".join(f"{lbl} {counts[k]}" for k, lbl in region_order)
    footer_text = f"TOTAL {total_stories} STORIES: {parts}"
    auditor.draw_text(
        draw, (W / 2, 1007.5), footer_text, font=f_foot, fill="#F7F3EA",
        box=(14, 996, W - 14, 1019), group="footer", anchor="mm"
    )

    auditor.check_overlaps()
    if auditor.violations:
        print(f"AUDIT FAILED ({len(auditor.violations)} issues):")
        for v in auditor.violations[:30]:
            print("  -", v)
        raise SystemExit(1)

    img.save(OUT_PATH, format="PNG", optimize=True)
    size_bytes = OUT_PATH.stat().st_size
    assert img.size == (1024, 1024), f"Wrong size: {img.size}"
    assert size_bytes <= 1048576, f"File too large: {size_bytes} bytes"
    print(f"OK: wrote {OUT_PATH} ({img.size[0]}x{img.size[1]}, {size_bytes:,} bytes)")
    print(f"Column bottom y-coords: {col_ends} (grid_bot={grid_bot})")
    print(f"Stories rendered: {len(rendered_nums)} (sum of region counts: {total_stories})")
    for k, lbl in region_order:
        print(f"  {lbl}: {counts[k]}")
    print("Geometry audit: 0 violations (all text boxes in-bounds, 0 overlaps, 0 badge collisions)")


if __name__ == "__main__":
    main()
