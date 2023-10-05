from django.urls import path, re_path
from .views import *
# from . import views
urlpatterns = [
    # Courses
    path('signup/', SignUp.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('verify_otp/', VerifyOTP.as_view(), name='verify-otp'),
    path('client/', Client.as_view(), name='client'),
    
    # re_path(r'^.*$',views.other_url),
    
    
    
]