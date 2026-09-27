from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import UserProfile, Post
from .forms import PostForm, SignUpForm, ProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

# Create your views here.


def home(request):

	if request.user.is_authenticated:
		form = PostForm(request.POST or None, request.FILES or None)
		if request.method == "POST":
			if form.is_valid():
				post = form.save(commit=False)
				post.user = request.user
				post.save()
				messages.success(request, ("Your Post Has Been Posted!"))
				return redirect('home')

		posts_list = Post.objects.all().order_by("-created_at")
		paginator = Paginator(posts_list, 10)
		page_number = request.GET.get('page')
		posts = paginator.get_page(page_number)

		return render(request, 'home.html', {"posts": posts, "form": form})
	else:
		posts_list = Post.objects.all().order_by("-created_at")
		paginator = Paginator(posts_list, 10)
		page_number = request.GET.get('page')
		posts = paginator.get_page(page_number)

		return render(request, 'home.html', {"posts": posts})


def profile_list(request):
	if request.user.is_authenticated:
		profiles = UserProfile.objects.exclude(user=request.user)
		return render(request, 'profile_list.html', {"profiles": profiles})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')


def unfollow(request, pk):

	if request.user.is_authenticated:
		profile = UserProfile.objects.get_or_create(user_id=pk)[0]
		request.user.profile.following.remove(profile)
		request.user.profile.save()
		messages.success(request, (f"You Have Successfully Unfollowed {profile.user.username}"))
		return redirect(request.META.get("HTTP_REFERER"))
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')


def follow(request, pk):

	if request.user.is_authenticated:
		profile = UserProfile.objects.get_or_create(user_id=pk)[0]
		request.user.profile.following.add(profile)
		request.user.profile.save()
		messages.success(request, (f"You Have Successfully Followed {profile.user.username}"))
		return redirect(request.META.get("HTTP_REFERER"))
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')


def profile(request, pk):

	if request.user.is_authenticated:
		profile = UserProfile.objects.get_or_create(user_id=pk)[0]
		posts_list = Post.objects.filter(user_id=pk).order_by("-created_at")
		paginator = Paginator(posts_list, 10)
		page_number = request.GET.get('page')
		posts = paginator.get_page(page_number)

		if request.method == "POST":
			current_user_profile = request.user.profile
			action = request.POST['follow']
			if action == "unfollow":
				current_user_profile.following.remove(profile)
			elif action == "follow":
				current_user_profile.following.add(profile)
			current_user_profile.save()

		return render(request, "profile.html", {"profile": profile, "posts": posts})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')


def followers(request, pk):

	if request.user.is_authenticated:
		if request.user.id == pk:
			profiles = UserProfile.objects.get_or_create(user_id=pk)[0]
			return render(request, 'followers.html', {"profiles": profiles})
		else:
			messages.success(request, ("That's Not Your Profile Page..."))
			return redirect('home')
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')


def follows(request, pk):

	if request.user.is_authenticated:
		if request.user.id == pk:
			profiles = UserProfile.objects.get_or_create(user_id=pk)[0]
			return render(request, 'follows.html', {"profiles": profiles})
		else:
			messages.success(request, ("That's Not Your Profile Page..."))
			return redirect('home')
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')


def login_user(request):

	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, ("You Have Been Logged In! Get Posting!"))
			return redirect('home')
		else:
			messages.success(request, ("There was an error logging in. Please Try Again..."))
			return redirect('login')
	else:
		return render(request, "login.html", {})


def logout_user(request):
	logout(request)
	messages.success(request, ("You Have Been Logged Out."))
	return redirect('home')


def register_user(request):

	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("You have successfully registered! Welcome!"))
			return redirect('home')
	return render(request, "register.html", {'form': form})


def update_user(request):

	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		profile_user = UserProfile.objects.get_or_create(user__id=request.user.id)[0]
		user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
		profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=profile_user)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			login(request, current_user)
			messages.success(request, ("Your Profile Has Been Updated!"))
			return redirect('home')
		return render(request, "update_user.html", {'user_form': user_form, 'profile_form': profile_form})
	else:
		messages.success(request, ("You Must Be Logged In To View That Page..."))
		return redirect('home')


def post_like(request, pk):

	if request.user.is_authenticated:
		post = get_object_or_404(Post, id=pk)
		if post.liked_by.filter(id=request.user.id):
			post.liked_by.remove(request.user)
		else:
			post.liked_by.add(request.user)
		return redirect(request.META.get("HTTP_REFERER"))
	else:
		messages.success(request, ("You Must Be Logged In To View That Page..."))
		return redirect('home')


def post_show(request, pk):

	post = get_object_or_404(Post, id=pk)
	if post:
		return render(request, "show_post.html", {'post': post})
	else:
		messages.success(request, ("That Post Does Not Exist..."))
		return redirect('home')


def delete_post(request, pk):
	if request.user.is_authenticated:
		post = get_object_or_404(Post, id=pk)
		if request.user.username == post.user.username:
			if request.method == "POST":
				post.delete()
				messages.success(request, ("The Post Has Been Deleted!"))
				return redirect('home')
			return render(request, "delete_post.html", {'post': post})
		else:
			messages.success(request, ("You Don't Own That Post!!"))
			return redirect('home')
	else:
		messages.success(request, ("Please Log In To Continue..."))
		return redirect('login')


def edit_post(request, pk):

	if request.user.is_authenticated:
		post = get_object_or_404(Post, id=pk)
		if request.user.username == post.user.username:
			form = PostForm(request.POST or None, request.FILES or None, instance=post)
			if request.method == "POST":
				if form.is_valid():
					post = form.save(commit=False)
					post.user = request.user
					post.save()
					messages.success(request, ("Your Post Has Been Updated!"))
					return redirect('home')
			else:
				return render(request, "edit_post.html", {'form': form, 'post': post})
		else:
			messages.success(request, ("You Don't Own That Post!!"))
			return redirect('home')
	else:
		messages.success(request, ("Please Log In To Continue..."))
		return redirect('home')


def search(request):
	if request.method == "POST":
		search = request.POST['search']
		searched = Post.objects.filter(content__contains=search)
		return render(request, 'search.html', {'search': search, 'searched': searched})
	else:
		return render(request, 'search.html', {})
