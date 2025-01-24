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

from admin_func.models import Department, Education, Feedback, Students, Users
from db import get_db
from django.db.models import F

def head_home(request):
    head_id = request.session.get('u_id')
    head = Users.objects.get(u_id = head_id)
    head_name = head.u_name
    head_email = head.u_email

    dept_codes_all = Department.objects.values_list('d_abbr_code', flat=True)

    # dept_codes_ug = Department.objects.filter(d_program=0).values_list('d_abbr_code', flat=True)
    # dept_codes_pg = Department.objects.filter(d_program=1).values_list('d_abbr_code', flat=True)
    
    dept_codes_all_list = list(dept_codes_all)

    
    dept_codes_ug_list = [d for d in dept_codes_all_list if len(d) == 2]
    dept_codes_pg_list = [d for d in dept_codes_all_list if len(d) == 3]
    

    head_details = {
        "head_role" : "Placement Head of RVCE",
        "head_name" : head_name,
        "head_email" : head_email,
        "ug_num" : len(dept_codes_ug_list),
        "ug_list": dept_codes_ug_list,
        "pg_num" : len(dept_codes_pg_list),
        "pg_list": dept_codes_pg_list,
    }
    return render(request, '4_1_head_home.html', {"head_details" : head_details})


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
        # client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')
        # db = client['Placement']
        db = get_db()  # Reuse the shared MongoDB connection

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
    # client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
    # db = client['Placement']
    db = get_db()  # Reuse the shared MongoDB connection
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
    dept_codes = Department.objects.values_list('d_abbr_code', flat=True)
    dept_codes_list = list(dept_codes)  # Convert to a list if needed
    # print(dept_codes_list)

    db = get_db()  # Reuse the shared MongoDB connection

    job_collection = db['job']
    appl_collection = db['application']
    oa_collection = db['oa_interview']

    # Find all jobs
    jobs = list(job_collection.find())
    # job = job_collection.find_one({"_id": job_id})
    jobs_list = []
    for job in jobs:
        job_details = {}
        # job_details = job
        job_details['job_id'] = str(job['_id'])
        job_id = job_details['job_id']

        job_details['job_title'] = job['job_title'] or ''
        job_details['job_type'] = job['job_type'] or ''
        # job_details['job_duration'] = job['job_duration'] or ''
        # job_details['job_desc'] = job['job_desc'] or ''
        job_details['job_salary'] = job['job_salary'] or ''
        # job_details['cgpaMinCriteria'] = job['cgpaMinCriteria'] or ''
        # job_details['cgpaMaxCriteria'] = job['cgpaMaxCriteria'] or ''
        job_details['degreeCriteria'] = job['degreeCriteria'] or ''
        # job_details['job_locations'] = job['job_locations'] or ''
        job_details['deptsCriteria'] = job['deptsCriteria'] or ''
        # job_details['yearOfPassingCriteria'] = job['yearOfPassingCriteria'] or ''
        # job_details['job_enrolledDate'] = job['job_enrolledDate'] or ''
        # job_details['job_pptDate'] = job['job_pptDate'] or ''
        # job_details['job_oaDate'] = job['job_oaDate'] or ''
        # job_details['job_interviewDate'] = job['job_interviewDate'] or ''
        job_details['job_stage'] = job['job_stage'] or ''
        # job_details['job_companyId'] = job['job_companyId'] or ''
        job_details['job_companyName'] = job['job_companyName'] or ''
        job_details['job_id'] = job_id or ''

        applications = list(appl_collection.find({"appl_job_id": job_id, "appl_stage": job_details['job_stage']}))
        # print(applications)
        applicants = []
        
        for application in applications:
            # comp_id = request.session.get('u_id')
            stud_details = Students.objects.get(st_id = application["appl_student_id"])
            applicant = {}
            applicant['appl_id'] = application['appl_id']
            applicant["st_id"] = stud_details.st_id
            applicant["st_name"] = stud_details.st_name
            applicant["st_email"] = stud_details.st_email
            applicant["st_section"] = stud_details.st_section
            # applicant["st_year_of_passing"] = stud_details.st_year_of_passing

            stud_edu_details = Education.objects.get(e_student_id = application["appl_student_id"])
            applicant["e_cgpa"] = stud_edu_details.e_cgpa
            applicant["e_10thmarks"] = stud_edu_details.e_10thmarks
            applicant["e_12thmarks"] = stud_edu_details.e_12thmarks
            # applicant["e_backlogs"] = stud_edu_details.e_backlogs

            applicants.append(applicant)
            # cp_name = company.cp_name
            # cp_type = company.cp_type
            # cp_location = company.cp_location
            # cp_contact_email = company.cp_contact_email
            # cp_contact_phone = company.cp_contact_phone
            # cp_contact_name = company.cp_contact_name
            # company_details = {
            #     "cp_id": comp_id,
            #     "cp_name": cp_name,
            #     "cp_type": cp_type,
            #     "cp_location": cp_location,
            #     "cp_contact_email": cp_contact_email,
            #     "cp_contact_phone": cp_contact_phone,
            #     "cp_contact_name": cp_contact_name
            # }
        # print(applicants)
        job_details["applicants"] = applicants
        jobs_list.append(job_details)

    # stages = [[0, "You have posted a job offer, Waiting for college approval", job_details['job_enrolledDate']], [1, "College has scheduled slots, registrations open" , job_reglastdate], [2, "Applications closed, Waiting for college shortlists", ''], [3, "Shortlisted at college level", ''], [4, "PPT done", job_details['job_pptDate']], [5, "OA - Round 1 done", job_details['job_oaDate']], [6, "Interview - Round 2 done", job_details['job_interviewDate']]]
    # print(jobs_list)   
    return render(request, '4_3_head_track.html', {"jobs_list": jobs_list, "dept_list": dept_codes_list})

def head_review_feedback(request):
    all_fb = Feedback.objects.all()
    feedbacks = []
    for fb in all_fb:
        f_rating = fb.f_rating
        f_suggestion = fb.f_suggestion
        f_usertype = fb.f_usertype
        fb_dict = {"f_rating": f_rating, "f_suggestion": f_suggestion, "f_usertype": f_usertype}
        feedbacks.append(fb_dict)
    # print(feedbacks)
    return render(request, '4_4_head_reviewfb.html', {"feedbacks": feedbacks})

