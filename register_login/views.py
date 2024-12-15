from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Department, Education, Students

# Create your views here.

def reg_common_view(request):
    return render(request, 'register_common.html')

@csrf_exempt
def reg_common_submit(request):
    if request.method == "POST":
        usertype = request.POST.get('usertype')
        useremail = request.POST.get('useremail')
        password = request.POST.get('password')
        
        print(f"useremail: {useremail}, Usertype: {usertype}, Password: {password}")

        # Query database to verify user credentials
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM users
                    WHERE u_email = %s AND u_type = %s AND u_pass = %s
                """, [useremail, usertype, password])

                result = cursor.fetchone()

                # Check if the user exists
                if result[0] > 0:
                    message = "Login successful!"
                    print("Successful login")
                    return render(request, 'register_stud.html', {'message': message})
                else:
                    message = "Invalid credentials. Please try again."
                    print("Invalid credentials")
                    return render(request, 'register_common.html')

        except Exception as e:
            message = f"An error occurred: {str(e)}"
    else:
        return render("register_common.html")

@csrf_exempt
def reg_stud_submit(request):
    if request.method == "POST":
        print(request.POST)
        # technical_list = request.POST.getlist("technicalSkills[]")
        # print(technical_list)
        
        st_name = request.POST.get('fullName').strip()
        st_dob = request.POST.get('dob')
        st_gender = request.POST.get('gender')
        st_section = request.POST.get('sec')
        st_email = request.POST.get('email').strip()
        st_phone = request.POST.get('phone').strip()
        st_id = request.POST.get('usn').strip()
        st_year_of_passing = request.POST.get('yearOfGraduation').strip()
        ug_pg = request.POST.get('UGPG') 
        if ug_pg == "UG":
            st_program = bin(0)[2:]
        else:
            st_program = bin(1)[2:]
        is_spc = request.POST.get('UGPG') 
        if is_spc == "Yes":
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
        e_be_cgpa = request.POST.get('be_cgpa')

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


        # edu = Education(
        #     e_program=e_program,
        #     e_student_id=Students.objects.get(st_id=st_id),
        #     e_cgpa=e_cgpa,
        #     e_10thmarks=e_10thmarks,
        #     e_10thstream=e_10thstream,
        #     e_12thmarks=e_12thmarks,
        #     e_12thstream=e_12thstream,
        #     e_backlogs=e_backlogs,
        #     e_be_cgpa=e_be_cgpa,
        # )
        # edu.save()

        with connection.cursor() as cursor:
            # %s is a placeholder for any datatype, prevents SQL injection
            cursor.execute("""
                INSERT INTO students (st_id, st_program, st_name, st_email, st_phone, st_dept_id, st_dob, st_year_of_passing, st_section, st_gender)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (st_id, st_program, st_name, st_email, st_phone, st_dept_id, st_dob, st_year_of_passing, st_section, st_gender))

            cursor.execute("""
                INSERT INTO education (e_student_id, e_10thmarks, e_10thstream, e_12thmarks, e_12thstream, e_cgpa, e_backlogs, e_be_cgpa, e_program)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (e_student_id, e_10thmarks, e_10thstream, e_12thmarks, e_12thstream, e_cgpa, e_backlogs, e_be_cgpa, e_program))

            cursor.execute("""
                INSERT INTO skills (sk_student_id,sk_technical,sk_soft,sk_certifications,sk_technologies,sk_achievements,sk_languages,sk_interested_domains,sk_project_name,sk_project_desc)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,  %s, %s)
            """, (sk_student_id,sk_technical,sk_soft,sk_certifications,sk_technologies,sk_achievements,sk_languages,sk_interested_domains,sk_project_name,sk_project_desc))

            if w_job_title and w_company_name and w_experience_months and len(w_job_title) == len(w_company_name) == len(w_experience_months):
                for job_title, company, months in zip(w_job_title, w_company_name, w_experience_months):
                    if job_title and company and months:  # Skip empty rows
                        cursor.execute("""
                            INSERT INTO work_experience (w_student_id, w_job_title, w_company_name, w_experience_months, w_program)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (w_student_id, job_title, company, months, w_program))

            if is_spc == "Yes":
                cursor.execute("""
                    INSERT INTO education (spc_id, spc_stud_id)
                    VALUES (%s, %s)
                """, (spc_id, spc_stud_id))
            

        return render(request, 'register_stud.html')
    else:
        return render(request, 'register_stud.html')
        

    