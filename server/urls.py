from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('savings.urls')),
    path('api/', include('transactions.urls')),
    path('api/', include('bills.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
