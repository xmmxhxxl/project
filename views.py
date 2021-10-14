from django.http import HttpResponse

def index(request):
        return HttpResponse("晓丽呀")

def login(request):
	return redirect("/index")

def use(request):
	return 0
