from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ProductionWork, CoreService, NetworkRegistryTicket

def index_view(request):
    project_count = ProductionWork.objects.count()
    service_count = CoreService.objects.count()
    ticket_count = NetworkRegistryTicket.objects.count()
    context = {
        'project_count': project_count,
        'service_count': service_count,
        'ticket_count': ticket_count
    }
    return render(request, 'index.html', context)

def capabilities_view(request):
    services = CoreService.objects.all()
    return render(request, 'capabilities.html', {'services': services})

def vault_view(request):
    works = ProductionWork.objects.all()
    return render(request, 'vault.html', {'works': works})

def registry_view(request):
    if request.method == "POST":
        identity = request.POST.get('identity')
        email = request.POST.get('email')
        
        org = request.POST.get('org') or request.POST.get('associated_organization') or "Independent Node"
        scope = request.POST.get('scope') or "General"
        
        specialization = request.POST.get('specialization') or "Full-Stack Developer"
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if the username already exists in the database
        if NetworkRegistryTicket.objects.filter(username=username).exists():
            messages.error(request, "REGISTRATION FAILED: Username already exists.")
            return redirect('registry')  # Redirects back to the registry page
            
        # Optional: Check if email already exists as well
        if NetworkRegistryTicket.objects.filter(secure_email=email).exists():
            messages.error(request, "REGISTRATION FAILED: Email already exists.")
            return redirect('registry')

        try:
            NetworkRegistryTicket.objects.create(
                full_identity=identity, 
                secure_email=email,
                associated_organization=org, 
                collaboration_scope=scope,
                specialization=specialization,
                username=username,
                password=password
            )
            messages.success(request, "CRITICAL UPDATE: Developer registration ticket successfully committed to the database.")
            return redirect('login') 
            
        except Exception as e:
            messages.error(request, "CRITICAL ERROR: Failed to write to the registry database.")
            return redirect('registry')
        
    return render(request, 'registry.html')
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NetworkRegistryTicket, ProductionWork  # Ensure your models are imported

def login_view(request):
    if request.method == "POST":
        login_input = request.POST.get('username')
        password_input = request.POST.get('password')
        
        try:
            # Authenticate via Email or Username
            if '@' in login_input:
                ticket = NetworkRegistryTicket.objects.get(secure_email=login_input, password=password_input)
            else:
                ticket = NetworkRegistryTicket.objects.get(username=login_input, password=password_input)
                
            # Store the active user's DB primary key in the session
            request.session['ticket_id'] = ticket.id
            
            messages.success(request, f"ACCESS GRANTED: Connection established for {ticket.full_identity}.")
            return redirect('dashboard')  # Redirect straight to the dashboard node
            
        except NetworkRegistryTicket.DoesNotExist:
            messages.error(request, "ACCESS DENIED: Invalid portal credentials.")
            return redirect('login')
            
    return render(request, 'login.html')

def dashboard_view(request):
    # Retrieve the logged-in ticket ID from the session
    ticket_id = request.session.get('ticket_id')
    if not ticket_id:
        messages.error(request, "RESTRICTED ACCESS: Please authenticate to view this dashboard.")
        return redirect('login')
        
    try:
        ticket = NetworkRegistryTicket.objects.get(id=ticket_id)
    except NetworkRegistryTicket.DoesNotExist:
        return redirect('login')
        
    # Pass the user's registry ticket details to the dashboard template
    return render(request, 'dashboard.html', {'ticket': ticket})

def logout_view(request):
    if 'ticket_id' in request.session:
        del request.session['ticket_id']
    messages.info(request, "Session closed. Connection terminated.")
    return redirect('login')