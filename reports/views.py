from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from datetime import datetime
import csv

from booking.models import RoomType, Room, RoomReservations

class SuperUserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    
class ReportTemplateView(SuperUserPassesTestMixin, TemplateView):
    template_name = 'report/report_form.html'
    
# Create your views here.
@user_passes_test(lambda user: user.is_superuser)
def report(request, start_date, end_date):

    # Get object class
    obj_class = {'room_types': RoomType, 'rooms': Room, 'reservations': RoomReservations}
    obj = request.GET.get('object')

    # Send response
    response = HttpResponse(content_type='text/csv;')
    
    # Get file name according to the class and update response
    filenames = {'room_types' : 'Room_types', 'rooms' : 'Rooms', 'reservations': 'Reservations'}
    response['Content-Disposition'] = f'attachment; filename={str(filenames[obj])} {str(datetime.now().date().strftime("%m-%d-%Y"))}.csv'

    # Writer
    writer = csv.writer(response)

    # Get all instances of the class
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if (start_date and end_date):
        rs = obj_class[obj].objects.filter(
            Q(check_out_date__gte=start_date) & Q(check_in_date__lte=end_date)).values('room_id')
    else:
        rs = obj_class[obj].objects.all()

    # Write headers
    headers = {
        'room_types': ['Type', 'Short Description', 'Description', 'Max Adults', 'Max Children', 'Price'],
        'rooms': ['Number', 'Building', 'Avaliability', 'Type'],
        'reservations': ['Room', 'Adults', 'Children', 'Total Price', 'Check In', 'Check Out']
    }
    writer.writerow(headers[obj])

    
    attributes = {
        'room_types': ['', 'short_description','description', 'max_adults', 'max_children'],
        'rooms': ['number', 'building', 'availability', 'room_type'],
        'reservations': ['room', 'adults', 'children', 'total_price', 'check_in_date', 'check_out_date']
    }

    # Populate the CSV
    for r in rs:
        row = []
        for att in attributes[obj]:
            row.append(str(getattr(r, att, str(r))))

        writer.writerow(row)

    return response


@user_passes_test(lambda user: user.is_superuser)
def reports(request):
    if (request.GET.get('start_date') and request.GET.get('end_date')):
        return report(request, '', '')
    else:
        return report(request, start_date=request.GET.get('start_date'), end_date=request.GET.get('end_date'))
