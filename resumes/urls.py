from django.urls import path
from . import views

urlpatterns = [
    path('', views.resume_list, name='resume_list'),
    path('create/', views.create_resume, name='create_resume'),
    path('edit/<int:pk>/', views.edit_resume, name='edit_resume'),
    path('detail/<int:pk>/', views.resume_detail, name='resume_detail'),
    path('pdf/<int:pk>/', views.generate_resume_pdf, name='generate_resume_pdf'),
    path('delete/<int:pk>/', views.delete_resume, name='delete_resume'),
]