from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('quiz/preferences/', views.quiz_preferences_view, name='quiz_preferences'),
    path('quiz/submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/<int:question_id>/answer/', views.answer_question, name='answer_question'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('edit_quiz/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('add_answers/<int:question_id>/', views.add_answers, name='add_answers'),
    path('stats/<int:conference_id>/', views.stats_view, name='stats'),
    path('manage_conferences/', views.manage_conferences, name='manage_conferences'),
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),
    path('feedback/', views.feedback, name='feedback'),
    path('create_conference_quiz/<int:conference_id>/', views.create_conference_quiz, name='create_conference_quiz'),
    path('close_quiz/<int:quiz_id>/', views.close_quiz, name='close_quiz'),
    path('release_quiz_questions/<int:quiz_id>/', views.release_quiz_questions, name='release_quiz_questions'),
]