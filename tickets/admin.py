from django.contrib import admin

from .models import Agent, Comment, Team, Ticket

admin.site.register(Team)
admin.site.register(Agent)
admin.site.register(Comment)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "team", "priority", "status", "assignee", "due_at")
    list_filter = ("team", "priority", "status")
