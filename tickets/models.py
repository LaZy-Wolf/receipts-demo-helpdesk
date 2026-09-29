from datetime import datetime, time

from django.conf import settings
from django.db import models
from django.utils import timezone


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    timezone = models.CharField(max_length=64, default="UTC")
    day_start = models.TimeField(default=time(9, 0))
    day_end = models.TimeField(default=time(17, 0))
    rr_cursor = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Agent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="agents")
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_username()


class Ticket(models.Model):
    PRIORITIES = [("urgent", "Urgent"), ("high", "High"), ("medium", "Medium"), ("low", "Low")]
    STATUSES = [("open", "Open"), ("pending", "Pending"), ("resolved", "Resolved"), ("closed", "Closed")]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tickets")
    subject = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    requester_email = models.EmailField()
    priority = models.CharField(max_length=10, choices=PRIORITIES, default="medium")
    status = models.CharField(max_length=10, choices=STATUSES, default="open")
    assignee = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets")
    created_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def is_open(self) -> bool:
        return self.status in ("open", "pending")

    def is_overdue(self, now: datetime | None = None) -> bool:
        now = now or datetime.now()
        return self.is_open() and self.due_at is not None and self.due_at < now

    def __str__(self):
        return f"#{self.pk} {self.subject}"


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at", "id"]
