from services.sender import LOGO_CID

BRAND_COLOR = "#9333ea"
BRAND_DARK = "#7e22ce"
BRAND_LIGHT = "#f3e8ff"
BRAND_MID = "#c084fc"
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=broccly.roomgrub.twa&pcampaignid=web_share"


def welcome_email(payload):
    subject = "Welcome to RoomGrub!"
    body = f"""
    <div style="background-color:{BRAND_LIGHT};padding:32px 16px;font-family:Segoe UI,Helvetica,Arial,sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;margin:0 auto;background:#ffffff;border-radius:16px;overflow:hidden;">
        <tr>
          <td style="background:{BRAND_COLOR};padding:32px 24px;text-align:center;">
            <img src="cid:{LOGO_CID}" width="64" height="64" alt="RoomGrub" style="border-radius:16px;display:block;margin:0 auto 12px;" />
            <div style="color:#ffffff;font-size:22px;font-weight:700;">RoomGrub</div>
            <div style="color:{BRAND_LIGHT};font-size:13px;margin-top:4px;">Split bills, share easy.</div>
          </td>
        </tr>
        <tr>
          <td style="padding:32px 28px;">
            <p style="font-size:17px;color:#111827;margin:0 0 12px;">Hi {payload['name']},</p>
            <p style="font-size:15px;color:#374151;line-height:1.6;margin:0 0 20px;">
              Welcome to RoomGrub! Your account is ready to go. Track shared
              expenses, split bills, and settle up with your roommates
              without the awkward money conversations.
            </p>
            <div style="text-align:center;margin:28px 0;">
              <a href="{PLAY_STORE_URL}" style="display:inline-block;background:{BRAND_COLOR};color:#ffffff;text-decoration:none;font-size:14px;font-weight:600;padding:12px 24px;border-radius:8px;">
                Get it on Google Play
              </a>
            </div>
            <p style="font-size:13px;color:#9ca3af;line-height:1.5;margin:24px 0 0;text-align:center;">
              Also available as a PWA on iOS &mdash; open RoomGrub in Safari and
              add it to your home screen.
            </p>
          </td>
        </tr>
        <tr>
          <td style="background:{BRAND_LIGHT};padding:16px 24px;text-align:center;">
            <span style="font-size:12px;color:{BRAND_DARK};">&copy; RoomGrub &middot; Made for roommates who split fair.</span>
          </td>
        </tr>
      </table>
    </div>
    """
    return subject, body


def _inr(amount):
    return f"&#8377;{amount:,.2f}"


def _initial(name):
    return name.strip()[:1].upper() if name.strip() else "?"


def _status_colors(pending_amount):
    if pending_amount > 0.01:
        return {"border": "#86efac", "bg": "#f0fdf4", "text": "#16a34a", "label": "Gets back"}
    if pending_amount < -0.01:
        return {"border": "#fca5a5", "bg": "#fff5f5", "text": "#dc2626", "label": "Owes"}
    return {"border": "#d8b4fe", "bg": BRAND_LIGHT, "text": BRAND_COLOR, "label": "Settled up"}


def expense_split_email(payload):
    expense_title = payload["expense_title"]
    total_pending = payload["total_pending"]
    members = payload["members"]
    settlements = payload.get("settlements", [])
    subject = f"Room balances updated after {expense_title}"

    member_rows = ""
    for member in members:
        amount = member["pending_amount"]
        sc = _status_colors(amount)
        amount_display = "&#8377;0" if sc["label"] == "Settled up" else _inr(amount)
        member_rows += f"""
            <tr>
              <td style="padding:6px 0;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {sc['border']};background:{sc['bg']};border-radius:12px;">
                  <tr>
                    <td style="padding:12px 14px;width:40px;">
                      <div style="width:36px;height:36px;border-radius:50%;background:{BRAND_MID};color:#ffffff;font-size:14px;font-weight:700;text-align:center;line-height:36px;">{_initial(member['name'])}</div>
                    </td>
                    <td style="padding:12px 4px;">
                      <div style="font-size:14px;font-weight:600;color:#1e1b4b;">{member['name']}</div>
                      <div style="font-size:12px;color:#6b7280;margin-top:1px;">{sc['label']}</div>
                    </td>
                    <td style="padding:12px 14px;text-align:right;white-space:nowrap;">
                      <span style="font-size:17px;font-weight:700;color:{sc['text']};">{amount_display}</span>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
        """

    settlement_rows = "".join(
        f"""
        <tr>
          <td style="padding:6px 0;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{BRAND_LIGHT};border-radius:10px;">
              <tr>
                <td style="padding:12px 14px;font-size:13px;">
                  <span style="font-weight:600;color:#1e1b4b;">{s['from_name']}</span>
                  <span style="color:#9ca3af;"> pays </span>
                  <span style="font-weight:600;color:#1e1b4b;">{s['to_name']}</span>
                </td>
                <td style="padding:12px 14px;text-align:right;white-space:nowrap;">
                  <span style="font-size:13px;font-weight:700;color:{BRAND_DARK};">{_inr(s['amount'])}</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """
        for s in settlements
    )
    settlements_section = f"""
        <div style="font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:.03em;margin:22px 0 4px;">Who pays whom</div>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
          {settlement_rows}
        </table>
    """ if settlements else """
        <div style="text-align:center;padding:20px 0 4px;">
          <div style="font-size:15px;font-weight:700;color:#16a34a;">All clear!</div>
          <div style="font-size:13px;color:#6b7280;margin-top:2px;">No pending transfers. Everyone is even.</div>
        </div>
    """

    body = f"""
    <div style="background-color:{BRAND_LIGHT};padding:32px 16px;font-family:Segoe UI,Helvetica,Arial,sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;margin:0 auto;background:#ffffff;border-radius:16px;overflow:hidden;">
        <tr>
          <td style="background:{BRAND_COLOR};padding:28px 24px;text-align:center;">
            <img src="cid:{LOGO_CID}" width="48" height="48" alt="RoomGrub" style="border-radius:12px;display:block;margin:0 auto 10px;" />
            <div style="color:#ffffff;font-size:18px;font-weight:700;">Room balances updated</div>
            <div style="color:{BRAND_LIGHT};font-size:13px;margin-top:4px;">After: {expense_title}</div>
          </td>
        </tr>
        <tr>
          <td style="padding:24px 24px 8px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:18px;">
              <tr>
                <td width="50%" style="background:#fdf3f3;border-radius:12px;padding:14px;">
                  <div style="font-size:11px;color:#991b1b;text-transform:uppercase;letter-spacing:.03em;">Total Pending</div>
                  <div style="font-size:19px;font-weight:700;color:#dc2626;margin-top:4px;">{_inr(total_pending)}</div>
                </td>
                <td width="12"></td>
                <td width="50%" style="background:#f3fbf6;border-radius:12px;padding:14px;">
                  <div style="font-size:11px;color:#166534;text-transform:uppercase;letter-spacing:.03em;">Transfers Needed</div>
                  <div style="font-size:19px;font-weight:700;color:#16a34a;margin-top:4px;">{len(settlements)}</div>
                </td>
              </tr>
            </table>

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              {member_rows}
            </table>

            {settlements_section}
          </td>
        </tr>
        <tr>
          <td style="background:{BRAND_LIGHT};padding:16px 24px;text-align:center;">
            <span style="font-size:12px;color:{BRAND_DARK};">&copy; RoomGrub &middot; Made for roommates who split fair.</span>
          </td>
        </tr>
      </table>
    </div>
    """
    return subject, body


def monthly_summary_email(payload):
    from services.pdf_statement import build_monthly_statement_pdf

    month = payload["month"]
    total = sum(e["amount"] for e in payload["expenses"])
    members = payload["members"]
    top_spender = max(members, key=lambda m: m["total_paid"]) if members else None
    subject = f"Your {month} room statement"

    member_rows = ""
    for m in members:
        net = m["total_paid"] - m["total_share"]
        sc = _status_colors(net)
        net_display = "&#8377;0" if sc["label"] == "Settled up" else _inr(net)
        member_rows += f"""
            <tr>
              <td style="padding:6px 0;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {sc['border']};background:{sc['bg']};border-radius:12px;">
                  <tr>
                    <td style="padding:12px 14px;width:40px;">
                      <div style="width:36px;height:36px;border-radius:50%;background:{BRAND_MID};color:#ffffff;font-size:14px;font-weight:700;text-align:center;line-height:36px;">{_initial(m['name'])}</div>
                    </td>
                    <td style="padding:12px 4px;">
                      <div style="font-size:14px;font-weight:600;color:#1e1b4b;">{m['name']}</div>
                      <div style="font-size:12px;color:#6b7280;margin-top:1px;">Paid {_inr(m['total_paid'])} &middot; share {_inr(m['total_share'])}</div>
                    </td>
                    <td style="padding:12px 14px;text-align:right;white-space:nowrap;">
                      <span style="font-size:15px;font-weight:700;color:{sc['text']};">{net_display}</span>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
        """

    top_spender_html = ""
    if top_spender and total > 0:
        share_pct = (top_spender["total_paid"] / total) * 100
        top_spender_html = f"""
            <div style="background:{BRAND_LIGHT};border-radius:12px;padding:14px 16px;margin-top:20px;">
              <div style="font-size:12px;color:{BRAND_DARK};text-transform:uppercase;letter-spacing:.03em;">Top spender</div>
              <div style="font-size:14px;color:#1e1b4b;margin-top:4px;">
                <b>{top_spender['name']}</b> paid the most this month &mdash; {_inr(top_spender['total_paid'])} ({share_pct:.0f}% of total).
              </div>
            </div>
        """

    body = f"""
    <div style="background-color:{BRAND_LIGHT};padding:32px 16px;font-family:Segoe UI,Helvetica,Arial,sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;margin:0 auto;background:#ffffff;border-radius:16px;overflow:hidden;">
        <tr>
          <td style="background:{BRAND_COLOR};padding:28px 24px;text-align:center;">
            <img src="cid:{LOGO_CID}" width="48" height="48" alt="RoomGrub" style="border-radius:12px;display:block;margin:0 auto 10px;" />
            <div style="color:#ffffff;font-size:18px;font-weight:700;">Your {month} statement</div>
            <div style="color:{BRAND_LIGHT};font-size:13px;margin-top:4px;">Full breakdown attached as PDF</div>
          </td>
        </tr>
        <tr>
          <td style="padding:24px 24px 8px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:18px;">
              <tr>
                <td width="50%" style="background:#fdf3f3;border-radius:12px;padding:14px;">
                  <div style="font-size:11px;color:#991b1b;text-transform:uppercase;letter-spacing:.03em;">Total Expenses</div>
                  <div style="font-size:19px;font-weight:700;color:#dc2626;margin-top:4px;">{_inr(total)}</div>
                </td>
                <td width="12"></td>
                <td width="50%" style="background:#f3fbf6;border-radius:12px;padding:14px;">
                  <div style="font-size:11px;color:#166534;text-transform:uppercase;letter-spacing:.03em;">Expense Items</div>
                  <div style="font-size:19px;font-weight:700;color:#16a34a;margin-top:4px;">{len(payload['expenses'])}</div>
                </td>
              </tr>
            </table>

            <div style="font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:.03em;margin:4px 0;">Totals by member</div>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              {member_rows}
            </table>

            {top_spender_html}

            <p style="font-size:12px;color:#9ca3af;margin:20px 0 0;text-align:center;">
              The attached PDF has the full itemized breakdown &mdash; every
              expense, who paid, and who participated.
            </p>
          </td>
        </tr>
        <tr>
          <td style="background:{BRAND_LIGHT};padding:16px 24px;text-align:center;">
            <span style="font-size:12px;color:{BRAND_DARK};">&copy; RoomGrub &middot; Made for roommates who split fair.</span>
          </td>
        </tr>
      </table>
    </div>
    """

    pdf_bytes = build_monthly_statement_pdf(payload)
    attachments = [{
        "filename": f"RoomGrub-statement-{month.replace(' ', '-')}.pdf",
        "content": list(pdf_bytes),
        "content_type": "application/pdf",
    }]
    return subject, body, attachments
