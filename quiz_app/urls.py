# quiz_app/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('quiz/submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/preferences/', views.quiz_preferences_view, name='quiz_preferences'),
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('quiz/<int:question_id>/answer/', views.answer_question, name='answer_question'),
    path('feedback/', views.feedback, name='feedback'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # Login
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout
    path('signup/', views.signup, name='signup'),  # signup
]

