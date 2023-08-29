from django.shortcuts import render,redirect
import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.utils import timezone

# Create your views here.

def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        username = request.POST.get("username")
        password = request.POST.get("password")
        date_joined = timezone.now()
        user = User.objects.create_user(
            username=username, password=password, date_joined=date_joined
        )
        user.save()
        print("User created")
        return redirect("/sign-in")

    return render(request, "sign-up.html")




def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        last_login = timezone.now()
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print("Login Succesfull")
            return redirect("/")
        else:
            messages.info(request, "Invalid credentials")
            return redirect("/sign-in")

    return render(request, "sign-in.html")

def logout(request):
    auth.logout(request)
    return redirect("/sign-in")


