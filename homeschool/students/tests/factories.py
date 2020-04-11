import factory

class StudenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "students.Student"

    school = factory.SubFactory("homeschool.schools.tests.factories.SchoolFactory")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")