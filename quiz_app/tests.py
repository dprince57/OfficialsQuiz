# quiz_app/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Question, Answer, UserAnswer

class QuizAppTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.question = Question.objects.create(text="What is the penalty for offsides?")
        self.correct_answer = Answer.objects.create(
            question=self.question, text="5-yard penalty", is_correct=True, rule_reference="Rule 7-1-5"
        )
        self.wrong_answer = Answer.objects.create(
            question=self.question, text="10-yard penalty", is_correct=False, rule_reference="Rule 7-1-5"
        )

    def test_correct_answer(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(f'/quiz/{self.question.id}/answer/', {'answer': self.correct_answer.id})
        self.assertRedirects(response, '/quiz/')

    def test_incorrect_answer(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(f'/quiz/{self.question.id}/answer/', {'answer': self.wrong_answer.id})
        self.assertContains(response, "The correct answer was:")
