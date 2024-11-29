from django.contrib import admin
from .models import Question, Answer, UserAnswer, Quiz, Conference, GeneralQuestion, QuizPDF, GeneralAnswer


class AnswerInline(admin.TabularInline):
    """
    Inline for managing answers directly within the question admin interface.
    """
    model = Answer
    extra = 3  # Allows adding 3 answers by default
    fields = ('text', 'is_correct')  # Only show these fields for inline editing


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin for managing questions, with inline answers.
    """
    list_display = ('text', 'quiz',)  # Displays question text and associated quiz
    list_filter = ('quiz',)  # Adds a filter for quizzes
    search_fields = ('text',)  # Allows searching questions by text
    inlines = [AnswerInline]  # Adds the AnswerInline


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """
    Admin for managing quizzes.
    """
    list_display = ('title', 'conference', 'is_active', 'creator')  # Shows these fields in the admin list
    list_filter = ('conference', 'is_active')  # Adds filters for conference and active status
    search_fields = ('title',)  # Allows searching quizzes by title


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    """
    Admin for managing conferences.
    """
    list_display = ('name', 'logo')  # Displays conference name and logo
    search_fields = ('name',)  # Allows searching conferences by name


class GeneralAnswerInline(admin.TabularInline):
    """
    Inline admin for displaying GeneralAnswers linked to a GeneralQuestion.
    """
    model = GeneralAnswer
    extra = 1  # Allows adding new answers directly in the GeneralQuestion admin
    fields = ('text', 'is_correct')  # Fields to display in the inline admin
    readonly_fields = ()  # Add fields here if you want them to be read-only

@admin.register(GeneralQuestion)
class GeneralQuestionAdmin(admin.ModelAdmin):
    """
    Admin for managing general questions.
    """
    list_display = ('text', 'is_active')  # Displays question text and active status
    list_filter = ('is_active',)  # Adds a filter for active status
    search_fields = ('text',)  # Allows searching general questions by text
    inlines = [GeneralAnswerInline]  # Includes related GeneralAnswer objects in the admin view


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    """
    Admin for managing user answers.
    """
    list_display = ('user', 'question', 'answer', 'is_correct', 'answered_at')  # Includes timestamp of answer
    list_filter = ('is_correct', 'question')  # Adds filters for correctness and questions
    search_fields = ('user__username', 'question__text')  # Allows searching by user or question text


@admin.register(QuizPDF)
class QuizPDFAdmin(admin.ModelAdmin):
    """
    Admin for managing uploaded quiz PDFs.
    """
    list_display = ('file', 'uploaded_at')  # Displays file name and upload timestamp
    search_fields = ('file',)  # Allows searching by file name
