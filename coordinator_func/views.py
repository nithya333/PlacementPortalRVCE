from django.shortcuts import render

# Create your views here.
from datetime import datetime, timedelta
import random
import time
from bson import ObjectId
from django.db import connection
from django.shortcuts import redirect, render
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
from django.shortcuts import render
from django.http import JsonResponse
import json
from pymongo import MongoClient


def coordinator_home(request):
    return render(request, '3_1_coord_home.html')

def coordinator_shortlist(request):
    # MongoDB Connection
    client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
    db = client['Placement']
    job_collection = db['job']

    # Fetch jobs with status "upcoming"
    jobs = list(job_collection.find({"job_status": 0}))
    # Prepare calendar events
    events = []
    pending = []
    all_jobs = job_collection.find()
    for job in all_jobs:
        if "job_pptDate" in job and job["job_pptDate"] is not None:
            events.append({"id": job["_id"], "compName": f"{job['job_companyName']} - PPT", "start": job["job_pptDate"], "round": 0})
        if "job_oaDate" in job and job["job_oaDate"] is not None:
            events.append({"id": job["_id"], "compName": f"{job['job_companyName']} - OA", "start": job["job_oaDate"], "round": 1})
        if "job_interviewDate" in job and job["job_interviewDate"] is not None:
            events.append({"id": job["_id"], "compName": f"{job['job_companyName']} - Interview", "start": job["job_interviewDate"], "round": 2})
        if job["job_pptDate"] is None and job["job_oaDate"] is None and job["job_interviewDate"] is None:
            pending.append({"id": job["_id"], "compName": f"{job['job_companyName']}", "date_posted": job["job_enrolledDate"][:10], "job_title" : job["job_title"], "job_type" : job["job_type"],"job_duration" : job["job_duration"],"job_desc" : job["job_desc"],"job_domain" : job["job_domain"],"job_salary" : job["job_salary"], "eligible_branches" : ' , '.join(job["deptsCriteria"])})
    return render(request, '3_2_coord_shortlist.html')

 

@csrf_exempt  
def coordinator_shortlist_vmore(request, job_id):
    return render(request, '3_3_coord_shortlist_vmore.html')
# MongoDB Connection
# client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
# db = client['Placement']
# job_collection = db['job']
# appl_collection = db['application']

# applied_jobs = []
# events = []
# applications = appl_collection.find({"appl_student_id": request.session.get('u_id')})
# for appl in applications:
#     job = job_collection.find_one({"_id": appl["appl_job_id"]})
#     job_details = job
#     job_details.update(appl)
#     applied_jobs.append(job_details)
#     events.append({"id": job["_id"], "compName": f"{job['job_companyName']} - PPT", "start": job["job_pptDate"], "round": 0})
#     events.append({"id": job["_id"], "compName": f"{job['job_companyName']} - OA", "start": job["job_oaDate"], "round": 1})
#     events.append({"id": job["_id"], "compName": f"{job['job_companyName']} - Interview", "start": job["job_interviewDate"], "round": 2})
    
# return render(request, '2_1_student_home.html', context = {"events" : events})


def coordinator_track(request):
    return render(request, '3_4_coord_track.html')

def coordinator_applied(request):
    # MongoDB Connection
    client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
    db = client['Placement']
    job_collection = db['job']
    appl_collection = db['application']

    # Fetch jobs with status "upcoming"
    jobs = list(job_collection.find({"job_stage": 1}))

    # print(jobs)
    # Prepare calendar events
    # events = []
    # pending = []
    # all_jobs = job_collection.find()
    applied_jobs = []
    applications = appl_collection.find({"appl_student_id": request.session.get('u_id')})
    for appl in applications:
        job = job_collection.find_one({"_id": appl["appl_job_id"]})
        job_details = job
        job_details.update(appl)
        applied_jobs.append(job_details)

    # print(applied_jobs)
    # print(applications)
    # Close the connection
    # client.close()
    return render(request, '2_3_student_applied.html', {"applied": applied_jobs, "applications": applications})

@csrf_exempt  
def coordinator_applied_vmore(request, job_id):
    if request.method == 'GET':
        # Fetch the job_id from the URL
        print(job_id)

        # MongoDB Connection
        client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
        db = client['Placement']
        job_collection = db['job']
        appl_collection = db['application']

        job = job_collection.find_one({"_id": job_id})
        job_details = job

        appl = list(appl_collection.find({"appl_student_id": request.session.get('u_id'), "appl_job_id": job_id}))
        job_details.update(appl[0])
        job_reglastdate = (datetime.strptime(job_details['job_pptDate'], "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")
        job_details['job_reglastdate'] = job_reglastdate

        # print(job_details)
        # "stages" : [1,2,3,4,5,6,7], "stages_text" : ["Applied", "Applications Closed", "Shortlisted", "PPT", "OA", "Interview", "Recruited"]
        stages = [[1, "You have registered", job_details['appl_date']], [2, "Applications Closed" , job_details['job_reglastdate']], [3, "Shortlisted at college level", ''], [4, "PPT from the recruiter", job_details['job_pptDate']], [5, "OA - Round 1", job_details['job_oaDate']], [6, "Interview - Round 2", job_details['job_interviewDate']], [7, "You are recruited", '']]
        return render(request, '2_5_student_applied_vmore.html', {"job_details": job_details, "stages": stages})
    else:
        return render(request, '2_1_student_home.html')
    
