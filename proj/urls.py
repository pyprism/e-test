"""proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from base import views as base
from recipe import views as recipe

router = routers.DefaultRouter()
router.register('account', base.AccountViewSet)
router.register('restaurant', recipe.RestaurantViewSet)
router.register('menu', recipe.MenuViewSet)
router.register('vote', recipe.VoteViewSet)
router.register('vote_result', recipe.VoteResultViewSet, basename='vote_result')

urlpatterns = [
    path('v1/api/', include(router.urls), name='api'),
    path('v1/api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('', RedirectView.as_view(url='/v1/api/', permanent=False), name='index')
]
