def welcome_email(payload):
    subject = "Welcome to RoomGrub!"
    body = f"""
    <p>Hi {payload['name']},</p>
    <p>Welcome to RoomGrub! Your account is ready to go.</p>
    """
    return subject, body


def expense_split_email(payload):
    subject = f"New expense: {payload['expense_title']}"
    rows = "".join(
        f"<li>{member['name']}: owes {member['amount_owed']}</li>"
        for member in payload["members"]
    )
    body = f"""
    <p>{payload['paid_by']} added a new expense in your room.</p>
    <ul>{rows}</ul>
    """
    return subject, body


def monthly_summary_email(payload):
    subject = f"Your {payload['month']} room summary"
    rows = "".join(
        f"<li>{member['name']}: total owed {member['total_owed']}</li>"
        for member in payload["members"]
    )
    body = f"""
    <p>Here's your room's expense summary for {payload['month']}.</p>
    <ul>{rows}</ul>
    """
    return subject, body
