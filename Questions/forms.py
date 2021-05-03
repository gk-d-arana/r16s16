from django import forms
from .models import Answer, PendingQuestion, Question


class NewPendingQuestionForm(forms.ModelForm):
    pending_question_description = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 5, 'placeholder': 'Write something'}
    ), max_length=2000, help_text='The max length is 2000', required=False)

    class Meta:
        model = PendingQuestion
        fields = ['pending_question_title', 'pending_question_description']


class NewQuestionForm(forms.ModelForm):
    question_description = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 5, 'placeholder': 'Write something'}
    ), max_length=2000, help_text='The max length is 2000', required=False)

    class Meta:
        model = Question
        fields = ['question_title', 'question_description']


class AnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ['answer_text']
