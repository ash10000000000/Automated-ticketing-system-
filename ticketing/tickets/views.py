from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Ticket
from .serializers import TicketSerializer


class TicketViewSet(viewsets.ModelViewSet):
    """
    Allows authenticated customers/managers to create tickets and view their own.
    - On create, `created_by` is auto-set to the logged-in user.
    - The queryset is filtered to only show tickets created by the current user.
    """
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(created_by=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides a read-only list of incomplete tickets assigned to the logged-in agent.
    Agents (employees) use this endpoint to see their work queue.
    """
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(
            assigned_to=self.request.user,
            is_completed=False
        ).order_by('-created_at')
