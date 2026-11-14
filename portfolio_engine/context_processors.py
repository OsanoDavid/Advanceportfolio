from .models import NetworkRegistryTicket

def active_ticket_context(request):
    """
    Supplies the active NetworkRegistryTicket identity to all templates,
    powering the universal top navigation profile avatar and dropdown.
    """
    ticket_id = request.session.get('ticket_id')
    if ticket_id:
        try:
            ticket = NetworkRegistryTicket.objects.get(id=ticket_id)
            return {'active_ticket': ticket}
        except NetworkRegistryTicket.DoesNotExist:
            return {'active_ticket': None}
    return {'active_ticket': None}
