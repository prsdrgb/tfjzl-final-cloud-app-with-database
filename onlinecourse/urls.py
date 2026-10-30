from django.urls import path
from . import views

app_name = 'onlinecourse'
urlpatterns = [
    path('', views.CourseListView.as_view(), name='index'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('<int:pk>/', views.CourseDetailsView.as_view(), name='course_details'),
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),

    # Exam paths
    # submit: saves the learner's answers
    path('<int:course_id>/submit/', views.submit, name='submit'),
    # show_exam_result: shows the score for one submission
    path('course/<int:course_id>/submission/<int:submission_id>/result/',
         views.show_exam_result, name='show_exam_result'),
]
