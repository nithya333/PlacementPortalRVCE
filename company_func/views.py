import csv
from django.db import connection
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import psycopg2
import base64
from base64 import b64encode
from django.core.files.storage import FileSystemStorage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from db import get_db
from .models import Company, Department, Education, Students
from pymongo import MongoClient
import time
from bson import ObjectId
from datetime import datetime, timedelta
from django import forms


# Create your views here.

def company_home(request):
    # MongoDB Connection
    # client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
    # db = client['Placement']
    db = get_db()  # Reuse the shared MongoDB connection
    job_collection = db['job']

    events = []
    jobs = list(job_collection.find({"job_companyId": request.session.get('u_id'), "job_stage": 1}))
    for job in jobs:
        events.append({"id": job["_id"], "compName": f"PPT - {job['job_type']}", "start": job["job_pptDate"], "round": 0})
        events.append({"id": job["_id"], "compName": f"OA - {job['job_type']}", "start": job["job_oaDate"], "round": 1})
        events.append({"id": job["_id"], "compName": f"Interview - {job['job_type']}", "start": job["job_interviewDate"], "round": 2})
    # print(jobs)  

    comp_id = request.session.get('u_id')
    company = Company.objects.get(cp_id = comp_id)
    cp_name = company.cp_name
    cp_type = company.cp_type
    cp_location = company.cp_location
    cp_contact_email = company.cp_contact_email
    cp_contact_phone = company.cp_contact_phone
    cp_contact_name = company.cp_contact_name
    company_details = {
        "cp_id": comp_id,
        "cp_name": cp_name,
        "cp_type": cp_type,
        "cp_location": cp_location,
        "cp_contact_email": cp_contact_email,
        "cp_contact_phone": cp_contact_phone,
        "cp_contact_name": cp_contact_name
    }


    return render(request, '5_1_company_home.html', {"events": events, "company_details": company_details})


def company_postjob(request):
    # Context dictionary
    dept_codes = Department.objects.values_list('d_abbr_code', flat=True)
    dept_codes_list = list(dept_codes)  # Convert to a list if needed
    # print(dept_codes_list)
    context = {
        'dept_codes_list': dept_codes_list
    }
    return render(request, '5_2_company_postjob.html', context=context)

@csrf_exempt
def company_postjob_submit(request):
    if request.method == "POST":
        print(request.POST)
        # Parse the POST data
        post_data = request.POST 

        job_data = {}
        # Add additional fields or modify the data

        job_data['_id'] = str(ObjectId())  # Generate a new ObjectId

        job_data["job_title"] = request.POST.get("job_title").strip()
        job_data["job_type"] = request.POST.get("job_type")
        job_data["job_duration"] = request.POST.get("job_duration")
        job_data["job_desc"] = request.POST.get("job_desc").strip()
        job_data["job_domain"] = request.POST.get("job_domain")
        job_data["job_salary"] = (float)(request.POST.get("job_salary"))
        job_data["cgpaMinCriteria"] = (float)(request.POST.get("cgpaMinCriteria"))
        job_data["cgpaMaxCriteria"] = (float)(request.POST.get("cgpaMaxCriteria"))
        job_data["degreeCriteria"] = request.POST.get("degreeCriteria")

        job_data["job_locations"] = [word.strip() for word in request.POST.get("job_locations[]").split(",")]
        job_data["deptsCriteria"] = request.POST.getlist("deptsCriteria[]")
        # job_data["yearOfPassingCriteria"] = request.POST.getlist("yearOfPassingCriteria[]")
        job_data["yearOfPassingCriteria"] = [int(year) for year in request.POST.getlist("yearOfPassingCriteria[]")]
        job_data["skillsPreferences"] = [word.strip() for word in request.POST.get("skillsPreferences[]").split(",")]
        
        job_data["job_enrolledDate"] = time.strftime("%Y-%m-%d %H:%M:%S")
        job_data["job_pptDate"] = None
        job_data["job_oaDate"] = None
        job_data["job_interviewDate"] = None
        job_data["job_status"] = 0 # 0 - upcoming, 1 - ongoing, 2 - closed
        job_data["job_stage"] = 0 # 0 - company_posted, 1 - college alloted, 2 - student application, 3 - OA, 4 - Interview, 5 - Done
        job_data["job_companyId"] = request.session.get('u_id', 0)

        compId = job_data["job_companyId"]
        comp = Company.objects.get(cp_id = compId)
        compName = comp.cp_name

        # job_data["job_companyName"] = request.session.get('u_name', 'Guest')
        job_data["job_companyName"] = compName
        job_data["job_numStudents"] = 0
        job_data["job_lastUpdated"] = time.strftime("%Y-%m-%d %H:%M:%S")

        # Connect to MongoDB
        # client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
        # db = client['Placement']  # Database name
        db = get_db()  # Reuse the shared MongoDB connection
        job_collection = db['job']  # Collection name
        
        # Insert into MongoDB
        result = job_collection.insert_one(job_data)
        
        # Close the connection
        # client.close()

        # return render(request, '5_1_company_home.html')
        return redirect('/company/home')
    
def company_ong_recruitments(request):
    # client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
    # db = client['Placement']
    db = get_db()  # Reuse the shared MongoDB connection
    job_collection = db['job']

    # Fetch jobs with status "upcoming"
    jobs = list(job_collection.find({"job_companyId": request.session.get('u_id'), "job_status": {"$in": [0, 1]}}))
    for job in jobs:
        job['job_id'] = str(job['_id'])
        if (job['job_stage'] == 1):
            job_reglastdate = (datetime.strptime(job['job_pptDate'], "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")
            job['job_reglastdate'] = job_reglastdate
            reg_last_date = datetime.strptime(job['job_reglastdate'], "%Y-%m-%d")
            current_date = datetime.now()
            if reg_last_date < current_date:
                # Update the ob_stage in the job collection to 2
                job_collection.update_one(
                    {"_id": job["_id"]},
                    {"$set": {"job_stage": 2}}
                )
                # Set all applicants appl_stage to 2
                appl_collection = db['application']
                appl_collection.update_many(
                    {"appl_job_id": job["_id"]},
                    {"$set": {"appl_stage": 2}}
                )
                print(f"Job {job['_id']} has been moved to stage 2")
                return redirect('/company/ong_recruitments')
        elif (job['job_stage'] == 3):
            current_date = datetime.now()
            ppt_date = datetime.strptime(job['job_pptDate'], "%Y-%m-%d")
            if ppt_date < current_date:
                # Update the ob_stage in the job collection to 4
                job_collection.update_one(
                    {"_id": job["_id"]},
                    {"$set": {"job_stage": 4}}
                )
                # Set all applicants appl_stage to 2
                appl_collection = db['application']
                appl_collection.update_many(
                    {"appl_job_id": job["_id"]},
                    {"$set": {"appl_stage": 4}}
                )
                print(f"Job {job['_id']} has been moved to stage 4")
                return redirect('/company/ong_recruitments')

    return render(request, '5_3_company_ongoing.html', {"jobs": jobs, "stat": 1})

   
def company_past_recruitments(request):
    # client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
    # db = client['Placement']
    db = get_db()  # Reuse the shared MongoDB connection
    job_collection = db['job']

    jobs = list(job_collection.find({"job_companyId": request.session.get('u_id'), "job_status": 2}))
    for job in jobs:
        job['job_id'] = str(job['_id'])
    return render(request, '5_3_company_ongoing.html', {"jobs": jobs, "stat": 0})


@csrf_exempt  
def company_ong_recruitments_vmore(request, job_id):
    if request.method == 'GET':
        # Fetch the job_id from the URL
        print(job_id)

        # MongoDB Connection
        # client = MongoClient('mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Update with your MongoDB connection string
        # db = client['Placement']
        db = get_db()  # Reuse the shared MongoDB connection

        job_collection = db['job']
        appl_collection = db['application']
        oa_collection = db['oa_interview']

        job = job_collection.find_one({"_id": job_id})
        if job['job_stage'] == 0:
            job['job_reglastdate'] = ''
        else:
            job_reglastdate = (datetime.strptime(job['job_pptDate'], "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")
            job['job_reglastdate'] = job_reglastdate
        job_details = job
        job_details['job_id'] = str(job_details['_id'])
        if oa_collection.find_one({"job_id": job_id}):
            oa_details = oa_collection.find_one({"job_id": job_id})
            job_details['oa_link'] = oa_details['oa_link']
            job_details['oa_date'] = oa_details['oa_date']
            if 'interview_link' in oa_details:
                job_details['interview_link'] = oa_details['interview_link']
                job_details['interview_date'] = oa_details['interview_date']

        applications = list(appl_collection.find({"appl_job_id": job_id, "appl_stage": job_details['job_stage']}))
        # print(applications)
        applicants = []
        for applicantion in applications:
            # comp_id = request.session.get('u_id')
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
        print(applicants)
        stages = [[0, "You have posted a job offer, Waiting for college approval", job_details['job_enrolledDate']], [1, "College has scheduled slots, registrations open" , job_reglastdate], [2, "Applications closed, Waiting for college shortlists", ''], [3, "Shortlisted at college level", ''], [4, "PPT done", job_details['job_pptDate']], [5, "OA - Round 1 done", job_details['job_oaDate']], [6, "Interview - Round 2 done", job_details['job_interviewDate']]]
        return render(request, '5_4_company_ongoing_vmore.html', {"job_details": job_details, "applicants" : applicants, "stages": stages})
    else:
        return render(request, '5_1_company_home.html')

@csrf_exempt
def company_oa_int_link(request):
    if request.method == "POST":
        print(request.POST)
        job_id = request.POST.get('job_id')
        conduct_link = request.POST.get('conduct_link')
        conduct_date = request.POST.get('conduct_date')
        job_stage = request.POST.get('job_stage')

        # MongoDB Connection
        # client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection string
        # db = client['Placement']
        db = get_db()
        oa = db['oa_interview']

        if job_stage == "4":
            oa_data = {
                "job_id": job_id,
                "oa_link": conduct_link,
                "oa_date": conduct_date
            }
            result = oa.insert_one(oa_data)
        else:
            result = oa.update_one(
                {"job_id": job_id},
                {"$set": {"interview_link": conduct_link, "interview_date": conduct_date}}
            )
        return redirect('/company/ong_recruitments')

@csrf_exempt
def company_results(request):
    if request.method == "POST":
        job_id = request.POST.get('job_id')
        stage = (int)(request.POST.get('stage'))
        result_file = request.FILES["result_file"]
        # Read and decode the file
        decoded_file = result_file.read().decode("utf-8").splitlines()
        reader = csv.reader(decoded_file)
        header = next(reader)  
        # Find which column is "Application ID" and which column is "Result"
        print(header)
        appl_id_index = -1
        st_id_index = -1
        result_index = -1
        
        # Check for "Application ID"
        if "Application ID" in header:
            appl_id_index = header.index("Application ID")
        elif "ApplicationID" in header:
            appl_id_index = header.index("ApplicationID")
        elif "Application_ID" in header:
            appl_id_index = header.index("Application_ID")

        # Check for "Student ID"
        if "Student ID" in header:
            st_id_index = header.index("Student ID")
        elif "StudentID" in header:
            st_id_index = header.index("StudentID")
        elif "Student_ID" in header:
            st_id_index = header.index("Student_ID")
        if "Result" in header:
            result_index = header.index("Result")
        if appl_id_index == -1 or result_index == -1 or st_id_index == -1:
            return redirect('/company/ong_recruitments')
        
        results = []
        for row in reader:

            # Assuming CSV columns: Student ID, Name, Result
            results.append({
                "Application ID": row[appl_id_index],
                "Student ID": row[st_id_index],
                "Result": row[result_index]
            })
        
        # MongoDB Connection
        # client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection string
        # db = client['Placement']
        db = get_db()
        appl_collection = db['application']
        job_collection = db['job']
        stage_name = ""
        next_stage = stage
        if stage == 4:
            stage_name = "oa"
            next_stage = 5
        elif stage == 5:
            stage_name = "interview"
            next_stage = 6
        for result in results:
            print(result)
            # Update the result in the application collection
            if result["Result"] == "Select":
                if stage == 4:
                    appl_collection.update_one(
                        {"appl_id": result["Application ID"]},
                        {"$set": {f"appl_{stage_name}_result": result["Result"], "appl_stage": next_stage}}
                    )
                else:
                    appl_collection.update_one(
                        {"appl_id": result["Application ID"]},
                        {"$set": {f"appl_{stage_name}_result": result["Result"], "appl_stage": next_stage, "appl_status": 1}}
                    )
                    final_rec_collection = db['final_recruits']
                    final_rec_data = {
                        "job_id": job_id,
                        "appl_id": result["Application ID"],
                        "student_id": result["Student ID"],
                    }
                    final_rec_collection.insert_one(final_rec_data)
            else:
                if stage == 4:
                    appl_collection.update_one(
                        {"appl_id": result["Application ID"]},
                        {"$set": {f"appl_{stage_name}_result": result["Result"]}}
                    )
                else:
                    appl_collection.update_one(
                        {"appl_id": result["Application ID"]},
                        {"$set": {f"appl_{stage_name}_result": result["Result"], "appl_status": 2}}
                    )
        if stage == 4:
            job_collection.update_one(
                {"_id": job_id},
                {"$set": {"job_stage": next_stage}}
            )
        else:
            job_collection.update_one(
                    {"_id": job_id},
                    {"$set": {"job_stage": next_stage, "job_status": 2}}
                )
        # print(results)
        # csv_file = forms.FileField(label="Upload CSV File")
        # print(csv_file)
        return redirect('/company/ong_recruitments')


# @csrf_exempt
# def student_profile_submit(request):
#     if request.method == "POST":
#         print(request.POST)

#         st_name = request.POST.get('fullName').strip()
#         st_dob = request.POST.get('dob')
#         st_gender = request.POST.get('gender')
#         st_section = request.POST.get('sec')
#         st_email = request.POST.get('email').strip()
#         st_phone = request.POST.get('phone').strip()
#         st_id = request.POST.get('usn').strip()
#         st_year_of_passing = request.POST.get('yearOfGraduation').strip()
#         ug_pg = request.POST.get('UGPG') 
#         if ug_pg == "ug":
#             st_program = bin(0)[2:]
#         else:
#             st_program = bin(1)[2:]
#         is_spc = request.POST.get('spc') 
#         if is_spc == "yes":
#             spc_id = request.POST.get('spc_id')
#             spc_stud_id = st_id
#         dept = request.POST.get('branch')
#         departments = Department.objects.get(d_abbr_code = dept)
#         st_dept_id = departments.d_id
#         # print(departments.d_id)

#         e_program = st_program
#         e_student_id = st_id
#         e_cgpa = request.POST.get('cgpa')
#         e_10thmarks = request.POST.get('tenthMarks')
#         e_10thstream = request.POST.get('tenthStream')
#         e_12thmarks = request.POST.get('twelfthMarks')
#         e_12thstream = request.POST.get('twelfthStream')
#         e_backlogs = request.POST.get('backlogs')
#         e_be_cgpa = request.POST.get('be_cgpa') if 'be_cgpa' in request.POST else None

#         w_program = st_program
#         w_student_id = st_id
#         w_job_title = request.POST.getlist('w_jobtitle[]') if 'w_jobtitle[]' in request.POST else []
#         w_company_name = request.POST.getlist('w_compname[]') if 'w_compname[]' in request.POST else []
#         w_experience_months = request.POST.getlist('w_jobmonths[]') if 'w_jobmonths[]' in request.POST else []

#         sk_student_id = st_id
#         sk_technical = request.POST.getlist('technicalSkills[]') if 'technicalSkills[]' in request.POST else []
#         sk_soft = request.POST.getlist('softSkills[]') if 'softSkills[]' in request.POST else []
#         sk_certifications = request.POST.getlist('certifications[]') if 'certifications[]' in request.POST else []
#         sk_technologies = request.POST.getlist('technologies[]') if 'technologies[]' in request.POST else []
#         sk_achievements = request.POST.getlist('achievements[]') if 'achievements[]' in request.POST else []
#         sk_languages = request.POST.getlist('languages[]') if 'languages[]' in request.POST else []
#         sk_interested_domains = request.POST.getlist('domains[]') if 'domains[]' in request.POST else []
#         sk_project_name = request.POST.getlist('sk_project_name[]') if 'sk_project_name[]' in request.POST else []
#         sk_project_desc = request.POST.getlist('sk_project_desc[]') if 'sk_project_desc[]' in request.POST else []

#         a = Resumes(fi_name=st_name, fi_data=request.FILES['resume'])
#         a.save()

#         conn = psycopg2.connect(
#         host="localhost",
#         database="placement_sql",
#         user="postgres",
#         password="cse"
#         )
#         cursor = conn.cursor()

#         # Fetch the PDF data
#         cursor.execute("SELECT fi_data FROM resumes WHERE fi_id = %s", ('3'))
#         pdf_data = cursor.fetchone()[0]

#         # Return the PDF as an HTTP response
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = f'inline; filename="document_{3}.pdf"'
#         response.write(pdf_data)

#         cursor.close()
#         conn.close()

#         with connection.cursor() as cursor:
#             # Update students table
#             cursor.execute("""
#                 UPDATE students
#                 SET st_program = %s, st_name = %s, st_email = %s, st_phone = %s, st_dept_id = %s, st_dob = %s, 
#                     st_year_of_passing = %s, st_section = %s, st_gender = %s
#                 WHERE st_id = %s
#             """, (st_program, st_name, st_email, st_phone, st_dept_id, st_dob, st_year_of_passing, st_section, st_gender, st_id))

#             # Update education table
#             cursor.execute("""
#                 UPDATE education
#                 SET e_10thmarks = %s, e_10thstream = %s, e_12thmarks = %s, e_12thstream = %s, e_cgpa = %s, 
#                     e_backlogs = %s, e_be_cgpa = %s, e_program = %s
#                 WHERE e_student_id = %s
#             """, (e_10thmarks, e_10thstream, e_12thmarks, e_12thstream, e_cgpa, e_backlogs, e_be_cgpa, e_program, e_student_id))

#             # Update skills table
#             cursor.execute("""
#                 UPDATE skills
#                 SET sk_technical = %s, sk_soft = %s, sk_certifications = %s, sk_technologies = %s, sk_achievements = %s, 
#                     sk_languages = %s, sk_interested_domains = %s, sk_project_name = %s, sk_project_desc = %s
#                 WHERE sk_student_id = %s
#             """, (sk_technical, sk_soft, sk_certifications, sk_technologies, sk_achievements, sk_languages, 
#                 sk_interested_domains, sk_project_name, sk_project_desc, sk_student_id))

#             # Update work_experience table
#             if w_job_title and w_company_name and w_experience_months and len(w_job_title) == len(w_company_name) == len(w_experience_months):
#                 for job_title, company, months in zip(w_job_title, w_company_name, w_experience_months):
#                     if job_title and company and months:  # Skip empty rows
#                         cursor.execute("""
#                             UPDATE work_experience
#                             SET w_job_title = %s, w_company_name = %s, w_experience_months = %s, w_program = %s
#                             WHERE w_student_id = %s AND w_job_title = %s
#                         """, (job_title, company, months, w_program, w_student_id, job_title))

#             # Update spc table (if applicable)
#             if is_spc == "yes":
#                 cursor.execute("""
#                     UPDATE spc
#                     SET spc_stud_id = %s
#                     WHERE spc_id = %s
#                 """, (spc_stud_id, spc_id))


#         return render(request, '2_1_student_home.html')
#     else:
#         return render(request, 'register_stud.html')
    

