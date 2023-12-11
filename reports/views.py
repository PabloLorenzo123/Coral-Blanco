from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from datetime import datetime
import csv

from booking.models import RoomType, Room, Reservation, Guest

class SuperUserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    
class ReportTemplateView(SuperUserPassesTestMixin, TemplateView):
    template_name = 'report/report_form.html'
    
# Create your views here.
@user_passes_test(lambda user: user.is_superuser)
def report(request, start_date, end_date):

    # Get object class
    obj_class = {'room_types': RoomType, 'rooms': Room, 'reservations': Reservation, 'guests' : Guest}
    obj = obj_class[request.GET.get('object')]

    # Send response
    response = HttpResponse(content_type='text/csv;')
    
    # Get start date and end date
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Get file name according to the class and update response

    # Format file name according to the given dates or not given
    file_date = ""
    if (start_date and end_date):
        file_date = f'({datetime.strptime(start_date, "%Y-%m-%d").strftime("%m-%d-%Y")}) - ({datetime.strptime(end_date, "%Y-%m-%d").strftime("%m-%d-%Y")})'
    else:
        file_date = f'{str(datetime.now().date().strftime("%m-%d-%Y"))}'

    # Name file
    response['Content-Disposition'] = f'attachment; filename={obj.csv_file_name()} {file_date}.csv'

    # Writer
    writer = csv.writer(response)

    # If reservation option was choosen and a start and end date was chosen then we filter the database
    # otherwise we don't filter anything.
    if obj == Reservation:
        if (start_date and end_date):
            rs = obj.objects.filter(
                Q(check_out_date__gte=start_date) & Q(check_in_date__lte=end_date)
            )
        # Nothing to filter so obtain all objects from the database
        else:
            rs = obj.objects.all()

    # If guest option was choosen and a start and end date was chosen then we filter the database,
    # otherwise we don't filter anything
    elif obj == Guest:
        if (start_date and end_date):
            rs = obj.objects.filter(
                Q(created_at__gte=start_date) & Q(created_at__lte=end_date)
            )
        # Nothing to filter so obtain all objects from the database
        else:
            rs = obj.objects.all()

    # Else get all instances of the chosen class
    else:
        rs = obj.objects.all()

    # Write headers
    writer.writerow(obj.csv_headers())

    # If guest was chosen then we gotta write rows with the avaibility field
    if obj == Room:
        # Populate the CSV
        for r in rs:
            print("ssstarttt ---- " + start_date)
            print(end_date)
            writer.writerow(r.to_csv(start_date, end_date))
    else:
        # Populate the CSV
        for r in rs:
            writer.writerow(r.to_csv())

    return response


@user_passes_test(lambda user: user.is_superuser)
def reports(request):
    if (request.GET.get('start_date') and request.GET.get('end_date')):
        return report(request, '', '')
    else:
        return report(request, start_date=request.GET.get('start_date'), end_date=request.GET.get('end_date'))
