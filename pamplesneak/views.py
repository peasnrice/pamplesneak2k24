from django.shortcuts import render

# Returns Home Page from url /
def home(request):
    args = {}
    return render(request, "index.html", args)