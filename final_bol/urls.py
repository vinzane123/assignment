from django.contrib import admin
from boloo_app import views
from boloo_app.admin import *
from rest_framework import routers
from django.urls import path,include
from rest_framework.urlpatterns import format_suffix_patterns
admin.autodiscover()

router = routers.DefaultRouter()
router.register('items',views.ItemsView,basename='items')
router.register('token',views.TokenView,basename='token')
router.register('sync',views.SyncItems,basename='sync')         

urlpatterns = [
    path('admin/', admin.site.urls),
    path('getShipments/',views.list_items),
    path('',include(router.urls)),
]