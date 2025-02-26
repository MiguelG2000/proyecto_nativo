from django.shortcuts import render

# Create your views here.
def report_dashboard(request):
    return render(request, 'report/dashboard.html')