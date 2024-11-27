# quiz_app/models.py
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class QuizPDF(models.Model):
    file = models.FileField(upload_to='uploads/quiz_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz PDF uploaded at {self.uploaded_at}"


class Conference(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='conference_logos/', blank=True, null=True)
    admins = models.ManyToManyField(User, related_name='admin_conferences')
    members = models.ManyToManyField(User, related_name='member_conferences')

    def __str__(self):
        return self.name


class Quiz(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    publish_time = models.DateTimeField(default=now)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_quizzes')

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return f"{self.quiz.title}: {self.text}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"


class UserQuizStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_stats')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='user_stats')
    total_time = models.DurationField()
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}: {self.score}"


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:30]}: {'Correct' if self.is_correct else 'Incorrect'}"
