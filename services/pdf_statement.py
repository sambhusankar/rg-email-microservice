import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from services.sender import LOGO_PATH

BRAND = colors.HexColor("#9333ea")
BRAND_DARK = colors.HexColor("#7e22ce")
BRAND_LIGHT = colors.HexColor("#f3e8ff")
GREEN = colors.HexColor("#16a34a")
RED = colors.HexColor("#dc2626")
GREY = colors.HexColor("#6b7280")
INK = colors.HexColor("#111827")


def _inr(amount):
    return f"Rs. {amount:,.2f}"


def build_monthly_statement_pdf(payload):
    month = payload["month"]
    expenses = payload["expenses"]
    members = payload["members"]
    total = sum(e["amount"] for e in expenses)
    top_spender = max(members, key=lambda m: m["total_paid"]) if members else None

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=BRAND_DARK, fontSize=18, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=styles["Normal"], textColor=GREY, fontSize=10)
    section = ParagraphStyle("section", parent=styles["Heading2"], textColor=INK, fontSize=12, spaceBefore=16, spaceAfter=6)
    note = ParagraphStyle("note", parent=styles["Normal"], textColor=GREY, fontSize=8, spaceBefore=10)

    elements = []

    logo = Image(LOGO_PATH, width=13 * mm, height=13 * mm)
    header_table = Table(
        [[logo, Paragraph("RoomGrub<br/>Monthly Statement", h1), Paragraph(f"Statement period<br/><b>{month}</b>", sub)]],
        colWidths=[16 * mm, 110 * mm, None],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (2, 0), (2, 0), "RIGHT"),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    rule = Table([[""]], colWidths=[None], rowHeights=[1.4])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BRAND)]))
    elements.append(rule)
    elements.append(Spacer(1, 10))

    summary_data = [[
        Paragraph("TOTAL EXPENSES", ParagraphStyle("l1", fontSize=8, textColor=RED)),
        Paragraph("MEMBERS", ParagraphStyle("l2", fontSize=8, textColor=BRAND_DARK)),
        Paragraph("TOP SPENDER", ParagraphStyle("l3", fontSize=8, textColor=GREEN)),
    ], [
        Paragraph(_inr(total), ParagraphStyle("v1", fontSize=14, textColor=RED, fontName="Helvetica-Bold")),
        Paragraph(str(len(members)), ParagraphStyle("v2", fontSize=14, textColor=BRAND_DARK, fontName="Helvetica-Bold")),
        Paragraph(top_spender["name"] if top_spender else "-", ParagraphStyle("v3", fontSize=14, textColor=GREEN, fontName="Helvetica-Bold")),
    ]]
    summary_table = Table(summary_data, colWidths=[(doc.width - 12) / 3] * 3)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 1), colors.HexColor("#fdf3f3")),
        ("BACKGROUND", (1, 0), (1, 1), BRAND_LIGHT),
        ("BACKGROUND", (2, 0), (2, 1), colors.HexColor("#f3fbf6")),
        ("BOX", (0, 0), (0, 1), 0.5, colors.HexColor("#fca5a5")),
        ("BOX", (1, 0), (1, 1), 0.5, colors.HexColor("#d8b4fe")),
        ("BOX", (2, 0), (2, 1), 0.5, colors.HexColor("#86efac")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)

    elements.append(Paragraph("Expense History", section))
    item_rows = [["Date", "Item", "Amount", "Paid By", "Participants"]]
    for e in sorted(expenses, key=lambda e: e["date"]):
        item_rows.append([
            e["date"],
            e["title"],
            _inr(e["amount"]),
            e["paid_by"],
            ", ".join(e["participants"]),
        ])
    item_rows.append(["", "Total", _inr(total), "", ""])

    items_table = Table(item_rows, colWidths=[24 * mm, 40 * mm, 26 * mm, 28 * mm, None], repeatRows=1)
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#faf5ff")]),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#e5e7eb")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, BRAND_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(items_table)

    elements.append(Paragraph("Totals by Member", section))
    member_rows = [["Member", "Paid", "Share", "Net"]]
    for m in members:
        net = m["total_paid"] - m["total_share"]
        net_color = GREEN if net > 0.01 else (RED if net < -0.01 else GREY)
        net_label = f"+{_inr(net)}" if net > 0.01 else (f"-{_inr(-net)}" if net < -0.01 else _inr(0))
        member_rows.append([
            m["name"],
            _inr(m["total_paid"]),
            _inr(m["total_share"]),
            Paragraph(net_label, ParagraphStyle(f"net-{m['name']}", fontSize=9, textColor=net_color, fontName="Helvetica-Bold")),
        ])

    members_table = Table(member_rows, colWidths=[55 * mm, 35 * mm, 35 * mm, None], repeatRows=1)
    members_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#faf5ff")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(members_table)

    if top_spender and total > 0:
        share_pct = (top_spender["total_paid"] / total) * 100
        elements.append(Paragraph("Analytics", section))
        analytics = Paragraph(
            f'<font color="#9333ea"><b>{top_spender["name"]}</b></font> paid the most this month '
            f'&mdash; <b>{_inr(top_spender["total_paid"])}</b> ({share_pct:.0f}% of total room spend).',
            ParagraphStyle("analytics", fontSize=10, textColor=INK, leading=14),
        )
        elements.append(analytics)

    elements.append(Paragraph(
        "This statement is generated automatically by RoomGrub and reflects expenses logged for the period above.",
        note,
    ))

    doc.build(elements)
    return buf.getvalue()
