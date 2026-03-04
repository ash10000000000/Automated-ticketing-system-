from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce

from .models import Ticket
from .forms import TicketForm


def landing_view(request):
    """Landing page — redirects to dashboard if already logged in."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


@login_required
def dashboard_view(request):
    """Main dashboard — shows different data for managers vs agents."""
    user = request.user

    if user.is_manager:
        tickets = Ticket.objects.filter(created_by=user).order_by('-created_at')
    else:
        tickets = Ticket.objects.filter(assigned_to=user).order_by('-created_at')

    now = timezone.now()

    # Annotate overdue status onto each ticket for template use
    for ticket in tickets:
        ticket.is_overdue = not ticket.is_completed and ticket.deadline < now

    total_tickets = tickets.count()
    completed_tickets = tickets.filter(is_completed=True).count()
    open_tickets = total_tickets - completed_tickets
    overdue_tickets = sum(1 for t in tickets if t.is_overdue)

    context = {
        'tickets': tickets,
        'total_tickets': total_tickets,
        'completed_tickets': completed_tickets,
        'open_tickets': open_tickets,
        'overdue_tickets': overdue_tickets,
    }
    return render(request, 'dashboard.html', context)


@login_required
def create_ticket_view(request):
    """Create a new ticket (manager only)."""
    if not request.user.is_manager:
        messages.error(request, 'Only managers can create tickets.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()  # This triggers auto-assignment via model's save()
            messages.success(
                request,
                f'Ticket "{ticket.title}" created and assigned to {ticket.assigned_to or "nobody (no agents available)"}!'
            )
            return redirect('dashboard')
    else:
        form = TicketForm()

    return render(request, 'create_ticket.html', {'form': form})


@login_required
def agent_dashboard_view(request):
    """Agent's work queue — shows incomplete assigned tickets."""
    tickets = Ticket.objects.filter(
        assigned_to=request.user,
        is_completed=False
    ).order_by('-created_at')

    now = timezone.now()
    for ticket in tickets:
        ticket.is_overdue = ticket.deadline < now

    total_load = sum(t.size for t in tickets)
    overdue_count = sum(1 for t in tickets if t.is_overdue)

    context = {
        'tickets': tickets,
        'total_load': total_load,
        'overdue_count': overdue_count,
    }
    return render(request, 'agent_dashboard.html', context)


@login_required
def ticket_detail_view(request, ticket_id):
    """View a single ticket's details."""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Check that the user has permission to view this ticket
    if ticket.created_by != request.user and ticket.assigned_to != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this ticket.')
        return redirect('dashboard')

    now = timezone.now()
    ticket.is_overdue = not ticket.is_completed and ticket.deadline < now

    return render(request, 'ticket_detail.html', {'ticket': ticket})


@login_required
def complete_ticket_view(request, ticket_id):
    """Mark a ticket as completed (assigned agent only)."""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.assigned_to != request.user:
        messages.error(request, 'Only the assigned agent can complete this ticket.')
        return redirect('dashboard')

    if request.method == 'POST':
        ticket.is_completed = True
        ticket.save()
        messages.success(request, f'Ticket "{ticket.title}" marked as completed!')

    return redirect('agent_dashboard')


@login_required
def bulk_ticket_action_view(request):
    """Handle bulk close/delete actions for managers."""
    if not request.user.is_manager:
        messages.error(request, 'Only managers can perform bulk actions.')
        return redirect('dashboard')

    if request.method == 'POST':
        ticket_ids = request.POST.getlist('ticket_ids')
        action = request.POST.get('action')

        if not ticket_ids:
            messages.error(request, 'No tickets selected.')
            return redirect('dashboard')

        tickets = Ticket.objects.filter(id__in=ticket_ids, created_by=request.user)
        count = tickets.count()

        if action == 'close':
            tickets.update(is_completed=True)
            messages.success(request, f'{count} ticket(s) marked as completed.')
        elif action == 'delete':
            tickets.delete()
            messages.success(request, f'{count} ticket(s) deleted.')
        else:
            messages.error(request, 'Unknown action.')

    return redirect('dashboard')
