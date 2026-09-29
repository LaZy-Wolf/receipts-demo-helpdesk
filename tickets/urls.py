from django.urls import path

from . import views

urlpatterns = [
    path("tickets/", views.tickets),
    path("tickets/export.csv", views.export_csv),
    path("tickets/<int:pk>/", views.ticket_detail),
    path("tickets/<int:pk>/comments/", views.add_comment),
    path("tickets/<int:pk>/close/", views.close_ticket),
    path("tickets/<int:pk>/reopen/", views.reopen_ticket),
]
