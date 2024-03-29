import datetime as dt
import re

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.http import require_GET

from .forms import GridIronUrlForm
from .grid_iron_calc import grid_iron_calc, grid_iron_db_to_csv
from .models import Gridiron

from rest_framework import viewsets
from .serializers import GridironSerializer


def grid_iron_view(request):
    """Routes to grid iron calculator page template.
    Arguments:
        request [object] -- HTTPRequest object
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
    """Renders the Gridiron team results.
    Arguments:
        request {object} -- HTTPRequest object
    Returns:
        [dict] -- renders the content to the url in the form of a dict.
    """
    if request.method == 'POST':
        if GridIronUrlForm(request.POST).is_valid():
            practiscore_url = request.POST.get('p_url')
    else:
        exception_content = {
            'message': 'grid_iron incorrect method error.',
        }
        return render(request, 'error.html', exception_content)

    try:
        team_dict, match_name = grid_iron_calc(practiscore_url)
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
        'match_name': match_name,
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


@require_GET
def grid_iron_db_csv(request):
    team_list = grid_iron_db_to_csv()

    return HttpResponse("\n".join(team_list), content_type="text/plain")


class GridironViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Gridiron.objects.all()
    serializer_class = GridironSerializer
    # permission_classes = [permissions.IsAuthenticated]
