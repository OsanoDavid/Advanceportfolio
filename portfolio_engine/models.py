from django.db import models

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
    
    # New Software Development Customizations
    specialization = models.CharField(
        max_length=50, 
        choices=[
            ('frontend', 'Frontend'),
            ('backend', 'Backend'),
            ('database', 'Database'),
            ('middleware', 'Middleware')
        ],
        default='backend'
    )
    
    # Portal Credentials 
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True) # Standard password character length limit
    
    # Profile & Identity Fields
    phone_number = models.CharField(max_length=40, blank=True, default='')
    id_number = models.CharField(max_length=50, blank=True, default='')
    reg_number = models.CharField(max_length=50, blank=True, default='')
    gender = models.CharField(max_length=30, blank=True, default='')
    github_link = models.URLField(blank=True, default='')
    live_link = models.URLField(blank=True, default='')
    
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket from {self.full_identity} ({self.get_specialization_display()})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField(max_length=5000)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        return f"Message from {self.name} ({self.received_at:%Y-%m-%d})"
