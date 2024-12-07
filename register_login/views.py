from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
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
                # Query to check if the user exists in the database
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM users
                    WHERE u_email = %s AND u_type = %s AND u_pass = %s
                """, [useremail, usertype, password])

                # Fetch the result of the query
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
            # Handle exceptions (e.g., connection errors, syntax errors)
            message = f"An error occurred: {str(e)}"
    else:
        return render("register_common.html")

@csrf_exempt
def reg_stud_submit(request):
    if request.method == "POST":
        print(request.POST)
        technical_list = request.POST.getlist("technicalSkills[]")
        print(technical_list)
        # usertype = request.POST.get('usertype')
        # useremail = request.POST.get('useremail')
        # password = request.POST.get('password')
        
        # print(f"useremail: {useremail}, Usertype: {usertype}, Password: {password}")
        return render(request, 'register_stud.html')

    