from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# from .models import Department, Education, Students, Resumes
import psycopg2
import base64
from base64 import b64encode
from django.core.files.storage import FileSystemStorage

# Create your views here.

def student_home(request):
    return render(request, '2_1_student_home.html')


def student_profile(request):
    return render(request, '2_2_student_profile.html')


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
#                     SELECT u_id
#                     FROM users
#                     WHERE u_email = %s AND u_type = %s AND u_pass = %s
#                 """, [useremail, usertype, password])

#                 result = cursor.fetchone()

#                 # Check if the user exists
#                 if result:  # This will be True if a row was fetched
#                     u_id = result[0]  # Fetch the `u_id` from the result tuple
#                     request.session['u_type'] = usertype
#                     request.session['u_id'] = u_id
#                     # username = request.session.get('username')

#                     message = "Login successful!"
#                     print(f"Successful login for user ID: {u_id}")

#                     if usertype == "Student":
#                         return render(request, 'register_stud.html', {'message': message})
#                     elif usertype == "Coordinator":
#                         return render(request, 'register_fac.html', {'message': message})
#                     elif usertype == "Company":
#                         return render(request, 'register_comp.html', {'message': message})
#                     elif usertype == "Admin":
#                         return render(request, 'home_admin.html', {'message': message})
#                 else:
#                     message = "Invalid credentials. Please try again."
#                     print("Invalid credentials")
#                     return render(request, '1_1_register_common.html')

#         except Exception as e:
#             message = f"An error occurred: {str(e)}"
#     else:
#         return render("1_1_register_common.html")