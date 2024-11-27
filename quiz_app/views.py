# quiz_app/views.py
import os
import random
import re

import pdfplumber
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import QuizPreferenceForm, QuizPDFForm
from .models import Question, Answer, UserAnswer


def quiz_preferences_view(request):
    form = QuizPreferenceForm(request.POST or None)
    if form.is_valid():
        # Handle form submission (redirect to the quiz page)
        return redirect('quiz')

    return render(request, 'quiz_preferences.html', {'form': form})


@login_required
def upload_pdf(request):
    if request.method == "POST":
        form = QuizPDFForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded PDF
            quiz_pdf = form.save()
            file_path = quiz_pdf.file.path

            # Parse and save questions/answers
            parse_and_save_pdf(file_path)

            return redirect('quiz')  # Adjust redirect to your desired page

    else:
        form = QuizPDFForm()

    return render(request, 'upload_pdf.html', {'form': form})


def parse_and_save_pdf(file_path):
    """
    Parse the PDF and save extracted questions and answers into the database.
    """
    import pdfplumber

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            questions = extract_questions_and_answers(text)
            for question_text, answers in questions:
                question = Question.objects.create(text=question_text)
                for answer in answers:
                    Answer.objects.create(
                        question=question,
                        text=answer["text"],
                        is_correct=answer["is_correct"],
                        rule_reference="Default Rule"
                    )


def extract_questions_and_answers(text):
    """
    Extract questions and answers from the text.
    """
    import re

    lines = text.split("\n")
    questions = []
    current_question = None
    current_answers = []
    reading_answers = False

    for i, line in enumerate(lines):
        line = line.strip()

        # Detect questions starting with "Q#"
        question_match = re.match(r"^(Q\d+)\s(.*)", line)
        if question_match:
            if current_question and current_answers:
                questions.append((current_question.strip(), current_answers))
                current_answers = []

            current_question = question_match.group(2).strip()
            reading_answers = False
            continue

        # Detect answers prefixed by "o"
        if line == "o":
            reading_answers = True
            continue

        if reading_answers:
            current_answers.append({"text": line, "is_correct": "__" in line})
            continue

        if current_question:
            current_question += f" {line}"

    if current_question and current_answers:
        questions.append((current_question.strip(), current_answers))

    return questions



@login_required
def home(request):
    user_answers = UserAnswer.objects.filter(user=request.user)
    incorrect_answers = []

    for user_answer in user_answers.filter(is_correct=False):
        correct_answer = user_answer.question.answers.get(is_correct=True)  # Get the correct answer
        incorrect_answers.append({
            'question': user_answer.question.text,
            'your_answer': user_answer.answer.text,
            'correct_answer': correct_answer.text,
            'rule_reference': correct_answer.rule_reference,
        })

    return render(request, 'home.html', {'incorrect_answers': incorrect_answers})


@login_required
def quiz_view(request):
    # Initialize quiz session data
    if 'quiz_data' not in request.session:
        num_questions = int(request.GET.get('num_questions', 10))  # Default: 10 questions
        questions = list(Question.objects.all())
        random.shuffle(questions)  # Shuffle the questions
        selected_questions = questions[:num_questions]

        request.session['quiz_data'] = {
            'questions': [q.id for q in selected_questions],
            'current_index': 0,
            'score': 0,
            'wrong_questions': []
        }

    quiz_data = request.session['quiz_data']
    current_index = quiz_data['current_index']

    # Check if quiz is complete
    if current_index >= len(quiz_data['questions']):
        wrong_questions = Question.objects.filter(id__in=quiz_data['wrong_questions'])
        score = quiz_data['score']

        # Clear quiz session data
        del request.session['quiz_data']

        return render(request, 'quiz_results.html', {
            'score': score,
            'total': len(quiz_data['questions']),
            'wrong_questions': wrong_questions
        })

    # Get the current question
    question_id = quiz_data['questions'][current_index]
    question = Question.objects.get(id=question_id)
    answers = question.answers.all()

    # Handle form submission
    if request.method == 'POST':
        selected_answer_id = int(request.POST.get('answer'))
        selected_answer = Answer.objects.get(id=selected_answer_id)

        if selected_answer.is_correct:
            quiz_data['score'] += 1
        else:
            quiz_data['wrong_questions'].append(question.id)

        # Save the user's answer
        UserAnswer.objects.create(
            user=request.user,
            question=question,
            answer=selected_answer,
            is_correct=selected_answer.is_correct
        )

        # Move to the next question
        quiz_data['current_index'] += 1
        request.session['quiz_data'] = quiz_data  # Save progress
        return redirect('quiz')

    return render(request, 'quiz.html', {
        'question': question,
        'answers': answers,
        'current_index': current_index + 1,
        'total_questions': len(quiz_data['questions'])
    })


@login_required
def answer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    selected_answer_id = request.POST.get('answer')
    selected_answer = get_object_or_404(Answer, id=selected_answer_id)

    is_correct = selected_answer.is_correct
    UserAnswer.objects.create(
        user=request.user,
        question=question,
        answer=selected_answer,
        is_correct=is_correct
    )

    if is_correct:
        return redirect('quiz')
    else:
        correct_answer = question.answers.get(is_correct=True)
        return render(request, 'feedback.html', {
            'question': question,
            'correct_answer': correct_answer,
            'selected_answer': selected_answer
        })


@login_required
def feedback(request):
    # Example context for feedback page
    context = {
        "message": "This is a placeholder for feedback functionality.",
    }
    return render(request, "feedback.html", context)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def submit_quiz(request):
    if request.method == 'POST':
        # Handle the submitted quiz data
        # Extract and process the answers here
        return JsonResponse({'status': 'success', 'message': 'Quiz submitted successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Answer, Conference
from .forms import QuizForm, QuestionForm, AnswerForm

@login_required
def create_quiz(request):
    if not request.user.admin_conferences.exists():
        return render(request, 'error.html', {'message': 'You are not an admin of any conference.'})

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.creator = request.user
            quiz.save()
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'create_quiz.html', {'form': form})


@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    questions = quiz.questions.all()

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        question_form = QuestionForm()

    return render(request, 'edit_quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'question_form': question_form
    })


@login_required
def add_answers(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__creator=request.user)
    answers = question.answers.all()

    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('add_answers', question_id=question.id)
    else:
        answer_form = AnswerForm()

    return render(request, 'add_answers.html', {
        'question': question,
        'answers': answers,
        'answer_form': answer_form
    })


@login_required
def stats_view(request, conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    if request.user not in conference.admins.all():
        return render(request, 'error.html', {'message': 'You are not an admin of this conference.'})

    quizzes = conference.quizzes.all()

    return render(request, 'stats.html', {'quizzes': quizzes})
