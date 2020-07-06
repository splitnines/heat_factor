import datetime as dt
import re
import sys

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from .classificationwhatif import ClassificationWhatIf
from .forms import (AccuStatsForm1, AccuStatsForm2, GetUppedForm,
                    PractiscoreUrlForm, PPSForm1, PPSForm2)
from .heatfactor import heatfactor
from .uspsastats import uspsastats
from .pointspersecond import pointspersec


def sys_logger(app_name, *app_data):
    """Poor excuse for a logging system"""
    print(f'SYS_LOGGER: {app_name}, {app_data}', file=sys.stderr)


def home(request):
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


def heat_factor(request):
    """Renders the Heat Factor graph for a given USPSA match link.

    Arguments:
        request {object} -- HTTPRequest object

    Returns:
        [dict] -- renders the content to the url in the form of a dict
                  containing the matplotlib image and the data.
    """
    sys_logger('heat_factor', request.POST.get('p_url'))

    try:
        chart = heatfactor(request.POST.get('p_url'))

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


def bad_url(request):
    """Routes to bad_url.html for heat_factor function.  When the user
       provides an incorrect practiscore URL this function is called.  This
       acts as a backup to the javascript function doing form validation
       at the browser.

    Arguments:
        request {object} -- HTTPRequest object

    Returns:
        [object] -- HTTPResponse object
    """
    if request.method == 'POST':
        if PractiscoreUrlForm(request.POST).is_valid():
            forms = {
                'practiscore_url_form': PractiscoreUrlForm(request.POST),
            }

            return render(request, 'bad_url.html', forms)

        else:

            return HttpResponseRedirect('/')

    if request.method == 'GET':
        forms = {
            'practiscore_url_form': PractiscoreUrlForm(),
        }

        return render(request, 'bad_url.html', forms)


def get_upped(request):
    """Creates a ClassificationWhatIf object and calls various methods on that
       object to produce the percentage a shooter needs to move up a class or
       for a new shooter to get an initial classification.

    Arguments:
        request {object} -- HTTPRequest object

    Returns:
        [object] -- HTTPResponse object
    """
    mem_num = request.POST.get('mem_num_1')
    division = request.POST.get('division_1')

    sys_logger('get_upped', mem_num, division)

    exception_content = {
            'response_text': f"""
                <font color=\"red\">2 Mikes, 2 No-shoots:</font> Member number
                <font color=\"red\">{mem_num}</font> in
                <font color=\"red\">{division}</font> division.<br> If
                your USPSA classifier scores are set to priviate this
                tool won\'t work.<br> Also, if you don\'t have at least 3
                qualifing classifier scores on record this tool won\'t work.
                """,
            'date': dt.datetime.now()
        }

    try:
        shooter = ClassificationWhatIf(mem_num, division)

    except Exception:

        return render(request, 'get_upped.html', exception_content)

    if shooter.get_shooter_class() == 'GM':
        content = {
            'response_text': f"""
                You\'re a <font color=\"red\">{shooter.get_shooter_class()}
                </font>. Nowhere to go from here."""
        }

        return render(request, 'get_upped.html', content)

    if shooter.get_shooter_class() == 'U':
        try:
            initial_dict = shooter.get_initial()

        except Exception:

            return render(request, 'get_upped.html', exception_content)

        initial_calssification_html = '<br>'.join(
            [f"""You need a score of <font color=\"red\">{initial_dict[k]}%
             </font> in your next classifier to achieve an initial
             classification of <font color=\"red\">{k}</font> class."""
             for k in initial_dict]
        )
        content = {
            'response_text': initial_calssification_html,
            'date': dt.datetime.now(),
        }

        return render(request, 'get_upped.html', content)

    if shooter.get_upped() > 100:
        content = {
            'response_text': f"""
                You can not move up in your next classifier because you need
                a score greater than <font color=\"red\">100%</font>. Enjoy
                {shooter.get_shooter_class()} class.
            """,
            'date': dt.datetime.now(),
        }

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
            'date': dt.datetime.now(),
        }

        return render(request, 'get_upped.html', content)


def points(request):
    """Handles the interface between the HTML template containing the user
       supplied data and the backend API interface that produces an image

    Arguments:
        request {[object]} -- HTTPRequest object containing the form data
                              from the HTML template

    Returns:
        [object] -- HTTPResponse object containing either the matplotlib
                    BytesIO image or an Exception
    """
    if request.method == 'POST':
        if AccuStatsForm2(request.POST).is_valid():
            form_data = {
                'username': request.POST.get('username'),
                'password': request.POST.get('password'),
                'mem_num': request.POST.get('mem_num'),
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

            sys_logger(
                'points', form_data.get('mem_num'), form_data.get('division')
            )

            try:
                image = uspsastats(form_data)

            except Exception as e:
                exception_content = {
                    'message': e.args[0],
                }

                return render(request, 'error.html', exception_content)

            content = {
                'graph': image,
                'date': dt.datetime.now(),
                'accu_stats_form2': AccuStatsForm2(),
            }

            return render(request, 'points.html', content)

        else:

            return HttpResponseRedirect('/')

    if request.method == 'GET':
        exception_content = {
                    'message': 'You\'re doing it wrong.'
                }

        return render(request, 'error.html', exception_content)


def pps(request):
    """Handles the interface between the HTML template containing the user
       supplied data and the backend API interface that produces an image

    Arguments:
        request {[object]} -- HTTPRequest object containing the form data
                              from the HTML template

    Returns:
        [object] -- HTTPResponse object containing either the matplotlib
                    BytesIO image or an Exception
    """
    if request.method == 'POST':
        if PPSForm2(request.POST).is_valid():

            form_data = {
                'username': request.POST.get('username_pps'),
                'password': request.POST.get('password_pps'),
                'mem_num': request.POST.get('mem_num_pps'),
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
                    )else ''
                ),
            }

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

        else:

            return HttpResponseRedirect('/')

    if request.method == 'GET':
        exception_content = {
                    'message': 'You\'re doing it wrong.'
                }

        return render(request, 'error.html', exception_content)


def error(request):
    return render(request, 'error.html')


def covid_da(request):
    return render(request, 'COVID-19_data_analysis.html')
