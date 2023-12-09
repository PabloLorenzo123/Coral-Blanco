from django.urls import path

from .views import (
    ReportTemplateView,
    reports
)

urlpatterns = [
    path('report_form', ReportTemplateView.as_view(), name='reports'),
    path('download_report', reports, name='download_report'),
]