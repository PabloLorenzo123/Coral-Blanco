from django.views.generic import ListView, DetailView, TemplateView
from datetime import date, timedelta

from booking.models import RoomType

# Create your views here.
class HomePageView(TemplateView):
    # For the date inputs.
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['today'] = today
        context['tomorrow'] = today + timedelta(days=1)
        return context

    
