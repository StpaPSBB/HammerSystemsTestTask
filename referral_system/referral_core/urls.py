from django.urls import path
from .views import AuthView, VerifyView, ProfileView, LogoutAPIView

urlpatterns = [
    path('auth/', AuthView.as_view(), name='auth'),
    path('verify/', VerifyView.as_view(), name='verify'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutAPIView.as_view(), name='logout')
]