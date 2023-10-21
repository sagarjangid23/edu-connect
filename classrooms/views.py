from django.shortcuts import render, redirect
from fpdf import FPDF
from django.http import HttpResponse
from django.contrib import messages
import jwt
from django.conf import settings
from datetime import timedelta, datetime
from django.utils import timezone
from .forms import GenerateCertificateForm, VerifyCertificateForm
from .models import Teacher, Student, Result, Certificate


def home(request):
    return render(request, "home.html")


def display_teachers(request):
    teachers = Teacher.objects.all()
    context = {
        "title": "Teacher",
        "teachers": teachers,
    }
    return render(request, "display.html", context)


def display_students(request):
    students = Student.objects.all()
    context = {
        "title": "Student",
        "students": students,
    }
    return render(request, "display.html", context)


def corresponding_students(request, teacher_id):
    students = Teacher.objects.filter(id=teacher_id).first().students.all()

    if students:
        return render(request, "corresponding_students.html", {"students": students})
    else:
        messages.error(request, "No corresponding students for this teacher.")
        return redirect('teachers')


def corresponding_teachers(request, student_id):
    teachers = Student.objects.filter(id=student_id).first().teachers.all()
    
    if teachers:
        return render(request, "corresponding_teachers.html", {"teachers": teachers})
    else:
        return redirect('students')


def generate_pdf(data):
    pdf = FPDF("L", "mm", "Letter")
    pdf.add_page()
    pdf.set_margin(20)

    pdf.set_font("helvetica", "BIU", 24)
    pdf.cell(0, 20, "Certificate of Completion", 0, 1, "C")

    pdf.set_font("helvetica", "I", 18)

    text = f"This is to certify that `{data['student']}`, son of `{data['parent']}` has successfully completed the `{data['subject']}` course with a grade of `{data['grade']}`.\nThis certificate valid from {data['issued']}  to  {data['expired']}."
    pdf.multi_cell(0, 18, text, 0, align="J")
    pdf.ln()

    pdf.set_font("helvetica", "I", 12)
    pdf.cell(0, 6, f"Certificate token:", 0, 1)
    pdf.set_font("helvetica", "I", 8)
    pdf.cell(0, 6, f"{data['token']}", 0, 1)
    pdf.ln()

    pdf.set_font(size=24, style="I")
    pdf.cell(0, 8, data["teacher"], 0, 1, "C")
    pdf.set_font(style="I", size=14)
    pdf.cell(0, 8, "(teacher signature)", 0, 1, "C")
    pdf.image(data["signature"], x="C", w=60)
    return pdf


def generate_certificate_token(certificate_id):
    """
    Generates a token for a certificate.
    :return: A generated token.
    """
    iat = datetime.now(tz=timezone.utc)
    exp = datetime.now(tz=timezone.utc) + timedelta(days=180)
    payload = {
        "id": certificate_id,
        "iat": iat,
        "exp": exp,
    }
    encoded_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return encoded_token


def generate_certificate(request):
    if request.method == "POST":
        form = GenerateCertificateForm(request.POST)

        if form.is_valid():
            teacher = form.cleaned_data["teacher"]
            student = form.cleaned_data["student"]

            result = Result.objects.filter(teacher=teacher, student=student).first()

            if result:
                certificate, created = Certificate.objects.get_or_create(result=result)

                if created:
                    token = generate_certificate_token(certificate.id)
                    certificate.token = token
                    certificate.save()

                try:
                    decoded_token = jwt.decode(
                        str(certificate.token),
                        settings.SECRET_KEY,
                        algorithms=["HS256"],
                    )

                    # Retrieve result, teacher and student info
                    teacher = certificate.result.teacher
                    student = certificate.result.student
                    issued = datetime.utcfromtimestamp(decoded_token["iat"]).date()
                    expired = datetime.utcfromtimestamp(decoded_token["exp"]).date()

                    data = {
                        # result details
                        "issued": issued,
                        "expired": expired,
                        "grade": result.grade,
                        "token": certificate.token,
                        # teacher details
                        "teacher": teacher.name,
                        "subject": teacher.subject,
                        "signature": teacher.signature.path,
                        # student details
                        "student": student.name,
                        "parent": student.parent_name,
                    }

                    filename = f"{data['student']}-{data['subject']}-certificate.pdf"

                    # Generate pdf
                    pdf = generate_pdf(data)
                    response = HttpResponse(
                        bytes(pdf.output()), content_type="application/pdf"
                    )
                    response["Content-Disposition"] = f'filename="{filename}"'

                    return response
                except jwt.ExpiredSignatureError:
                    messages.error(request, "Certificate has expired.")
                except Exception as e:
                    messages.error(request, f"Some issues occur. {e}")
            else:
                messages.error(request, "No certificate found for this pair.")
    else:
        form = GenerateCertificateForm()

    context = {"form": form}
    return render(request, "generate_certificate.html", context)


def verify_certificate(request):
    if request.method == "POST":
        form = VerifyCertificateForm(request.POST)

        if form.is_valid():
            certificate_token = form.cleaned_data["certificate_token"]

            try:
                jwt.decode(certificate_token, settings.SECRET_KEY, algorithms=["HS256"])
                messages.success(request, "Yes, this certificate is verified.")
            except jwt.ExpiredSignatureError:
                messages.error(request, "Certificate has expired.")
            except jwt.InvalidTokenError:
                messages.error(request, "Invalid certificate token.")
            except:
                messages.error(request, f"Some issues occur.")
    else:
        form = VerifyCertificateForm()

    context = {"form": form}
    return render(request, "verify_certificate.html", context)
