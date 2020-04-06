import uuid
from django.db import models

# Create your models here.
class Course(models.Model):
	""" A Course is a container for the tasks in a subject area """
	name = models.CharField(max_length=256)
	grade_level = models.ForeignKey("schools.GradeLevel", on_delete=models.CASCADE)

	def __str__(self):
		return self.name

class CourseTask(models.Model):
	"""A student's required action in a course."""

	course = models.ForeignKey("courses.Course" , on_delete=models.CASCADE)
	uuid = models.UUIDField(default=uuid.uuid4, db_index=True)
	description = models.TextField()

	def __str__(self):
		return self.description