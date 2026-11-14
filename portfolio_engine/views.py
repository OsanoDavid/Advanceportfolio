import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.urls import reverse
from django.utils.http import urlencode, url_has_allowed_host_and_scheme
from .models import ContactMessage, ProductionWork, CoreService, NetworkRegistryTicket


def portfolio_projects():
    works = list(ProductionWork.objects.all().order_by('-id'))
    services = list(CoreService.objects.all())
    
    projects = []
    seen_titles = set()
    
    # 1. Prioritize user-managed production works from the database
    for work in works:
        title_lower = work.title.lower()
        seen_titles.add(title_lower)
        tech_list = [t.strip() for t in work.architecture_stack.split(',') if t.strip()]
        projects.append({
            'title': work.title,
            'summary': work.sub_title or work.detailed_scope[:240],
            'details': work.detailed_scope,
            'technologies': tech_list or ['Python', 'Django', 'Web System'],
            'accent': '#00f2fe' if any(w in work.architecture_stack.lower() for w in ['python', 'django']) else '#ff007f',
            'live_url': work.live_deployment,
            'repo_url': work.source_repository,
        })
        
    # 2. Add core services if not already represented
    project_map = {
        'gender-based violence': {
            'title': 'SafeReport — GBV Reporting System',
            'summary': 'A confidential reporting experience designed to make incident submission clear and safe. Structured reporting helps teams review cases while protecting sensitive information.',
            'technologies': ['Django', 'Python', 'HTML/CSS', 'End-to-end encryption'],
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
    for service in services:
        name = service.system_name.lower()
        if not any(key in name for key in seen_titles) and not any(name in st for st in seen_titles):
            metadata = next((value for key, value in project_map.items() if key in name), {})
            seen_titles.add(name)
            projects.append({
                'title': metadata.get('title', service.system_name),
                'summary': metadata.get('summary', service.operational_capability[:280]),
                'details': service.operational_capability,
                'technologies': metadata.get('technologies', ['Python', 'Architecture']),
                'accent': service.glowing_accent_color,
                'live_url': '',
                'repo_url': '',
            })
            
    # 3. Include baseline portfolio applications if not added
    builtin_projects = [
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
    ]
    for p in builtin_projects:
        if not any(p['title'].lower() in st for st in seen_titles):
            projects.append(p)
            
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


def github_gateway_view(request):
    ticket_id = request.session.get('ticket_id')
    if not ticket_id or not NetworkRegistryTicket.objects.filter(pk=ticket_id).exists():
        messages.info(request, 'Sign in with a registered account before accessing GitHub.')
        return redirect(f"{reverse('login')}?{urlencode({'next': reverse('github_gateway')})}")
    return redirect('https://github.com/OsanoDavid')

def registry_view(request):
    if request.method == "POST":
        identity = request.POST.get('identity', '').strip()
        email = request.POST.get('email', '').strip()
        id_number = request.POST.get('id_number', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        reg_number = request.POST.get('reg_number', '').strip()
        gender = request.POST.get('gender', '').strip()
        
        org_select = request.POST.get('org_select', '')
        org_custom = request.POST.get('org_custom', '').strip()
        if org_select == 'Other' and org_custom:
            org = org_custom
        else:
            org = org_custom or org_select or request.POST.get('org') or request.POST.get('associated_organization') or "Independent Node"
            
        scope = request.POST.get('scope', '').strip() or "General Software Development"
        
        specializations = request.POST.getlist('specializations')
        custom_spec = request.POST.get('spec_custom', '').strip()
        if custom_spec and 'Other' in specializations:
            specializations = [s for s in specializations if s != 'Other'] + [custom_spec]
        if specializations:
            specialization = ", ".join(specializations)
        else:
            specialization = request.POST.get('specialization') or "Full-Stack Developer"

        github_link = request.POST.get('github_link', '').strip()
        live_link = request.POST.get('live_link', '').strip()
        
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not identity or not email or not username or not password or password != password_confirm:
            messages.error(request, "REGISTRATION FAILED: Complete the required fields and confirm your password.")
            return redirect('registry')
        
        # Check if the username already exists in the database
        if NetworkRegistryTicket.objects.filter(username=username).exists():
            messages.error(request, "REGISTRATION FAILED: Username already exists.")
            return redirect('registry')
            
        # Check if email already exists
        if NetworkRegistryTicket.objects.filter(secure_email=email).exists():
            messages.error(request, "REGISTRATION FAILED: Email already exists.")
            return redirect('registry')

        try:
            ticket = NetworkRegistryTicket.objects.create(
                full_identity=identity, 
                secure_email=email,
                associated_organization=org, 
                collaboration_scope=scope,
                specialization=specialization,
                username=username,
                password=make_password(password),
                phone_number=phone_number,
                id_number=id_number,
                reg_number=reg_number,
                gender=gender,
                github_link=github_link,
                live_link=live_link,
            )
            # Establish session and activate developer profile immediately
            request.session['ticket_id'] = ticket.id
            messages.success(request, f"PROFILE ACTIVATED: Identity verified. Welcome to CORE_NODE, {ticket.full_identity}!")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, "CRITICAL ERROR: Failed to write to the registry database.")
            return redirect('registry')
        
    return render(request, 'registry.html')

def login_view(request):
    if request.method == "POST":
        login_input = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '')

        # Auto-provision super admin if authenticating with master credentials on remote deployment
        superadmin_pwd = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '@OsanoAdmin2026!')
        if login_input.lower() in ['osanodavid', 'admin', 'osanodavid09@gmail.com'] and password_input == superadmin_pwd:
            if not User.objects.filter(username__in=['OsanoDavid', 'admin'], is_superuser=True).exists():
                try:
                    call_command('setup_superadmin')
                except Exception:
                    pass
        
        ticket = None
        # 1. First authenticate with Django User model (supports superusers / staff)
        auth_user = authenticate(request, username=login_input, password=password_input)
        if not auth_user and '@' in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                auth_user = authenticate(request, username=user_obj.username, password=password_input)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                auth_user = None

        if auth_user:
            login(request, auth_user)
            ticket, _ = NetworkRegistryTicket.objects.get_or_create(username=auth_user.username)
            ticket.is_superadmin = auth_user.is_superuser
            if not ticket.full_identity:
                ticket.full_identity = auth_user.get_full_name() or auth_user.username
            if not ticket.secure_email:
                ticket.secure_email = auth_user.email
            ticket.save()
            request.session['ticket_id'] = ticket.id
            messages.success(request, f"SUPER ADMIN ACCESS: Welcome back to Core Node Terminal, {ticket.full_identity}.")
            requested_url = request.POST.get('next') or request.GET.get('next', '')
            if requested_url and url_has_allowed_host_and_scheme(
                requested_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(requested_url)
            return redirect('dashboard')

        # 2. Authenticate standard NetworkRegistryTicket
        try:
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


def admin_login_view(request):
    """
    Dedicated Root Super Admin Terminal Gateway.
    Separate from the standard user login page, with enhanced cyber root terminal UI.
    """
    if request.method == "POST":
        login_input = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '')

        # Auto-provision super admin if authenticating with master credentials on fresh deployment
        superadmin_pwd = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '@OsanoAdmin2026!')
        if login_input.lower() in ['osanodavid', 'admin', 'osanodavid09@gmail.com'] and password_input == superadmin_pwd:
            if not User.objects.filter(username__in=['OsanoDavid', 'admin'], is_superuser=True).exists():
                try:
                    call_command('setup_superadmin')
                except Exception:
                    pass

        auth_user = authenticate(request, username=login_input, password=password_input)
        if not auth_user and '@' in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                auth_user = authenticate(request, username=user_obj.username, password=password_input)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                auth_user = None

        if auth_user:
            if not (auth_user.is_superuser or auth_user.is_staff):
                messages.error(
                    request,
                    "CLEARANCE DENIED: Standard user node credentials detected. The Super Admin Terminal requires Root Super Administrator clearance."
                )
                return redirect('admin_login')

            login(request, auth_user)
            ticket, _ = NetworkRegistryTicket.objects.get_or_create(username=auth_user.username)
            ticket.is_superadmin = True
            if not ticket.full_identity:
                ticket.full_identity = auth_user.get_full_name() or auth_user.username
            if not ticket.secure_email:
                ticket.secure_email = auth_user.email
            ticket.save()
            request.session['ticket_id'] = ticket.id
            messages.success(request, f"ROOT TERMINAL UNLOCKED: Welcome back, Super Administrator {ticket.full_identity}.")
            requested_url = request.POST.get('next') or request.GET.get('next', '')
            if requested_url and url_has_allowed_host_and_scheme(
                requested_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(requested_url)
            return redirect('dashboard')

        # Check standard NetworkRegistryTicket
        try:
            if '@' in login_input:
                ticket = NetworkRegistryTicket.objects.get(secure_email=login_input)
            else:
                ticket = NetworkRegistryTicket.objects.get(username=login_input)

            if bool(password_input) and (check_password(password_input, ticket.password or '') or ticket.password == password_input):
                if not ticket.is_superadmin:
                    messages.error(
                        request,
                        "ROOT ACCESS RESTRICTED: Standard user accounts cannot unlock the Super Admin Gateway. Please use the Developer User Gateway."
                    )
                    return redirect('admin_login')
                request.session['ticket_id'] = ticket.id
                messages.success(request, f"SUPER ADMIN ACCESS: Welcome back {ticket.full_identity}.")
                return redirect('dashboard')
        except NetworkRegistryTicket.DoesNotExist:
            pass

        messages.error(request, "ROOT ACCESS REJECTED: Invalid administrator credentials or key handshake failed.")
        return redirect('admin_login')

    return render(request, 'admin_login.html')

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
        
    if request.method == "POST":
        action = request.POST.get('action')

        # Super Admin Project Deployment Controls
        if ticket.is_superadmin:
            if action == 'add_project':
                title = request.POST.get('title', '').strip()
                sub_title = request.POST.get('sub_title', '').strip()
                stack = request.POST.get('stack', '').strip()
                scope = request.POST.get('detailed_scope', '').strip()
                live_url = request.POST.get('live_url', '').strip()
                repo_url = request.POST.get('source_repository', '').strip()
                status = request.POST.get('system_status', 'Operational').strip()
                if title:
                    ProductionWork.objects.create(
                        title=title,
                        sub_title=sub_title,
                        architecture_stack=stack or "Python, Django, Cloud",
                        detailed_scope=scope or sub_title or "Production deployed application.",
                        live_deployment=live_url,
                        source_repository=repo_url,
                        system_status=status or "Operational",
                    )
                    messages.success(request, f"DEPLOYMENT RECORDED: Project '{title}' committed to Production Vault.")
                    return redirect('dashboard')

            elif action == 'update_project':
                proj_id = request.POST.get('project_id')
                work = ProductionWork.objects.filter(pk=proj_id).first()
                if work:
                    work.title = request.POST.get('title', work.title).strip()
                    work.sub_title = request.POST.get('sub_title', work.sub_title).strip()
                    work.architecture_stack = request.POST.get('stack', work.architecture_stack).strip()
                    work.live_deployment = request.POST.get('live_url', '').strip()
                    work.source_repository = request.POST.get('source_repository', '').strip()
                    work.system_status = request.POST.get('system_status', work.system_status).strip()
                    work.detailed_scope = request.POST.get('detailed_scope', work.detailed_scope).strip()
                    work.save()
                    messages.success(request, f"DEPLOYMENT REFRESHED: Project '{work.title}' updated successfully.")
                    return redirect('dashboard')

            elif action == 'delete_project':
                proj_id = request.POST.get('project_id')
                ProductionWork.objects.filter(pk=proj_id).delete()
                messages.success(request, "DEPLOYMENT DECOMMISSIONED: Project removed from Production Vault.")
                return redirect('dashboard')

        if action == 'update_profile':
            new_identity = request.POST.get('full_identity', '').strip()
            new_org = request.POST.get('associated_organization', '').strip()
            new_phone = request.POST.get('phone_number', '').strip()
            new_spec = request.POST.get('specialization', '').strip()
            new_scope = request.POST.get('collaboration_scope', '').strip()
            new_github = request.POST.get('github_link', '').strip()
            new_live = request.POST.get('live_link', '').strip()
            remove_photo = request.POST.get('remove_photo') == '1'
            
            if new_identity:
                ticket.full_identity = new_identity
            if new_org:
                ticket.associated_organization = new_org
            ticket.phone_number = new_phone
            if new_spec:
                ticket.specialization = new_spec
            if new_scope:
                ticket.collaboration_scope = new_scope
            ticket.github_link = new_github
            ticket.live_link = new_live

            # Handle profile photo upload
            if remove_photo:
                if ticket.profile_photo:
                    try:
                        ticket.profile_photo.delete(save=False)
                    except Exception:
                        pass
                ticket.profile_photo = None
                ticket.profile_photo_url = ''
            elif 'profile_photo' in request.FILES:
                photo = request.FILES['profile_photo']
                allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if photo.content_type in allowed and photo.size <= 5 * 1024 * 1024:
                    if ticket.profile_photo:
                        try:
                            ticket.profile_photo.delete(save=False)
                        except Exception:
                            pass
                    ticket.profile_photo = photo
                else:
                    messages.error(request, "UPLOAD ERROR: Use JPG/PNG/WEBP image under 5 MB.")
                    return redirect('dashboard')

            ticket.save()
            messages.success(request, "PROFILE RE-CONFIGURED: Node telemetry and profile data updated successfully.")
            return redirect('dashboard')
            
        elif action == 'change_password':
            old_pwd = request.POST.get('old_password', '')
            new_pwd = request.POST.get('new_password', '')
            confirm_pwd = request.POST.get('confirm_password', '')
            
            if not check_password(old_pwd, ticket.password or ''):
                messages.error(request, "SECURITY ALERT: Current password verification failed.")
            elif len(new_pwd) < 6:
                messages.error(request, "SECURITY ALERT: New password must be at least 6 characters.")
            elif new_pwd != confirm_pwd:
                messages.error(request, "SECURITY ALERT: New password and confirmation do not match.")
            else:
                ticket.password = make_password(new_pwd)
                ticket.save(update_fields=['password'])
                if ticket.is_superadmin:
                    try:
                        u = User.objects.get(username=ticket.username)
                        u.set_password(new_pwd)
                        u.save()
                    except User.DoesNotExist:
                        pass
                messages.success(request, "SECURITY PROTOCOL UPDATED: Access credentials successfully changed.")
            return redirect('dashboard')
            
        elif action == 'send_inquiry':
            msg_text = request.POST.get('message', '').strip()
            subject = request.POST.get('subject', 'Project Proposal').strip()
            if not msg_text:
                messages.error(request, "TRANSMISSION ERROR: Message content cannot be empty.")
            else:
                full_msg = f"[{subject.upper()}] {msg_text}"
                ContactMessage.objects.create(
                    name=f"{ticket.full_identity} (@{ticket.username})",
                    email=ticket.secure_email,
                    message=full_msg,
                )
                messages.success(request, "TRANSMISSION CONFIRMED: Your message was securely routed to David Osano's terminal.")
            return redirect('dashboard')

    user_messages = ContactMessage.objects.filter(email=ticket.secure_email).order_by('-received_at')[:5]
    all_projects = ProductionWork.objects.all().order_by('-id') if ticket.is_superadmin else None
    all_messages = ContactMessage.objects.all().order_by('-received_at')[:10] if ticket.is_superadmin else None
    all_tickets = NetworkRegistryTicket.objects.all().order_by('-registered_at')[:10] if ticket.is_superadmin else None

    context = {
        'ticket': ticket,
        'user_messages': user_messages,
        'works_count': ProductionWork.objects.count(),
        'services_count': CoreService.objects.count(),
        'all_projects': all_projects,
        'all_messages': all_messages,
        'all_tickets': all_tickets,
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    if 'ticket_id' in request.session:
        del request.session['ticket_id']
    messages.info(request, "Session closed. Connection terminated.")
    return redirect('login')
