import csv
import os
import pprint

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Ingest CSV data from Homeschool Skedtrack"

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("grade")

    def handle(self, *args, **options):
        self.stdout.write("Check for user")
        user = User.objects.get(email=options["email"])

        self.stdout.write("Read in CSV data")

        courses = []
        for dirpath, dirnames, filenames in os.walk("courses_exports"):
            for filename in filenames:
                courses.append(self.process_course(filename, f"{dirpath}/{filename}"))

        self.persist_to_school(user, options["grade"], courses)

    def process_course(self, course_name, file_path):
        self.stdout.write(f"Processing {course_name}...")
        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file.readlines())

        searching_tasks = True
        sequence = 1
        tasks = []
        row_length = 1
        for row in reader:
            if searching_tasks:
                # Stop searching after finding the task column labels.
                if row and row[0] == "Sequence":
                    searching_tasks = False
                    row_length = len(row)
                continue

            try:
                if sequence == int(row[0]):
                    tasks.append(row)
                    sequence += 1
            except ValueError:
                # Hit extra line from poor description wrapping.
                # Join this to the previous task.
                tasks[-1][-1] = "\n".join([tasks[-1][-1], row[0]])
                tasks[-1].extend(row[1:])

        # Clean up the cases when there were commas in the descriptions.
        description_index = 3
        for task in tasks:
            while len(task) != row_length:
                more_description = task.pop(description_index + 1)
                task[description_index] = ", ".join(
                    [task[description_index], more_description]
                )

        return {"name": course_name, "tasks": tasks}

    def persist_to_school(self, user, grade_level, courses):
        """Create a school with all its records."""
        print(user)
        print(grade_level)
        pprint.pprint(courses[0])