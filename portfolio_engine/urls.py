from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('capabilities/', views.capabilities_view, name='capabilities'),
    path('vault/', views.vault_view, name='vault'),
    path('contact/', views.contact_view, name='contact'),
    path('send-sms/', views.send_sms_view, name='send_sms'),
    path('github/', views.github_gateway_view, name='github_gateway'),
    path('registry/', views.registry_view, name='registry'),
    path('login/', views.login_view, name='login'),
    path('root-terminal/', views.admin_login_view, name='admin_login'),

    # New connection endpoints
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]

