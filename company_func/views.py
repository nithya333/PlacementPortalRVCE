from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import psycopg2
import base64
from base64 import b64encode
from django.core.files.storage import FileSystemStorage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Company, Department, Resumes
from pymongo import MongoClient
import time
from bson import ObjectId
# Create your views here.

def company_home(request):
    return render(request, '5_1_company_home.html')


def company_postjob(request):
    # Context dictionary
    dept_codes = Department.objects.values_list('d_abbr_code', flat=True)
    dept_codes_list = list(dept_codes)  # Convert to a list if needed
    # print(dept_codes_list)
    context = {
        'dept_codes_list': dept_codes_list
    }
    return render(request, '5_2_company_postjob.html', context=context)

@csrf_exempt
def company_postjob_submit(request):
    if request.method == "POST":
        print(request.POST)
        # Parse the POST data
        post_data = request.POST 

        job_data = {}
        # Add additional fields or modify the data

        job_data['_id'] = str(ObjectId())  # Generate a new ObjectId

        job_data["job_title"] = request.POST.get("job_title").strip()
        job_data["job_type"] = request.POST.get("job_type")
        job_data["job_duration"] = request.POST.get("job_duration")
        job_data["job_desc"] = request.POST.get("job_desc").strip()
        job_data["job_domain"] = request.POST.get("job_domain")
        job_data["job_salary"] = (float)(request.POST.get("job_salary"))
        job_data["cgpaMinCriteria"] = (float)(request.POST.get("cgpaMinCriteria"))
        job_data["cgpaMaxCriteria"] = (float)(request.POST.get("cgpaMaxCriteria"))
        job_data["degreeCriteria"] = request.POST.get("degreeCriteria")

        job_data["job_locations"] = [word.strip() for word in request.POST.get("job_locations[]").split(",")]
        job_data["deptsCriteria"] = request.POST.getlist("deptsCriteria[]")
        # job_data["yearOfPassingCriteria"] = request.POST.getlist("yearOfPassingCriteria[]")
        job_data["yearOfPassingCriteria"] = [int(year) for year in request.POST.getlist("yearOfPassingCriteria[]")]
        job_data["skillsPreferences"] = [word.strip() for word in request.POST.get("skillsPreferences[]").split(",")]
        
        job_data["job_enrolledDate"] = time.strftime("%Y-%m-%d %H:%M:%S")
        job_data["job_pptDate"] = None
        job_data["job_oaDate"] = None
        job_data["job_interviewDate"] = None
        job_data["job_status"] = 0 # 0 - upcoming, 1 - ongoing, 2 - closed
        job_data["job_stage"] = 0 # 0 - company_posted, 1 - college alloted, 2 - student application, 3 - OA, 4 - Interview, 5 - Done
        job_data["job_companyId"] = request.session.get('u_id', 0)

        compId = job_data["job_companyId"]
        comp = Company.objects.get(cp_id = compId)
        compName = comp.cp_name

        # job_data["job_companyName"] = request.session.get('u_name', 'Guest')
        job_data["job_companyName"] = compName
        job_data["job_numStudents"] = 0
        job_data["job_lastUpdated"] = time.strftime("%Y-%m-%d %H:%M:%S")

        # Connect to MongoDB
        client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
        db = client['Placement']  # Database name
        job_collection = db['job']  # Collection name
        
        # Insert into MongoDB
        result = job_collection.insert_one(job_data)
        
        # Close the connection
        client.close()

        return render(request, '5_1_company_home.html')
    
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
    

def company_ong_recruitments(request):
    return render(request, '5_2_student_postjo.html')

def company_college_history(request):
    return render(request, '5_2_student_postjo.html')