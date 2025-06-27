from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import ResumeForm
from .models import Resume
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from io import BytesIO
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

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

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        left_margin = 0.5 * inch
        right_margin = width - 0.5 * inch
        top_margin = height - 0.5 * inch
        bottom_margin = 0.5 * inch
        y = top_margin
        max_width = right_margin - left_margin - 0.2 * inch  # Account for indent

        # Function to add text with wrapping and dynamic page breaks
        def add_text(text, font, size, x, initial_y, section_title=None):
            nonlocal y, p
            p.setFont(font, size)
            text = re.sub(r'[•\s]+', ' ', text or "").strip()
            lines = text.split('\n')
            available_height = initial_y - bottom_margin
            line_height = 0.25 * inch

            if section_title:
                p.setFont("Helvetica-Bold", size)  # Make section titles bold
                p.setFillColor(HexColor("#2c3e50"))
                p.drawString(x, y, section_title)
                p.setFont("Helvetica", size)  # Reset to regular for content
                y -= 0.3 * inch
                available_height -= 0.3 * inch

            p.setFillColor(HexColor("#333333"))
            for line in lines:
                if line.strip():
                    wrapped_lines = simpleSplit(line, "Helvetica", size, max_width)
                    for wrapped_line in wrapped_lines:
                        if y <= bottom_margin:
                            p.showPage()
                            y = top_margin
                            if section_title:
                                p.setFont("Helvetica-Bold", size)
                                p.setFillColor(HexColor("#2c3e50"))
                                p.drawString(x, y, section_title)
                                p.setFont("Helvetica", size)
                                y -= 0.3 * inch
                        p.drawString(x + 0.2 * inch, y, wrapped_line)
                        y -= line_height
            y -= 0.2 * inch

        # Add Title
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(HexColor("#2c3e50"))
        p.drawString(left_margin, y, resume.title or "Untitled Resume")
        y -= 0.5 * inch

        # Add Full Name
        p.setFont("Helvetica-Bold", 14)
        full_name = resume.full_name if resume.full_name else "Name Not Provided"
        p.drawString(left_margin, y, full_name)
        y -= 0.3 * inch

        # Add Contact Info
        p.setFont("Helvetica", 10)
        if resume.email:
            p.drawString(left_margin, y, f"Email: {resume.email}")
            y -= 0.2 * inch
        if resume.phone:
            p.drawString(left_margin, y, f"Phone: {resume.phone}")
            y -= 0.2 * inch
        if resume.address:
            p.drawString(left_margin, y, "Address:")
            y -= 0.2 * inch
            add_text(str(resume.address), "Helvetica", 10, left_margin, y)

        # Add Personal Info
        add_text(resume.personal_info or "No personal info provided", "Helvetica", 10, left_margin, y, "Personal Information:")

        # Add Summary
        add_text(resume.summary or "No summary provided", "Helvetica", 10, left_margin, y, "Summary:")  # New Summary field

        # Add Education
        add_text(resume.education or "No education provided", "Helvetica", 10, left_margin, y, "Education:")

        # Add Experience
        add_text(resume.experience or "No experience provided", "Helvetica", 10, left_margin, y, "Experience:")

        # Add Skills
        add_text(resume.skills or "No skills provided", "Helvetica", 10, left_margin, y, "Skills:")

        p.showPage()
        p.save()
        buffer.seek(0)
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resume_{resume.id}.pdf"'
        response.write(pdf)
        return response

    except Exception as e:
        logger.error(f"Error generating PDF for resume ID {pk}: {str(e)}")
        return HttpResponse("Error generating PDF. Please try again later.", status=500)

@login_required
def delete_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        resume.delete()
        return redirect('resume_list')
    return render(request, 'resume_confirm_delete.html', {'resume': resume})