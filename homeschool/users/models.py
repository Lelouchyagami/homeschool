from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property

# Create your models here.
class User(AbstractUser):
	@cached_property
	def school(self):
		return self.school_set.latest("id")