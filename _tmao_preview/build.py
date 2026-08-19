import io, re, sys

BS = chr(92)
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HERE)   # the report repo root, one level up
JS = ROOT + "\\index.js"
CSS = ROOT + "\\index.css"

ESC = re.compile(BS + BS + "u([0-9a-fA-F]{4})")
js_raw = io.open(JS, encoding="utf-8").read()
js = ESC.sub(lambda m: chr(int(m.group(1), 16)), js_raw)
css = io.open(CSS, encoding="utf-8").read()


def must(text, label):
    if text not in js:
        print("FIDELITY FAIL [%s]" % label)
        sys.exit(1)


def field_after(marker, field):
    """read a string literal field out of the bundle, verbatim"""
    i = js.index(marker)
    k = js.index(field + ': "', i) + len(field) + 3
    return js[k:js.index('"', k)]


_FN = "function InterpretationTMAO01("
TITLE = field_after(_FN, "title")
SUBTITLE = field_after(_FN, "subtitle")

# the non-fasting caution, also read straight out of the bundle
_wi = js.index("isNonFastingSample(deviation) &&")
WARN = field_after(js[_wi:_wi + 40], "children")

for _lbl, _v in (("title", TITLE), ("subtitle", SUBTITLE), ("warning", WARN)):
    if not _v or len(_v) < 3:
        print("FIDELITY FAIL [%s] extracted %r" % (_lbl, _v))
        sys.exit(1)
    must(_v, _lbl)


def split_js_strings(seg):
    parts, buf, q, esc = [], "", None, False
    for ch in seg:
        if q is None:
            if ch == "'" or ch == '"':
                q, buf = ch, ""
            continue
        if esc:
            buf += ch
            esc = False
            continue
        if ch == BS:
            esc = True
            continue
        if ch == q:
            parts.append(buf)
            q = None
            continue
        buf += ch
    return parts


def contents_after(marker, expect):
    i = js.index(marker)
    j = js.index("contents: [", i)
    k = js.index("]\n", j)
    parts = split_js_strings(js[j + len("contents: ["):k])
    if len(parts) != expect:
        print("FIDELITY FAIL: %r expected %d paragraphs, got %d" % (marker[:30], expect, len(parts)))
        sys.exit(1)
    return parts


para1 = contents_after("function InterpretationTMAO01(", 2)
para2 = contents_after("relativeRisk: metaboTMAOIndex.relativeRisk", 3)

CUT = [6.2, 9.9]
BANDS = [33.3, 33.3, 33.4]
DISP_MAX = 20.0
COLORS = ["#2B8343", "#F4C61E", "#B41D23"]
LEVELS = ["\u4f4e\u98a8\u96aa", "\u4e2d\u98a8\u96aa", "\u9ad8\u98a8\u96aa"]
# mirrors bandRangeTexts in TMAORiskIndex
RANGES = ["0-%.1f" % CUT[0],
          "%.1f-%.1f" % (CUT[0] + 0.1, CUT[1]),
          "&#8805;%.1f" % (CUT[1] + 0.1)]
GRAD = ("linear-gradient(to right, %s 0%% 33.3%%, %s 33.3%% 66.6%%, %s 66.6%% 100%%)"
        % (COLORS[0], COLORS[1], COLORS[2]))
UM = "\u03bcM"


def level_idx(v):
    # mirrors the engine's generic computeLevelInfo(): low includes its bound
    return 0 if v <= CUT[0] else (1 if v <= CUT[1] else 2)


def bar_pos(v):
    if not (v >= 0):
        return -100.0
    if v <= CUT[0]:
        return v / CUT[0] * BANDS[0]
    if v <= CUT[1]:
        return BANDS[0] + (v - CUT[0]) / (CUT[1] - CUT[0]) * BANDS[1]
    rng = max(DISP_MAX - CUT[1], 1)
    return BANDS[0] + BANDS[1] + min((v - CUT[1]) / rng, 1) * BANDS[2]


def risk_index(v):
    li = level_idx(v)
    col = COLORS[li]
    pos = bar_pos(v)
    bands = ""
    for n in range(3):
        bands += ('<div style="width:%.1f%%" class="meta-guard-tw-inline-block meta-guard-tw-float-left">'
                  '<p style="color:#595959;font-size:14px">%s</p>'
                  '<p style="color:#BFBFBF" class="meta-guard-tw-text-[12px]">%s %s</p></div>'
                  % (BANDS[n], LEVELS[n], RANGES[n], UM))
    return ('<div class="meta-guard-tw-relative meta-guard-tw-pt-[78px]">'
            '<div class="meta-guard-tw-absolute meta-guard-tw-top-0 meta-guard-tw-left-[25%%]">'
            '<div style="color:%s" class="meta-guard-tw-inline-block meta-guard-tw-text-lg">%s</div>'
            '<strong style="color:%s" class="meta-guard-tw-inline-block meta-guard-tw-text-5xl meta-guard-tw-ml-5">'
            '%s<span class="meta-guard-tw-text-xl meta-guard-tw-ml-1">%s</span></strong></div>'
            '<div style="left:%.4f%%" class="meta-guard-tw-absolute meta-guard-tw-top-[58px] '
            'meta-guard-tw-text-center meta-guard-tw-w-[54px] -meta-guard-tw-ml-[27px]">'
            '<div style="border-top-color:#7F7F7F;border-left-color:transparent;border-right-color:transparent" '
            'class="meta-guard-tw-inline-block meta-guard-tw-border-x-4 meta-guard-tw-border-t-[18px]"></div></div>'
            '<div style="background-image:%s" class="meta-guard-tw-h-4 meta-guard-tw-relative">'
            '<div style="background-color:#000;left:33.3%%" class="meta-guard-tw-absolute '
            '-meta-guard-tw-top-2 meta-guard-tw-w-px meta-guard-tw-h-8 "></div>'
            '<div style="background-color:#000;left:66.6%%" class="meta-guard-tw-absolute '
            '-meta-guard-tw-top-2 meta-guard-tw-w-px meta-guard-tw-h-8 "></div></div>'
            '<div class="meta-guard-tw-mt-[10px] meta-guard-tw-w-full rv-clear">%s</div></div>'
            % (col, LEVELS[li], col, ("%g" % v), UM, pos, GRAD, bands))


def summary_card(v):
    li = level_idx(v)
    col = COLORS[li]
    pos = bar_pos(v) - 4.0
    if pos < 1:
        pos = 1.0
    SUMC = ["#A2BE75", "#89AD4C", "#628923"]
    RNG2 = RANGES
    icon_style = "" if col == COLORS[0] else ' style="color:%s"' % col
    segs = ""
    for n in range(3):
        arrow = ""
        if n == 2:
            arrow = ('<span style="border-top-color:#fff;border-bottom-color:#fff;border-right-color:#fff" '
                     'class="meta-guard-tw-absolute -meta-guard-tw-right-[1px] meta-guard-tw-inline-block '
                     'meta-guard-tw-w-0 meta-guard-tw-h-0 meta-guard-tw-border-solid meta-guard-tw-border-l-[10px] '
                     'meta-guard-tw-border-l-transparent meta-guard-tw-border-r-[1px] meta-guard-tw-border-t-[8px] '
                     'meta-guard-tw-border-b-[6px] -meta-guard-tw-top-[1px]"></span>')
        segs += ('<div class="meta-guard-tw-float-left meta-guard-tw-h-3 meta-guard-tw-relative%s" '
                 'style="background-color:%s;width:%.1f%%">'
                 '<span class="meta-guard-tw-text-[12px] meta-guard-tw-absolute meta-guard-tw-text-left '
                 'meta-guard-tw-block meta-guard-tw-top-3 meta-guard-tw-min-w-[40px]">%s</span>'
                 '<span class="meta-guard-tw-text-[11px] meta-guard-tw-absolute meta-guard-tw-text-left '
                 'meta-guard-tw-block meta-guard-tw-top-[26px] meta-guard-tw-whitespace-nowrap" '
                 'style="color:#BFBFBF">%s</span>%s</div>'
                 % ("" if n == 0 else " meta-guard-tw-ml-0.5", SUMC[n], BANDS[n] - 1,
                    LEVELS[n], RNG2[n], arrow))
    return ('<div class="meta-guard-tw-h-[84px]"><div>'
            '<div class="meta-guard-tw-inline-block meta-guard-tw-align-middle">'
            '<span class="rv-ph" style="padding:2px 5px;font-size:9px">icon</span></div>'
            '<div class="meta-guard-tw-inline-block meta-guard-tw-ml-2 meta-guard-tw-align-middle '
            'meta-guard-tw-text-[14px]"%s>%s</div></div>'
            '<div class="meta-guard-tw-mt-5"><div class="meta-guard-tw-relative meta-guard-tw-h-3">'
            '<div class="meta-guard-tw-table meta-guard-tw-text-center meta-guard-tw-h-4 meta-guard-tw-w-full">%s</div>'
            '<div class="meta-guard-tw-w-[30px] meta-guard-tw-h-[30px] meta-guard-tw-p-[2px] '
            '-meta-guard-tw-top-[36px] -meta-guard-tw-ml-[17px] meta-guard-tw-relative meta-guard-tw-inline-block '
            'meta-guard-tw-text-center meta-guard-tw-rounded-full" style="left:%.4f%%;background-color:#fff">'
            '<div class="meta-guard-tw-w-[26px] meta-guard-tw-h-[26px] meta-guard-tw-leading-[26px] '
            'meta-guard-tw-rounded-full meta-guard-tw-text-[12px]" style="color:#fff;background-color:#EC7F48">%s</div>'
            '</div></div></div></div>'
            % (icon_style, TITLE, segs, pos, ("%g" % v)))


def para_block(parts):
    inner = "".join('<p style="color:#606060">%s</p>' % p for p in parts)
    return ('<div style="background-color:#F5F6F7" class="meta-guard-tw-rounded-md meta-guard-tw-px-3 '
            'meta-guard-tw-text-justify meta-guard-tw-py-2 meta-guard-tw-leading-5 undefined">%s</div>' % inner)


HEADER = ('<div class="meta-guard-tw-h-[84px]">'
          '<div class="meta-guard-tw-h-full meta-guard-tw-float-left meta-guard-tw-pt-5">'
          '<span class="rv-ph">mProbe logo</span>'
          '<div class="meta-guard-tw-px-2 meta-guard-tw-text-lg meta-guard-tw-font-bold meta-guard-tw-mt-2 '
          'meta-guard-tw-leading-[18px] meta-guard-tw-text-center" '
          'style="border-left:2px solid #0d33c7;border-right:2px solid #0d33c7;color:#0d33c7">'
          '\u6aa2\u6e2c\u7d50\u679c\u5206\u6790</div></div>'
          '<div style="color:#0d33c7;border:1px solid #0d33c7" class="meta-guard-tw-h-[99%] meta-guard-tw-px-10 '
          'meta-guard-tw-float-right meta-guard-tw-rounded-full meta-guard-tw-pt-[12px]"><div>'
          '<span class="meta-guard-tw-inline-block meta-guard-tw-w-[60px] meta-guard-tw-font-bold">\u53d7\u6aa2\u8005</span>'
          '<span class="meta-guard-tw-inline-block meta-guard-tw-w-[100px]">\u738b\u5c0f\u660e</span>'
          '<span class="meta-guard-tw-inline-block meta-guard-tw-w-[60px] meta-guard-tw-font-bold">\u51fa\u751f\u65e5</span>'
          '<span class="meta-guard-tw-inline-block">1978-03-12</span></div><br><div>'
          '<span class="meta-guard-tw-inline-block meta-guard-tw-w-[60px] meta-guard-tw-font-bold">\u6aa2\u6e2c\u65e5</span>'
          '<span class="meta-guard-tw-inline-block meta-guard-tw-w-[100px]">2026-08-10</span>'
          '<span class="meta-guard-tw-inline-block meta-guard-tw-w-[60px] meta-guard-tw-font-bold">\u5831\u544a\u65e5</span>'
          '<span class="meta-guard-tw-inline-block">2026-08-18</span></div></div>'
          '<div class="meta-guard-tw-h-full meta-guard-tw-w-[1px] meta-guard-tw-float-right meta-guard-tw-mr-8" '
          'style="background:#0d33c7"></div></div>')

PAGENUM = ('<div class="meta-guard-tw-page-number" style="position:absolute;width:38px;text-align:center;'
           'bottom:20px;font-size:14px;height:40px;background:#0FA19C;color:#fff;line-height:40px;right:4mm;'
           'letter-spacing:2px;font-weight:bold;z-index:10">12</div>')


def chapter_page(v, non_fasting):
    warn = ""
    if non_fasting:
        warn = ('<p style="color:#B5820F" class="meta-guard-tw-mt-8 meta-guard-tw-text-center '
                'meta-guard-tw-text-sm">%s</p>' % WARN)
    # plain concatenation: the markup contains literal % (e.g. h-[99%]) so
    # %-formatting the whole string is not safe here
    return ('<section class="rv-paper meta-guard-tw-relative meta-guard-tw-h-[297mm] meta-guard-tw-w-[210mm] '
            'meta-guard-tw-my-0 meta-guard-tw-mx-auto meta-guard-tw-bg-cover" '
            'style="page-break-inside:avoid;page-break-after:always">'
            '<div class="meta-guard-tw-pl-10 meta-guard-tw-pr-10 meta-guard-tw-pt-14">'
            + HEADER
            + '<div class="meta-guard-tw-mt-4 meta-guard-tw-mb-3">'
              '<div style="color:#0C3475" class="meta-guard-tw-inline-block meta-guard-tw-text-3xl '
              'meta-guard-tw-font-bold">' + TITLE + '</div>'
              '<div class="meta-guard-tw-inline-block meta-guard-tw-text-base meta-guard-tw-ml-2">'
            + SUBTITLE + '</div></div>'
            + para_block(para1)
            + '<div class="meta-guard-tw-px-20 meta-guard-tw-py-20 rv-clear">'
            + risk_index(v) + warn + '</div>'
            + '<div class="meta-guard-tw-mt-5">' + para_block(para2) + '</div>'
            + '</div>' + PAGENUM + '</section>')


def cdr(level):
    key = "Moderate" if level == "mid" else "High"
    i = js.index("    TMAO: {")
    seg = js[i:js.index("\n    FLD: {", i)]
    sub = seg[seg.index(key + ": {"):]
    head = sub[:sub.index("dietAdjustment")]

    def one(field):
        k = sub.index(field + ': "') + len(field) + 3
        return sub[k:sub.index('"', k)]

    def arr(field):
        k = sub.index(field + ": [")
        return re.findall(r'"([^"]+)"', sub[k:sub.index("]", k)])

    return {"mainCause": one("mainCause"),
            "dietAdjustment": arr("dietAdjustment"),
            "regularTesting": one("regularTesting"),
            "symptomAlert": one("symptomAlert"),
            "SPEI": one("SPEI") if ('SPEI: "' in head) else None}


def disease_card(level):
    d = cdr(level)
    high = (level == "high")
    dot = "#C53230" if high else "#FFF100"
    title = "%s (%s)" % (TITLE, LEVELS[2] if high else LEVELS[1])
    lis = ""
    if d["SPEI"]:
        lis += ('<li style="margin-top:8px;line-height:20px"><strong>'
                '\u5c0b\u6c42\u5c08\u696d\u8a55\u4f30\u8207\u5e72\u9810:</strong>%s</li>' % d["SPEI"])
    lis += ('<li style="margin-top:8px;line-height:20px"><strong>\u98f2\u98df\u8abf\u6574:</strong>%s</li>'
            % "".join(d["dietAdjustment"]))
    lis += ('<li style="margin-top:8px;line-height:20px"><strong>\u5b9a\u671f\u6aa2\u6e2c:</strong>%s</li>'
            % d["regularTesting"])
    lis += ('<li style="margin-top:8px;line-height:20px"><strong>\u75c7\u72c0\u8b66\u8a0a:</strong>%s</li>'
            % d["symptomAlert"])
    return ('<div class="meta-guard-tw-rounded-[12px] meta-guard-tw-text-[14px] meta-guard-tw-leading-[16px]" '
            'style="padding:12px">'
            '<span class="meta-guard-tw-inline-block meta-guard-tw-mr-2 meta-guard-tw-w-3 meta-guard-tw-h-3 '
            'meta-guard-tw-rounded-full" style="background:%s"></span>'
            '<strong class="meta-guard-tw-text-[14px]" style="color:#0c3475">%s</strong>'
            '<p style="margin-top:6px;line-height:20px"><strong style="color:#0c3475">'
            '\u4e3b\u8981\u539f\u56e0:</strong>%s</p>'
            '<ul style="list-style:disc;padding-left:16px">%s</ul></div>'
            % (dot, title, d["mainCause"], lis))


# --- ListHeader assets, read out of the bundle ---
_dk = js.index('const DOCTOR_PNG = "')
DOCTOR_PNG = js[_dk + 20:js.index('"', _dk + 20)]
_li = js.index("const ListHeader = () => {")
_lseg = js[_li:js.index(chr(10) + "const ", _li + 10)]
_lm = re.search(r'children: "([^"]+)"', _lseg)
LIST_LABEL = _lm.group(1)
if not DOCTOR_PNG.startswith("data:image/png;base64,") or len(LIST_LABEL) < 2:
    print("FIDELITY FAIL [ListHeader assets]")
    sys.exit(1)


def advice_page(level):
    """reproduces InterpretationTMAO02"""
    return ('<section class="rv-paper meta-guard-tw-relative meta-guard-tw-h-[297mm] '
            'meta-guard-tw-w-[210mm] meta-guard-tw-my-0 meta-guard-tw-mx-auto meta-guard-tw-bg-cover" '
            'style="page-break-inside:avoid;page-break-after:always">'
            '<div class="meta-guard-tw-pl-10 meta-guard-tw-pr-10 meta-guard-tw-pt-14">'
            + HEADER
            + '<p class="meta-guard-tw-my-5">'
              '<img alt="" class="meta-guard-tw-inline-block meta-guard-tw-w-[50px] meta-guard-tw-h-[50px]" src="'
            + DOCTOR_PNG + '">'
              '<strong class="meta-guard-tw-text-[18px]" style="color:#0c3475">' + LIST_LABEL + '</strong></p>'
            + '<div style="background:#FBF3E8;border-radius:12px">' + disease_card(level) + '</div>'
            + '</div>' + PAGENUM + '</section>')


bars = ""
for v, cap in [(4.5, "TMAO_MOCK_VALUE = 4.5"),
               (7.8, "TMAO_MOCK_VALUE = 7.8   \u2190 \u76ee\u524d\u8a2d\u5b9a"),
               (13.2, "TMAO_MOCK_VALUE = 13.2")]:
    bars += ('<p class="rv-tier"><span>%s</span><span>\u2192 %s\uff0c\u6307\u6a19\u4f4d\u65bc %.1f%%</span></p>'
             '<div class="rv-crop"><div class="rv-crop-w">%s</div></div>'
             % (cap, LEVELS[level_idx(v)], bar_pos(v), risk_index(v)))

cards = ""
for lv, cap in [("mid", "\u4e2d\u98a8\u96aa \u2014 \u672a\u542b\u300c\u5c0b\u6c42\u5c08\u696d\u8a55\u4f30\u8207\u5e72\u9810\u300d"),
                ("high", "\u9ad8\u98a8\u96aa \u2014 \u542b\u300c\u5c0b\u6c42\u5c08\u696d\u8a55\u4f30\u8207\u5e72\u9810\u300d")]:
    cards += ('<p class="rv-tier"><span>%s</span></p><div class="rv-crop"><div class="rv-crop-w">%s</div></div>'
              % (cap, disease_card(lv)))

tmpl = io.open(os.path.join(_HERE, "tmpl.html"), encoding="utf-8").read()
out = (tmpl
       .replace("/*__REPORT_CSS__*/", css)
       .replace("__COMMIT__", "154331f")
       .replace("__PAGE_NORMAL__", chapter_page(7.8, False))
       .replace("__PAGE_NONFASTING__", chapter_page(7.8, True))
       .replace("__BARS__", bars)
       .replace("__SUMMARY_CARD__", '<div class="rv-crop"><div class="rv-crop-w">%s</div></div>' % summary_card(7.8))
       .replace("__DISEASE_CARDS__", cards)
       .replace("__ADVICE_MID__", advice_page("mid"))
       .replace("__ADVICE_HIGH__", advice_page("high")))

io.open(os.path.join(_HERE, "tmao-layout-preview.html"), "w", encoding="utf-8", newline="\n").write(out)
print("built tmao-layout-preview.html (%d bytes)" % len(out.encode("utf-8")))
print("para block 1: %d paragraphs" % len(para1))
print("para block 2: %d paragraphs" % len(para2))
for lv in ("mid", "high"):
    d = cdr(lv)
    print("cdr %-5s diet=%d SPEI=%s" % (lv, len(d["dietAdjustment"]), bool(d["SPEI"])))
