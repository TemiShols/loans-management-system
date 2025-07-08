from django.contrib import admin
from .models import LoanApplication, FraudFlag


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount_requested', 'purpose', 'status', 'date_applied')
    list_filter = ('status', 'date_applied')
    search_fields = ('user__username', 'purpose', 'status')
    autocomplete_fields = ['user']


@admin.register(FraudFlag)
class FraudFlagAdmin(admin.ModelAdmin):
    list_display = ('id', 'loan_application', 'reason', 'created_at')
    list_filter = ('reason',)
    search_fields = ('loan_application__user__username', 'reason')
