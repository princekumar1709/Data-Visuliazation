from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.utils import timezone

# Create your views here.

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        #check usernames and password already exist or not
        if User.objects.filter(username=username).exists():
             messages.info(request,'username already exists')
             return redirect('signup')
        else:
            user= User.objects.create_user(username=username,password=password)
            user.save()
            # print('User created successfully')
            return redirect('signin')  # Redirect to the login page
        
    #if request.method is 'GET'    
    else:
         return render(request,'signup.html')

def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        last_login = timezone.now()
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print("Login Succesfull")
            return redirect("homepage")
        else:
            messages.info(request,'Invalid username.')
            return redirect("signin")

    return render(request, "signin.html")

def logout(request):
    auth.logout(request)
    return redirect("homepage")


