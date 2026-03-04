from django.db import models
from django.conf import settings
from django.db.models import Sum, Q, Value
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model

class Ticket(models.Model):
    PRIORITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    duration_hours = models.IntegerField() 
    size = models.IntegerField()            
    deadline = models.DateTimeField()
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Only trigger auto-assignment on creation (if pk is None)
        if not self.pk and not self.assigned_to:
            self.assigned_to = self.get_least_busy_employee()
        super().save(*args, **kwargs)

    def get_least_busy_employee(self):
        User = get_user_model()
        
        # We filter for active employees who aren't managers
        employees = User.objects.filter(is_manager=False, is_active=True)
        
        # annotate each employee with the sum of 'size' for their incomplete tickets
        # Coalesce handles the 'None' case by returning 0 instead
        employee_loads = employees.annotate(
            total_load=Coalesce(
                Sum('assigned_tasks__size', filter=Q(assigned_tasks__is_completed=False)),
                Value(0)
            )
        ).order_by('total_load', 'id') # 'id' is a tie-breaker

        return employee_loads.first()