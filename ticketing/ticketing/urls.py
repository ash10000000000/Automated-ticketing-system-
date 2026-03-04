"""
URL configuration for ticketing project.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token

from tickets.frontend_views import (
    landing_view,
    dashboard_view,
    create_ticket_view,
    agent_dashboard_view,
    ticket_detail_view,
    complete_ticket_view,
    bulk_ticket_action_view,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Frontend pages
    path("", landing_view, name="landing"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("tickets/create/", create_ticket_view, name="create_ticket"),
    path("tickets/<int:ticket_id>/", ticket_detail_view, name="ticket_detail"),
    path("tickets/<int:ticket_id>/complete/", complete_ticket_view, name="complete_ticket"),
    path("tickets/bulk-action/", bulk_ticket_action_view, name="bulk_ticket_action"),
    path("agent/", agent_dashboard_view, name="agent_dashboard"),

    # REST API
    path("api/", include("tickets.urls")),
    path("api/api-token-auth/", obtain_auth_token, name="api_token_auth"),
]
