# TODO: Make sure to create an HTTPResponseRedirect to ("/register-success/")

from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from .forms import UserForm
from django.contrib.auth import authenticate, login
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.core.urlresolvers import reverse
from django.utils import timezone
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
import operator

posts = Post.objects.all().filter().order_by('-created_on')
postRequests = 0

def index(request):
    title = "Devhaven.io"

    if (request.user.is_authenticated()): # If the user is logged-in, display Welcome Back!
        title = "Welcome back {0}.".format(request.user)

    context = {
        "template_title": title,
        "authenticated": request.user.is_authenticated()
    } 

    return render(request, 'webapp/home.html', context)

def register(request):
    form = UserForm(request.POST or None)
    title = "Registration is quick and easy."
    instruction = "The <b>email*</b> is required but only the username is displayed.<br>As a matter of policy, we allow multiple accounts per user."
    displaySignUp = True

    context = {
        "title": title,
        "form": form,
        "instruction": instruction,
        "displaySignUp": displaySignUp,
        "authenticated": request.user.is_authenticated()
    }

    if form.is_valid():
        instruction = """We're excited to have you as a new user."""

        context = {
            "title" : "Welcome to the community!",
            "form": form,
            "instruction": instruction,
            "displaySignUp" : False,
            "authenticated": request.user.is_authenticated()
        }

        try:
            user = User.objects.create_user(form.cleaned_data.get('username'), form.cleaned_data.get('email'), form.cleaned_data.get('password'))
            user.save()
        except IntegrityError as e:
            context = {
                "title" : title,
                "form": form,
                "instruction": "We're sorry, but that user is already registered.",
                "displaySignUp" : True,
                "authenticated": request.user.is_authenticated()
            }            

    return render(request, 'webapp/register.html', context)

def login(request):
    next = request.GET.get('next', '/')
    instruction = "Sign in using your valid username and password (<b>case-sensitive</b>)."

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect(next)
            else:
                instruction = "This user is currently inactive."
        else:
            instruction = "Incorrect user and/or password combination."

    context = {
        'redirect_to': next,
        'instruction': instruction,
        'authenticated': request.user.is_authenticated()
    }
    
    return render(request, "webapp/login.html", context)

def Logout(request):
    auth.logout(request)
    return redirect('../login/')

@user_passes_test(lambda u: u.is_authenticated)
def add_post(request):
    form = PostForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid() and request.user.is_authenticated():
            try:
                post = Post.objects.create(author=request.user, title=form.cleaned_data.get("title"), text=form.cleaned_data.get("text"), 
				field = form.cleaned_data.get("field"))
                return redirect(post)
            except IntegrityError as e:
                print(e)
        else:
            print("Invalid form")
            print(form.errors)

    return render_to_response('webapp/startthread.html', 
                              { 'form': form,
                                "authenticated": request.user.is_authenticated() },
                              context_instance=RequestContext(request))

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    postAuthor = post.author

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.title = form.cleaned_data.get("title")
            post.author = postAuthor
            post.published_date = timezone.now()
            post.save()
            redirectLink = '../../' + str(post.slug)
            return redirect(redirectLink)
        else:
            print("Errors: " + str(form.errors))
    elif request.POST:
        form = PostForm(instance=post)

    return render(request, 'webapp/threadedit.html', {'post': post, 'authenticated': request.user.is_authenticated()})

def response_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    name = comment.name

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.name = name
            comment.published_date = timezone.now()
            comment.save()
            return render(request, 'webapp/responseeditmessage.html', {'authenticated': request.user.is_authenticated()})
        else:
            print("Errors: " + str(formerrors))
    elif request.POST:
        form = CommentForm(instance=comment)

    return render(request, 'webapp/responseedit.html', {'comment': comment, 'authenticated': request.user.is_authenticated()})

def delete_new(request, pk):
    postToDelete = Post.objects.get(pk=pk).delete()
    global posts
    posts = Post.objects.all().filter().order_by('-created_on')
    return render(request, 'webapp/deletemessage.html', {'authenticated': request.user.is_authenticated()})

def delete_response(request, pk):
    responseToDelete = Comment.objects.get(pk=pk).delete()
    return render(request, 'webapp/deletemessage.html', {'authenticated': request.user.is_authenticated()})

def view_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    form = CommentForm(request.POST or None)

    hit_count = HitCount.objects.get_for_object(post)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    print(hit_count_response)
	
    if form.is_valid() and request.user.is_authenticated():
        comment = form.save(commit=False)
        comment.post = post
        comment.name = request.user
        comment.save()
        return redirect(request.path)
    else:
        print(form.is_valid())   #form contains data and errors
        print(form.errors)

    form.initial['name'] = request.session.get('name')
    form.initial['email'] = request.session.get('email')
    form.initial['website'] = request.session.get('website')

    return render_to_response('webapp/threadlist.html',
                              {
                                  'post': post,
                                  'form': form,
                                  'authenticated': request.user.is_authenticated
                              },
                              context_instance=RequestContext(request))

def post_list(request):
    global posts
    global postRequests

    posts = Post.objects.all().filter().order_by('-created_on') # Use filter on the QuerySet to sort by time
    context = {'posts' : posts, 'authenticated': request.user.is_authenticated()}

    numComments = 0

    for post in posts:
        numComments = 0

        for comment in post.comment_set.all():
            numComments = numComments + 1

        post.commentCount = numComments

    return render(request, 'webapp/threadfeed.html', context)

def your_post(request):
    posts2 = Post.objects.filter(author__username=str(request.user))

    for post in posts2:
        numComments = 0

        for comment in post.comment_set.all():
            numComments = numComments + 1

        post.commentCount = numComments

    return render(request, 'webapp/yourthreads.html', {'authenticated': request.user.is_authenticated(), 'posts':posts2})