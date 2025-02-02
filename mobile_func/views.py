import json
from django.db import connection
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import psycopg2
import base64
from base64 import b64encode
from django.core.files.storage import FileSystemStorage
from db import get_db
from datetime import datetime, timedelta

# Create your views here.

def reg_common_view(request):
    return render(request, '1_1_register_common.html')


def login_common_view(request):
    return render(request, 'index.html')

@csrf_exempt
def submit_feedback(request):
    print(request.POST)
    feedback_userType = request.POST["feedback_userType"]
    feedback_rating = request.POST["feedback_rating"]
    feedback_suggestion = request.POST["feedback_suggestion"]
    with connection.cursor() as cursor:
        # %s is a placeholder for any datatype, prevents SQL injection
        cursor.execute("""
            INSERT INTO feedback (f_usertype, f_rating, f_suggestion)
            VALUES (%s, %s, %s)
        """, (feedback_userType, feedback_rating, feedback_suggestion))


    # Redirect back to the same page
    return redirect(request.META.get('HTTP_REFERER', '/'))

def get_sample(request):
    return HttpResponse("Hello")

@csrf_exempt
def verify_user(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        u_email = request_data.get("u_email")
        u_pass = request_data.get("u_pass")
        db = get_db()
        users_collection = db['users']        
        user = list(users_collection.find({"u_email": u_email, "u_pass": u_pass}))
        if len(user) > 0:
            return JsonResponse({"valid" : True, "u_name" : user[0]["u_name"]}, safe=False, status=200)
        else:
            return JsonResponse({"valid" : False, "u_name" : ""}, safe=False, status=200)


@csrf_exempt
def new_jobs(request):
    if request.method == "POST":
        try:
            # Parse JSON request body
            request_data = json.loads(request.body)
            st_id = request_data.get("st_id")
            # print(st_id)
            db = get_db()
            job_collection = db['job']
            appl_collection = db['application']

            jobs = list(job_collection.find({"job_stage": 1}))

            new_jobs = []
            for job in jobs:
                # print(job)
                # Check if student has already applied
                if appl_collection.find_one({"appl_student_id": st_id, "appl_job_id": job["_id"]}):
                    continue
                job_reglastdate = (datetime.strptime(job['job_pptDate'], "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")
                new_job = {
                    "_id": job["_id"],
                    "jobTitle": job["job_title"],
                    "jobType": job["job_type"],
                    "jobDuration": job["job_duration"],
                    "jobDesc": job["job_desc"],
                    "jobSalary": job["job_salary"],
                    "cgpaMinCriteria": job["cgpaMinCriteria"],
                    "cgpaMaxCriteria": job["cgpaMaxCriteria"],
                    "degreeCriteria": job["degreeCriteria"],
                    "deptsCriteria": job["deptsCriteria"],
                    "jobPptDate": job["job_pptDate"],
                    "jobRegDate": job_reglastdate,
                    "jobOaDate": job["job_oaDate"],
                    "jobInterviewDate": job["job_interviewDate"],
                    "jobStatus": job["job_status"],
                    "jobStage": job["job_stage"],
                    "jobCompanyName": job["job_companyName"]
                }
                new_jobs.append(new_job)

            # print(new_jobs)
            return JsonResponse(new_jobs, safe=False, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)
    

@csrf_exempt
def applied_jobs(request):
    if request.method == "POST":
        try:
            # Parse JSON request body
            request_data = json.loads(request.body)
            st_id = request_data.get("st_id")
            # print(st_id)
            db = get_db()
            job_collection = db['job']
            appl_collection = db['application']

            jobs = list(job_collection.find( {"job_status": {"$in": [1, 2]}}))

            new_jobs = []
            for job in jobs:
                # print(job)
                # Check if student has already applied
                if appl_collection.find_one({"appl_student_id": st_id, "appl_job_id": job["_id"]}):
                    
                    job_reglastdate = (datetime.strptime(job['job_pptDate'], "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")
                    new_job = {
                        "_id": job["_id"],
                        "jobTitle": job["job_title"],
                        "jobType": job["job_type"],
                        "jobDuration": job["job_duration"],
                        "jobDesc": job["job_desc"],
                        "jobSalary": job["job_salary"],
                        "cgpaMinCriteria": job["cgpaMinCriteria"],
                        "cgpaMaxCriteria": job["cgpaMaxCriteria"],
                        "degreeCriteria": job["degreeCriteria"],
                        "deptsCriteria": job["deptsCriteria"],
                        "jobPptDate": job["job_pptDate"],
                        "jobRegDate": job_reglastdate,
                        "jobOaDate": job["job_oaDate"],
                        "jobInterviewDate": job["job_interviewDate"],
                        "jobStatus": job["job_status"],
                        "jobStage": job["job_stage"],
                        "jobCompanyName": job["job_companyName"]
                    }
                    new_jobs.append(new_job)

            # print(new_jobs)
            return JsonResponse(new_jobs, safe=False, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)

    

