# helpdesk

Internal support desk: customers email in, tickets land in a team queue, agents work them.

- Django 5, SQLite in development, JSON API under `/api/`
- SLA due dates count **business hours only** (team hours, Monday to Friday, in the team's time zone)
- New tickets are assigned round-robin among the team's available agents

## Running

```bash
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
pytest
```

## API

All endpoints need a logged-in agent. Agents only see tickets of their own team.

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/tickets/` | Query: `status` (comma-separated, `all` for every status; default hides closed), `priority`, `mine=1`, `overdue=1` |
| POST | `/api/tickets/` | `{"subject", "body", "requester_email", "priority"}`. Sets `due_at` and the assignee. |
| GET | `/api/tickets/<id>/` | Ticket with comments |
| POST | `/api/tickets/<id>/comments/` | `{"body", "internal": false}` |
| POST | `/api/tickets/<id>/close/` | |
| POST | `/api/tickets/<id>/reopen/` | A reopened ticket gets a fresh SLA from the moment it is reopened |
| GET | `/api/tickets/export.csv` | Same tickets and filters as the list, as CSV |

The list is ordered by priority (urgent, high, medium, low), then oldest first.

## SLA targets (business hours)

| Priority | Target |
| --- | --- |
| urgent | 4 |
| high | 8 |
| medium | 24 |
| low | 72 |
