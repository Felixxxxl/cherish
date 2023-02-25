from django.shortcuts import render

# Create your views here.

def recipePage(request):
    return render(request,'recipe.html')