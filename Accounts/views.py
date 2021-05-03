from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from Questions.models import *
from .forms import LoginForm
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from Questions.views import tags_list
import uuid
from django.core.mail import send_mail
from .models import *
from django.conf import settings
from django.utils import timezone


def login_view(request):
    main_user = request.user
    if main_user.is_authenticated:
        return redirect(tags_list)
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect(tags_list)
        else:
            form = LoginForm()
        return render(request, 'login.html', {'form': form})


def signup(request):  # Creating A New User
    user = request.user
    if user.is_authenticated:
        return redirect(tags_list)
    if request.method == 'POST':
        username1 = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        try:
            new_user = User.objects.create_user(username=username1, email=email, password=password1,
                                                first_name=first_name, last_name=last_name)
            new_user.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user=new_user, auth_token=auth_token)
            profile_obj.save()
            profile_obj.is_verified = False
            send_mail_after_registration(email, auth_token)
            auth_login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
            request.session['signedup'] = "yes"
            return redirect('/token')
        except IntegrityError as e:
            if 'unique constraint'.lower() in str(e).lower():
                context = {
                    'error_message': 'Username Already Exists'
                }
                return render(request, 'signup.html', context)
    else:
        return render(request, 'signup.html', {})


def success(request):
    if 'verified' in request.session:
        try:
            del request.session['verified']
        except KeyError:
            pass
        return render(request, 'success.html')
    else:
        return render(request, 'Page404.html')


def token_send(request):
    if 'signedup' in request.session:
        try:
            del request.session['signedup']
        except KeyError:
            pass
        return render(request, 'token_send.html')
    else:
        return render(request, 'Page404.html')


def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()
        print(profile_obj)
        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect(login_view)
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            request.session['verified'] = "yes"
            return redirect('/success')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('/error')


def error_page(request):
    return render(request, 'Page404.html')


def send_mail_after_registration(email, token):
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


class UserUpdateView(UpdateView):  # Updating A User Info
    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'my_account.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user


def user_account(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    questions = Question.objects.all()
    answers = Answer.objects.all()
    last_question = Question.objects.filter(created_by=user).last()
    questions_count = 0
    answers_count = 0
    likes_count = 0
    owner_name = user.username
    owner_name = owner_name
    is_follower = False
    for question in questions:
        owner = question.created_by.username
        if owner == owner_name:
            questions_count += 1
    for answer in answers:
        owner = answer.created_by.username
        if owner == owner_name:
            answers_count += 1
            likes_count += answer.num_likes
    # getting all followers that follow "followed_user" (what prove they are following him is the value "Unfollow")
    # and getting them by the newest
    followers = UserFollowing.objects.filter(value='UnFollow', followed_user=user).order_by('-created')
    # getting followers users
    # getting the followers count
    followers_count = UserFollowing.objects.filter(value='UnFollow', followed_user=user).values(
        'following_user').count()
    for follower in followers:
        if follower.following_user == request.user:
            is_follower = True
            break
    context = {
        'last_question': last_question,
        'user_questions_count': questions_count,
        'user_answers_count': answers_count,
        'likes_count': likes_count,
        'user_profile': user,
        'followers_count': followers_count,
        'is_follower': is_follower,
        'followers': followers,
    }
    return render(request, 'user_account.html', context)


@login_required()
def follow_user(request, user_id):
    if request.method == 'POST':
        data = {}
        user_followed = User.objects.get(id=user_id)
        request_follower = User.objects.get(id=request.user.id)
        user_followers = UserFollowing.objects.filter(followed_user=user_followed).values('following_user')
        no_follow = True
        for user_follower in user_followers:
            if request_follower.id == user_follower['following_user']:
                follow = UserFollowing.objects.filter(following_user=request_follower,
                                                      followed_user=user_followed).first()
                print(follow)
                if follow.value == 'Follow':
                    follow.value = 'UnFollow'
                    follow.save()
                else:
                    follow.value = 'Follow'
                    follow.created = timezone.now()
                    follow.save()
                no_follow = False
                followers_count = UserFollowing.objects.filter(value='UnFollow', followed_user=user_followed).count()

                data = {
                    'value': follow.value,
                    'followers': followers_count
                }
                break
        if no_follow:
            new_follow = UserFollowing.objects.get_or_create(followed_user=user_followed,
                                                             following_user=request_follower, created=timezone.now()
                                                             , value='UnFollow')
            try:
                follow = UserFollowing.objects.filter(followed_user=user_followed)
            except AttributeError as e:
                pass
            followers_count = UserFollowing.objects.filter(value='UnFollow', followed_user=user_followed).count()
            try:
                data = {
                    'followers': followers_count,
                    'value': follow.value
                }
            except AttributeError as e:
                pass
        return JsonResponse(data, safe=False)
    else:
        return redirect(user_account, user_id=user_id)


def users_list(request):
    users = User.objects.all().order_by('-date_joined')
    page = request.GET.get('page', 1)
    paginator = Paginator(users, 8)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        'users': users
    }
    return render(request, 'users_list.html', context)


def followers_list(request, user_id):
    user_followed = get_object_or_404(User, id=user_id)
    user_followers = UserFollowing.objects.filter(value='UnFollow', followed_user=user_followed)
    page = request.GET.get('page', 1)
    paginator = Paginator(user_followers, 8)
    try:
        user_followers = paginator.page(page)
    except PageNotAnInteger:
        user_followers = paginator.page(1)
    except EmptyPage:
        user_followers = paginator.page(paginator.num_pages)
    context = {
        'user_followed': user_followed,
        'user_followers': user_followers,
    }
    return render(request, 'user_followers.html', context)
