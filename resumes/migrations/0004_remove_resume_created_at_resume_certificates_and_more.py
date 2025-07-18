# Generated by Django 5.2.3 on 2025-07-02 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0003_resume_summary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resume',
            name='created_at',
        ),
        migrations.AddField(
            model_name='resume',
            name='certificates',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='projects',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='section_order',
            field=models.TextField(default='["title", "email", "phone", "address", "summary", "education", "experience", "skills"]'),
        ),
        migrations.AlterField(
            model_name='resume',
            name='full_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='resume',
            name='title',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
