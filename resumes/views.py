from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import ResumeForm
from .models import Resume
import pdfkit
import logging
import os
import json

# Set up logging
logger = logging.getLogger(__name__)

# Configure wkhtmltopdf path
WKHTMLTOPDF_PATH = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"  # Confirm this path
pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

@login_required
def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            return redirect('resume_list')
    else:
        form = ResumeForm()
        if 'section_order' in form.fields:
            form.fields['section_order'].initial = ["title", "full_name", "email", "phone", "address", "summary", "education", "experience", "skills"]
        for field in form.fields:
            if field != 'section_order':
                form.fields[field].widget.attrs.pop('style', None)
    return render(request, 'resume_form.html', {'form': form})

@login_required
def edit_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            return redirect('resume_detail', pk=pk)
    else:
        form = ResumeForm(instance=resume)
        if 'section_order' in form.fields:
            form.fields['section_order'].initial = json.loads(resume.section_order) if resume.section_order else ["title", "full_name", "email", "phone", "address", "summary", "education", "experience", "skills"]
    return render(request, 'resume_form.html', {'form': form})

@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'resume_list.html', {'resumes': resumes})

@login_required
def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    return render(request, 'resume_detail.html', {'resume': resume})

@login_required
def generate_resume_pdf(request, pk):
    try:
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        logger.debug(f"Generating PDF for resume ID: {resume.id}, Full Name: {resume.full_name}")

        # Parse section order with default value if missing
        section_order = json.loads(resume.section_order) if resume.section_order else ["title", "full_name", "email", "phone", "address", "summary", "education", "experience", "skills"]

        # HTML content with dynamic order and consistent styling
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Helvetica', 'Arial', sans-serif;
                    color: #333;
                    padding: 0.2in;
                    font-size: 12pt;
                    background-color: #fff;
                    line-height: 1.5;
                    max-width: 8.5in;
                    margin: 0 auto;
                }}
                .resume-title {{
                    text-transform: uppercase;
                    font-weight: 700;
                }}
                h3 {{
                    font-weight: bold;
                    color: #2c3e50;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 3pt;
                    font-size: 14pt;
                }}
                p {{
                    margin: 4pt 0;
                    font-weight: 500;
                }}
                pre {{
                    margin: 0;
                    white-space: pre-wrap;
                    word-break: break-word;
                    font-weight: 700;
                    background-color: #f1f1f1;
                    padding: 4pt;
                    border-radius: 2pt;
                    font-size: 10pt;
                }}
                @media print {{
                    body {{
                        padding: 0.1in;
                    }}
                    h3 {{
                        font-size: 12pt;
                    }}
                    pre {{
                        font-size: 9pt;
                    }}
                }}
            </style>
        </head>
        <body>
        """
        for section in section_order:
            if section == 'title':
                html_content += f"<h3 class='resume-title'>{resume.title or 'Untitled Resume'}</h3>"
            elif section == 'full_name':
                html_content += f"<p><strong>Full Name:</strong> {resume.full_name or 'Not provided'}</p>"
            elif section == 'email':
                html_content += f"<p><strong>Email:</strong> {resume.email or 'Not provided'}</p>"
            elif section == 'phone':
                html_content += f"<p><strong>Phone:</strong> {resume.phone or 'Not provided'}</p>"
            elif section == 'address':
                html_content += f"<p><strong>Address:</strong> <pre>{resume.address or 'Not provided'}</pre></p>"
            elif section == 'personal_info':
                html_content += f"<h3>Personal Information:</h3><p><pre>{resume.personal_info or 'No personal info provided'}</pre></p>"
            elif section == 'summary':
                html_content += f"<h3>Summary:</h3><p><pre>{resume.summary or 'No summary provided'}</pre></p>"
            elif section == 'education':
                html_content += f"<h3>Education:</h3><p><pre>{resume.education or 'No education provided'}</pre></p>"
            elif section == 'experience':
                html_content += f"<h3>Experience:</h3><p><pre>{resume.experience or 'No experience provided'}</pre></p>"
            elif section == 'skills':
                html_content += f"<h3>Skills:</h3><p><pre>{resume.skills or 'No skills provided'}</pre></p>"
            elif section == 'certificates':
                html_content += f"<h3>Certificates:</h3><p><pre>{resume.certificates or 'No certificates provided'}</pre></p>"
            elif section == 'projects':
                html_content += f"<h3>Projects:</h3><p><pre>{resume.projects or 'No projects provided'}</pre></p>"
        html_content += "</body></html>"

        # Debug: Log HTML content length and sample
        logger.debug(f"HTML Content Length: {len(html_content)}")
        logger.debug(f"HTML Content Sample: {html_content[:500]}...")

        # Configure pdfkit options
        options = {
            'margin-top': '0.25in',
            'margin-right': '0.25in',
            'margin-bottom': '0.25in',
            'margin-left': '0.25in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
            'quiet': None,
            'debug-javascript': None,
            'page-size': 'Letter',
            'dpi': 300
        }

        # Generate PDF
        pdf = pdfkit.from_string(html_content, False, options=options, configuration=pdfkit_config)
        logger.debug(f"PDF Length: {len(pdf)} bytes")

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resume_{resume.id}.pdf"'
        return response

    except Exception as e:
        logger.error(f"Error generating PDF for resume ID {pk}: {str(e)}")
        return HttpResponse(f"Error generating PDF: {str(e)}. Ensure wkhtmltopdf is installed and path is correct.", status=500)

@login_required
def delete_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        resume.delete()
        return redirect('resume_list')
    return render(request, 'resume_confirm_delete.html', {'resume': resume})