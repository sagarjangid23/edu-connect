from django.db import models


class Subject(models.Model):
    """Represents a subject in the education system."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    qualifications = models.CharField(max_length=50)
    signature = models.ImageField(upload_to="signatures/")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    students = models.ManyToManyField("Student", blank=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_email = models.EmailField(unique=True)
    teachers = models.ManyToManyField("Teacher")

    def __str__(self):
        return self.name


class Result(models.Model):
    GRADE_CHOICES = [
        ("A+", "A+"),
        ("A", "A"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B", "B"),
        ("B-", "B-"),
        ("C+", "C+"),
        ("C", "C"),
        ("C-", "C-"),
        ("D+", "D+"),
        ("D", "D"),
        ("D-", "D-"),
        ("F", "F"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_index=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, db_index=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    date_assigned = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.teacher.subject.name}"

    class Meta:
        unique_together = ["student", "teacher"]


class Certificate(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)

    def __str__(self):
        return str(self.result)
