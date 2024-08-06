from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('train/', views.train, name='train'),
    path('students/', views.student_list, name='student_list'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('stop_camera/', views.stop_camera, name='stop_camera'),
    path('detected_student_info/', views.detected_student_info, name='detected_student_info'),
    path('main/', views.main_page, name='main_page'),
]
