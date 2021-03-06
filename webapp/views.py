# Import all the models and libraries we need
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
from .models import Post, Comment, SearchTerm
from .forms import PostForm, CommentForm, SearchForm
from django.core.urlresolvers import reverse
from django.utils import timezone
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
import operator
import math

posts = Post.objects.all().filter().order_by('-created_on') # Get all the posts on Devhaven.io

def filterPages(posts, context):
    for post in posts:
        post.commentCount = len(post.comment_set.all())

    for post in posts: # Generate mailto link (html href doesn't allow concatenation of strings)
        post.reportLink = "mailto:henry.david.zhu@gmail.com?Subject=Flagged%20-%20" + post.title + "%20(Reason%20below)"

    context['posts'] = posts

def index(request):
    global posts

    posts = Post.objects.all().filter().order_by('-created_on') # Use filter on the QuerySet to sort by time
    context = {'posts' : posts, 'authenticated': request.user.is_authenticated()}

    if request.method == "POST":
        searchForm = SearchForm(request.POST or None)

        if searchForm.is_valid():
            category = searchForm.cleaned_data.get('category')

            if category == 'all':
                return redirect("../")
            else:
                searchPosts = Post.objects.all().filter(field=category).order_by('-created_on')
                filterPages(searchPosts, context)
                
                return render(request, 'webapp/home.html', context)
        else:
            print(searchForm.errors)

    filterPages(posts, context)

    return render(request, 'webapp/home.html', context)

def filtercategory(request, category):
    global posts

    posts = Post.objects.all().order_by('-created_on') # Use filter on the QuerySet to sort by time
    context = {'posts': posts, 'authenticated': request.user.is_authenticated()}

    if category == 'all':
        for post in posts:
            post.commentcount = len(post.comment_set.all())

        for post in posts: # Generate mailto link (html href doesn't allow concatenation of strings)
            post.reportLink = "mailto:henry.david.zhu@gmail.com?Subject=Flagged%20-%20" + post.title + "%20(Reason%20below)"
    else:
        searchPosts = Post.objects.all().filter(field=category).order_by('-created_on')

        for post in searchPosts:
            post.commentCount = len(post.comment_set.all())

        for post in searchPosts: # Generate mailto link (html href doesn't allow concatenation of strings)
            post.reportLink = "mailto:henry.david.zhu@gmail.com?Subject=Flagged%20-%20" + post.title + "%20(Reason%20below)"

        context['posts'] = searchPosts

    return render(request, 'webapp/searchthreads.html', context)

def userprofile(request, author):
    userPosts = Post.objects.all().filter(author__username=author).order_by('created_on').reverse()

    for post in userPosts:
        post.commentCount = len(post.comment_set.all())

    for post in userPosts: # Generate mailto link (html href doesn't allow concatenation of strings)
        post.reportLink = "mailto:henry.david.zhu@gmail.com?Subject=Flagged%20-%20" + post.title + "%20(Reason%20below)"

    context = {'posts': userPosts, 'authenticated': request.user.is_authenticated(), 'username': author}

    return render(request, 'webapp/userprofile.html', context)

def register(request):
    form = UserForm(request.POST or None) # Registration form
    title = "Register." # Title
    instruction = "The <b>email*</b> is required but only the username is displayed." #Instruction towards user
    displaySignUp = True # Only display the sign up if the user hasn't finished registering yet

    context = {
        "title": title,
        "form": form,
        "instruction": instruction,
        "displaySignUp": displaySignUp,
        "authenticated": request.user.is_authenticated() # Whether the user is authenticated or not
    }

    if form.is_valid():
        instruction = """We're excited to have you as a new user.""" # Welcome message when user has finished up the registration process

        context = {
            "title" : "Welcome to the community!",
            "form": form,
            "instruction": instruction,
            "displaySignUp" : False,
            "authenticated": request.user.is_authenticated()
        }

        try:
            user = User.objects.create_user(form.cleaned_data.get('username'), form.cleaned_data.get('email'), form.cleaned_data.get('password')) # If the user is valid, save the user into the database
            user.save()
            return HttpResponseRedirect("../login")
        except IntegrityError as e:
            context = {
                "title" : title,
                "form": form,
                "instruction": "We're sorry, but that user is already registered.", # When the username is already taken
                "displaySignUp" : True,
                "authenticated": request.user.is_authenticated()
            }            

    return render(request, 'webapp/register.html', context)

def login(request):
    next = request.GET.get('next', '/') # Direct the user to the home page after he / she logs in.
    instruction = "Login validation is <b>case-sensitive</b>."

    if request.method == "POST":
        username = request.POST['username'] # Get the username entered
        password = request.POST['password'] # Get the password entered 
        user = authenticate(username=username, password=password) # Get the user

        if user is not None: # If user exists
            if user.is_active: # If user is active
                auth_login(request, user) # Log the user in
                return HttpResponseRedirect(next) # REdirect the user to the main page
            else:
                instruction = "This user is currently inactive." # Display that the user is inactive
        else:
            instruction = "Incorrect user and/or password combination." # Displayt hat the user has entered incorrect data

    context = {
        'redirect_to': next,
        'instruction': instruction,
        'authenticated': request.user.is_authenticated()
    }
    
    return render(request, "webapp/login.html", context)

def logout(request):
    auth.logout(request) # Log the user out
    return redirect('../login/')

@user_passes_test(lambda u: u.is_authenticated)
def add_post(request):
    form = PostForm(request.POST or None) # Form for posting threads
    error = ""

    context = { 'form': form, "authenticated": request.user.is_authenticated(), "error": error }

    if request.method == "POST":
        if form.is_valid() and request.user.is_authenticated(): # Check if the form is validated and the user has been authenticated
            comparePosts = Post.objects.all()

            duplicate = False

            for post in comparePosts:
                if post.title == form.cleaned_data.get("title"):
                    duplicate = True
                    break

            print("Duplicate: " + str(duplicate))

            if duplicate:
                print("Title has already been used before.")
                context["error"] = "Validation error: Title has already been used before."
            else:
                try:
                    post = Post.objects.create(author=request.user, title=form.cleaned_data.get("title"), text=form.cleaned_data.get("text"), 
    				field = form.cleaned_data.get("field"))
                    return redirect(post)
                except IntegrityError as e:
                    print(e)
        else:
            print("Invalid form")
            print(form.errors)
            context["error"] = "Validation error: The text field is blank."

    return render_to_response('webapp/startthread.html', context,
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

    post.commentCount = len(post.comment_set.all())

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

def your_post(request):
    posts2 = Post.objects.all().filter(author__username=str(request.user)).order_by('-created_on') # Use filter on the QuerySet to sort by time
    numPosts = len(posts2)
	
    for post in posts2:
        post.commentCount = len(post.comment_set.all())

    for post in posts2:
        post.reportLink = "mailto:henry.david.zhu@gmail.com?Subject=Flagged%20-%20" + post.title + "%20(Reason%20below)"

    return render(request, 'webapp/yourthreads.html', {'authenticated': request.user.is_authenticated(), 'posts':posts2, 'numPosts':numPosts})