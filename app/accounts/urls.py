from accounts.views import TokenRefreshAndAccessView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("api/auth/sign-in", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh", TokenRefreshAndAccessView.as_view(), name="token_refresh"),
]
