from django.urls import path
from . import views

urlpatterns = [
    path('', views.dhcp_request, name='dhcp_request'),
    path('leases/', views.view_leases, name='view_leases'),
]