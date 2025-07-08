from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import LoanApplication, FraudFlag
from .serializers import RegisterSerializer, LoanApplicationSerializer


@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_loan(request):
    serializer = LoanApplicationSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        amount = serializer.validated_data['amount_requested']
        domain = user.email.split('@')[-1]
        now = timezone.now()

        recent_loans = LoanApplication.objects.filter(
            user=user,
            date_applied__gte=now - timezone.timedelta(hours=24)
        ).count()

        same_domain_users = User.objects.filter(email__iendswith=f"@{domain}").count()

        loan = serializer.save(user=user, status='pending')
        reasons = []

        if recent_loans > 3:
            FraudFlag.objects.create(loan_application=loan, reason="More than 3 loans in 24 hours")
            reasons.append("More than 3 loans in 24 hours")

        if amount > 5_000_000:
            FraudFlag.objects.create(loan_application=loan, reason="High loan amount > NGN 5,000,000")
            reasons.append("High loan amount")

        if same_domain_users > 10:
            FraudFlag.objects.create(loan_application=loan, reason="Email domain used by > 10 users")
            reasons.append("Email domain suspicious")

        if reasons:
            loan.status = 'flagged'
            loan.save()


            send_mail(
                subject='[ALERT] Fraudulent Loan Detected',
                message=f"Loan ID {loan.id} flagged. Reasons:\n" + "\n".join(reasons),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True
            )

        return Response(LoanApplicationSerializer(loan).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_loans(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-date_applied')
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(loans, request)
    serializer = LoanApplicationSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_loan_status(request, pk):
    try:
        loan = LoanApplication.objects.get(pk=pk)
    except LoanApplication.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)

    status_input = request.data.get('status')
    if status_input not in ['approved', 'rejected', 'flagged']:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    loan.status = status_input
    loan.save()
    return Response({'message': f'Loan status updated to {status_input}'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def flagged_loans(request):
    loans = LoanApplication.objects.filter(status='flagged').order_by('-date_applied')
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(loans, request)
    serializer = LoanApplicationSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)
