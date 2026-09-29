from .models import Ticket


def iso(dt):
    return dt.isoformat() if dt else None


def comment_json(comment) -> dict:
    return {"author": comment.author.username, "body": comment.body, "internal": comment.internal,
            "created_at": iso(comment.created_at)}


def ticket_json(ticket: Ticket, with_comments: bool = False) -> dict:
    data = {
        "id": ticket.pk,
        "subject": ticket.subject,
        "requester_email": ticket.requester_email,
        "priority": ticket.priority,
        "status": ticket.status,
        "assignee": ticket.assignee.user.username if ticket.assignee else None,
        "created_at": iso(ticket.created_at),
        "due_at": iso(ticket.due_at),
        "closed_at": iso(ticket.closed_at),
    }
    if with_comments:
        data["body"] = ticket.body
        data["comments"] = [comment_json(c) for c in ticket.comments.select_related("author")]
    return data
