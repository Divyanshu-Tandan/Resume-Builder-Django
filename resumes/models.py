from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # Add this import

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    personal_info = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    certificates = models.TextField(null=True, blank=True)
    projects = models.TextField(blank=True)
    section_order = models.TextField(default='["title", "full_name", "email", "phone", "address", "summary", "education", "experience", "skills"]')
    created_at = models.DateTimeField(auto_now_add=True)  # Set to auto-populate on creation
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or 'Untitled Resume'