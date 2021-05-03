from django.db import models
from django.utils.text import Truncator
from django.contrib.auth.models import User


class Tag(models.Model):  # Tags That Questions Are Related To
    tag_name = models.CharField(max_length=25, unique=True)
    tag_description = models.CharField(max_length=150)
    tag_created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tag_name

    def get_answers_count(self):  # To Get Questions Number
        return Answer.objects.filter(question__tag=self).count()

    def get_last_answer(self):  # To Get The Latest Question
        return Answer.objects.filter(question__tag=self).order_by('created_date').last()


class Question(models.Model):
    question_title = models.CharField(max_length=200)
    question_description = models.CharField(max_length=200, null=True)
    tag = models.ForeignKey(Tag, related_name='questions', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='questions', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='questions', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)
    updated_date = models.DateTimeField(null=True)

    def __str__(self):
        truncted_question_description = Truncator(self.question_description)
        return truncted_question_description.chars(30)

    def __str__(self):
        return self.question_title


class PendingQuestion(models.Model):
    pending_question_title = models.CharField(max_length=200)
    pending_question_description = models.CharField(max_length=200, null=True)
    tag = models.ForeignKey(Tag, related_name='pending_questions', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='pending_questions', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)
    updated_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.pending_question_title


class Answer(models.Model):
    answer_text = models.TextField(max_length=2500)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    liked = models.ManyToManyField(User, default=None, blank=True, null=True,  related_name='liked')
    created_by = models.ForeignKey(User, related_name='answers', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)
    updated_date = models.DateTimeField(null=True)

    def __str__(self):
        truncted_message = Truncator(self.answer_text)  # To Return The First 30 Letters Of An Answer
        return truncted_message.chars(30)

    @property
    def num_likes(self):
        return self.liked.all().count()


LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, default="Like", max_length=10)

    def __str__(self):
        return str(self.answer)
