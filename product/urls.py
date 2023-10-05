from django.urls import path, re_path
from .views import *
from . import views
urlpatterns = [
    # Courses
    path('create_product/', CreateProduct.as_view(), name='create-product'),
    path('purchase_product/', PurchaseProduct.as_view(), name='purchase_product'),
    re_path(r'^.*$',views.other_url),
    
]