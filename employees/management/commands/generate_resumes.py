from django.core.management.base import BaseCommand
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from employees.models import JobApplication
import os


class Command(BaseCommand):
    help = 'Generate sample resumes for job applicants'

    def handle(self, *args, **kwargs):
        applicants_data = [
            {
                'name': 'Michael Johnson',
                'email': 'michael@example.com',
                'phone': '9876543210',
                'skills': 'Python, Django, REST API, PostgreSQL, Docker',
                'experience': '5 years in software development',
                'education': 'B.Tech in Computer Science',
            },
            {
                'name': 'Lisa Anderson',
                'email': 'lisa@example.com',
                'phone': '9876543211',
                'skills': 'HR Management, Recruitment, Employee Relations',
                'experience': '7 years in HR management',
                'education': 'MBA in Human Resources',
            },
            {
                'name': 'Robert Taylor',
                'email': 'robert@example.com',
                'phone': '9876543212',
                'skills': 'Digital Marketing, SEO, Social Media, Analytics',
                'experience': '4 years in marketing',
                'education': 'B.A. in Marketing',
            },
            {
                'name': 'Emily Davis',
                'email': 'emily@example.com',
                'phone': '9876543213',
                'skills': 'Java, Spring Boot, Microservices, AWS',
                'experience': '6 years in backend development',
                'education': 'M.Tech in Software Engineering',
            },
            {
                'name': 'James Wilson',
                'email': 'james@example.com',
                'phone': '9876543214',
                'skills': 'React, JavaScript, TypeScript, Node.js',
                'experience': '3 years in frontend development',
                'education': 'B.Sc. in Information Technology',
            },
            {
                'name': 'Sophia Martinez',
                'email': 'sophia@example.com',
                'phone': '9876543215',
                'skills': 'Financial Analysis, Budgeting, Excel, SAP',
                'experience': '8 years in finance',
                'education': 'MBA in Finance',
            },
            {
                'name': 'Daniel Brown',
                'email': 'daniel@example.com',
                'phone': '9876543216',
                'skills': 'DevOps, Kubernetes, CI/CD, Jenkins, Terraform',
                'experience': '5 years in DevOps',
                'education': 'B.E. in Computer Engineering',
            },
            {
                'name': 'Olivia Garcia',
                'email': 'olivia@example.com',
                'phone': '9876543217',
                'skills': 'UI/UX Design, Figma, Adobe XD, Prototyping',
                'experience': '4 years in design',
                'education': 'B.Des. in Interaction Design',
            },
            {
                'name': 'William Lee',
                'email': 'william@example.com',
                'phone': '9876543218',
                'skills': 'Data Science, Machine Learning, Python, TensorFlow',
                'experience': '3 years in data science',
                'education': 'M.Sc. in Data Science',
            },
            {
                'name': 'Ava Thompson',
                'email': 'ava@example.com',
                'phone': '9876543219',
                'skills': 'Project Management, Agile, Scrum, JIRA',
                'experience': '6 years in project management',
                'education': 'PMP Certified, B.Tech in IT',
            },
        ]

        media_path = 'media/resumes'
        os.makedirs(media_path, exist_ok=True)

        for data in applicants_data:
            filename = f"{data['name'].replace(' ', '_')}_Resume.pdf"
            filepath = os.path.join(media_path, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18, spaceAfter=12)
            story.append(Paragraph(data['name'], title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Contact
            contact_style = ParagraphStyle('Contact', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)
            story.append(Paragraph(f"{data['email']} | {data['phone']}", contact_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Education
            heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=6)
            story.append(Paragraph('EDUCATION', heading_style))
            story.append(Paragraph(data['education'], styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Experience
            story.append(Paragraph('EXPERIENCE', heading_style))
            story.append(Paragraph(data['experience'], styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Skills
            story.append(Paragraph('SKILLS', heading_style))
            story.append(Paragraph(data['skills'], styles['Normal']))
            
            doc.build(story)
            self.stdout.write(f'[OK] Generated resume: {filename}')
        
        # Update job applications with resume files
        applications = JobApplication.objects.all()
        for i, app in enumerate(applications):
            if i < len(applicants_data):
                filename = f"{applicants_data[i]['name'].replace(' ', '_')}_Resume.pdf"
                app.resume = f'resumes/{filename}'
                app.save()
        
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Generated {len(applicants_data)} resumes!'))
