import logging
import random
import pdfplumber
import re

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import *

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *

logger = logging.getLogger(__name__)


# View for superusers to manage conferences
@user_passes_test(lambda u: u.is_superuser)
def manage_conferences(request):
    conferences = Conference.objects.all()
    if request.method == 'POST':
        form = ConferenceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_conferences')
    else:
        form = ConferenceForm()

    return render(request, 'manage_conferences.html', {
        'conferences': conferences,
        'form': form
    })


# Dashboard for conference admins
@login_required
def conference_admin_dashboard(request):
    conferences = request.user.admin_conferences.all()
    return render(request, 'admin_dashboard.html', {
        'conferences': conferences
    })


# Unified home page for all users
@login_required
def home(request):
    if request.user.is_superuser:
        return render(request, 'home.html', {
            'role': 'superuser',
            'conferences': Conference.objects.all()
        })
    elif request.user.admin_conferences.exists():
        return render(request, 'home.html', {
            'role': 'admin',
            'conferences': request.user.admin_conferences.all()
        })
    elif request.user.member_conferences.exists():
        return render(request, 'home.html', {
            'role': 'member',
            'conferences': request.user.member_conferences.all()
        })
    else:
        return render(request, 'home.html', {
            'role': 'none'
        })


# Profile editing view
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})


# View for quiz functionality
@login_required
def quiz_view(request):
    # Initialize session data for quiz
    if 'quiz_data' not in request.session:
        num_questions = int(request.GET.get('num_questions', 10))
        # Fetch only valid, active questions
        questions = list(GeneralQuestion.objects.filter(is_active=True))
        if not questions:
            return render(request, 'error.html', {'message': 'No active questions available for the quiz.'})

        random.shuffle(questions)
        # Store valid question IDs in session
        selected_questions = questions[:num_questions]
        request.session['quiz_data'] = {
            'questions': [q.id for q in selected_questions],
            'current_index': 0,
            'score': 0,
            'wrong_questions': []
        }

    quiz_data = request.session['quiz_data']
    current_index = quiz_data['current_index']

    # Handle end of quiz
    if current_index >= len(quiz_data['questions']):
        wrong_questions = GeneralQuestion.objects.filter(id__in=quiz_data['wrong_questions'])
        score = quiz_data['score']
        del request.session['quiz_data']
        return render(request, 'quiz_results.html', {
            'score': score,
            'total': len(quiz_data['questions']),
            'wrong_questions': wrong_questions
        })

    # Retrieve the current question
    try:
        question_id = quiz_data['questions'][current_index]
        question = get_object_or_404(GeneralQuestion, id=question_id)
        answers = question.answers.all()  # Fetch related answers
    except GeneralQuestion.DoesNotExist:
        return render(request, 'error.html', {'message': 'Question not found in the database.'})

    # Handle answer submission
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        if selected_answer and answers.filter(id=int(selected_answer), is_correct=True).exists():
            quiz_data['score'] += 1
        else:
            quiz_data['wrong_questions'].append(question.id)
        quiz_data['current_index'] += 1
        request.session['quiz_data'] = quiz_data
        return redirect('quiz')

    return render(request, 'quiz.html', {
        'question': question,
        'answers': answers,  # Pass answers to template
        'current_index': current_index + 1,
        'total_questions': len(quiz_data['questions'])
    })


# Submit quiz view
@login_required
def submit_quiz(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'message': 'Quiz submitted successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


# View to answer a specific question
@login_required
def answer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
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
            correct_answer = question.answers.filter(is_correct=True).first()
            return render(request, 'feedback.html', {
                'question': question,
                'correct_answer': correct_answer,
                'selected_answer': selected_answer
            })
    return redirect('quiz')


# Create a quiz
@login_required
def create_quiz(request):
    if not request.user.admin_conferences.exists():
        return render(request, 'error.html', {'message': 'You are not an admin of any conference.'})
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.save()
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'create_quiz.html', {'form': form})


# Add answers to a question
@login_required
def add_answers(request, question_id):
    question = get_object_or_404(Question, id=question_id)
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


# Upload a quiz PDF
@login_required
def upload_pdf(request):
    if request.method == 'POST':
        form = QuizPDFForm(request.POST, request.FILES)
        if form.is_valid():
            quiz_pdf = form.save()
            file_path = quiz_pdf.file.path
            try:
                parse_and_save_pdf(file_path)
            except Exception as e:
                logger.error(f"Error parsing PDF: {e}")
                return render(request, 'error.html', {'message': f"Error parsing PDF: {e}"})
            return redirect('home')
    else:
        form = QuizPDFForm()
    return render(request, 'upload_pdf.html', {'form': form})


# Feedback view
@login_required
def feedback(request):
    return render(request, 'feedback.html', {
        'message': 'This is a placeholder for feedback functionality.'
    })


def parse_and_save_pdf(file_path):
    """
    Parse the uploaded PDF and save extracted questions and answers into the database.
    """
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            # Extract questions and answers
            parsed_data = extract_questions_and_answers(text)
            for question_text, answers in parsed_data:  # Unpack the tuple here
                # Save question to database
                question = GeneralQuestion.objects.create(text=question_text, is_active=False)

                # Save answers to database
                for answer in answers:
                    GeneralAnswer.objects.create(
                        question=question,
                        text=answer["text"],
                        is_correct=answer["is_correct"],
                    )


def extract_questions_and_answers(text):
    """
    Extracts questions and their answers from a given text.

    :param text: The raw text extracted from a PDF page.
    :return: A list of tuples, where each tuple contains a question (str)
             and a list of answers (dict with 'text' and 'is_correct' keys).
    """
    lines = text.split("\n")
    questions = []
    current_question = None
    current_answers = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        # Detect a new question starting with "Q#"
        question_match = re.match(r"(Q\d+)\s(.*)", line)
        if question_match:
            # Save the previous question and its answers
            if current_question and current_answers:
                questions.append((current_question.strip(), current_answers))
                current_answers = []

            # Start a new question
            current_question = question_match.group(2).strip()

        # Detect standalone "o" indicating the start of an answer
        elif line == "o" and i + 1 < len(lines):
            # The next line is the answer text
            answer_text = lines[i + 1].strip()
            is_correct = "__" in answer_text  # Detect correct answers by underline
            cleaned_text = answer_text.replace("__", "").strip()  # Clean underline markers
            current_answers.append({"text": cleaned_text, "is_correct": is_correct})
            i += 1  # Skip the next line since it's part of the answer

        # Append additional lines to the current question
        elif current_question and not re.match(r"(Q\d+)\s", line):
            current_question += f" {line.strip()}"

        i += 1

    # Add the last question and answers
    if current_question and current_answers:
        questions.append((current_question.strip(), current_answers))

    return questions


# View for user signup
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to log in after successful signup
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


# Quiz preferences view
@login_required
def quiz_preferences_view(request):
    form = QuizPreferenceForm(request.POST or None)
    if form.is_valid():
        # Process preferences and redirect to quiz page
        num_questions = form.cleaned_data.get('num_questions')
        timer = form.cleaned_data.get('timer')
        return redirect(f'/quiz/?num_questions={num_questions}&timer={timer}')

    return render(request, 'quiz_preferences.html', {'form': form})


# Conference stats view for admins
@login_required
def stats_view(request, conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    if request.user not in conference.admins.all():
        return render(request, 'error.html', {'message': 'You are not authorized to view stats for this conference.'})

    quizzes = conference.quizzes.all()
    stats = []

    for quiz in quizzes:
        user_stats = quiz.user_stats.all()
        stats.append({
            'quiz': quiz,
            'total_attempts': user_stats.count(),
            'average_score': user_stats.aggregate_avg('score'),  # Placeholder, calculate avg score
        })

    return render(request, 'stats.html', {
        'conference': conference,
        'stats': stats,
    })


@login_required
def create_conference_quiz(request, conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    if request.user not in conference.admins.all():
        return render(request, 'error.html', {'message': 'not authorized to create quizzes for this conference.'})

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.conference = conference
            quiz.creator = request.user
            quiz.save()
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'create_quiz.html', {'form': form, 'conference': conference})


@login_required
def edit_quiz(request, quiz_id):
    """
    View to edit a conference quiz and add questions.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user not in quiz.conference.admins.all():
        return render(request, 'error.html', {'message': 'You are not authorized to edit this quiz.'})

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
        'question_form': question_form,
    })


@login_required
def close_quiz(request, quiz_id):
    """
    View to close a quiz, making it inactive.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user not in quiz.conference.admins.all():
        return render(request, 'error.html', {'message': 'You are not authorized to close this quiz.'})

    quiz.is_active = False
    quiz.save()
    return redirect('edit_quiz', quiz_id=quiz.id)


@login_required
def release_quiz_questions(request, quiz_id):
    """
    View to release quiz questions to the general question pool.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user not in quiz.conference.admins.all():
        return render(request, 'error.html', {'message': 'You are not authorized to release questions from this quiz.'})

    for question in quiz.questions.all():
        GeneralQuestion.objects.create(text=question.text)

    return redirect('edit_quiz', quiz_id=quiz.id)


@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def review_questions(request):
    # Fetch inactive questions
    inactive_questions = Question.objects.filter(is_active=False)

    if request.method == 'POST':
        question_ids = request.POST.getlist('activate')
        Question.objects.filter(id__in=question_ids).update(is_active=True)
        return redirect('review_questions')

    return render(request, 'review_questions.html', {
        'inactive_questions': inactive_questions,
    })


@login_required
def conference_home(request):
    conferences = request.user.admin_conferences.all()
    return render(request, 'conference_home.html', {
        'conferences': conferences,
    })


@login_required
def conference_create_quiz(request, conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    if request.user not in conference.admins.all():
        return render(request, 'error.html', {'message': 'You are not authorized to create quizzes for this conference.'})

    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        answers = request.POST.getlist('answers')
        correct_answer = int(request.POST.get('correct_answer'))
        quiz = Quiz.objects.filter(conference=conference).first()

        if not quiz:
            quiz = Quiz.objects.create(conference=conference, creator=request.user)

        question = Question.objects.create(quiz=quiz, text=question_text)
        for index, answer_text in enumerate(answers):
            Answer.objects.create(
                question=question,
                text=answer_text,
                is_correct=(index == correct_answer),
            )

        if 'save_publish' in request.POST:
            quiz.is_published = True
            quiz.save()
            return redirect('conference_home')
        elif 'add_question' in request.POST:
            return redirect('conference_create_quiz', conference_id=conference_id)

    return render(request, 'create_quiz.html', {'conference': conference})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def review_questions(request):
    inactive_questions = GeneralQuestion.objects.filter(is_active=False)

    if request.method == 'POST':
        question_ids = request.POST.getlist('activate')
        GeneralQuestion.objects.filter(id__in=question_ids).update(is_active=True)
        return redirect('review_questions')

    return render(request, 'review_questions.html', {'inactive_questions': inactive_questions})


def logout_view(request):
    """
    Logs out the user and redirects to the home page with a confirmation message.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')  # Replace 'home' with the name of your home page view