from django.contrib import admin
from .models import Teacher, Student, Result, Certificate, Subject

admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Result)
admin.site.register(Certificate)
