import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from tickets.models import Ticket

User = get_user_model()

SPECIALTIES = ['Networking', 'Security', 'Frontend', 'Backend', 'DevOps']
PRIORITIES = ['Low', 'Medium', 'High']

TICKET_TITLES = [
    'Login page not loading',
    'Dashboard timeout error',
    'Payment gateway failure',
    'Email notifications delayed',
    'User profile update bug',
    'Search index out of date',
    'API rate limiting issue',
    'Mobile app crash on startup',
    'SSL certificate expiring',
    'Database connection pool leak',
    'File upload size limit error',
    'Two-factor auth not sending SMS',
    'Report generation slow',
    'Password reset link expired',
    'Session timeout too short',
    'CORS error on staging',
    'Webhook delivery failures',
    'Cron job not running',
    'Memory usage spike on server',
    'UI layout broken on Safari',
]


class Command(BaseCommand):
    help = 'Seeds the database with 5 test agents, 1 manager, and 20 random tickets.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding database...'))

        # ── Create 1 Manager ──
        manager, created = User.objects.get_or_create(
            username='manager1',
            defaults={
                'email': 'manager1@ticketing.dev',
                'is_manager': True,
                'specialty': 'Management',
            }
        )
        if created:
            manager.set_password('pass1234')
            manager.save()
            self.stdout.write(self.style.SUCCESS(f'  Created manager: {manager.username}'))
        else:
            self.stdout.write(f'  Manager already exists: {manager.username}')

        # ── Create 5 Agents (Employees) ──
        agents = []
        for i in range(1, 6):
            agent, created = User.objects.get_or_create(
                username=f'agent{i}',
                defaults={
                    'email': f'agent{i}@ticketing.dev',
                    'is_manager': False,
                    'specialty': SPECIALTIES[i - 1],
                }
            )
            if created:
                agent.set_password('pass1234')
                agent.save()
                self.stdout.write(self.style.SUCCESS(
                    f'  Created agent: {agent.username} (specialty: {agent.specialty})'
                ))
            else:
                self.stdout.write(f'  Agent already exists: {agent.username}')
            agents.append(agent)

        # ── Create 20 Tickets ──
        now = timezone.now()
        created_count = 0

        for i, title in enumerate(TICKET_TITLES):
            if Ticket.objects.filter(title=title).exists():
                self.stdout.write(f'  Ticket already exists: "{title}"')
                continue

            # Mix of past and future deadlines so we can test the overdue logic
            if i % 3 == 0:
                # Past deadline → will be overdue
                deadline = now - timedelta(days=random.randint(1, 10))
            else:
                # Future deadline → not overdue yet
                deadline = now + timedelta(days=random.randint(1, 30))

            Ticket.objects.create(
                title=title,
                description=f'Auto-generated test ticket: {title}',
                priority=random.choice(PRIORITIES),
                duration_hours=random.randint(1, 16),
                size=random.randint(1, 10),
                deadline=deadline,
                created_by=manager,
                # assigned_to is auto-set by the model's save() method
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {created_count} tickets across {len(agents)} agents.'
        ))
        self.stdout.write(self.style.NOTICE('Workload distribution:'))
        for agent in agents:
            load = Ticket.objects.filter(
                assigned_to=agent, is_completed=False
            ).count()
            self.stdout.write(f'  {agent.username}: {load} active tickets')
