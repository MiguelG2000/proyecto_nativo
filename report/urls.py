from django.urls import path

from report.views import (
    report_dashboard,)
urlpatterns = [
        path('', report_dashboard, name='report_dashboard'),
    ]