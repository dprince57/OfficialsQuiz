# quiz_app/forms.py
from django import forms
from .models import Answer, QuizPDF


class QuizPreferenceForm(forms.Form):
    NUM_QUESTIONS_CHOICES = [
        (10, "10 Questions"),
        (25, "25 Questions"),
        (50, "50 Questions"),
    ]
    TIMER_CHOICES = [
        (20, "20 Minutes"),
        (30, "30 Minutes"),
        (45, "45 Minutes"),
    ]
    num_questions = forms.ChoiceField(choices=NUM_QUESTIONS_CHOICES, initial=10, label="Number of Questions")
    timer = forms.ChoiceField(choices=TIMER_CHOICES, initial=20, label="Timer Duration")


class AnswerForm(forms.Form):
    answer = forms.ModelChoiceField(queryset=Answer.objects.none(), widget=forms.RadioSelect)

    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.all()


class QuizPDFForm(forms.ModelForm):
    class Meta:
        model = QuizPDF
        fields = ['file']


from django import forms
from .models import Quiz, Question, Answer, Conference


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'publish_time', 'conference']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']


class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ['name', 'logo']
