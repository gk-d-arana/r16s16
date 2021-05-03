from django.urls import path
from . import views
urlpatterns = [
    path('', views.home_view, name='home'),
    path('tags_list', views.tags_list, name='tags_list'),
    path('search/', views.tag_question_search, name='search'),
    path('tag/<int:tag_id>', views.tag_questions, name='tag_questions'),
    path('tag/new_tag', views.new_tag, name='new_tag'),
    path('tag/<int:tag_id>/pending_questions', views.pending_question, name='pending_questions'),
    path('pending_questions/approve_all_questions', views.approve_all_questions, name='approve_all_questions'),
    path('pending_questions/unapprove_all_questions', views.unapprove_all_questions, name='unapprove_all_questions'),
    path('pending_questions/<int:question_id>/approve_question', views.approve_question, name='approve_question'),
    path('pending_questions/<int:question_id>/unapprove_question', views.unapprove_question, name='unapprove_question'),
    path('tag/<int:tag_id>/new_question', views.new_question, name='new_question'),
    path('tag/<int:tag_id>/question/<int:question_id>', views.question_answers, name='question_answers'),
    path('tag/<int:tag_id>/question/<int:question_id>/like_answer', views.like_answer, name='like_answer'),
    path('tag/<int:tag_id>/question/<int:question_id>/reply/', views.reply_question, name='reply_question'),
    path('tag/<int:tag_id>/question/<int:question_id>/answer/<int:answer_id>/edit', views.AnswerUpdateView.as_view(), name='edit_answer'),
]
