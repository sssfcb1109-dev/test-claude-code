from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from datetime import datetime

OUTPUT = "/home/user/test-claude-code/AI_Usage_Report_2026.pdf"

# ── Color palette ──────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#1A237E")
BLUE   = colors.HexColor("#1565C0")
TEAL   = colors.HexColor("#00838F")
LIGHT  = colors.HexColor("#E3F2FD")
ACCENT = colors.HexColor("#FF6F00")
GREY   = colors.HexColor("#546E7A")
WHITE  = colors.white
BLACK  = colors.HexColor("#212121")

# ── Styles ─────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def style(name, **kwargs):
    base = styles[name]
    return ParagraphStyle(
        f"custom_{name}_{id(kwargs)}",
        parent=base,
        **kwargs
    )

TITLE_STYLE = style("Title",
    fontSize=28, textColor=WHITE, alignment=TA_CENTER,
    spaceAfter=6, fontName="Helvetica-Bold")

SUBTITLE_STYLE = style("Normal",
    fontSize=14, textColor=colors.HexColor("#B3E5FC"),
    alignment=TA_CENTER, spaceAfter=4)

DATE_STYLE = style("Normal",
    fontSize=10, textColor=colors.HexColor("#90CAF9"),
    alignment=TA_CENTER, spaceAfter=0)

H1 = style("Heading1",
    fontSize=16, textColor=NAVY, fontName="Helvetica-Bold",
    spaceBefore=14, spaceAfter=6, borderPad=4)

H2 = style("Heading2",
    fontSize=12, textColor=BLUE, fontName="Helvetica-Bold",
    spaceBefore=10, spaceAfter=4)

BODY = style("Normal",
    fontSize=10, textColor=BLACK, leading=15,
    alignment=TA_JUSTIFY, spaceAfter=6)

BULLET = style("Normal",
    fontSize=10, textColor=BLACK, leading=15,
    leftIndent=16, spaceAfter=3,
    bulletIndent=6, bulletFontName="Helvetica")

CAPTION = style("Normal",
    fontSize=8, textColor=GREY, alignment=TA_CENTER,
    spaceBefore=2, spaceAfter=8)

HIGHLIGHT = style("Normal",
    fontSize=13, textColor=NAVY, fontName="Helvetica-Bold",
    alignment=TA_CENTER, spaceAfter=0)

HIGHLIGHT_SUB = style("Normal",
    fontSize=9, textColor=GREY, alignment=TA_CENTER,
    spaceAfter=0)

SOURCE = style("Normal",
    fontSize=7.5, textColor=GREY, leading=11, spaceAfter=2)

# ── Helpers ────────────────────────────────────────────────────────────────────

def make_style(name, **kwargs):
    base = styles[name]
    return ParagraphStyle(
        f"ms_{name}_{abs(hash(str(kwargs)))}",
        parent=base,
        **kwargs
    )

def section_header(text):
    """Returns a colored section banner."""
    sh_style = make_style("Heading1",
        fontSize=13, textColor=WHITE,
        fontName="Helvetica-Bold", spaceBefore=0, spaceAfter=0)
    return Table(
        [[Paragraph(text, sh_style)]],
        colWidths=["100%"],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ])
    )

def kpi_table(items):
    """3-column KPI cards. items = [(value, label), ...]"""
    cells = []
    for val, lbl in items:
        cell = [Paragraph(val, HIGHLIGHT), Paragraph(lbl, HIGHLIGHT_SUB)]
        cells.append(cell)
    # Pad to multiple of 3
    while len(cells) % 3:
        cells.append([""])
    rows = [cells[i:i+3] for i in range(0, len(cells), 3)]
    t = Table(rows, colWidths=[5.9*cm, 5.9*cm, 5.9*cm])
    ts = TableStyle([
        ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#BBDEFB")),
        ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#BBDEFB")),
        ("BACKGROUND",  (0, 0), (-1, -1), LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ])
    t.setStyle(ts)
    return t

def data_table(headers, rows, col_widths=None):
    data = [[Paragraph(str(h), style("Normal",
                fontSize=9, textColor=WHITE,
                fontName="Helvetica-Bold", alignment=TA_CENTER))
             for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), style("Normal",
                        fontSize=9, textColor=BLACK, leading=13))
                     for c in row])
    t = Table(data, colWidths=col_widths)
    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  BLUE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#90CAF9")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("ALIGN",         (1, 1), (-1, -1), "CENTER"),
    ])
    t.setStyle(ts)
    return t

def bar_chart(categories, values, title, width=400, height=160):
    drawing = Drawing(width, height + 30)
    bc = VerticalBarChart()
    bc.x = 40; bc.y = 30
    bc.width = width - 60; bc.height = height - 20
    bc.data = [values]
    bc.bars[0].fillColor = BLUE
    bc.bars[0].strokeColor = None
    bc.categoryAxis.categoryNames = categories
    bc.categoryAxis.labels.fontSize = 8
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.labels.dy = -6
    bc.valueAxis.labels.fontSize = 8
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(values) * 1.15
    bc.valueAxis.valueStep = max(values) / 5
    drawing.add(bc)
    drawing.add(String(width / 2, height + 18, title,
                       fontSize=9, fillColor=GREY,
                       textAnchor="middle", fontName="Helvetica-Bold"))
    return drawing

# ── Cover page ─────────────────────────────────────────────────────────────────

def cover_page(story):
    # Full-width color band via 1-cell table
    cover = Table(
        [[Paragraph("Global AI Usage Report", TITLE_STYLE)],
         [Paragraph("How Many People Are Using Artificial Intelligence?", SUBTITLE_STYLE)],
         [Paragraph(f"March 2026  ·  Comprehensive Global Analysis", DATE_STYLE)]],
        colWidths=["100%"],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
            ("TOPPADDING",    (0, 0), (0, 0),  40),
            ("BOTTOMPADDING", (0, 2), (0, 2),  40),
            ("LEFTPADDING",   (0, 0), (-1, -1), 20),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ])
    )
    story.append(cover)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "This report synthesizes the latest data from DataReportal, Microsoft AI Economy Institute, "
        "McKinsey, Stanford HAI, Grand View Research, DemandSage, and dozens of additional primary "
        "sources to provide a comprehensive picture of artificial intelligence adoption worldwide.",
        BODY))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=6))

# ── Section 1 ─────────────────────────────────────────────────────────────────

def section1(story):
    story.append(section_header("1.  Global AI User Base"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "As of early 2026, artificial intelligence has crossed a historic milestone: over "
        "<b>1.35–1.5 billion people</b> actively use AI tools each month — roughly "
        "<b>16.3 % of the world's population</b> and approximately one in five internet users. "
        "Despite this rapid ascent, around 5 billion internet users have yet to adopt AI, "
        "underscoring that the technology remains in the early stages of mass diffusion.",
        BODY))

    story.append(kpi_table([
        ("1.4 B+", "Monthly Active\nAI Users Globally"),
        ("16.3 %", "Share of World\nPopulation"),
        ("5 B+", "Internet Users Not\nYet Using AI"),
    ]))
    story.append(Spacer(1, 0.25*cm))
    story.append(Paragraph(
        "For context, social-media platforms took more than a decade to achieve comparable "
        "user numbers. Standalone AI tools — led by ChatGPT — reached this threshold in "
        "roughly <b>three years</b>, a rate of adoption unprecedented in the history of "
        "consumer technology.",
        BODY))

# ── Section 2 ─────────────────────────────────────────────────────────────────

def section2(story):
    story.append(section_header("2.  AI Adoption by Region & Country"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Adoption rates vary enormously across geographies. Emerging-market nations — "
        "particularly in South and South-East Asia and the Middle East — are adopting AI "
        "faster than more mature economies, driven by mobile-first internet access and "
        "younger demographic profiles.",
        BODY))

    story.append(Paragraph("Top Countries by AI Adoption Rate (Working-Age Population)", H2))
    rows = [
        ["India",       "~73 %",   "Fastest absolute growth; 4× wealthier nations' pace"],
        ["UAE",         "64.0 %",  "Highest adoption in the Middle East"],
        ["Singapore",   "60.9 %",  "Asia-Pacific leader"],
        ["Chile",       "~60 %",   "Latin America leader"],
        ["South Korea", "~30 %",   "+80 % YoY — fastest growth rate globally"],
        ["EU Average",  "32.7 %",  "Individuals aged 16–74"],
        ["USA",         "28.3 %",  "77.2 M monthly ChatGPT users"],
        ["UK",          "~29 %",   "Strong enterprise uptake"],
        ["China",       "~83 %*",  "*Awareness metric; ChatGPT blocked — 250 M domestic users"],
    ]
    story.append(data_table(
        ["Country / Region", "Adoption Rate", "Notable Context"],
        rows,
        col_widths=[4.5*cm, 3*cm, 10.3*cm]
    ))
    story.append(Paragraph(
        "Sources: DataReportal Digital 2026; Microsoft AI Economy Institute; AllAboutAI Global Adoption Index.",
        SOURCE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Regional Market Share", H2))
    story.append(data_table(
        ["Region", "2025 Market Share", "Growth (CAGR)", "Outlook"],
        [
            ["North America",  "36.9 %", "~17 %",  "Dominant today; incremental gains"],
            ["Asia-Pacific",   "33.0 %", "19.8 %", "Expected to dominate by 2030 (~47 %)"],
            ["Europe",         "~18 %",  "~16 %",  "Regulatory environment shaping pace"],
            ["Rest of World",  "~12 %",  "~21 %",  "Fastest-growing but smallest base"],
        ],
        col_widths=[4*cm, 3.5*cm, 3.5*cm, 6.8*cm]
    ))
    story.append(Paragraph(
        "Note: Global North adoption rate 24.7 %; Global South 14.1 % — gap widening.",
        SOURCE))

# ── Section 3 ─────────────────────────────────────────────────────────────────

def section3(story):
    story.append(section_header("3.  Leading AI Platforms & User Counts"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "ChatGPT — launched in November 2022 — remains by far the most-used AI platform, "
        "accounting for roughly 80 % of the AI chatbot market. However, competition from "
        "Google, Microsoft, Anthropic, and a wave of domestic Asian models is intensifying.",
        BODY))

    story.append(data_table(
        ["Platform", "Monthly Active Users", "Key Metric", "Market Share"],
        [
            ["ChatGPT (OpenAI)",    "~1 B MAU / 900 M WAU",  "5.72 B web visits/mo; 2.5 B prompts/day", "~80.5 %"],
            ["Google Gemini",       "400–750 M MAU",          "Integrated in Google Search (2 B+ users)", "~21.5 % (global)"],
            ["Microsoft Copilot",   "~101 M users",           "85 % of Fortune 500 firms",                "~12.6 % (AI search)"],
            ["Anthropic Claude",    "~30 M MAU",              "25 B API calls/month",                     "~4.7 %"],
            ["Perplexity AI",       "30–40 M MAU",            "30 M daily queries",                       "~6.2 % (US)"],
            ["DeepSeek",            "n/a",                    "Domestic China focus",                     "~3.7 %"],
            ["Grok (xAI)",          "n/a",                    "X / Twitter integration",                  "~3.4 %"],
        ],
        col_widths=[4*cm, 4.5*cm, 5.5*cm, 3.8*cm]
    ))
    story.append(Paragraph(
        "Sources: DemandSage ChatGPT Statistics 2026; First Page Sage Chatbot Market Share Mar 2026; "
        "SEOProfy Perplexity Statistics.",
        SOURCE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Enterprise Reach", H2))
    story.append(Paragraph(
        "• <b>92 %</b> of Fortune 500 companies use ChatGPT in some capacity.", BULLET))
    story.append(Paragraph(
        "• OpenAI holds <b>7 M+ workplace seats</b> and <b>1 M+ business customers</b>.", BULLET))
    story.append(Paragraph(
        "• OpenAI's annualised revenue: <b>$10 B</b> (June 2025); valuation: <b>$730 B</b>.", BULLET))
    story.append(Paragraph(
        "• <b>78 %</b> of organisations reported using AI in 2024–25, up from 55 % the prior year "
        "(McKinsey State of AI 2025).", BULLET))

# ── Section 4 ─────────────────────────────────────────────────────────────────

def section4(story):
    story.append(section_header("4.  AI Adoption by Industry"))
    story.append(Spacer(1, 0.3*cm))
    story.append(data_table(
        ["Sector", "Adoption Rate", "Key Highlights"],
        [
            ["IT / Telecom",          "83–85 %",  "48 % deploying agentic AI (highest); $4.7 T gross value by 2035"],
            ["Manufacturing",         "77 %",     "23 % avg reduction in downtime; 98 % expect efficiency gains"],
            ["Education",             "~86 %*",   "*Student usage; 92 % use AI for assessments (up from 53 % in 2024)"],
            ["Healthcare",            "40 %",     "CAGR 36.83 %; market $868 B by 2030; 223 FDA-approved AI devices (2023)"],
            ["Financial Services",    "~68 %",    "$20 B+ annual AI spending; robo-advisors manage $1.2 T in assets"],
            ["Retail / CPG",          "~47 %",    "47 % deploying agentic AI; GenAI highest ROI in marketing & sales"],
        ],
        col_widths=[4.5*cm, 3*cm, 10.3*cm]
    ))
    story.append(Paragraph(
        "Sources: McKinsey State of AI 2025; Mezzi AI Adoption Rates by Industry; NVIDIA State of AI 2026.",
        SOURCE))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "<b>71 %</b> of organisations regularly use generative AI in at least one business function, "
        "and <b>86 %</b> of companies plan to increase their AI budgets — with <b>40 %</b> targeting "
        "increases of 10 % or more.",
        BODY))

# ── Section 5 ─────────────────────────────────────────────────────────────────

def section5(story):
    story.append(section_header("5.  Market Size & Growth Projections"))
    story.append(Spacer(1, 0.3*cm))

    story.append(kpi_table([
        ("$244 B", "Global AI Market\n2025"),
        ("$800 B+", "Projected Market\n2030"),
        ("$19.9 T", "Cumulative GenAI\nEconomic Impact by 2030"),
    ]))
    story.append(Spacer(1, 0.3*cm))

    story.append(data_table(
        ["Metric", "2025", "2026", "2029–2030", "CAGR"],
        [
            ["Global AI Market",         "$244 B",  "$312 B",   "$800 B+",   "~27 %"],
            ["Gartner AI Spend",          "$1.5 T",  "$2.0 T",   "$3.3 T",    "~22 %"],
            ["Generative AI Market",      "$22–64 B","—",         "$220–325 B","29–41 %"],
            ["AI User Base",              "1.35 B",  "—",         "—",         "~40 %+"],
            ["AI Platforms Market",       "—",       "Growing",   "+$101 B",   "40.5 %"],
        ],
        col_widths=[5.5*cm, 3*cm, 3*cm, 3.5*cm, 2.8*cm]
    ))
    story.append(Paragraph("Sources: Grand View Research; Gartner; Master of Code GenAI Statistics.", SOURCE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Workforce Impact", H2))
    story.append(Paragraph(
        "• AI projected to <b>create 170 M new jobs</b> while displacing 92 M by 2030 (net positive of 78 M).", BULLET))
    story.append(Paragraph(
        "• LinkedIn reports a <b>13× increase</b> in AI-related job postings over 5 years; talent supply only grew 8×.", BULLET))
    story.append(Paragraph(
        "• Workers using generative AI save an average of <b>5.4 % of their work hours</b> per week.", BULLET))
    story.append(Paragraph(
        "• Agentic AI expected to resolve <b>80 % of customer-service issues</b> autonomously by 2029.", BULLET))

# ── Section 6 ─────────────────────────────────────────────────────────────────

def section6(story):
    story.append(section_header("6.  Demographics of AI Users"))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Age Distribution", H2))
    story.append(data_table(
        ["Age Group", "Weekly AI Usage", "Notes"],
        [
            ["Gen Z (18–25)",      "~70 %",  "Highest adoption; under-25s = 42 % of ChatGPT's user base"],
            ["Millennials (26–41)","56 %",   "Deloitte; 29.7 % of ChatGPT users are aged 25–34"],
            ["Adults 18–29",       "46 %",   "Pew Research"],
            ["Adults 30–49",       "~35 %",  "Moderate usage; workplace-driven"],
            ["Adults 50–64",       "~28 %",  "Growing; productivity focus"],
            ["Adults 65+",         "23 %",   "Lowest adoption; awareness gap key barrier"],
        ],
        col_widths=[4.5*cm, 3.5*cm, 9.8*cm]
    ))
    story.append(Paragraph("Sources: TheySaid How Generations Use AI 2026; National University AI Statistics.", SOURCE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Gender Gap", H2))
    story.append(Paragraph(
        "A notable gender divide persists in AI adoption:", BODY))
    story.append(Paragraph(
        "• <b>44 %</b> of men vs. <b>33 %</b> of women report using AI (2024 figures).", BULLET))
    story.append(Paragraph(
        "• AI awareness gap: 38 % among men vs. 23 % among women.", BULLET))
    story.append(Paragraph(
        "• In educational settings, the gap narrows significantly: 53 % male vs. 51 % female students use AI.", BULLET))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Education & Socio-Economic Factors", H2))
    story.append(Paragraph(
        "• University-educated individuals: <b>62 %</b> report understanding and using AI "
        "vs. <b>40 %</b> without a degree.", BULLET))
    story.append(Paragraph(
        "• College-educated daily workplace AI use rose from 22 % → 34 % in one year; "
        "non-college-educated use <i>declined</i> 6 points — a widening digital divide.", BULLET))
    story.append(Paragraph(
        "• EU youth (under 30): 44 % use AI for private purposes vs. 25 % of the general population.", BULLET))

# ── Section 7 — Key Takeaways ──────────────────────────────────────────────────

def section7(story):
    story.append(section_header("7.  Key Takeaways"))
    story.append(Spacer(1, 0.3*cm))
    takeaways = [
        ("<b>Milestone crossed:</b>  Over 1.4 billion people — roughly 1 in 6 humans — "
         "actively use AI tools each month, yet 5 billion internet users have not yet adopted AI."),
        ("<b>South beats North:</b>  Emerging markets (India, UAE, Chile) are adopting AI faster "
         "than developed economies, driven by mobile access and youthful demographics."),
        ("<b>ChatGPT dominates</b> with ~80 % chatbot market share and ~1 B monthly active users, "
         "growing from 300 M weekly actives to 900 M in under 12 months."),
        ("<b>Enterprise is all-in:</b>  78 % of organisations now use AI; 92 % of Fortune 500 "
         "companies use ChatGPT; 86 % plan to increase AI budgets."),
        ("<b>Economic magnitude:</b>  The global AI market will reach $800 B+ by 2030, with "
         "cumulative generative AI economic impact projected at $19.9 trillion."),
        ("<b>Workforce transformation:</b>  AI will create 170 M new jobs while displacing 92 M — "
         "a net positive — but reskilling and bridging the digital divide are critical imperatives."),
        ("<b>Demographic divide:</b>  Gen Z leads adoption; a widening gender and education gap "
         "risks concentrating AI's benefits among the already privileged."),
    ]
    for i, text in enumerate(takeaways, 1):
        story.append(Paragraph(f"{i}.  {text}", BODY))
        story.append(Spacer(1, 0.1*cm))

# ── Section 8 — Paid vs Free ──────────────────────────────────────────────────

def section8(story):
    story.append(PageBreak())
    story.append(section_header("8.  Paid vs. Free User Breakdown"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Despite the explosive growth of AI user counts, the vast majority of users remain on "
        "free tiers. Monetisation — converting curious free users into paying subscribers — "
        "remains the central challenge for AI platforms in 2026.",
        BODY))

    story.append(Paragraph("Paid Subscriber Market Share (Recon Analytics, Jan 2026)", H2))
    story.append(data_table(
        ["Platform", "Paid Share", "Est. Paid Users", "Price (entry)"],
        [
            ["ChatGPT (OpenAI)",  "55.2 %", "~15 M+ paying",        "$20/mo (Plus)"],
            ["Google Gemini",     "15.7 %", "Not disclosed",         "$19.99/mo (AI Pro)"],
            ["Microsoft Copilot","11.5 %",  "~15 M M365 seats",     "$30/user/mo"],
            ["All Others",        "17.6 %", "—",                     "Various"],
        ],
        col_widths=[4.5*cm, 3*cm, 4*cm, 6.3*cm]
    ))
    story.append(Paragraph("Source: Recon Analytics Paid AI Subscriber Report, January 2026.", SOURCE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Per-Platform Paid vs. Free Detail", H2))
    story.append(data_table(
        ["Platform", "Free Users (~%)", "Paid Users (~%)", "Key Notes"],
        [
            ["ChatGPT",           "~81 %", "~19 %*",
             "Plus $20/mo · Pro $200/mo · 5M biz users; *among engaged users"],
            ["Google Gemini",     ">95 %",  "<5 %",
             "AI Pro $19.99/mo · AI Ultra $249.99/mo; no public paid count"],
            ["Anthropic Claude",  "~90 %+", "<10 %",
             "Pro $20 · Max5× $100 · Max20× $200; 300K+ biz customers"],
            ["Microsoft Copilot", "96.7 %", "3.3 %",
             "3.3% of M365 seats convert to paid Copilot (Feb 2026 earnings)"],
        ],
        col_widths=[3.5*cm, 3*cm, 3*cm, 8.3*cm]
    ))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Free-to-Paid Conversion Benchmarks", H2))
    story.append(data_table(
        ["Model / Platform", "Conversion Rate", "Context"],
        [
            ["Cursor AI",                  "36 %",  "360K paying / 1M users — fastest-growing SaaS ever"],
            ["Free trial (with card)",     "~43 %", "Industry average — credit card required"],
            ["Free trial (no card)",       "~14 %", "Industry average — no card barrier"],
            ["SaaS free trials (broad)",   "~29 %", "Cross-industry benchmark"],
            ["Freemium model (general)",   "~4.2 %","Typical for mass-market freemium"],
            ["GitHub Copilot",             "3.1 %", "4.7M paid / 150M GitHub users"],
            ["Microsoft M365 Copilot",     "3.3 %", "15M paid / 450M M365 seats"],
            ["ChatGPT (all weekly actives)","~1.7 %","~15M paid / 900M weekly actives"],
        ],
        col_widths=[5.5*cm, 3.5*cm, 8.8*cm]
    ))
    story.append(Paragraph(
        "Sources: Backlinko ChatGPT Statistics 2026; The Register (Microsoft earnings); "
        "GetPanto GitHub Copilot Statistics; RevenueCat State of Subscription Apps 2026.",
        SOURCE))
    story.append(Spacer(1, 0.2*cm))

    story.append(kpi_table([
        ("$8.90/mo", "ChatGPT Blended\nARPU (+19 % YoY)"),
        ("$25 B", "OpenAI Annualised\nRevenue (Feb 2026)"),
        ("~$3 B → $14 B", "Anthropic ARR\n(2025 → 2026 est.)"),
    ]))


# ── Section 9 — AI Coding Tools ───────────────────────────────────────────────

def section9(story):
    story.append(Spacer(1, 0.4*cm))
    story.append(section_header("9.  AI Coding Assistants"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "The AI coding assistant market has become one of the most competitive segments in "
        "the AI industry. <b>62 % of professional developers</b> now use an AI coding tool; "
        "<b>41 % of all code written in 2025</b> was AI-generated or AI-assisted. "
        "The market is valued at <b>$6.8–$7.4 B</b> in 2025 and projected to reach "
        "<b>$30 B by 2032</b>.",
        BODY))

    story.append(data_table(
        ["Tool", "Users / Scale", "ARR (2026)", "Market Share", "\"Most Loved\""],
        [
            ["GitHub Copilot\n(Microsoft)",
             "20M cumulative users\n4.7M paid subscribers",
             "$1 B+",    "~42 %", "9 %"],
            ["Cursor AI\n(Anysphere)",
             "1M+ DAU\n360K paying (36% CVR)",
             "$2 B+",    "~18 %", "19 %"],
            ["Claude Code\n(Anthropic)",
             "#1 most-used agent\n71% of agentic-AI devs",
             "$1–2.5 B", "Top 3", "46 %"],
            ["Windsurf\n(Cognition AI)",
             "1M+ active users\n350+ enterprise customers",
             "$82 M*",   "Small", "—"],
            ["Replit AI",
             "35–40M total users\n750K businesses",
             "$265 M",   "~5 %",  "—"],
            ["Amazon Q Developer",
             "Not disclosed\n50K Accenture devs",
             "N/A",      "~4 %",  "—"],
            ["Tabnine",
             "1M+ users",
             "N/A",      "~1–5 %","—"],
        ],
        col_widths=[3.8*cm, 5.2*cm, 2.5*cm, 2.8*cm, 3.5*cm]
    ))
    story.append(Paragraph(
        "* Acquired by Cognition AI (July 2025) for ~$250M; Google licensed tech for ~$2.4B. "
        "\"Most Loved\" from Pragmatic Engineer Survey (15K devs, Feb 2026). "
        "Sources: GetPanto; TechCrunch; Gradually.ai Claude Code Statistics 2026.",
        SOURCE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Claude Code Highlights", H2))
    story.append(Paragraph(
        "• Launched as limited preview Feb 2025; GA May 2025. Reached "
        "<b>$1 B annualised revenue faster than any AI coding tool in history</b>.", BULLET))
    story.append(Paragraph(
        "• <b>46 % \"most loved\" rating</b> — far ahead of Cursor (19 %) and "
        "GitHub Copilot (9 %) among 15,000 surveyed developers.", BULLET))
    story.append(Paragraph(
        "• <b>95 % first-try code correctness</b> — highest among tested AI coding agents.", BULLET))
    story.append(Paragraph(
        "• Used internally at Microsoft, Google, and OpenAI.", BULLET))
    story.append(Paragraph(
        "• Accounts for <b>~10 % of Anthropic's total revenue</b>; estimated $2–2.5 B run rate "
        "by early 2026.", BULLET))


# ── Section 10 — Other AI Tools ───────────────────────────────────────────────

def section10(story):
    story.append(Spacer(1, 0.4*cm))
    story.append(section_header("10.  Other AI Tools: Image, Video, Audio & Productivity"))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Image Generation", H2))
    story.append(data_table(
        ["Tool", "Users / Scale", "Revenue (2025)", "Market Share"],
        [
            ["Midjourney",
             "19–21M registered; 1.2–2.5M DAU",
             "~$500M",  "26.8 %"],
            ["DALL-E (OpenAI)",
             "916M images created (cumul. 2024)",
             "via ChatGPT", "24.4 %"],
            ["Stable Diffusion\n(open source)",
             "12.59B images total (80% of all AI images)\n10M+ users across platforms",
             "N/A (open)", "Dominant\n(OS ecosystem)"],
            ["Adobe Firefly",
             "24B assets generated by May 2025\n75% of Fortune 500",
             "$400M\n(2024–25)", "Enterprise\nleader"],
        ],
        col_widths=[3.8*cm, 5.5*cm, 3*cm, 5.5*cm]
    ))
    story.append(Paragraph(
        "Sources: DemandSage Midjourney Statistics 2026; Quantumrun Stable Diffusion & Adobe Firefly Stats.", SOURCE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Video & Audio AI", H2))
    story.append(data_table(
        ["Tool", "Users / Scale", "Revenue / Valuation", "Notes"],
        [
            ["Runway ML",
             "300K customers\n(all major film studios)",
             "$300M rev\n$5.3B valuation",
             "Gen-4.5 = #1 Video Arena; raised $308M Apr 2025"],
            ["OpenAI Sora",
             "~3.3M downloads; 8M+ videos",
             "Shut down\nMar 24, 2026",
             "Unsustainable GPU costs; compute reallocated to GPT-5"],
            ["ElevenLabs\n(Audio AI)",
             "1M+ users; 250K+ AI agents\n60% of Fortune 500",
             "$100M ARR\n$11B valuation",
             "Raised $500M Feb 2026; 70+ languages; IPO targeted"],
        ],
        col_widths=[3.5*cm, 4.5*cm, 3.8*cm, 6*cm]
    ))
    story.append(Paragraph(
        "Sources: Sacra Runway; Fueler ElevenLabs Statistics 2026; VO3 AI Sora Shutdown Report.", SOURCE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Productivity & Companion AI", H2))
    story.append(data_table(
        ["Tool", "Users", "Revenue", "Notes"],
        [
            ["Grammarly AI",
             "30–40M DAU; 70K orgs\n96% of Fortune 500",
             "$700M ARR",
             "GrammarlyGO powered by GPT-4 + Claude; $13B valuation"],
            ["Notion AI",
             "100M total users\n4M+ paying",
             "$400M (2024)",
             "5× growth since 2022; AI bundled into Business/Enterprise plans"],
            ["Character.AI",
             "~20M MAU\n194M website visitors/mo",
             "$32M (2024)",
             "17min avg session (2× ChatGPT); 51% aged 18–24"],
            ["Replika\n(AI companion)",
             "30M registered\n~2M MAU",
             "~$24M (2024)",
             "70% users report reduced loneliness; 2.7 hrs/day avg engagement"],
        ],
        col_widths=[3.5*cm, 4.5*cm, 2.8*cm, 7*cm]
    ))
    story.append(Paragraph(
        "Sources: ElectroIQ Grammarly Statistics; Super.so Notion Statistics 2026; "
        "DemandSage Character.AI Statistics; NikolaRoza Replika Statistics 2026.",
        SOURCE))


# ── Sources ────────────────────────────────────────────────────────────────────

def sources_page(story):
    story.append(PageBreak())
    story.append(section_header("Selected Sources"))
    story.append(Spacer(1, 0.3*cm))
    srcs = [
        "DataReportal – Digital 2026: One Billion People Using AI (datareportal.com)",
        "Microsoft AI Economy Institute – Global AI Adoption 2025",
        "McKinsey – The State of AI 2025",
        "Stanford HAI – AI Index Report 2025",
        "DemandSage – ChatGPT Statistics 2026",
        "First Page Sage – Top Generative AI Chatbots by Market Share, March 2026",
        "Grand View Research – Generative AI Market Report",
        "Gartner – Total AI Spending Forecast 2025–2029",
        "Mezzi – AI Adoption Rates by Industry 2025",
        "NVIDIA Blog – State of AI Report 2026",
        "Omniflow – AI Usage Statistics 2026",
        "AllAboutAI – Global AI Adoption Rate by Country 2026",
        "Rest of World – Generative AI Adoption Trends Around the World",
        "TheySaid – How Different Generations Use AI in 2026",
        "Eurostat / IndexBox – 2025 EU AI Usage Data",
        "AmplifAI – 90+ Generative AI Statistics 2026",
        "Master of Code – 350+ Generative AI Statistics January 2026",
        "SEOProfy – 60 Perplexity AI Statistics 2026",
        "Netguru – AI Adoption Statistics 2026",
        "Vention Teams – State of AI 2026 Report",
        "Backlinko – ChatGPT Statistics 2026",
        "Recon Analytics – Paid AI Subscriber Report, January 2026",
        "The Register – Microsoft Copilot 3.3% Conversion (February 2026)",
        "RevenueCat – State of Subscription Apps 2026",
        "GetPanto – GitHub Copilot Statistics 2026",
        "TechCrunch – Cursor $2B ARR (March 2026)",
        "Gradually.ai – Claude Code Statistics 2026",
        "Pragmatic Engineer Survey – AI Coding Tools (15K devs, Feb 2026)",
        "DemandSage – Midjourney Statistics 2026",
        "Quantumrun – Adobe Firefly & Stable Diffusion Statistics 2026",
        "Sacra – Runway ML Revenue & Valuation",
        "Fueler – ElevenLabs Usage & Revenue 2026",
        "VO3 AI – OpenAI Sora Shutdown Report (March 2026)",
        "ElectroIQ – Grammarly AI Statistics",
        "Super.so – Notion Statistics 2026",
        "DemandSage – Character.AI Statistics 2026",
        "NikolaRoza – Replika AI Statistics 2026",
    ]
    for s in srcs:
        story.append(Paragraph(f"• {s}", SOURCE))

# ── Build PDF ─────────────────────────────────────────────────────────────────

def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.8*cm, bottomMargin=2*cm,
        title="Global AI Usage Report 2026",
        author="AI Research Compilation",
        subject="How Many People Are Using AI in the World"
    )

    story = []
    cover_page(story)
    story.append(Spacer(1, 0.4*cm))
    section1(story)
    story.append(Spacer(1, 0.3*cm))
    section2(story)
    story.append(Spacer(1, 0.3*cm))
    section3(story)
    story.append(Spacer(1, 0.3*cm))
    section4(story)
    story.append(Spacer(1, 0.3*cm))
    section5(story)
    story.append(Spacer(1, 0.3*cm))
    section6(story)
    story.append(Spacer(1, 0.3*cm))
    section7(story)
    section8(story)
    section9(story)
    section10(story)
    sources_page(story)

    doc.build(story)
    print(f"PDF generated: {OUTPUT}")

build()
