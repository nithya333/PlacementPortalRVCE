from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import psycopg2
import base64
from base64 import b64encode
# from .models import Department, Education, Students, Resumes
from pymongo import MongoClient
import time
from bson import ObjectId
# Create your views here.

from django.shortcuts import render
from django.http import JsonResponse
import json
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
db = client['placement']
job_collection = db['job']

def head_home(request):
    return render(request, '4_1_head_home.html')


def head_allot_slots(request):
    if request.method == 'GET':
        # Fetch jobs with status "upcoming"
        jobs = list(job_collection.find({"status": 0}))
        # Prepare calendar events
        events = []
        all_jobs = job_collection.find()
        for job in all_jobs:
            if "PPTdate" in job:
                events.append({"title": f"{job['company_name']} - PPT", "start": job["PPTdate"]})
            if "OAdate" in job:
                events.append({"title": f"{job['company_name']} - OA", "start": job["OAdate"]})
            if "InterviewDate" in job:
                events.append({"title": f"{job['company_name']} - Interview", "start": job["InterviewDate"]})
        print(jobs)
        return render(request, '4_2_head_allot.html', {"jobs": jobs, "events": events})

    elif request.method == 'POST':
        # Save allocated dates
        data = json.loads(request.body)
        # job_id = data.get('job_id')
        # ppt_date = data.get('ppt_date')
        # oa_date = data.get('oa_date')
        # interview_date = data.get('interview_date')

        # job_collection.update_one(
        #     {"_id": job_id},
        #     {"$set": {
        #         "PPTdate": ppt_date,
        #         "OAdate": oa_date,
        #         "InterviewDate": interview_date
        #     }}
        # )
        return JsonResponse({"success": True})
    return render(request, '4_2_head_allot.html')

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
