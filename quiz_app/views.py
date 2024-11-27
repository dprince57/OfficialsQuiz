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
from .forms import QuizPreferenceForm, PDFUploadForm
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
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_pdf = form.save()  # Save the uploaded file
            parse_and_upload_pdf(uploaded_pdf.file.path)  # Call the parser
            return redirect('upload_pdf')  # Redirect to the same page after parsing

    else:
        form = PDFUploadForm()

    return render(request, 'upload_pdf.html', {'form': form})


def parse_and_upload_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                print(f"Page {page.page_number} has no readable text!")
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
    lines = text.split("\n")
    questions = []
    current_question = None
    current_answers = []

    for i, line in enumerate(lines):
        question_match = re.match(r"(Q\d+)\s(.*)", line)
        if question_match:
            if current_question and current_answers:
                questions.append((current_question.strip(), current_answers))
                current_answers = []

            current_question = question_match.group(2).strip()

        elif re.match(r"^\s*o\s", line):
            answer_text = collect_full_answer(lines, i)
            is_correct = "__" in answer_text
            cleaned_text = answer_text.replace("__", "").strip()
            current_answers.append({"text": cleaned_text, "is_correct": is_correct})

        elif current_question and not re.match(r"^\s*o\s", line) and not re.match(r"(Q\d+)\s", line):
            current_question += f" {line.strip()}"

    if current_question and current_answers:
        questions.append((current_question.strip(), current_answers))

    return questions


def collect_full_answer(lines, start_index):
    answer = lines[start_index].lstrip("o").strip()
    for i in range(start_index + 1, len(lines)):
        if not re.match(r"^\s*o\s", lines[i]) and not re.match(r"(Q\d+)\s", lines[i]):
            answer += f" {lines[i].strip()}"
        else:
            break
    return answer



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
    form = QuizPreferenceForm(request.POST or None)
    if form.is_valid():
        # Get user preferences
        num_questions = int(form.cleaned_data['num_questions'])
        timer_duration = int(form.cleaned_data['timer'])

        # Fetch the requested number of random questions
        questions = Question.objects.order_by("?")[:num_questions]

        return render(request, 'quiz.html', {
            'questions': questions,
            'timer_duration': timer_duration,
        })

    # Default view with form
    return render(request, 'quiz_preferences.html', {'form': form})


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

