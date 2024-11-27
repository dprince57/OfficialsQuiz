# quiz_app/models.py
from django.contrib.auth.models import User
from django.db import models


class UploadedPDF(models.Model):
    file = models.FileField(upload_to='uploads/pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class QuizPDF(models.Model):
    file = models.FileField(upload_to='uploads/quiz_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz PDF uploaded at {self.uploaded_at}"

class Question(models.Model):
    text = models.TextField()  # The question text

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  # Marks whether this is the correct answer
    rule_reference = models.TextField()  # Rule associated with this specific answer

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:30]}: {'Correct' if self.is_correct else 'Incorrect'}"
