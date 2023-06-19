from django.shortcuts import render

# Create your views here.

def entry(request):
    return render(request, "frontend/entry.js", content_type="text/javascript")