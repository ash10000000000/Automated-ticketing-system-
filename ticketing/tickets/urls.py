from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, AgentViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'agent/tickets', AgentViewSet, basename='agent-ticket')

urlpatterns = [
    path('', include(router.urls)),
]
