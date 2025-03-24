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

from coordinator_func.models import Coordinator
from db import get_db
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
    coord_id = request.session.get('u_id')
    coord = Coordinator.objects.get(cd_id = coord_id)
    cd_program = coord.cd_program
    cd_program =- "UG" if cd_program == 0 else "PG"
    cd_email = coord.cd_email
    cd_phone = coord.cd_phone
    cd_dept_id = coord.cd_dept_id
    dept_details = Department.objects.get(d_id = cd_dept_id)
    dept_name = dept_details.d_name
    dept_establish_year = dept_details.d_establish_year
    dept_intake = dept_details.d_intake
    dept_abbr_code = dept_details.d_abbr_code

    coordinator_details = {
        "coord_id" : coord_id,
        "cd_program" : cd_program,
        "cd_email" : cd_email,
        "cd_phone" : cd_phone,
        "dept_name" : dept_name,
        "dept_establish_year" : dept_establish_year,
        "dept_intake" : dept_intake,
        "dept_abbr_code" : dept_abbr_code
    }
    return render(request, '3_1_coord_home.html', {"coordinator_details" : coordinator_details})

def coordinator_shortlist(request):
    # MongoDB Connection
    
    db = get_db()  # Reuse the shared MongoDB connection

    job_collection = db['job']

    # Fetch jobs with status "upcoming"
    jobs = list(job_collection.find({"job_stage": 2}))
    for job in jobs:
        job["job_id"] = job["_id"]
    return render(request, '3_2_coord_shortlist.html', {"jobs": jobs})

 

@csrf_exempt  
def coordinator_shortlist_vmore(request, job_id):
    db = get_db()  # Reuse the shared MongoDB connection

    job_collection = db['job']
    appl_collection = db['application']
    oa_collection = db['oa_interview']

    job = job_collection.find_one({"_id": job_id})
    job_details = job
    job_details['job_id'] = str(job_details['_id'])
    
    applications = list(appl_collection.find({"appl_job_id": job_id, "appl_stage": job_details['job_stage']}))
    applicants = []
    for applicantion in applications:
        stud_details = Students.objects.get(st_id = applicantion["appl_student_id"])
        applicant = applicantion
        applicant["st_id"] = stud_details.st_id
        applicant["st_name"] = stud_details.st_name
        applicant["st_email"] = stud_details.st_email
        applicant["st_section"] = stud_details.st_section
        applicant["st_year_of_passing"] = stud_details.st_year_of_passing

        stud_edu_details = Education.objects.get(e_student_id = applicantion["appl_student_id"])
        applicant["e_cgpa"] = stud_edu_details.e_cgpa
        applicant["e_10thmarks"] = stud_edu_details.e_10thmarks
        applicant["e_10thstream"] = stud_edu_details.e_10thstream
        applicant["e_12thmarks"] = stud_edu_details.e_12thmarks
        applicant["e_12thstream"] = stud_edu_details.e_12thstream
        applicant["e_backlogs"] = stud_edu_details.e_backlogs

        applicants.append(applicant)
       
    print(applicants)
       
    return render(request, '3_3_coord_shortlist_vmore.html', {"job_details" : job_details, "applicants" : applicants})


@csrf_exempt
def coordinator_shortlist_selected(request):
    if request.method == 'POST':
        db = get_db()
        job_collection = db['job']
        appl_collection = db['application']
        coord_id = request.session.get('u_id')

        job_id = request.POST.get('job_id')
        job_collection.update_one(
                {"_id": job_id},
                {"$set": {"job_stage": 3,  "job_shortlisted_by": coord_id}}
            )
        
        # print(request.POST)
        for key in request.POST:
            if key.startswith("appl_id_"):
                appl_id = key[8:]
                appl_result = request.POST.getlist(key)
                print(appl_result)
                if "on" in appl_result:
                    print(f"{appl_id} is selected")
                    appl_collection.update_one(
                        {"appl_id": appl_id},
                        {"$set": {"appl_stage": 3}}
                    )
                else:
                    print(f"{appl_id} is not selected")
                    appl_collection.update_one(
                        {"appl_id": appl_id},
                        {"$set": {"appl_status": 2}}
                    )

        return redirect('/coordinator/shortlist')

def coordinator_track(request):
    cd_dept_id = Coordinator.objects.get(cd_id =  request.session.get('u_id')).cd_dept_id
    d_abbr_code = Department.objects.get(d_id = cd_dept_id).d_abbr_code


    db = get_db()  # Reuse the shared MongoDB connection

    job_collection = db['job']
    appl_collection = db['application']
    oa_collection = db['oa_interview']

    jobs = list(job_collection.find())

    # job = job_collection.find_one({"_id": job_id})
    jobs_list = []
    for job in jobs:
        if d_abbr_code not in job["deptsCriteria"]:
            continue
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
    return render(request, '3_4_coord_track.html', {"jobs_list": jobs_list})


def coordinator_applied(request):
    # MongoDB Connection
    
    db = get_db()  # Reuse the shared MongoDB connection

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
        db = get_db()  # Reuse the shared MongoDB connection

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
    
