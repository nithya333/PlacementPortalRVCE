from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Department, Education, Students, Resumes
import psycopg2
import base64
from base64 import b64encode
from django.core.files.storage import FileSystemStorage

# Create your views here.

def reg_common_view(request):
    return render(request, '1_1_register_common.html')


def login_common_view(request):
    return render(request, 'index.html')

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
                    SELECT u_id
                    FROM users
                    WHERE u_email = %s AND u_type = %s AND u_pass = %s
                """, [useremail, usertype, password])

                result = cursor.fetchone()

                # Check if the user exists
                if result:  # This will be True if a row was fetched
                    u_id = result[0]  # Fetch the `u_id` from the result tuple
                    request.session['u_type'] = usertype
                    request.session['u_id'] = u_id
                    # username = request.session.get('username')

                    message = "Login successful!"
                    print(f"Successful login for user ID: {u_id}")

                    if usertype == "Student":
                        return render(request, '1_2_register_stud.html', {'message': message})
                    elif usertype == "Coordinator":
                        return render(request, '1_3_register_fac.html', {'message': message})
                    elif usertype == "Company":
                        return render(request, '1_4_register_comp.html', {'message': message})
                    elif usertype == "Admin":
                        return render(request, 'home_admin.html', {'message': message})
                else:
                    message = "Invalid credentials. Please try again."
                    print("Invalid credentials")
                    return render(request, '1_1_register_common.html')

        except Exception as e:
            message = f"An error occurred: {str(e)}"
    else:
        return render("1_1_register_common.html")
    
@csrf_exempt
def login_common_submit(request):
    if request.method == "POST":
        usertype = request.POST.get('usertype')
        useremail = request.POST.get('useremail')
        password = request.POST.get('password')

        print(f"useremail: {useremail}, Usertype: {usertype}, Password: {password}")

        # Query database to verify user credentials
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u_id
                    FROM users
                    WHERE u_email = %s AND u_type = %s AND u_pass = %s
                """, [useremail, usertype, password])

                result = cursor.fetchone()

                # Check if the user exists
                if result:  # This will be True if a row was fetched
                    u_id = result[0]  # Fetch the `u_id` from the result tuple
                    request.session['u_type'] = usertype
                    request.session['u_id'] = u_id
                    # username = request.session.get('username')

                    message = "Login successful!"
                    print(f"Successful login for user ID: {u_id}")

                    if usertype == "Student":
                        return render(request, '2_1_student_home.html', {'message': message})
                    elif usertype == "Coordinator":
                        return render(request, 'register_fac.html', {'message': message})
                    elif usertype == "Company":
                        return render(request, 'register_comp.html', {'message': message})
                    elif usertype == "Admin":
                        return render(request, 'home_admin.html', {'message': message})
                else:
                    message = "Invalid credentials. Please try again."
                    print("Invalid credentials")
                    return render(request, '1_1_register_common.html')

        except Exception as e:
            message = f"An error occurred: {str(e)}"
    else:
        return render("index.html")
    
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

            if is_spc == "yes":
                cursor.execute("""
                    INSERT INTO spc (spc_id, spc_stud_id)
                    VALUES (%s, %s)
                """, (spc_id, spc_stud_id))
            

        return render(request, '2_1_student_home.html')
    else:
        return render(request, 'register_stud.html')
    

# @csrf_exempt
# def reg_common_submit(request):
#     if request.method == "POST":
#         usertype = request.POST.get('usertype')
#         useremail = request.POST.get('useremail')
#         password = request.POST.get('password')
        
#         print(f"useremail: {useremail}, Usertype: {usertype}, Password: {password}")

#         # Query database to verify user credentials
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT COUNT(*)
#                     FROM users
#                     WHERE u_email = %s AND u_type = %s AND u_pass = %s
#                 """, [useremail, usertype, password])

#                 result = cursor.fetchone()

#                 # Check if the user exists
#                 if result[0] > 0:
#                     message = "Login successful!"
#                     print("Successful login")
#                     return render(request, 'register_stud.html', {'message': message})
#                 else:
#                     message = "Invalid credentials. Please try again."
#                     print("Invalid credentials")
#                     return render(request, '1_1_register_common.html')

#         except Exception as e:
#             message = f"An error occurred: {str(e)}"
#     else:
#         return render("1_1_register_common.html")

@csrf_exempt
def reg_fac_submit(request):
    if request.method == "POST":
        print(request.POST)
        cd_name = request.POST.get('fullName').strip()
        cd_id = request.POST.get('co_id').strip()
        # cd_dob = request.POST.get('dob')
        # cd_gender = request.POST.get('gender')
        program = request.POST.get('UGPG')
        dept = request.POST.get('branch')
        cd_email = request.POST.get('email').strip()
        cd_phone = request.POST.get('phone').strip()
        st_name = request.POST.get('fullName').strip()

        if program == "ug":
            cd_program = bin(0)[2:]
        else:
            cd_program = bin(1)[2:]
        
        dept = request.POST.get('branch')
        departments = Department.objects.get(d_abbr_code = dept)
        cd_dept_id = departments.d_id


        with connection.cursor() as cursor:
            # %s is a placeholder for any datatype, prevents SQL injection
            cursor.execute("""
                INSERT INTO coordinator (cd_name, cd_id, cd_email, cd_phone, cd_program, cd_dept_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cd_name, cd_id, cd_email, cd_phone, cd_program, cd_dept_id))
            

        return render(request, 'register_fac.html')
    else:
        return render(request, 'register_fac.html')
        


@csrf_exempt
def reg_comp_submit(request):
    if request.method == "POST":
        print(request.POST)
        cp_id = request.POST.get('compId').strip()
        cp_name = request.POST.get('compName').strip()
        cp_type = request.POST.get('compType')
        cp_location = request.POST.get('compLoc').strip()
        cp_contact_name = request.POST.get('contName').strip()
        cp_contact_email = request.POST.get('contEmail')
        cp_contact_phone = request.POST.get('contPhone')
        
        with connection.cursor() as cursor:
            # %s is a placeholder for any datatype, prevents SQL injection
            cursor.execute("""
                INSERT INTO company (cp_id, cp_name, cp_type, cp_location, cp_contact_name, cp_contact_email, cp_contact_phone )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (cp_id, cp_name, cp_type, cp_location, cp_contact_name, cp_contact_email, cp_contact_phone ))
            

        return render(request, 'register_comp.html')
    else:
        return render(request, 'register_comp.html')
    
# @csrf_exempt
# def reg_admin_submit(request):
#     if request.method == "POST":
#         print(request.POST)
#         cp_id = request.POST.get('compId').strip()
#         cp_name = request.POST.get('compName').strip()
#         cp_type = request.POST.get('compType')
#         cp_location = request.POST.get('compLoc').strip()
#         cp_contact_name = request.POST.get('contName').strip()
#         cp_contact_email = request.POST.get('contEmail')
#         cp_contact_phone = request.POST.get('contPhone')
        
#         with connection.cursor() as cursor:
#             # %s is a placeholder for any datatype, prevents SQL injection
#             cursor.execute("""
#                 INSERT INTO company (cp_id, cp_name, cp_type, cp_location, cp_contact_name, cp_contact_email, cp_contact_phone )
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """, (cp_id, cp_name, cp_type, cp_location, cp_contact_name, cp_contact_email, cp_contact_phone ))
            

#         return render(request, 'register_comp.html')
#     else:
#         return render(request, 'register_comp.html')
        

    