from django.http import HttpResponse

def account_home(request):
    return HttpResponse("Accounts page working 👤")
