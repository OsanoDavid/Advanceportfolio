from django.contrib import admin
from .models import ContactMessage, ProductionWork, CoreService, NetworkRegistryTicket

admin.site.register(ProductionWork)
admin.site.register(CoreService)
admin.site.register(NetworkRegistryTicket)
admin.site.register(ContactMessage)
