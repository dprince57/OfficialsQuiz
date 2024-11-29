from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class GeneralQuestion(models.Model):
    """
    Represents general quiz questions available to all users.
    """
    text = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text


class GeneralAnswer(models.Model):
    question = models.ForeignKey(GeneralQuestion, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

class Conference(models.Model):
    """
    Represents a conference, which can have quizzes and specific admins/members.
    """
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='conference_logos/', blank=True, null=True)
    admins = models.ManyToManyField(User, related_name='admin_conferences')
    members = models.ManyToManyField(User, related_name='member_conferences')

    def __str__(self):
        return self.name


class Quiz(models.Model):
    """
    Represents a quiz tied to a specific conference.
    """
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)  # Whether the quiz is open for participation
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_quizzes')

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Represents a question specific to a conference quiz.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return f"{self.quiz.title}: {self.text}"


class Answer(models.Model):
    """
    Represents an answer for a specific question in a conference quiz.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"


class UserAnswer(models.Model):
    """
    Represents an answer given by a user to a specific question.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='user_answers')
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, related_name='user_answers')
    is_correct = models.BooleanField()  # Whether the selected answer was correct
    answered_at = models.DateTimeField(auto_now_add=True)  # Timestamp of the answer

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:50]}: {'Correct' if self.is_correct else 'Incorrect'}"


class QuizPDF(models.Model):
    """
    Represents an uploaded PDF file for quizzes.
    """
    file = models.FileField(upload_to='uploads/quiz_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz PDF uploaded at {self.uploaded_at}"