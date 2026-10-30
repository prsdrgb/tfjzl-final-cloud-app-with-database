from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from onlinecourse.models import Course, Lesson, Question, Choice, Enrollment


class Command(BaseCommand):
    help = "Adds a demo course, lessons, exam questions and a test learner"

    def handle(self, *args, **options):
        course, _ = Course.objects.get_or_create(
            name="Intro to Python",
            defaults={"description": "Learn the basics of Python programming from scratch."})
        for i, (t, c) in enumerate([
            ("Variables and Types", "Numbers, strings and booleans."),
            ("Loops and Conditions", "Using if, for and while."),
            ("Functions", "Writing reusable code with def."),
        ], start=1):
            Lesson.objects.get_or_create(course=course, order=i, defaults={"title": t, "content": c})

        data = [
            ("Which keyword defines a function in Python?", [("def", True), ("func", False), ("function", False)]),
            ("Which of these are Python data types?", [("int", True), ("str", True), ("char[]", False)]),
        ]
        for text, choices in data:
            q, made = Question.objects.get_or_create(course=course, question_text=text, defaults={"grade": 1})
            if made:
                for ct, ok in choices:
                    Choice.objects.create(question=q, choice_text=ct, is_correct=ok)

        # Preset logins (username / password)
        #   root / root       -> admin + learner (enrolled in the demo course)
        #   prasad / prasad12345 -> learner only
        root, made = User.objects.get_or_create(username="root", defaults={"is_staff": True, "is_superuser": True})
        if made:
            root.set_password("root")
            root.save()
        user, made = User.objects.get_or_create(username="prasad")
        if made:
            user.set_password("prasad12345")
            user.save()
        for u in (root, user):
            Enrollment.objects.get_or_create(user=u, course=course, defaults={"mode": "honor"})
        self.stdout.write("Demo data ready. Login: root / root")
