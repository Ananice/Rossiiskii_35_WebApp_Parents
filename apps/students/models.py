from django.db import models
from django.conf import settings

from apps.parents.models import Parent
from apps.employees.models import Employee


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        null=True,
        blank=True
    )

    # То, что уже используется в views.py
    full_name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=50, unique=True)
    group = models.CharField(max_length=50, blank=True, null=True)
    specialty = models.CharField(max_length=255, blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    # Связи, которые подразумеваются логикой дашборда
    parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, blank=True)
    advisor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"
