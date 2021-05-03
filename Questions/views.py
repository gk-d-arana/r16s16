from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, Http404
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from Accounts.models import Profile
from django.db.models import Count
from django.views.generic import UpdateView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def home_view(request):
    return render(request, 'BaseHome.html')


def tags_list(request):  # Home Page That Has The Tag
    if request.user.is_authenticated:
        print('yes')
    else:
        print('no')
    tags = Tag.objects.all()
    tags = tags.order_by('-tag_created_date')
    page = request.GET.get('page', 1)
    paginator = Paginator(tags, 10)
    try:
        tags = paginator.page(page)
    except PageNotAnInteger:
        tags = paginator.page(1)
    except EmptyPage:
        tags = paginator.page(paginator.num_pages)
    return render(request, 'Home.html', {'tags': tags})


@staff_member_required
def new_tag(request):
    if request.method == 'POST':
        tag_name = request.POST.get('tag_name')
        tag_description = request.POST.get('tag_description')
        new_tag_ = Tag.objects.create(tag_name=tag_name, tag_description=tag_description)
        new_tag_.save()
        return redirect(tags_list)
    else:
        return redirect(tags_list)


def tag_questions(request, tag_id):  # Questions Related To A Tag
    tag = get_object_or_404(Tag, pk=tag_id)
    query_set = tag.questions.order_by('-created_date').annotate(comments=Count('answers'))
    page = request.GET.get('page', 1)
    paginator = Paginator(query_set, 15)
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    return render(request, 'questions.html', {'tag': tag, 'questions': questions})


def question_answers(request, tag_id, question_id):  # Answer Related To A Question
    question = get_object_or_404(Question, tag__pk=tag_id, pk=question_id)
    session_key = 'view_question_{}'.format(question.pk)
    tag = get_object_or_404(Tag, id=tag_id)
    pending_questions = PendingQuestion.objects.filter(tag=tag)
    if not request.session.get(session_key, False):
        question.views += 1
        question.save()
        request.session[session_key] = True
    return render(request, 'question_answers.html', {'question': question, 'pending_questions': pending_questions})


@login_required
def like_answer(request, tag_id, question_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('/login')
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        answer = get_object_or_404(Answer, id=answer_id)
        if user in answer.liked.all():
            answer.liked.remove(user)
        else:
            answer.liked.add(user)
        like, created = Like.objects.get_or_create(user=user, answer_id=answer_id)
        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        else:
            like.value = 'Like'
            answer.save()
            like.save()
        data = {
            'value': like.value,
            'likes': answer.liked.all().count()
        }
        return JsonResponse(data, safe=False)
    return redirect(question_answers, tag_id, question_id)


@login_required()
def pending_question(request, tag_id):  # Accepting Added Questions By Admins
    main_user = request.user
    if main_user.is_staff:
        tag = get_object_or_404(Tag, id=tag_id)
        pending_questions = PendingQuestion.objects.filter(tag=tag)
        return render(request, 'pending_questions.html', {'pending_questions': pending_questions, 'tag': tag})
    else:
        return render(request, 'Page404.html', {})


@login_required()
def new_question(request, tag_id):  # Creating A Question That Requires A Logged In User
    main_user = request.user
    if main_user.is_staff:
        tag = get_object_or_404(Tag, pk=tag_id)
        if request.method == "POST":
            form = NewQuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.tag = tag
                question.created_by = request.user
                question.save()
                return redirect(tag_questions, tag_id=tag_id)
        else:
            form = NewQuestionForm()
        return render(request, 'new_question.html', {'tag': tag, 'form': form})
    else:
        tag = get_object_or_404(Tag, pk=tag_id)
        user = request.user
        profile_obj = Profile.objects.filter(user=user).first()
        try:
            if not profile_obj.is_verified:  # We put Not profile_obj.is_verified Because The Default value is False
                return render(request, 'token_send.html')
        except AttributeError:
            pass
        if request.method == "POST":
            form = NewPendingQuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.tag = tag
                question.created_by = request.user
                question.save()
                return render(request, 'wait_question_approve.html', {'tag_id': tag_id})
        else:
            form = NewPendingQuestionForm()
        return render(request, 'new_question.html', {'tag': tag, 'form': form})


@login_required
def reply_question(request, tag_id, question_id):  # Creating An Answer For A Question That Requires A Logged In User
    question = get_object_or_404(Question, tag__pk=tag_id, pk=question_id)
    user = request.user
    profile_obj = Profile.objects.filter(user=user).first()
    try:
        if not profile_obj.is_verified:  # We put Not profile_obj.is_verified Because The Default value is False
            return render(request, 'token_send.html')
    except AttributeError:
        pass
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.created_by = request.user
            answer.save()
            question.updated_by = request.user
            question.updated_date = timezone.now()
            question.save()
            return redirect('question_answers', tag_id=tag_id, question_id=question_id)
    else:
        form = AnswerForm()
    return render(request, 'reply_question.html', {'question': question, 'form': form})


@method_decorator(login_required, name='dispatch')
class AnswerUpdateView(UpdateView):  # Editing An Answer
    model = Answer
    fields = ('answer_text',)
    template_name = 'edit_answer.html'
    pk_url_kwarg = 'answer_id'
    context_object_name = 'answer'

    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.updated_by = self.request.user
        answer.updated_date = timezone.now()
        answer.save()
        return redirect('question_answers', tag_id=answer.question.tag.pk, question_id=answer.question.pk)


def error_404(request, exception):
    data = {}
    return render(request, 'Page404.html', data)


def error_500(request):
    data = {}
    return render(request, 'Page404.html', data)


def approve_all_questions(request):
    main_user = request.user
    if main_user.is_staff:
        pending_questions_ = PendingQuestion.objects.all()
        for pending_question_ in pending_questions_:
            the_new_question = Question.objects.create(
                    question_title=pending_question_.pending_question_title,
                    question_description=pending_question_.pending_question_description,
                    tag=pending_question_.tag,
                    created_by=pending_question_.created_by,
                    created_date=pending_question_.created_date)
            the_new_question.save()
            pending_question_.delete()
        return redirect(pending_question)
    else:
        return render(request, 'Page404.html', {})


def unapprove_all_questions(request):
    main_user = request.user
    if main_user.is_staff:
        pending_questions_ = PendingQuestion.objects.all()
        for pending_question_ in pending_questions_:
            pending_question_.delete()
        return redirect(pending_question)
    else:
        return render(request, 'Page404.html', {})


def approve_question(request, question_id):
    main_user = request.user
    if main_user.is_staff:
        if request.is_ajax():   
            pending_question_ = get_object_or_404(PendingQuestion, id=question_id)
            the_new_question = Question.objects.create(
                    question_title=pending_question_.pending_question_title,
                    question_description=pending_question_.pending_question_description,
                    tag=pending_question_.tag,
                    created_by=pending_question_.created_by,
                    created_date=pending_question_.created_date)
            the_new_question.save()
            pending_question_.delete()
            pending_questions_count = PendingQuestion.objects.all().count()
            return JsonResponse({"message": "success", 'pending_questions_count': pending_questions_count})
        return JsonResponse({"message": 'Wrong route'})
    else:
        return render(request, 'Page404.html', {})


def unapprove_question(request, question_id):
    main_user = request.user
    if main_user.is_staff:
        if request.is_ajax():
            pending_question_ = get_object_or_404(PendingQuestion, id=question_id)
            pending_question_.delete()
            pending_questions_count = PendingQuestion.objects.all().count()
            return JsonResponse({"message": "success", 'pending_questions_count': pending_questions_count})
        return JsonResponse({"message": 'Wrong route'})
    else:
        return render(request, 'Page404.html', {})


def tag_question_search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        tags = Tag.objects.filter(tag_name__contains=searched)
        questions = Question.objects.filter(question_title__contains=searched)
        questions = questions.order_by('-created_date')
        context = {
            'searched': searched,
            'tags': tags,
            'questions': questions
        }
        return render(request, 'tag_question_search.html', context)
    else:
        return render(request, 'search.html', {})


"""    user = request.user
    profile_obj = Profile.objects.filter(user=user).first()
    if not profile_obj.is_verified:  # We put Not profile_obj.is_verified Because The Default value is False
        return render(request, 'token_send.html')"""