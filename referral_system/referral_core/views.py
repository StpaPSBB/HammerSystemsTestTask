from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.contrib.sessions.backends.db import SessionStore
from django.core.validators import RegexValidator
import random
import time
import re
from .models import User

User = get_user_model()

class AuthView(APIView):
    """
    Validates phone number and sends sms code.
    """
    permission_classes=[AllowAny]
    renderer_classes=[JSONRenderer, TemplateHTMLRenderer]
    template_name='auth.html'

    def get(self, response):
        return Response({})
    
    def post(self, request):

        phone_number = request.data.get('phone_number')
        context = {}
        if not phone_number:
            return Response({"error": "Phone number required"},
                             status=status.HTTP_404_NOT_FOUND)
        
        phone_pattern = r'^\+\d{9,15}$'
        if not re.match(phone_pattern, phone_number):
            return Response({"error": "Phone number must be in international format (e.g. +79991234567)"},
                             status=400)
        
        request.session['verification_phone'] = phone_number
        request.session.save()
        
        time.sleep(random.uniform(1, 2))
        return Response({"message": "Code sent"}, status=200)


class VerifyView(APIView):
    """
    Verifies code and creates/authorizes user.
    """
    permission_classes=[AllowAny]
    renderer_classes=[JSONRenderer, TemplateHTMLRenderer]
    template_name='verify.html'

    def get(self, response):
        return Response({})
    
    def post(self, request):
        phone_number = request.session.get('verification_phone')
        context = {}
        if not phone_number:
            return Response(
                {"error": "Phone number required"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        code = request.data.get('code')
        if not code or len(code) != 4 or not code.isdigit():
            return Response(
                {"error": "Incorrect verification code format"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user, created = User.objects.get_or_create(phone_number=phone_number)
        login(request, user)
        if 'verification_phone' in request.session:
            del request.session['verification_phone']

        return Response({
            "message": "Authenticated",
            "invite_code": user.self_invite_code
        }, status=200)


class ProfileView(APIView):
    """
    Lists referrals and shows profile.
    """
    permission_classes=[IsAuthenticated]
    renderer_classes=[JSONRenderer, TemplateHTMLRenderer]
    template_name='profile.html'

    def get(self, request):

        referrals = User.objects.filter(
            activated_invite_code=request.user.self_invite_code
        ).values('phone_number')

        return Response(
            {
                "phone_number": request.user.phone_number,
                "invite_code": request.user.self_invite_code,
                "activated_invite_code": request.user.activated_invite_code,
                "referrals": list(referrals)
            },
            status=status.HTTP_200_OK
        )
    
    def post(self, request):

        new_code = request.data.get('invite_code')

        if new_code == request.user.self_invite_code:
            return Response(
                {"error": "You can't activate your own invite code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.activated_invite_code:
            return Response(
                {"error": "You can activate only one invite code"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not new_code or len(new_code) != 6:
            return Response(
                {"error": "Incorrect invite code format"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not User.objects.filter(self_invite_code=new_code).exists():
            return Response(
                {"error": "Invite code doesn't exists"},
                status=status.HTTP_404_NOT_FOUND
            )

        request.user.activated_invite_code = new_code
        request.user.save()

        return Response(
            {
                "status": "Code successfully activated",
                "activated_invite_code": new_code
            },
            status=status.HTTP_200_OK
        )