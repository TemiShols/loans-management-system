from rest_framework import serializers
from django.contrib.auth.models import User
from .models import LoanApplication, FraudFlag
from rest_framework.validators import UniqueValidator


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class FraudFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudFlag
        fields = ['id', 'reason', 'created_at']


class LoanApplicationSerializer(serializers.ModelSerializer):
    fraud_flags = FraudFlagSerializer(many=True, read_only=True)

    class Meta:
        model = LoanApplication
        fields = ['id', 'amount_requested', 'purpose', 'status', 'date_applied', 'fraud_flags']


