from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.http import urlencode, url_has_allowed_host_and_scheme
from .models import ContactMessage, ProductionWork, CoreService, NetworkRegistryTicket


def portfolio_projects():
    services = list(CoreService.objects.all())
    work = ProductionWork.objects.filter(title__icontains='Gender-Based Violence').first()
    project_map = {
        'gender-based violence': {
            'title': 'SafeReport — GBV Reporting System',
            'summary': 'A confidential reporting experience designed to make incident submission clear and safe. Structured reporting helps teams review cases while protecting sensitive information.',
            'technologies': ['Django', 'Python', 'HTML/CSS', 'End-to-end encryption'],
            'live_url': work.live_deployment if work else '',
        },
        'attaches': {
            'title': 'Attachees Management System',
            'summary': 'A centralized portal for coordinating student attachments and internship workflows. Role-aware views organize records, logbooks, and supervisor follow-up.',
            'technologies': ['Django', 'Python', 'RBAC', 'Responsive UI'],
        },
        'digital logbook': {
            'title': 'SIST Digital Logbook Management System',
            'summary': "Built for Kisii University's School of Information Sciences & Technology. Student and supervisor views organize attachment activity in clear, structured logbook tables.",
            'technologies': ['Java', 'Spring Boot', 'Thymeleaf', 'RBAC'],
        },
    }
    projects = []
    for service in services:
        name = service.system_name.lower()
        metadata = next((value for key, value in project_map.items() if key in name), {})
        projects.append({
            'title': metadata.get('title', service.system_name),
            'summary': metadata.get('summary', service.operational_capability[:280]),
            'details': service.operational_capability,
            'technologies': metadata.get('technologies', []),
            'accent': service.glowing_accent_color,
            'live_url': metadata.get('live_url', ''),
            'repo_url': '',
        })

    projects.extend([
        {
            'title': 'Horti-Lift',
            'summary': 'A full-stack horticulture application developed during GDG. It pairs a Vite-powered frontend with a Python FastAPI backend and structured database migrations.',
            'details': 'The backend uses Alembic to manage database schema migrations.',
            'technologies': ['Vite', 'Python', 'FastAPI', 'Alembic'],
            'accent': '#00f2fe', 'live_url': '', 'repo_url': '',
        },
        {
            'title': 'Campus Lost & Found',
            'summary': 'A campus marketplace for reporting and finding misplaced items. Search and filtering help people find a match, while a guided claim flow makes the next step clear.',
            'details': 'Built with Laravel and cloud PostgreSQL, with deployment on Render. The core workflows use Item and Claim records.',
            'technologies': ['Laravel', 'PostgreSQL', 'Render', 'Search & filters'],
            'accent': '#9d4edd', 'live_url': '', 'repo_url': '',
        },
        {
            'title': 'IMMMS — Fourth-Year Capstone',
            'summary': 'A fourth-year BSc. IT capstone project at Kisii University. Its interface and core workflows can be described precisely once the project scope is confirmed.',
            'details': 'Final-year capstone project. Project expansion and interface details are pending confirmation.',
            'technologies': ['BSc. IT', 'Kisii University', 'Capstone'],
            'accent': '#ff007f', 'live_url': '', 'repo_url': '',
        },
    ])
    return projects

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
    return render(request, 'capabilities.html', {'projects': portfolio_projects()})

def vault_view(request):
    ticket_id = request.session.get('ticket_id')
    if not ticket_id:
        messages.info(request, 'Sign in with a registered account to access the Production Vault.')
        login_url = reverse('login')
        query = urlencode({'next': reverse('vault')})
        return redirect(f'{login_url}?{query}')

    try:
        ticket = NetworkRegistryTicket.objects.get(id=ticket_id)
    except NetworkRegistryTicket.DoesNotExist:
        request.session.pop('ticket_id', None)
        messages.info(request, 'Your session has expired. Sign in again to access the Production Vault.')
        login_url = reverse('login')
        query = urlencode({'next': reverse('vault')})
        return redirect(f'{login_url}?{query}')

    works = ProductionWork.objects.all()
    return render(request, 'vault.html', {
        'ticket': ticket,
        'works': works,
        'projects': portfolio_projects(),
        'skill_groups': [
            {'title': 'Frontend & UI', 'skills': ['HTML5', 'CSS3', 'Tailwind CSS', 'JavaScript', 'Thymeleaf', 'Responsive Design', 'UI/UX Prototyping']},
            {'title': 'Backend & Frameworks', 'skills': ['Python', 'Django', 'Java', 'Spring Boot', 'PHP', 'Laravel']},
            {'title': 'Databases & Cloud', 'skills': ['PostgreSQL', 'MySQL', 'MariaDB', 'Docker', 'Render', 'Koyeb', 'Git', 'GitHub']},
        ],
    })


def contact_view(request):
    if request.method != 'POST':
        return redirect('vault')
    ticket_id = request.session.get('ticket_id')
    if not ticket_id or not NetworkRegistryTicket.objects.filter(pk=ticket_id).exists():
        messages.info(request, 'Sign in with a registered account before sending an email.')
        next_url = f"{reverse('vault')}#contact"
        return redirect(f"{reverse('login')}?{urlencode({'next': next_url})}")
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    message = request.POST.get('message', '').strip()
    if not name or not email or not message:
        messages.error(request, 'Please complete your name, email, and message.')
    elif not email.lower().endswith('@gmail.com'):
        messages.error(request, 'Please enter a valid @gmail.com address.')
    else:
        submission = ContactMessage(name=name, email=email, message=message)
        try:
            submission.full_clean()
            submission.save()
            messages.success(request, 'Message received. Thank you for reaching out.')
        except ValidationError:
            messages.error(request, 'Please enter a valid email and keep your message within the form limits.')
    return redirect('/vault/#contact')


def send_sms_view(request):
    ticket_id = request.session.get('ticket_id')
    if not ticket_id or not NetworkRegistryTicket.objects.filter(pk=ticket_id).exists():
        messages.info(request, 'Sign in with a registered account before opening SMS.')
        return redirect(f"{reverse('login')}?{urlencode({'next': reverse('send_sms')})}")
    return render(request, 'send_sms.html')

def registry_view(request):
    if request.method == "POST":
        identity = request.POST.get('identity', '').strip()
        email = request.POST.get('email', '').strip()
        
        org = request.POST.get('org') or request.POST.get('associated_organization') or "Independent Node"
        scope = request.POST.get('scope') or "General"
        
        specialization = request.POST.get('specialization') or "Full-Stack Developer"
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not identity or not email or not username or not password or password != password_confirm:
            messages.error(request, "REGISTRATION FAILED: Complete the required fields and confirm your password.")
            return redirect('registry')
        
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
                password=make_password(password)
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
        login_input = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '')
        
        try:
            # Authenticate via Email or Username
            if '@' in login_input:
                ticket = NetworkRegistryTicket.objects.get(secure_email=login_input)
            else:
                ticket = NetworkRegistryTicket.objects.get(username=login_input)

            password_matches = bool(password_input) and check_password(password_input, ticket.password or '')
            if not password_matches and ticket.password == password_input:
                password_matches = True
                ticket.password = make_password(password_input)
                ticket.save(update_fields=['password'])
            if not password_matches:
                raise NetworkRegistryTicket.DoesNotExist
                
            # Store the active user's DB primary key in the session
            request.session['ticket_id'] = ticket.id
            
            messages.success(request, f"ACCESS GRANTED: Connection established for {ticket.full_identity}.")
            requested_url = request.POST.get('next') or request.GET.get('next', '')
            if requested_url and url_has_allowed_host_and_scheme(
                requested_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(requested_url)
            return redirect('dashboard')
            
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
