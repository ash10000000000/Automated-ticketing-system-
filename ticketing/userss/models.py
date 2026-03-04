from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Determines if the user is a manager (can raise tickets)
    is_manager = models.BooleanField(default=False)

    # The employee's area of expertise
    specialty = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.username} ({'Manager' if self.is_manager else 'Employee'})"