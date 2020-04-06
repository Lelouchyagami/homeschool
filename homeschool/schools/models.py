from django.conf import settings
from django.db import models


class School(models.Model):
    """A school to hold students"""

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The school administrator",
    )

class SchoolYear(models.Model):
	""" A school year to bound start and end dates of the academic year """
	school = models.ForeignKey("schools.School",on_delete=models.CASCADE)
	start_date = models.DateField()
	end_date = models.DateField()

class GradeLevel(models.Model):
	""" A student is in a Grade Level in a school """
	school_year = models.ForeignKey("schools.SchoolYear", on_delete=models.CASCADE)

