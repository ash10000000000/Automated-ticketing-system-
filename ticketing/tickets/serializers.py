from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Ticket

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_manager', 'specialty', 'is_active']
        read_only_fields = ['id']


class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'priority',
            'duration_hours', 'size', 'deadline',
            'created_by', 'assigned_to',
            'is_completed', 'is_overdue', 'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'assigned_to', 'is_overdue', 'created_at']

    def get_is_overdue(self, obj):
        """Returns True if the ticket is incomplete and past its deadline."""
        if not obj.is_completed and obj.deadline < timezone.now():
            return True
        return False
