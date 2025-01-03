from django.db import models
from django.contrib.postgres.fields import ArrayField

class Users(models.Model):
    u_type = models.CharField(max_length=15)
    u_id = models.CharField(primary_key=True, max_length=15)
    u_pass = models.CharField(max_length=30, default="rvce123")
    u_email = models.CharField(max_length=50, blank=True, null=True)
    u_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'

class Department(models.Model):
    d_id = models.BigIntegerField(primary_key=True)
    d_program = models.BooleanField(default=False)
    d_name = models.CharField(max_length=60)
    d_hod = models.CharField(max_length=30, blank=True, null=True)
    d_domains = ArrayField(
            models.CharField(blank=True, null=True)
        )
    # d_domains = models.JSONField(blank=True, null=True)  # For character varying[]
    d_establish_year = models.BigIntegerField(blank=True, null=True)
    d_intake = models.BigIntegerField(blank=True, null=True)
    d_abbr_code = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'department'

class Education(models.Model):
    e_program = models.BooleanField(default=False)
    e_student_id = models.OneToOneField('Students', models.DO_NOTHING, primary_key=True)
    e_cgpa = models.FloatField(blank=True, null=True)
    e_10thmarks = models.FloatField(blank=True, null=True)
    e_12thmarks = models.FloatField(blank=True, null=True)
    e_be_cgpa = models.FloatField(blank=True, null=True)
    e_10thstream = models.CharField(blank=True, null=True)
    e_12thstream = models.CharField(blank=True, null=True)
    e_backlogs = models.BigIntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'education'

class Spc(models.Model):
    spc_id = models.CharField(primary_key=True)
    spc_stud_id = models.OneToOneField('Students', models.DO_NOTHING)
    spc_activity_count = models.BigIntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'spc'


class Students(models.Model):
    st = models.OneToOneField('Users', models.CASCADE, primary_key=True)
    st_program = models.BooleanField(default=False)
    st_name = models.CharField(max_length=60)
    st_email = models.CharField(max_length=50, blank=True, null=True)
    st_phone = models.BigIntegerField(blank=True, null=True)
    st_dept_id = models.ForeignKey(Department, models.DO_NOTHING)
    st_section = models.CharField(max_length=5, blank=True, null=True)
    st_year_of_passing = models.BigIntegerField(blank=True, null=True)
    st_dob = models.DateField(blank=True, null=True)
    st_is_placed = ArrayField(
        models.BooleanField(default=False), size=2, blank=True, null=True
    )
    st_gender = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'students'

class Coordinator(models.Model):
    cd_id = models.OneToOneField('Users', models.CASCADE, primary_key=True)
    cd_program = models.BooleanField(default=False)
    cd_name = models.CharField(max_length=40, blank=True, null=True)
    cd_email = models.CharField(max_length=30, blank=True, null=True)
    cd_phone = models.BigIntegerField(blank=True, null=True)
    cd_dept_id = models.ForeignKey('Department', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'coordinator'

class Company(models.Model):
    cp = models.OneToOneField('Users', models.CASCADE, primary_key=True)
    cp_name = models.CharField(max_length=30)
    cp_type = models.CharField(max_length=40, blank=True, null=True)
    cp_location = models.CharField(max_length=20, blank=True, null=True)
    cp_contact_name = models.CharField(max_length=60, blank=True, null=True)
    cp_contact_email = models.CharField(max_length=40, blank=True, null=True)
    cp_contact_phone = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company'

class Resumes(models.Model):
    # title = models.CharField(max_length=255)
    # uploaded_at = models.DateTimeField(auto_now_add=True)
    fi_id = models.BigAutoField(primary_key=True)
    fi_name = models.CharField(max_length=60, blank=True, null=True)
    fi_data = models.FileField(upload_to='resumes/')  # Specify the upload path

    class Meta:
        managed = False
        db_table = 'resumes'