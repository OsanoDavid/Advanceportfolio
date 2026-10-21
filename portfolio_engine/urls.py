from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('capabilities/', views.capabilities_view, name='capabilities'),
    path('vault/', views.vault_view, name='vault'),
    path('registry/', views.registry_view, name='registry'),
    path('login/', views.login_view, name='login'),
    
    # New connection endpoints
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
