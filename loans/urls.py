from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', ObtainAuthToken.as_view(), name='login'),
    path('loans/apply/', views.apply_loan, name='apply-loan'),
    path('loans/my/', views.my_loans, name='my-loans'),
    path('loans/<int:pk>/status/', views.update_loan_status, name='update-loan-status'),
    path('loans/flagged/', views.flagged_loans, name='flagged-loans'),
]
