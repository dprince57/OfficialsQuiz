# quiz_app/admin.py
from django.contrib import admin
from .models import Question, Answer, UserAnswer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(UserAnswer)
