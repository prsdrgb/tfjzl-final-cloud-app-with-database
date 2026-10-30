from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Course, Enrollment, Question, Choice, Submission


def registration_request(request):
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html')
    username = request.POST['username']
    password = request.POST['psw']
    if User.objects.filter(username=username).exists():
        messages.error(request, "User already exists.")
        return render(request, 'onlinecourse/user_registration_bootstrap.html')
    user = User.objects.create_user(username=username, password=password)
    login(request, user)
    return redirect('onlinecourse:index')


def login_request(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['psw'])
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        messages.error(request, "Invalid username or password.")
    return render(request, 'onlinecourse/user_login_bootstrap.html')


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.order_by('-total_enrollment')[:10]


class CourseDetailsView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_enrolled'] = (user.is_authenticated and
                                  Enrollment.objects.filter(user=user, course=self.object).exists())
        return context


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    if user.is_authenticated and not Enrollment.objects.filter(user=user, course=course).exists():
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))


# Collect the ids of every choice the learner ticked in the exam form.
# Each checkbox is named "choice_<id>" and its value is the choice id.
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            submitted_answers.append(int(request.POST[key]))
    return submitted_answers


# submit: save the learner's answers as a Submission, then show the result
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not request.user.is_authenticated or request.method != 'POST':
        return redirect('onlinecourse:course_details', pk=course.id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(extract_answers(request))
    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result', args=(course.id, submission.id)))


# show_exam_result: work out the score and show the result page
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = list(submission.choices.values_list('id', flat=True))

    grade = 0       # points the learner earned
    possible = 0    # total points available
    for question in course.question_set.all():
        possible += question.grade
        if question.is_get_score(selected_ids):
            grade += question.grade

    percent = int(grade / possible * 100) if possible > 0 else 0
    context = {
        'course': course,
        'selected_ids': selected_ids,
        'grade': grade,
        'possible': possible,
        'percent': percent,
        'passed': percent >= 80,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
