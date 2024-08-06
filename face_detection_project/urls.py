from django.contrib import admin
from django.urls import path, include
from detection import views  # Import views from the detection app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page, name='home'),  # Set the main page at the root URL
    path('detection/', include('detection.urls')),  # Include URLs from the detection app
]
