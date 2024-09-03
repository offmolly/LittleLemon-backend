from django.shortcuts import render

def home(request):
    return render(request,"home.html")

def readme(request):
    return render(request,"readme.html")