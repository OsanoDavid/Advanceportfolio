import os

print("⚡ Initializing compilation of the Advanced Cyberpunk Portfolio System...")

# Define rigid directory layout with unique app name 'portfolio_engine'
structure = {
    "portfolio_backend": ["__init__.py", "settings.py", "urls.py", "wsgi.py", "asgi.py"],
    "portfolio_engine": ["__init__.py", "admin.py", "apps.py", "models.py", "views.py", "urls.py"],
    "templates": ["base.html", "index.html", "capabilities.html", "vault.html", "registry.html"],
    "static/css": ["cyberpunk.css"],
    "static/js": ["engine.js"],
    "static/images": []
}

for folder, files in structure.items():
    os.makedirs(folder, exist_ok=True)
    for file in files:
        with open(os.path.join(folder, file), "w", encoding="utf-8") as f:
            f.write("")

# 1. Root manage.py file
with open("manage.py", "w", encoding="utf-8") as f:
    f.write("""#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""")

# 2. Master settings.py
with open("portfolio_backend/settings.py", "w", encoding="utf-8") as f:
    f.write("""import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-quantum-neon-encryption-key-2026'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'portfolio_engine',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portfolio_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'portfolio_backend.wsgi.application'
ASGI_APPLICATION = 'portfolio_backend.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'production_vault.sqlite3',
    }
}

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
""")

# 3. WSGI & ASGI configs
with open("portfolio_backend/wsgi.py", "w", encoding="utf-8") as f:
    f.write("import os\nfrom django.core.wsgi import get_wsgi_application\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_backend.settings')\napplication = get_wsgi_application()\n")
with open("portfolio_backend/asgi.py", "w", encoding="utf-8") as f:
    f.write("import os\nfrom django.core.asgi import get_asgi_application\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_backend.settings')\napplication = get_asgi_application()\n")

# 4. Core Routing Architecture
with open("portfolio_backend/urls.py", "w", encoding="utf-8") as f:
    f.write("""from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portfolio_engine.urls')),
]
""")

with open("portfolio_engine/urls.py", "w", encoding="utf-8") as f:
    f.write("""from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('capabilities/', views.capabilities_view, name='capabilities'),
    path('vault/', views.vault_view, name='vault'),
    path('registry/', views.registry_view, name='registry'),
]
""")

# 5. Apps Config
with open("portfolio_engine/apps.py", "w", encoding="utf-8") as f:
    f.write("""from django.apps import AppConfig
class PortfolioEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio_engine'
""")

# 6. Secure Database Models
with open("portfolio_engine/models.py", "w", encoding="utf-8") as f:
    f.write("""from django.db import models

class ProductionWork(models.Model):
    title = models.CharField(max_length=250)
    sub_title = models.CharField(max_length=200, blank=True)
    architecture_stack = models.CharField(max_length=400, help_text="e.g., Spring Boot, Java, MySQL, Docker")
    detailed_scope = models.TextField()
    source_repository = models.URLField(blank=True)
    live_deployment = models.URLField(blank=True)
    completion_date = models.DateField(blank=True, null=True)
    system_status = models.CharField(max_length=50, default="Operational")

    def __str__(self):
        return f"{self.title} -> {self.system_status}"

class CoreService(models.Model):
    system_name = models.CharField(max_length=150)
    operational_capability = models.TextField()
    glowing_accent_color = models.CharField(max_length=7, default="#00f2fe")

    def __str__(self):
        return self.system_name

class NetworkRegistryTicket(models.Model):
    full_identity = models.CharField(max_length=180)
    secure_email = models.EmailField()
    associated_organization = models.CharField(max_length=250, blank=True)
    collaboration_scope = models.TextField()
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket from {self.full_identity}"
""")

# 7. View Controllers
with open("portfolio_engine/views.py", "w", encoding="utf-8") as f:
    f.write("""from django.shortcuts import render, redirect
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
        org = request.POST.get('org')
        scope = request.POST.get('scope')
        
        NetworkRegistryTicket.objects.create(
            full_identity=identity, secure_email=email,
            associated_organization=org, collaboration_scope=scope
        )
        messages.success(request, "CRITICAL UPDATE: Collaboration ticket successfully committed to the database.")
        return redirect('registry')
    return render(request, 'registry.html')
""")

# 8. Admin Integration Panel
with open("portfolio_engine/admin.py", "w", encoding="utf-8") as f:
    f.write("""from django.contrib import admin
from .models import ProductionWork, CoreService, NetworkRegistryTicket

admin.site.register(ProductionWork)
admin.site.register(CoreService)
admin.site.register(NetworkRegistryTicket)
""")

# 9. Cyberpunk Layout Stylesheet (Separated CSS)
with open("static/css/cyberpunk.css", "w", encoding="utf-8") as f:
    f.write("""* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Courier New', Courier, monospace; }
body { background-color: #020204; color: #f8fafc; overflow-x: hidden; min-height: 100vh; }

#system-loader {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: #020204; z-index: 10000; display: flex; justify-content: center; align-items: center;
    transition: opacity 0.4s ease, visibility 0.4s;
}
.loader-spinner {
    width: 80px; height: 80px; border: 4px solid transparent;
    border-top-color: #00f2fe; border-right-color: #ff007f; border-bottom-color: #9d4edd;
    border-radius: 50%; animation: velocity-spin 0.7s linear infinite;
    box-shadow: 0 0 30px rgba(0, 242, 254, 0.3);
}
@keyframes velocity-spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

navbar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1.8rem 8%; background: rgba(2, 2, 4, 0.95);
    backdrop-filter: blur(15px); position: sticky; top: 0; z-index: 500;
    border-bottom: 2px solid rgba(157, 78, 221, 0.25);
}
.brand-engine { font-size: 1.8rem; font-weight: 900; color: #00f2fe; text-shadow: 0 0 15px #00f2fe; }
.nav-grid { display: flex; list-style: none; gap: 3rem; }
.nav-grid a { color: #94a3b8; text-decoration: none; font-weight: bold; font-size: 1.05rem; transition: 0.3s; }
.nav-grid a:hover { color: #ff007f; text-shadow: 0 0 12px #ff007f; }

.wrapper { max-width: 1300px; margin: 4rem auto; padding: 0 3rem; }
.terminal-hero { display: flex; align-items: center; justify-content: space-between; min-height: 65vh; gap: 4rem; }
.hero-header h1 { font-size: 4rem; font-weight: 900; text-transform: uppercase; line-height: 1.1; }
.hero-header span { color: #ff007f; text-shadow: 0 0 25px #ff007f; }
.identity-vault {
    width: 320px; height: 320px; border-radius: 16px; border: 3px solid #00f2fe;
    background: #080810; display: flex; justify-content: center; align-items: center;
    box-shadow: 0 0 35px rgba(0, 242, 254, 0.25); overflow: hidden; position: relative;
}

.metrics-row { display: flex; gap: 2.5rem; margin-top: 3rem; }
.metric-node { background: #06060c; border-left: 4px solid #9d4edd; padding: 1rem 2rem; border-radius: 0 8px 8px 0; }
.metric-node h4 { font-size: 2rem; color: #fff; text-shadow: 0 0 10px #9d4edd; }

.layout-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 3rem; }
.neon-card {
    background: #06060c; border: 1px solid rgba(0, 242, 254, 0.15);
    padding: 3rem; border-radius: 14px; transition: 0.35s cubic-bezier(0.25, 1, 0.5, 1);
}
.neon-card:hover { 
    transform: translateY(-8px); border-color: #ff007f; 
    box-shadow: 0 0 35px rgba(255, 0, 127, 0.35); 
}

.interactive-btn {
    display: inline-block; padding: 1rem 2.5rem; border-radius: 4px;
    background: transparent; border: 2px solid #00f2fe; color: #fff;
    font-weight: bold; text-decoration: none; text-transform: uppercase; cursor: pointer; transition: 0.3s;
}
.interactive-btn:hover { background: #00f2fe; color: #000; box-shadow: 0 0 25px #00f2fe; }
.input-field {
    width: 100%; padding: 1rem; background: #090915; border: 1px solid #1e293b;
    color: #fff; margin: 0.8rem 0 1.5rem 0; border-radius: 4px; font-family: monospace;
}
.input-field:focus { border-color: #9d4edd; outline: none; box-shadow: 0 0 15px rgba(157, 78, 221, 0.4); }
""")

# 10. Loading Engine JavaScript (Separated JS)
with open("static/js/engine.js", "w", encoding="utf-8") as f:
    f.write("""window.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('system-loader');
    setTimeout(() => {
        loader.style.opacity = '0';
        setTimeout(() => { loader.style.visibility = 'hidden'; }, 400);
    }, 300);
});""")

# 11. HTML Architecture Engine Layouts
with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write("""{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum System Infrastructure Portfolio</title>
    <link rel="stylesheet" href="{% static 'css/cyberpunk.css' %}">
</head>
<body>
    <div id="system-loader"><div class="loader-spinner"></div></div>
    <navbar>
        <div class="brand-engine">CORE_NODE//</div>
        <ul class="nav-grid">
            <li><a href="{% url 'index' %}">System Status</a></li>
            <li><a href="{% url 'capabilities' %}">Capabilities</a></li>
            <li><a href="{% url 'vault' %}">Production Vault</a></li>
            <li><a href="{% url 'registry' %}">Network Registry</a></li>
        </ul>
    </navbar>
    {% block master_content %}{% endblock %}
    <script src="{% static 'js/engine.js' %}"></script>
</body>
</html>
""")

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write("""{% extends 'base.html' %}
{% block master_content %}
<div class="wrapper">
    <div class="terminal-hero">
        <div class="hero-header">
            <h1>Engineered For <br><span>Maximum Impact</span></h1>
            <p style="color: #64748b; font-size: 1.2rem; margin: 2rem 0; max-width: 650px; line-height: 1.7;">
                Architecting state-of-the-art backend processing infrastructures, structural database migrations, and high-performance systemic automations. Turn operational data logs into client solutions.
            </p>
            <div style="margin-bottom: 2rem; border-left: 2px solid #00f2fe; padding-left: 1.5rem;">
                <p style="color: #00f2fe; margin-bottom: 0.5rem;">📡 Secure Signal: <span style="color:#fff;">+254 7XX XXX XXX</span></p>
                <p style="color: #9d4edd;">💻 Main Branches: <a href="#" style="color:#fff;">GitHub</a> | <a href="#" style="color:#fff;">LinkedIn</a></p>
            </div>
            <div class="metrics-row">
                <div class="metric-node"><h4>{{ project_count }}</h4><p style="color:#64748b;">Deployments</p></div>
                <div class="metric-node"><h4>{{ service_count }}</h4><p style="color:#64748b;">Core Modules</p></div>
                <div class="metric-node"><h4>{{ ticket_count }}</h4><p style="color:#64748b;">Cleared Leads</p></div>
            </div>
        </div>
        <div class="identity-vault">
            <span style="color: #334155; font-style: italic;">[ drop profile.jpg in static/images/ ]</span>
        </div>
    </div>
</div>
{% endblock %}
""")

with open("templates/capabilities.html", "w", encoding="utf-8") as f:
    f.write("""{% extends 'base.html' %}
{% block master_content %}
<div class="wrapper">
    <h2 style="font-size: 2.5rem; text-transform: uppercase; margin-bottom: 3rem; text-align: center;">Operational <span style="color:#00f2fe;">Capabilities</span></h2>
    <div class="layout-grid">
        {% for service in services %}
        <div class="neon-card" style="border-left: 5px solid {{ service.glowing_accent_color }};">
            <h3 style="color: #fff; margin-bottom: 1rem; text-transform: uppercase;">{{ service.system_name }}</h3>
            <p style="color: #94a3b8; line-height: 1.7;">{{ service.operational_capability }}</p>
        </div>
        {% empty %}
        <div class="neon-card" style="grid-column: 1/-1; border-left: 4px solid #ff007f;">
            <h3 style="color:#ff007f;">No core modules loaded</h3>
            <p style="color:#64748b; margin-top: 1rem;">Access the database gateway at <code>/admin</code> to dynamically inject structural capabilities.</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
""")

with open("templates/vault.html", "w", encoding="utf-8") as f:
    f.write("""{% extends 'base.html' %}
{% block master_content %}
<div class="wrapper">
    <h2 style="font-size: 2.5rem; text-transform: uppercase; margin-bottom: 3rem; text-align: center;">Production <span style="color:#9d4edd;">Vault</span></h2>
    <div class="layout-grid">
        {% for work in works %}
        <div class="neon-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <h3 style="color:#00f2fe; text-transform:uppercase;">{{ work.title }}</h3>
                <span style="background:rgba(0,242,254,0.1); color:#00f2fe; padding:0.3rem 0.8rem; font-size:0.8rem; border-radius:4px; font-weight:bold;">{{ work.system_status }}</span>
            </div>
            <p style="color:#ff007f; font-size:0.85rem; font-weight:bold; margin: 0.6rem 0 1.5rem 0;">{{ work.architecture_stack }}</p>
            <p style="color:#94a3b8; line-height: 1.6; margin-bottom: 2rem;">{{ work.detailed_scope }}</p>
            {% if work.source_repository %}<a href="{{ work.source_repository }}" class="interactive-btn" style="padding:0.6rem 1.5rem; font-size:0.85rem;">Source Code</a>{% endif %}
        </div>
        {% empty %}
        <div class="neon-card" style="grid-column: 1/-1; text-align: center;">
            <p style="color:#64748b;">The code vault is empty. Authenticate via the Django Admin to sync your active project deployments.</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
""")

with open("templates/registry.html", "w", encoding="utf-8") as f:
    f.write("""{% extends 'base.html' %}
{% block master_content %}
<div class="wrapper" style="max-width: 700px;">
    <h2 style="font-size: 2.5rem; text-transform: uppercase; margin-bottom: 1rem; text-align: center;">Network <span style="color:#ff007f;">Registry</span></h2>
    <p style="color:#64748b; text-align:center; margin-bottom: 4rem;">Securely submit enterprise communication routing requests below to unlock developer code branches.</p>
    
    {% if messages %}
        {% for message in messages %}
            <div style="padding: 1.2rem; background: rgba(0, 242, 254, 0.1); border: 2px solid #00f2fe; color: #fff; border-radius: 4px; margin-bottom: 2rem; font-weight: bold;">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}

    <div class="neon-card">
        <form method="POST">
            {% csrf_token %}
            <label style="color:#00f2fe; font-weight: bold;">Full Name / System Identity</label>
            <input type="text" name="identity" class="input-field" required placeholder="e.g., Lead Architect">
            
            <label style="color:#9d4edd; font-weight: bold;">Communication Relay Email</label>
            <input type="email" name="email" class="input-field" required placeholder="e.g., tech@firm.com">
            
            <label style="color:#ff007f; font-weight: bold;">Organization Context</label>
            <input type="text" name="org" class="input-field" placeholder="Optional">
            
            <label style="color:#fff; font-weight: bold;">System Scope Specification</label>
            <textarea name="scope" class="input-field" rows="5" required placeholder="Specify your architectural requirements..."></textarea>
            
            <button type="submit" class="interactive-btn" style="width: 100%; margin-top: 1rem;">Commit Token Registry Entry</button>
        </form>
    </div>
</div>
{% endblock %}
""")

print("🚀 Complete system compiled flawlessly without relying on conflicting Django commands!")