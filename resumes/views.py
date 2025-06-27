from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import ResumeForm
from .models import Resume
import pdfkit
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)

# Configure wkhtmltopdf path (adjust based on your installation)
WKHTMLTOPDF_PATH = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"  # Windows example
# For Linux/macOS, use something like: "/usr/local/bin/wkhtmltopdf"
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

        # HTML content mirroring the preview with updated styling
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Helvetica', 'Arial', sans-serif;
                    color: #333;
                    padding: 0.25in; /* Reduced from 0.5in */
                    font-size: 16px; /* Increased base font size */
                }}
                h3 {{
                    font-weight: bold; /* Enhanced boldness */
                    color: #2c3e50;
                    border-bottom: 2px solid #ddd; /* Thicker border for boldness */
                    padding-bottom: 5px;
                    font-size: 18px; /* Increased size for headers */
                }}
                p {{
                    margin: 5px 0;
                    font-weight: 500; /* Slightly bolder text */
                }}
                pre {{
                    margin: 0;
                    white-space: pre-wrap; /* Preserve newlines and allow wrapping */
                    word-break: break-word; /* Break long words if necessary */
                    font-weight: 500; /* Slightly bolder text */
                }}
            </style>
        </head>
        <body>
            <h3>{resume.title or 'Untitled Resume'}</h3>
            <p><strong>Full Name:</strong> {resume.full_name or 'Not provided'}</p>
            <p><strong>Email:</strong> {resume.email or 'Not provided'}</p>
            <p><strong>Phone:</strong> {resume.phone or 'Not provided'}</p>
            <p><strong>Address:</strong> <pre>{resume.address or 'Not provided'}</pre></p>
            <h3>Personal Information:</h3>
            <p><pre>{resume.personal_info or 'No personal info provided'}</pre></p>
            <h3>Summary:</h3>
            <p><pre>{resume.summary or 'No summary provided'}</pre></p>
            <h3>Education:</h3>
            <p><pre>{resume.education or 'No education provided'}</pre></p>
            <h3>Experience:</h3>
            <p><pre>{resume.experience or 'No experience provided'}</pre></p>
            <h3>Skills:</h3>
            <p><pre>{resume.skills or 'No skills provided'}</pre></p>
        </body>
        </html>
        """

        # Configure pdfkit options
        options = {
            'margin-top': '0.25in',  # Reduced from 0.5in
            'margin-right': '0.25in',  # Reduced from 0.5in
            'margin-bottom': '0.25in',  # Reduced from 0.5in
            'margin-left': '0.25in',  # Reduced from 0.5in
            'encoding': "UTF-8",
            'no-outline': None
        }

        # Generate PDF with configured path
        pdf = pdfkit.from_string(html_content, False, options=options, configuration=pdfkit_config)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resume_{resume.id}.pdf"'
        return response

    except Exception as e:
        logger.error(f"Error generating PDF for resume ID {pk}: {str(e)}")
        return HttpResponse("Error generating PDF. Please try again later. Ensure wkhtmltopdf is installed and the path is correct.", status=500)

@login_required
def delete_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        resume.delete()
        return redirect('resume_list')
    return render(request, 'resume_confirm_delete.html', {'resume': resume})