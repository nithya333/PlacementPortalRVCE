from django.contrib import admin
from .models import Department, Education, Students, Users

# Register your models here.
admin.site.register(Department)
admin.site.register(Education)
admin.site.register(Students)
admin.site.register(Users)