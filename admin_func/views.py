from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import psycopg2
import base64
from base64 import b64encode
# from .models import Company
from pymongo import MongoClient
import time
from bson import ObjectId
# Create your views here.

from django.shortcuts import render
from django.http import JsonResponse
import json
from pymongo import MongoClient


def head_home(request):
    return render(request, '4_1_head_home.html')


def head_allot_slots(request):
    if request.method == 'POST':
        # Save allocated dates
        # data = json.loads(request.body)
        print(request.POST)
        job_id = request.POST.get('job_id')
        ppt_date = request.POST.get('ppt_slot')
        oa_date = request.POST.get('oa_slot')
        interview_date = request.POST.get('interview_slot')
        print(job_id, ppt_date, oa_date, interview_date)
        # MongoDB Connection
        client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')
        db = client['Placement']
        job_collection = db['job']
        job_collection.update_one(
            {"_id": job_id},
            {"$set": {
                "job_pptDate": ppt_date,
                "job_oaDate": oa_date,
                "job_interviewDate": interview_date,
                "job_stage": 1,
                "job_status": 1,
                "job_lastUpdated": time.strftime('%Y-%m-%d %H:%M:%S')
            }}
        )

        # Close the connection
        # client.close()

    # if request.method == 'GET':

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
    # print(events)
    # print(pending)
    # events = [{"id": "111g23u", "compName" : "Google", "start" : "2024-12-02" , "round" : 0}]

    # Close the connection
    # client.close()
    return render(request, '4_2_head_allot.html', {"pending": pending, "events": events})
        

def head_track_placements(request):
    return render(request, '4_3_head_track.html')

def head_review_feedback(request):
    return render(request, '4_4_head_reviewfb.html')

def head_postjob(request):
    # Context dictionary
    dept_codes = Department.objects.values_list('d_abbr_code', flat=True)
    dept_codes_list = list(dept_codes)  # Convert to a list if needed
    # print(dept_codes_list)
    context = {
        'dept_codes_list': dept_codes_list
    }
    return render(request, '5_2_company_postjob.html', context=context)
