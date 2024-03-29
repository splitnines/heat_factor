import datetime as dt
import json
import re
import sys

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.http import require_GET

from .classificationwhatif import ClassificationWhatIf, uspsa_model_util
from .forms import (
    AccuStatsForm1, AccuStatsForm2, GetUppedForm,
    PPSForm1, PPSForm2, PractiscoreUrlForm
)
from .heatfactor import heatfactor
from .models import Uspsa
from .pointspersecond import pointspersec
from .uspsastats import uspsastats
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UspsaSerializer


def sys_logger(app_name, *app_data):
    """Poor excuse for a logging system"""
    print(f'SYS_LOGGER: {app_name}, {app_data}', file=sys.stderr)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def home_view(request):
    """Routes to site home page template.
    Arguments:
        request {object} -- HTTPRequest object
    Returns:
        [object] -- HTTPResponse object
    """
    if request.method == 'GET':
        forms = {
            'practiscore_url_form': PractiscoreUrlForm(),
            'get_upped_form': GetUppedForm(),
            'accu_stats_form1': AccuStatsForm1(),
            'pps_form1': PPSForm1(),
        }
        return render(request, 'home.html', forms)
    else:
        return redirect('')


def heat_factor_view(request):
    """Renders the Heat Factor graph for a given USPSA match link.
    Arguments:
        request {object} -- HTTPRequest object
    Returns:
        [dict] -- renders the content to the url in the form of a dict
                  containing the matplotlib image and the data.
    """
    practiscore_url = None
    chart = None
    if request.method == 'POST':
        if PractiscoreUrlForm(request.POST).is_valid():
            practiscore_url = request.POST.get('p_url')
    else:
        exception_content = {
            'message': 'heat_factor incorrect method error.',
        }
        return render(request, 'error.html', exception_content)

    sys_logger('heat_factor', practiscore_url)
    try:
        chart = heatfactor(practiscore_url)
    except Exception as e:
        if re.match('Error downloading AWS S3 json file.', e.args[0]):
            exception_content = {
                'message': e.args[0]
            }
            return render(request, 'error.html', exception_content)

        elif re.match('Bad URL.', e.args[0]):
            return redirect('/bad_url/')

    content = {
        'chart': chart,
        'date': dt.datetime.now(),
    }
    return render(request, 'heat_factor.html', content)


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
            'practiscore_url_form': PractiscoreUrlForm(),
        }
        return render(request, 'bad_url.html', forms)


def get_upped_view(request):
    """Creates a ClassificationWhatIf object and calls various methods on that
       object to produce the percentage a shooter needs to move up a class or
       for a new shooter to get an initial classification.
    Arguments:
        request {object} -- HTTPRequest object
    Returns:
        [object] -- HTTPResponse object
    """
    mem_num = None
    division = None
    if request.method == 'POST':
        if GetUppedForm(request.POST).is_valid():
            mem_num = request.POST.get('mem_num_1')
            division = request.POST.get('division_1')
        else:
            exception_content = {
                'message': 'get_upped incorrect method error.',
            }
            return render(request, 'error.html', exception_content)
    sys_logger('get_upped', mem_num, division)

    # exception_content = {
    #         'response_text': f"""
    #             <font color=\"red\">2 Mikes, 2 No-shoots:</font> Member number
    #             <font color=\"red\">{mem_num}</font> in
    #             <font color=\"red\">{division}</font> division.<br> If
    #             your USPSA classifier scores are set to priviate this
    #             tool won\'t work.<br> Also, if you don\'t have at least 3
    #             qualifing classifier scores on record this tool won\'t work.
    #             """,
    #         'date': str(dt.datetime.now())
    #     }
    exception_content = {
            'response_text': f"""
                This tool is no longer working because USPSA.org is now blocking 
                my access to the classifier data.
                """,
            'date': str(dt.datetime.now())
        }
    try:
        shooter = ClassificationWhatIf(mem_num, division)
        uspsa_model_util(Uspsa, mem_num, division)
    except Exception:
        # if request.is_ajax():
        if is_ajax(request):
            return HttpResponse(
                json.dumps(exception_content), content_type="application/json"
            )
        else:
            return render(request, 'get_upped.html', exception_content)
        # return render(request, 'get_upped.html', exception_content)

    if shooter.get_shooter_class() == 'GM':
        content = {
            'response_text': f"""
                You\'re a <font color=\"red\">{shooter.get_shooter_class()}
                </font>. Nowhere to go from here.""",
            'date': str(dt.datetime.now()),
        }
        # if request.is_ajax():
        if is_ajax(request):
            return HttpResponse(
                json.dumps(content), content_type="application/json"
            )
        else:
            return render(request, 'get_upped.html', content)

    if shooter.get_shooter_class() == 'U':
        try:
            initial_dict = shooter.get_initial()
        except Exception:
            # if request.is_ajax():
            if is_ajax(request):
                return HttpResponse(
                    json.dumps(exception_content),
                    content_type="application/json"
                )
            else:
                return render(request, 'get_upped.html', exception_content)

        initial_calssification_html = '<br>'.join(
            [f"""You need a score of <font color=\"red\">{initial_dict[k]}%
             </font> in your next classifier to achieve an initial
             classification of <font color=\"red\">{k}</font> class."""
             for k in initial_dict]
        )
        content = {
            'response_text': initial_calssification_html,
            'date': str(dt.datetime.now()),
        }
        # if request.is_ajax():
        if is_ajax(request):
            return HttpResponse(
                json.dumps(content), content_type="application/json"
            )
        else:
            return render(request, 'get_upped.html', content)

    if shooter.get_upped() > 100:
        content = {
            'response_text': f"""
                You can not move up in your next classifier because you need
                a score greater than <font color=\"red\">100%</font>. Enjoy
                {shooter.get_shooter_class()} class.
            """,
            'date': str(dt.datetime.now()),
        }
        # if request.is_ajax():
        if is_ajax(request):
            return HttpResponse(
                json.dumps(content), content_type="application/json"
            )
        else:
            return render(request, 'get_upped.html', content)

    else:
        try:
            next_class_up = shooter.get_next_class()
        except Exception:
            return render(request, 'get_upped.html', exception_content)

        content = {
            'response_text': f"""
                You need a score of <font color=\"red\">
                {str(shooter.get_upped())}%</font> to make
                <font color=\"red\">{next_class_up}</font> class.
            """,
            'date': str(dt.datetime.now()),
        }
        # if request.is_ajax():
        if is_ajax(request):
            return HttpResponse(
                json.dumps(content), content_type="application/json"
            )
        else:
            return render(request, 'get_upped.html', content)


def points_view(request):
    """Handles the interface between the HTML template containing the user
       supplied data and the backend API interface that produces an image
    Arguments:
        request {[object]} -- HTTPRequest object containing the form data
                              from the HTML template
    Returns:
        [object] -- HTTPResponse object containing either the matplotlib
                    BytesIO image or an Exception
    """
    form_data = dict()
    if request.method == 'POST':
        if AccuStatsForm2(request.POST).is_valid():
            form_data = {
                'username': request.POST.get('username'),
                'password': request.POST.get('password'),
                'mem_num': request.POST.get('mem_num').strip(),
                'division': request.POST.get('division'),

                'delete_match': (
                    request.POST.get('delete_match')
                    if isinstance(
                        request.POST.get('delete_match'), str
                    ) else ''
                ),

                'shooter_end_date': (
                    request.POST.get('shooter_end_date')
                    if isinstance(
                        request.POST.get('shooter_end_date'), str
                    ) else ''
                ),

                'shooter_start_date': (
                    request.POST.get('shooter_start_date')
                    if isinstance(
                        request.POST.get('shooter_start_date'), str
                    ) else ''
                ),
            }

    if request.method == 'GET':
        exception_content = {
            'message': 'You\'re doing it wrong.'
        }
        return render(request, 'error.html', exception_content)

    sys_logger(
        'points', form_data.get('mem_num'), form_data.get('division')
    )
    try:
        image = uspsastats(form_data)
    except Exception as e:
        exception_content = {
            'message': f'{e.args[0]}',
        }
        return render(request, 'error.html', exception_content)

    content = {
        'graph': image,
        'date': dt.datetime.now(),
        'accu_stats_form2': AccuStatsForm2(),
    }
    return render(request, 'points.html', content)


def pps_view(request):
    """Handles the interface between the HTML template containing the user
       supplied data and the backend API interface that produces an image
    Arguments:
        request {[object]} -- HTTPRequest object containing the form data
                              from the HTML template
    Returns:
        [object] -- HTTPResponse object containing either the matplotlib
                    BytesIO image or an Exception
    """
    form_data = dict()
    if request.method == 'POST':
        if PPSForm2(request.POST).is_valid():
            form_data = {
                'username': request.POST.get('username_pps'),
                'password': request.POST.get('password_pps'),
                'mem_num': request.POST.get('mem_num_pps').strip(),
                'division': request.POST.get('division_pps'),
                'delete_match': (
                    request.POST.get('delete_match_pps')
                    if isinstance(
                        request.POST.get('delete_match_pps'), str
                    ) else ''
                ),
                'end_date': (
                    request.POST.get('end_date_pps')
                    if isinstance(
                        request.POST.get('end_date_pps'), str
                    ) else ''
                ),
                'start_date': (
                    request.POST.get('start_date_pps')
                    if isinstance(
                        request.POST.get('start_date_pps'), str
                    )
                    else ''
                ),
            }

    if request.method == 'GET':
        exception_content = {
            'message': 'You\'re doing it wrong.'
        }
        return render(request, 'error.html', exception_content)

    sys_logger('pps', form_data['mem_num'], form_data['division'])
    try:
        image = pointspersec(form_data)
    except Exception as e:
        exception_content = {
            'message': e.args[0],
        }
        return render(request, 'error.html', exception_content)

    content = {
        'image': image,
        'date': dt.datetime.now(),
        'pps_form2': PPSForm2(),
    }
    return render(request, 'pps.html', content)


def error_view(request):
    return render(request, 'error.html')


@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /grid_iron_calc/",
        "Disallow: /mgnt/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


class UspsaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Uspsa.objects.all().order_by('-date_updated')
    serializer_class = UspsaSerializer
    permission_classes = [permissions.IsAuthenticated]
