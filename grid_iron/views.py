import datetime as dt
# import json
import re
# import sys

from django.shortcuts import redirect, render
# from django.http import HttpResponse

from .forms import GridIronUrlForm
from .grid_iron_calc import grid_iron_calc
from .models import Gridiron

from rest_framework import viewsets
# from rest_framework import permissions
from .serializers import GridironSerializer


def grid_iron_view(request):
    """Routes to site home page template.
    Arguments:
        request {object} -- HTTPRequest object
    Returns:
        [object] -- HTTPResponse object
    """
    if request.method == 'GET':
        forms = {
            'p_url': GridIronUrlForm(),
        }
        return render(request, 'grid_iron_calc.html', forms)
    else:
        return redirect('')


def grid_iron_results_view(request):
    """Renders the Heat Factor graph for a given USPSA match link.
    Arguments:
        request {object} -- HTTPRequest object
    Returns:
        [dict] -- renders the content to the url in the form of a dict
                  containing the matplotlib image and the data.
    """
    practiscore_url = None
    team_dict = None
    if request.method == 'POST':
        if GridIronUrlForm(request.POST).is_valid():
            practiscore_url = request.POST.get('p_url')
    else:
        exception_content = {
            'message': 'grid_iron incorrect method error.',
        }
        return render(request, 'error.html', exception_content)

    try:
        team_dict = grid_iron_calc(practiscore_url)
    except Exception as e:
        if re.match('Error downloading AWS S3 json file.', e.args[0]):
            exception_content = {
                'message': e.args[0]
            }
            return render(request, 'error.html', exception_content)

        elif re.match('Bad URL.', e.args[0]):
            return redirect('/bad_url/')

    content = {
        'team_dict': team_dict,
        'date': dt.datetime.now(),
    }
    return render(request, 'grid_iron_results.html', content)


def bad_url_view(request):
    """Routes to bad_url.html for heat_factor function.  When the user
       provides an incorrect practiscore URL this function is called.  This
       acts as a backup to the javascript function doing form validation
       at the browser.
    Arguments:
        request {object} -- HTTPRequest object
    Returns:
        [object] -- HTTPResponse object
    """
    if request.method == 'GET':
        forms = {
            'practiscore_url_form': GridIronUrlForm(),
        }
        return render(request, 'bad_url.html', forms)


def error_view(request):
    return render(request, 'error.html')


class GridironViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Gridiron.objects.all()
    serializer_class = GridironSerializer
    # permission_classes = [permissions.IsAuthenticated]
