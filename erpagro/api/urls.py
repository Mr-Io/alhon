"""
URL configuration for erpagro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from .import views

app_name="api"
urlpatterns = [
    path("suppliers/", views.supplier_list, name="supplier-list"),
    path("suppliers/<int:pk>/", views.supplier_detail, name="supplier-detail"),
    path("warehouses/<int:pk>/", views.warehouse_detail, name="warehouse-detail"),
    path("agrofoodtypes/<int:pk>/", views.agrofoodtype_detail, name="agrofoodtype-detail"),
    path("carriers/<int:pk>/", views.carrier_detail, name="carrier-detail"),
    path("entries/<int:pk>/", views.entry_detail, name="entry-detail"),
    path("exits/", views.exit_list, name="exit-list"),
    path("exits/<int:pk>/", views.exit_detail, name="exit-detail"),
]