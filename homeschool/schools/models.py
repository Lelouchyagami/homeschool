from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from homeschool.core.models import DaysOfWeekModel

User = get_user_model()

class School(models.Model):
    """A school to hold students"""

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The school administrator",
    )

@receiver(post_save,sender=User)
def create_school(sender, instance, created, **kwargs):
    """A new user gets an associated school."""
    if created:
        School.objects.create(admin=instance)


class SchoolYear(DaysOfWeekModel):
    """A school year to bound start and end dates of the academic year"""

    school = models.ForeignKey("schools.School", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()


class GradeLevel(models.Model):
    """A student is in a grade level in a given school year"""

    name = models.CharField(max_length=128)
    school_year = models.ForeignKey("schools.SchoolYear", on_delete=models.CASCADE,related_name="grade_levels")

    def __str__(self):
        return self.name