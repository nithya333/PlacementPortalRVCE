from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Department, Education, Students, Resumes
import psycopg2
import base64
from base64 import b64encode
from django.core.files.storage import FileSystemStorage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Create your views here.

def student_home(request):
    return render(request, '2_1_student_home.html')


def student_profile(request):
    return render(request, '2_2_student_profile.html')

    
@csrf_exempt
def student_profile_submit(request):
    if request.method == "POST":
        print(request.POST)

        st_name = request.POST.get('fullName').strip()
        st_dob = request.POST.get('dob')
        st_gender = request.POST.get('gender')
        st_section = request.POST.get('sec')
        st_email = request.POST.get('email').strip()
        st_phone = request.POST.get('phone').strip()
        st_id = request.POST.get('usn').strip()
        st_year_of_passing = request.POST.get('yearOfGraduation').strip()
        ug_pg = request.POST.get('UGPG') 
        if ug_pg == "ug":
            st_program = bin(0)[2:]
        else:
            st_program = bin(1)[2:]
        is_spc = request.POST.get('spc') 
        if is_spc == "yes":
            spc_id = request.POST.get('spc_id')
            spc_stud_id = st_id
        dept = request.POST.get('branch')
        departments = Department.objects.get(d_abbr_code = dept)
        st_dept_id = departments.d_id
        # print(departments.d_id)

        e_program = st_program
        e_student_id = st_id
        e_cgpa = request.POST.get('cgpa')
        e_10thmarks = request.POST.get('tenthMarks')
        e_10thstream = request.POST.get('tenthStream')
        e_12thmarks = request.POST.get('twelfthMarks')
        e_12thstream = request.POST.get('twelfthStream')
        e_backlogs = request.POST.get('backlogs')
        e_be_cgpa = request.POST.get('be_cgpa') if 'be_cgpa' in request.POST else None

        w_program = st_program
        w_student_id = st_id
        w_job_title = request.POST.getlist('w_jobtitle[]') if 'w_jobtitle[]' in request.POST else []
        w_company_name = request.POST.getlist('w_compname[]') if 'w_compname[]' in request.POST else []
        w_experience_months = request.POST.getlist('w_jobmonths[]') if 'w_jobmonths[]' in request.POST else []

        sk_student_id = st_id
        sk_technical = request.POST.getlist('technicalSkills[]') if 'technicalSkills[]' in request.POST else []
        sk_soft = request.POST.getlist('softSkills[]') if 'softSkills[]' in request.POST else []
        sk_certifications = request.POST.getlist('certifications[]') if 'certifications[]' in request.POST else []
        sk_technologies = request.POST.getlist('technologies[]') if 'technologies[]' in request.POST else []
        sk_achievements = request.POST.getlist('achievements[]') if 'achievements[]' in request.POST else []
        sk_languages = request.POST.getlist('languages[]') if 'languages[]' in request.POST else []
        sk_interested_domains = request.POST.getlist('domains[]') if 'domains[]' in request.POST else []
        sk_project_name = request.POST.getlist('sk_project_name[]') if 'sk_project_name[]' in request.POST else []
        sk_project_desc = request.POST.getlist('sk_project_desc[]') if 'sk_project_desc[]' in request.POST else []

        a = Resumes(fi_name=st_name, fi_data=request.FILES['resume'])
        a.save()

        conn = psycopg2.connect(
        host="localhost",
        database="placement_sql",
        user="postgres",
        password="cse"
        )
        cursor = conn.cursor()

        # Fetch the PDF data
        cursor.execute("SELECT fi_data FROM resumes WHERE fi_id = %s", ('3'))
        pdf_data = cursor.fetchone()[0]

        # Return the PDF as an HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="document_{3}.pdf"'
        response.write(pdf_data)

        cursor.close()
        conn.close()

        with connection.cursor() as cursor:
            # Update students table
            cursor.execute("""
                UPDATE students
                SET st_program = %s, st_name = %s, st_email = %s, st_phone = %s, st_dept_id = %s, st_dob = %s, 
                    st_year_of_passing = %s, st_section = %s, st_gender = %s
                WHERE st_id = %s
            """, (st_program, st_name, st_email, st_phone, st_dept_id, st_dob, st_year_of_passing, st_section, st_gender, st_id))

            # Update education table
            cursor.execute("""
                UPDATE education
                SET e_10thmarks = %s, e_10thstream = %s, e_12thmarks = %s, e_12thstream = %s, e_cgpa = %s, 
                    e_backlogs = %s, e_be_cgpa = %s, e_program = %s
                WHERE e_student_id = %s
            """, (e_10thmarks, e_10thstream, e_12thmarks, e_12thstream, e_cgpa, e_backlogs, e_be_cgpa, e_program, e_student_id))

            # Update skills table
            cursor.execute("""
                UPDATE skills
                SET sk_technical = %s, sk_soft = %s, sk_certifications = %s, sk_technologies = %s, sk_achievements = %s, 
                    sk_languages = %s, sk_interested_domains = %s, sk_project_name = %s, sk_project_desc = %s
                WHERE sk_student_id = %s
            """, (sk_technical, sk_soft, sk_certifications, sk_technologies, sk_achievements, sk_languages, 
                sk_interested_domains, sk_project_name, sk_project_desc, sk_student_id))

            # Update work_experience table
            if w_job_title and w_company_name and w_experience_months and len(w_job_title) == len(w_company_name) == len(w_experience_months):
                for job_title, company, months in zip(w_job_title, w_company_name, w_experience_months):
                    if job_title and company and months:  # Skip empty rows
                        cursor.execute("""
                            UPDATE work_experience
                            SET w_job_title = %s, w_company_name = %s, w_experience_months = %s, w_program = %s
                            WHERE w_student_id = %s AND w_job_title = %s
                        """, (job_title, company, months, w_program, w_student_id, job_title))

            # Update spc table (if applicable)
            if is_spc == "yes":
                cursor.execute("""
                    UPDATE spc
                    SET spc_stud_id = %s
                    WHERE spc_id = %s
                """, (spc_stud_id, spc_id))


        return render(request, '2_1_student_home.html')
    else:
        return render(request, 'register_stud.html')
    

def student_applied(request):
    return render(request, '2_3_student_applied.html')


def student_new(request):
    return render(request, '2_4_student_new.html')

@csrf_exempt  # Temporarily bypass CSRF for testing; remove or configure properly in production.
def student_applied_vmore(request, job_id):
    if request.method == 'GET':
        # Fetch the job_id from the URL
        print(job_id)
        return render(request, '2_5_student_applied_vmore.html')
    else:
        return render(request, '2_1_student_home.html')
    

def export_student_resume(request, u_id):
    conn = psycopg2.connect(
        host="localhost",
        database="placement_sql",
        user="postgres",
        password="cse"
    )
    cursor = conn.cursor()
    try:
        # Fetch student data
        cursor.execute("SELECT * FROM students WHERE st_id = %s", (u_id,))
        student = cursor.fetchone()

        if not student:
            return HttpResponse("Student not found.", status=404)

        cursor.execute("SELECT * FROM education WHERE e_student_id = %s", (u_id,))
        education = cursor.fetchone()

        cursor.execute("SELECT * FROM skills WHERE sk_student_id = %s", (u_id,))
        skills = cursor.fetchone()

        cursor.execute("SELECT * FROM work_experience WHERE w_student_id = %s", (u_id,))
        work_experience = cursor.fetchall()

        cursor.execute("SELECT * FROM spc WHERE spc_stud_id = %s", (u_id,))
        spc = cursor.fetchone()

        # Close the connection
        cursor.close()
        conn.close()

        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="resume_{u_id}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add background color (cream)
        def set_background(canvas, doc):
            canvas.saveState()
            canvas.setFillColorRGB(1, 0.95, 0.8)  # Cream color
            canvas.rect(0, 0, letter[0], letter[1], fill=1)
            canvas.restoreState()

        # Add heading "Resume"
        heading_style = styles["Heading1"]
        heading_style.alignment = 1  # Center alignment
        story.append(Paragraph("Resume", heading_style))
        story.append(Spacer(1, 24))  # Add some space

        # Add Student Details
        story.append(Paragraph(f"<b>Student Name:</b> {student[2]}", styles['Normal']))
        story.append(Paragraph(f"<b>Email:</b> {student[3]}", styles['Normal']))
        story.append(Paragraph(f"<b>Phone:</b> {student[4]}", styles['Normal']))
        story.append(Paragraph(f"<b>Program:</b> {'UG' if student[1] == '0' else 'PG'}", styles['Normal']))
        story.append(Paragraph(f"<b>Department ID:</b> {student[5]}", styles['Normal']))
        story.append(Paragraph(f"<b>DOB:</b> {student[8]}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Add Education Details
        if education:
            story.append(Paragraph("<b>Education:</b>", styles['Heading2']))
            story.append(Paragraph(f"<b>Current CGPA:</b> {education[2]}", styles['Normal']))
            story.append(Paragraph(f"<b>10th Marks:</b> {education[3]}", styles['Normal']))
            story.append(Paragraph(f"<b>12th Marks:</b> {education[4]}", styles['Normal']))
            story.append(Paragraph(f"<b>B.E. CGPA:</b> {education[5]}", styles['Normal']))
            story.append(Paragraph(f"<b>10th stream:</b> {education[6]}", styles['Normal']))
            story.append(Paragraph(f"<b>12th stream:</b> {education[7]}", styles['Normal']))
            story.append(Paragraph(f"<b>No of backlogs:</b> {education[8]}", styles['Normal']))
            story.append(Spacer(1, 12))

        # Add Skills
        if skills:
            story.append(Paragraph("<b>Skills:</b>", styles['Heading2']))
            story.append(Paragraph(f"<b>Technical Skills:</b> {', '.join(skills[1])}", styles['Normal']))
            story.append(Paragraph(f"<b>Soft Skills:</b> {', '.join(skills[2])}", styles['Normal']))
            story.append(Paragraph(f"<b>Certifications:</b> {', '.join(skills[3])}", styles['Normal']))
            story.append(Paragraph(f"<b>Technologies:</b> {', '.join(skills[4])}", styles['Normal']))
            story.append(Paragraph(f"<b>Projects:</b> {', '.join(skills[5])}", styles['Normal']))
            story.append(Paragraph(f"<b>Achievements:</b> {', '.join(skills[7])}", styles['Normal']))
            story.append(Paragraph(f"<b>Languages:</b> {', '.join(skills[8])}", styles['Normal']))
            story.append(Paragraph(f"<b>Interested Domains:</b> {', '.join(skills[10])}", styles['Normal']))
            story.append(Spacer(1, 12))

        # Add Work Experience
        if work_experience:
            story.append(Paragraph("<b>Work Experience:</b>", styles['Heading2']))
            for exp in work_experience:
                story.append(Paragraph(f"<b>Job Title:</b> {exp[2]}", styles['Normal']))
                story.append(Paragraph(f"<b>Company:</b> {exp[3]}", styles['Normal']))
                story.append(Paragraph(f"<b>Experience:</b> {exp[4]} months", styles['Normal']))
                story.append(Spacer(1, 12))

        # Add SPC Details (if applicable)
        if spc:
            story.append(Paragraph(f"<b>SPC ID:</b> {spc[0]}", styles['Normal']))
            story.append(Spacer(1, 12))

        # Build the PDF
        doc.build(story, onFirstPage=set_background, onLaterPages=set_background)

        return response
    
    except Exception as e:
        # Handle errors
        cursor.close()
        conn.close()
        return HttpResponse(f"An error occurred: {e}", status=500)