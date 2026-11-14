from django.apps import AppConfig
from django.db.models.signals import post_migrate


def auto_provision_superadmin(sender, **kwargs):
    """
    Ensures root superadmin accounts exist on every environment
    whenever database migrations run.
    """
    if sender.name == 'portfolio_engine':
        from django.core.management import call_command
        try:
            call_command('setup_superadmin')
        except Exception:
            pass


class PortfolioEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio_engine'

    def ready(self):
        post_migrate.connect(auto_provision_superadmin, sender=self)
