import io, os
_HERE = os.path.dirname(os.path.abspath(__file__))

AGE, GUARD, PRO, CARDIO, TMAO = range(5)
PROFILES = ["MetaAge", "MetaGuard", "MetaPro", "MetaCardio", "MetaTMAO"]

# (component, 中文說明, chapter-no by profile or None, visible-in set, note)
A = "all"


def P(*ids):
    return set(ids)


ROWS = [
    ("FrontCover", "封面", None, P(AGE, GUARD, PRO, CARDIO, TMAO), ""),
    ("Preface", "前言", None, P(AGE, GUARD, PRO, CARDIO, TMAO), ""),
    ("Directory", "目錄", None, P(AGE, GUARD, PRO, CARDIO, TMAO), "由各章 tocs 自動生成"),
    ("Summary", "檢測結果總覽", "1", P(AGE, GUARD, PRO, CARDIO, TMAO), "含人形器官圖與各疾病風險卡片"),
    ("SummaryTrend", "健康動態追蹤", None, P(AGE, GUARD, PRO, CARDIO, TMAO), "TMAO 未納入 notEmptyModels"),

    ("InterpretationAging01-03", "生理年齡", "2.1", P(AGE, GUARD, PRO), ""),
    ("InterpretationAging04", "生理年齡 · 桑基圖", "2.1", P(PRO), "僅 MetaPro"),
    ("InterpretationAging05", "生理年齡 · 續", "2.1", P(AGE, GUARD, PRO), ""),
    ("InterpretationAging06", "代謝途徑解析", "2.1", P(PRO), "僅 MetaPro"),
    ("FirstPage", "健康管理建議（綜合多疾病）", None, P(PRO), "DEFECT"),

    ("ImmunityRisk / ImmunityRiskNew", "免疫力評估", "2.2", P(AGE, GUARD, PRO, TMAO), "GAP"),

    ("InterpretationAD01-07", "阿茲海默症", "2.3", P(GUARD, PRO), ""),
    ("InterpretationCVA01-07", "腦中風", "2.4 / 2.1", P(GUARD, PRO, CARDIO), "MetaCardio 時為 2.1"),
    ("InterpretationAMI01-06", "急性心肌梗塞", "2.5 / 2.2", P(GUARD, PRO, CARDIO), "MetaCardio 時為 2.2"),
    ("InterpretationTMAO01", "氧化三甲胺", "2.6 / 2.3 / 2.1", P(GUARD, PRO, CARDIO, TMAO), "NEW"),
    ("InterpretationTMAO02", "TMAO 建議卡片（精簡建議頁）", None, P(GUARD, CARDIO, TMAO), "NEW"),
    ("InterpretationNAFLD01-07", "代謝異常相關脂肪性肝病", "2.7", P(GUARD, PRO), "編號原為 2.6"),
    ("InterpretationT2D01-07", "第二型糖尿病", "2.8", P(GUARD, PRO), "編號原為 2.7"),
    ("InterpretationCKD01-07", "慢性腎臟病", "2.9", P(GUARD, PRO), "編號原為 2.8"),

    ("AppendixOne02 / 03", "附錄1：檢測機構及平臺", "3", P(AGE, GUARD, PRO, CARDIO, TMAO), ""),
    ("AppendixTwoAllPathway", "附錄2：完整代謝途徑", "4", P(PRO), "僅 MetaPro"),
    ("AppendixThree01 / 02", "附錄：檢測說明", "5", P(AGE, GUARD, PRO, CARDIO, TMAO), ""),
    ("AppendixFour", "附錄：參考文獻", "6", P(AGE, GUARD, PRO, CARDIO, TMAO), ""),
    ("BackCover", "封底", None, P(AGE, GUARD, PRO, CARDIO, TMAO), "MetaCardio 用固定整頁圖"),
]

CH = {
    "DEFECT": ("hint2", "僅 MetaPro，TMAO 走專用頁"),
    "GAP": ("hint2", "gate 未加 !isMetaTMAO"),
    "NEW": ("new", "本次新增"),
}


def cell(row, pid):
    comp, zh, no, vis, note = row
    if pid in vis:
        if note == "NEW":
            return '<td class="on is-new">&#9679;</td>'
        return '<td class="on">&#9679;</td>'
    return '<td class="off">&middot;</td>'


def build_matrix():
    head = "".join('<th class="pcol">%s</th>' % p for p in PROFILES)
    body = ""
    for row in ROWS:
        comp, zh, no, vis, note = row
        badge = ""
        if note in CH:
            kind, label = CH[note]
            badge = ' <span class="badge b-%s">%s</span>' % (kind, label)
        elif note:
            badge = ' <span class="hint">%s</span>' % note
        cls = ' class="row-new"' if note == "NEW" else ""
        body += ("<tr%s><td class=\"comp\">%s</td><td class=\"zh\">%s%s</td>"
                 "<td class=\"no\">%s</td>%s</tr>"
                 % (cls, comp, zh, badge, no or "&mdash;",
                    "".join(cell(row, p) for p in range(5))))
    return ('<div class="tablewrap"><table class="matrix">'
            '<thead><tr><th>元件</th><th>頁面</th><th>章節</th>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>' % (head, body))


def profile_counts():
    out = ""
    for pid, name in enumerate(PROFILES):
        n = sum(1 for r in ROWS if pid in r[3])
        has_tmao = any(pid in r[3] and r[4] == "NEW" for r in ROWS)
        has_advice = any(pid in r[3] and r[0] in ("FirstPage", "InterpretationTMAO02") for r in ROWS)
        out += ('<div class="pcard"><p class="pname">%s</p>'
                '<p class="pstat">%d 個區塊</p>'
                '<p class="pline">TMAO 章節 %s</p>'
                '<p class="pline">建議卡片 %s</p></div>'
                % (name, n,
                   '<b class="yes">有</b>' if has_tmao else '<b class="no">無</b>',
                   '<b class="yes">有</b>' if has_advice else '<b class="no">無</b>'))
    return out


HTML = """<title>全版報告結構</title>
<style>
:root{--bg:#F7F8FA;--card:#fff;--ink:#151A21;--soft:#4E5765;--faint:#858E9C;
--rule:#DCE1E8;--rule2:#C2CAD4;--accent:#0C3475;--new:#0FA19C;--bad:#B41D23;--warn:#B5820F;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--bg:#101317;--card:#171B21;--ink:#E4E8EE;--soft:#A7B0BE;--faint:#7A8492;
--rule:#282F38;--rule2:#39424E;--accent:#8CAEDD;--new:#4FC3BE;--bad:#E4737A;--warn:#D9A93C;}}
:root[data-theme="dark"]{--bg:#101317;--card:#171B21;--ink:#E4E8EE;--soft:#A7B0BE;
--faint:#7A8492;--rule:#282F38;--rule2:#39424E;--accent:#8CAEDD;--new:#4FC3BE;--bad:#E4737A;--warn:#D9A93C;}
*{box-sizing:border-box}
body{margin:0;padding:0 22px 90px;background:var(--bg);color:var(--ink);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang TC","Microsoft JhengHei","Noto Sans TC",sans-serif;
font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:1060px;margin:0 auto}
header{padding:50px 0 22px;border-bottom:2px solid var(--ink);margin-bottom:30px}
.eyebrow{font-family:ui-monospace,Consolas,monospace;font-size:11px;letter-spacing:.14em;
text-transform:uppercase;color:var(--faint);margin:0 0 12px}
h1{font-family:ui-serif,Georgia,"Songti TC",serif;font-size:clamp(28px,4.5vw,40px);
line-height:1.18;font-weight:600;margin:0 0 12px;text-wrap:balance}
.lede{font-size:16.5px;color:var(--soft);max-width:66ch;margin:0}
h2{font-family:ui-serif,Georgia,"Songti TC",serif;font-size:23px;font-weight:600;margin:0 0 5px}
.note{font-size:13.5px;color:var(--faint);margin:0 0 20px;padding-bottom:11px;
border-bottom:1px solid var(--rule)}
section{margin-bottom:56px}
code{font-family:ui-monospace,Consolas,monospace;font-size:12.5px;
background:color-mix(in srgb,var(--ink) 8%,transparent);padding:1px 5px;border-radius:2px}

.callout{border-left:3px solid var(--bad);background:color-mix(in srgb,var(--bad) 9%,transparent);
padding:15px 18px;margin:0 0 40px;font-size:15px;color:var(--soft)}
.callout strong{color:var(--ink)}
.callout.warnbox{border-left-color:var(--warn);background:color-mix(in srgb,var(--warn) 9%,transparent)}

.tablewrap{overflow-x:auto}
table.matrix{border-collapse:collapse;width:100%;min-width:840px;font-size:14px;background:var(--card)}
table.matrix th,table.matrix td{padding:9px 10px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
table.matrix thead th{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;
color:var(--faint);font-weight:600;border-bottom:1px solid var(--rule2);white-space:nowrap}
th.pcol{text-align:center;width:78px}
td.comp{font-family:ui-monospace,Consolas,monospace;font-size:11.5px;color:var(--accent);white-space:nowrap}
td.zh{min-width:190px}
td.no{font-family:ui-monospace,Consolas,monospace;font-size:12px;color:var(--soft);white-space:nowrap}
td.on,td.off{text-align:center;font-size:15px}
td.on{color:var(--accent)}
td.on.is-new{color:var(--new)}
td.off{color:var(--rule2)}
tr.row-new{background:color-mix(in srgb,var(--new) 8%,transparent)}
tr.row-new td.comp{color:var(--new);font-weight:600}
.badge{display:inline-block;font-size:10px;letter-spacing:.05em;padding:1px 6px;border-radius:2px;
vertical-align:1px;font-family:ui-monospace,Consolas,monospace}
.b-bad{background:var(--bad);color:#fff}
.b-warn{background:var(--warn);color:#fff}
.b-hint2{background:transparent;color:var(--faint);border:1px solid var(--rule2)}
.b-new{background:var(--new);color:#fff}
.hint{font-size:11.5px;color:var(--faint)}

.pgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:14px}
.pcard{background:var(--card);border:1px solid var(--rule);border-radius:3px;padding:14px 16px}
.pname{font-family:ui-monospace,Consolas,monospace;font-size:13px;font-weight:600;margin:0 0 6px;color:var(--accent)}
.pstat{font-size:12px;color:var(--faint);margin:0 0 8px;font-family:ui-monospace,Consolas,monospace}
.pline{font-size:13px;color:var(--soft);margin:0 0 2px}
.pline b.yes{color:var(--new)}
.pline b.no{color:var(--bad)}

ol.fix{counter-reset:f;list-style:none;padding:0;margin:0}
ol.fix>li{counter-increment:f;display:grid;grid-template-columns:26px 1fr;gap:0 12px;
padding:16px 0;border-bottom:1px solid var(--rule)}
ol.fix>li::before{content:counter(f);font-family:ui-monospace,Consolas,monospace;
font-size:12px;color:var(--faint);padding-top:3px}
.ft{font-weight:600;margin:0 0 4px}
.fb{margin:0;color:var(--soft);font-size:14.5px;max-width:70ch}
footer{margin-top:52px;padding-top:18px;border-top:1px solid var(--rule);
font-size:13px;color:var(--faint);line-height:1.7}
a{color:var(--accent)}
</style>
<div class="wrap">
<header>
  <p class="eyebrow">報告結構 · 自程式擷取</p>
  <h1>全版報告結構與 TMAO 的位置</h1>
  <p class="lede">從 <code>AllReport()</code>（<code>index.js</code> L56090-56447）逐行擷取的頁面順序與顯示條件，
  對照五個套件別。實心點代表該套組會輸出該區塊。</p>
</header>

<p class="callout warnbox"><strong>TMAO 建議文案有兩條輸出路徑。</strong>
  MetaPro 走既有的綜合建議頁 <code>FirstPage</code>；MetaGuard、MetaCardio、MetaTMAO 走新增的
  <code>InterpretationTMAO02</code>（只放 TMAO 的精簡建議頁）。
  後者以 <code>firstPageWillRender()</code> 判斷前者是否會出現，會出現時回傳 <code>null</code>，
  因此不會有同一份報告出現兩張 TMAO 建議卡片。<strong>既有四個套組的輸出完全不變。</strong></p>

<section>
  <h2>一、各套組輸出什麼</h2>
  <p class="note">「建議卡片」指由 <code>CDR</code> 文案產生的疾病建議區塊，可能來自 <code>FirstPage</code>（MetaPro）或 <code>InterpretationTMAO02</code>（其餘套組）。</p>
  <div class="pgrid">__PCARDS__</div>
</section>

<section>
  <h2>二、完整頁面順序</h2>
  <p class="note">依 <code>AllReport()</code> 的實際 render 順序排列。章節欄位有多個數字者，代表不同套組編號不同。</p>
  __MATRIX__
</section>

<section>
  <h2>三、TMAO 在各套組的位置</h2>
  <p class="note">同一份程式碼，三種落點。</p>
  <div class="tablewrap"><table class="matrix" style="min-width:640px">
  <thead><tr><th>套組</th><th>profile_key 第二段</th><th>章節編號</th><th>前一章</th><th>後一章</th></tr></thead>
  <tbody>
  <tr><td class="comp">MetaCardio</td><td class="no">MetaCardio</td><td class="no">2.3</td><td class="zh">2.2 急性心肌梗塞</td><td class="zh">附錄1</td></tr>
  <tr><td class="comp">MetaTMAO</td><td class="no">MetaTMAO</td><td class="no">2.1</td><td class="zh">1 檢測結果總覽</td><td class="zh">附錄1</td></tr>
  <tr><td class="comp">MetaGuard</td><td class="no">MetaGuard</td><td class="no">2.6</td><td class="zh">2.5 急性心肌梗塞</td><td class="zh">2.7 脂肪性肝病</td></tr>
  <tr><td class="comp">MetaPro</td><td class="no">MetaPro</td><td class="no">2.6</td><td class="zh">2.5 急性心肌梗塞</td><td class="zh">2.7 脂肪性肝病</td></tr>
  <tr><td class="comp">MetaAge</td><td class="no">MetaAge</td><td class="no">&mdash;</td><td class="zh" colspan="2">不輸出（<code>showTMAO</code> 對 MetaAge 為 false）</td></tr>
  </tbody></table></div>
</section>

<section>
  <h2>四、建議卡片的兩條路徑</h2>
  <p class="note">TMAO 需獨立於 MetaPro 之外，因此不能只靠 <code>FirstPage</code>。</p>
  <div class="tablewrap"><table class="matrix" style="min-width:600px">
  <thead><tr><th>套組</th><th>TMAO 章節</th><th>建議卡片</th><th>由哪個元件輸出</th></tr></thead>
  <tbody>
  <tr><td class="comp">MetaAge</td><td class="no">&mdash;</td><td class="no">&mdash;</td><td class="zh">不輸出 TMAO</td></tr>
  <tr><td class="comp">MetaGuard</td><td class="no">2.6</td><td class="no">有</td><td class="comp">InterpretationTMAO02</td></tr>
  <tr><td class="comp">MetaPro</td><td class="no">2.6</td><td class="no">有</td><td class="comp">FirstPage（既有綜合頁）</td></tr>
  <tr><td class="comp">MetaCardio</td><td class="no">2.3</td><td class="no">有</td><td class="comp">InterpretationTMAO02</td></tr>
  <tr><td class="comp">MetaTMAO</td><td class="no">2.1</td><td class="no">有</td><td class="comp">InterpretationTMAO02</td></tr>
  </tbody></table></div>

  <p class="note" style="margin-top:22px;border:0;padding-bottom:0">低風險不輸出建議卡片，與 AD／CKD／FLD／T2D 一致。</p>

  <ol class="fix">
    <li><div>
      <p class="ft">為什麼另開一頁，而不是把 <code>FirstPage</code> 搬出來</p>
      <p class="fb"><code>FirstPage</code> 頂部有固定的「生理年齡／實際年齡／老化速度」表格，資料來自
      <code>MetaboAging</code>。搬出來獨立掛載後，TMAO-only 報告沒有 Aging 資料，那張表會顯示成
      <code>-</code>；而且會連帶讓 CVA／AMI 的建議文案也出現在 MetaCardio，屬於既有行為變更。
      <strong>代價：</strong>報告中存在兩種建議頁型 &mdash;&mdash; MetaPro 是綜合多疾病，其餘是單一疾病精簡頁。</p>
    </div></li>
    <li><div>
      <p class="ft">範圍控制靠 LIMS，不在程式層設白名單</p>
      <p class="fb"><code>showTMAO</code> 維持 <code>!isMetaAge</code>。TMAO 出現在哪些套組，
      由 LIMS 端「哪個套組勾選了 <code>MetaboTMAO</code> 服務」決定 &mdash;&mdash;
      MetaPro 不勾就不會有。日後要加進別的套組不需改程式，也避免「有資料卻不顯示」這種難以除錯的狀態。</p>
    </div></li>
    <li><div>
      <p class="ft">免疫章節 gate 未加 <code>!isMetaTMAO</code> <span class="badge b-new">已確認可接受</span></p>
      <p class="fb">TMAO-only 樣本不會有免疫資料，不會誤觸發。<strong>latent 風險：</strong>
      若日後在 MetaTMAO profile 加掛免疫檢測服務，免疫章節會出現在 TMAO-only 報告中。</p>
    </div></li>
  </ol>
</section>

<footer>
  頁面順序、顯示條件與章節編號皆自 <code>index.js</code> 的 <code>AllReport()</code> 擷取，非人工整理。
  單一頁面的實際渲染樣貌見 <em>TMAO 章節版面預覽</em>。
  MetaCardio 的完整設計稿可參考 repo 內 <code>HOTW260410SRAC07_R01_猝死包套組 1.pdf</code>（28 頁，2026-04 版，尚無 TMAO 章節）。
</footer>
</div>
"""

out = HTML.replace("__MATRIX__", build_matrix()).replace("__PCARDS__", profile_counts())
io.open(os.path.join(_HERE, "tmao-full-report-structure.html"), "w", encoding="utf-8", newline="\n").write(out)
print("built tmao-full-report-structure.html (%d bytes)" % len(out.encode("utf-8")))
for pid, name in enumerate(PROFILES):
    n = sum(1 for r in ROWS if pid in r[3])
    tm = any(pid in r[3] and r[4] == "NEW" for r in ROWS)
    ad = any(pid in r[3] and r[0] in ("FirstPage", "InterpretationTMAO02") for r in ROWS)
    print("  %-11s blocks=%2d  TMAO=%-3s advice=%s" % (name, n, "yes" if tm else "no", "yes" if ad else "NO"))
