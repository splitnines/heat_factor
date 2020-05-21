import re
import datetime as dt
import sys
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import (
    PractiscoreUrlForm, GetUppedForm, AccuStatsForm1, AccuStatsForm2
)
from .heatfactor import get_match_def, get_chart
from .classificationwhatif import ClassificationWhatIf
from .USPSA_Stats import (
    get_dataframe, get_match_links, get_graph, check_mem_num
)


def sys_logger(app_name, *app_data):
    """Poor excuse for a logging system"""

    print(f'SYS_LOGGER: {app_name}, {app_data}', file=sys.stderr)


def home(request):
    """Routes to site home/landing page.

    Arguments:
        request {object} -- HTTPRequest object

    Returns:
        [object] -- HTTPResponse object
    """
    if request.method == 'POST':

        practiscore_url_form = PractiscoreUrlForm(request.POST)
        get_upped_form = GetUppedForm(request.POST)
        accu_stats_form1 = AccuStatsForm1(request.POST)

        if (
            practiscore_url_form.is_valid() and
            get_upped_form.is_valid() and
                accu_stats_form1.is_valid()
        ):

            return render(
                request, 'home.html', {
                    'practiscore_url_form': practiscore_url_form,
                    'get_upped_form': get_upped_form,
                    'accu_stats_form1': accu_stats_form1,
                }
            )

        else:

            return HttpResponseRedirect('/')
    else:

        practiscore_url_form = PractiscoreUrlForm()
        get_upped_form = GetUppedForm()
        accu_stats_form1 = AccuStatsForm1()

    return render(
        request, 'home.html', {
            'practiscore_url_form': practiscore_url_form,
            'get_upped_form': get_upped_form,
            'accu_stats_form1': accu_stats_form1,
        }
    )


def heat_factor(request):
    """Renders the Heat Factor graph for a given USPSA match link.

    Arguments:
        request {object} -- HTTPRequest object

    Returns:
        [object] -- HTTPResponse object
    """
    url = request.POST.get('p_url')

    sys_logger('heat_factor', url)

    ps_regex = (
        re.compile(
            r'^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$'
        )
    )
    if re.search(ps_regex, url):
        # todo: rewite this as a try block, change alternate return statement
        # of get_match_def to raise ValueError
        match_def = get_match_def(url)

        if 'match_name' in match_def:
            chart = get_chart(match_def)

            return render(
                request, 'heat_factor.html', {
                    'chart': chart, 'date': dt.datetime.now()
                }
            )
        elif match_def == 'problem downloading aws json file.':

            return render(request, 'error.html', {'message': match_def})
    else:

        # Redirect on bad_url detection
        return redirect('/bad_url/')


def bad_url(request):
    """Routes to bad_url.html for heat_factor function.  When the user
       provides an incorrect practiscore URL this function is called.

    Arguments:
        request {object} -- HTTPRequest object

    Returns:
        [object] -- HTTPResponse object
    """
    if request.method == 'POST':
        practiscore_url_form = PractiscoreUrlForm(request.POST)

        if practiscore_url_form.is_valid():

            return render(
                request, 'bad_url.html', {
                    'practiscore_url_form': practiscore_url_form
                }
            )
        else:

            return HttpResponseRedirect('/')
    else:
        practiscore_url_form = PractiscoreUrlForm()

    return render(
        request, 'bad_url.html', {
            'practiscore_url_form': practiscore_url_form
        }
    )


def get_upped(request):
    """Creates a ClassificationWhatIf object and calls various methods on that
       object to produce the percentage a shooter needs to move up a class or
       for a new shooter to get an initial classification.

    Arguments:
        request {object} -- HTTPRequest object

    Returns:
        [object] -- HTTPResponse object
    """
    mem_num = request.POST.get('mem_num')
    division = request.POST.get('division')
    DAY = dt.datetime.now()

    sys_logger('get_upped', mem_num, division)

    try:
        shooter = ClassificationWhatIf(mem_num, division)

    except AttributeError:

        return render(
            request, 'get_upped.html',
            {
                'response_text': '<font color=\"red\">2 Mikes, 2 '
                'No-shoots:</font> Member number '
                f'<font color=\"red\">{mem_num}</font> in '
                f'<font color=\"red\">{division}</font> division.<br> If '
                'your USPSA classifier scores are set to priviate this '
                'tool won\'t work.<br> If you don\'t have at least 3 '
                'qualifing classifier scores on record this tool '
                'won\'t work.', 'date': DAY
            }
        )
    if shooter.get_shooter_class() == 'GM':

        return render(
            request, 'get_upped.html',
            {
                'response_text': 'You\'re a <font color=\"blue\">'
                f'{shooter.get_shooter_class()}</font>.  Nowhere to go from '
                'here.',
                'date': DAY
            }
        )
    if shooter.get_shooter_class() == 'U':

        try:
            initial_dict = shooter.get_initial()

        except ValueError:

            return render(
                request, 'get_upped.html',
                {
                    'response_text': '<font color=\"red\">2 Mikes, 2 '
                    'No-shoots:</font> Member number '
                    f'<font color=\"red\">{mem_num}</font> in '
                    f'<font color=\"red\">{division}</font> division.<br> If '
                    'your USPSA classifier scores are set to priviate this '
                    'tool won\'t work.<br> If you don\'t have at least 3 '
                    'qualifing classifier scores on record this tool '
                    'won\'t work.', 'date': DAY
                }
            )
        initial_calssification_html = '<br>'.join(
            [f'You need a score of <font color=\"green\">{initial_dict[k]}%'
             '</font> in your next classifier to achieve an initial '
             f'classification of <font color=\"green\">{k}</font> class.'
             for k in initial_dict]
        )

        return render(
            request, 'get_upped.html', {
                'response_text': initial_calssification_html, 'date': DAY
            }
        )
    if shooter.get_upped() > 100:

        return render(
            request, 'get_upped.html',
            {
                'response_text': 'You can not move up in your next '
                'classifier because you need a score greater than '
                '<font color=\"red\">100%</font>. Enjoy '
                f'{shooter.get_shooter_class()} class',
                'date': DAY
            }
        )
    else:

        try:
            next_class_up = shooter.get_next_class()

        except AttributeError:

            return render(
                request, 'get_upped.html',
                {
                    'response_text': '<font color=\"red\">2 Mikes, 2 '
                    'No-shoots:</font> Member number '
                    f'<font color=\"red\">{mem_num}</font> in '
                    f'<font color=\"red\">{division}</font> division.<br> If '
                    'your USPSA classifier scores are set to priviate this '
                    'tool won\'t work.<br> If you don\'t have at least 3 '
                    'qualifing classifier scores on record this tool '
                    'won\'t work.', 'date': DAY
                }
            )

        return render(
            request, 'get_upped.html',
            {
                'response_text': 'You need a score of '
                f'<font color=\"green\">{str(shooter.get_upped())}'
                '%</font> to make <font color=\"green\">'
                f'{next_class_up}</font> class.',
                'date': DAY
            }
        )


def points(request):
    """Produces a chart showing the shooters match points plotted over time.

    Arguments:
        request {object} -- HTTPRequest object

    Returns:
        [object] -- HTTPResponse object
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    mem_num = request.POST.get('mem_num')
    division = request.POST.get('division')

    DAY = dt.date.today()

    # perform check_mem_num here.  no point in moving forward if an
    # invalid USPSA membership number is provided.
    try:
        check_mem_num(mem_num)

    except ValueError:

        return render(
            request, 'error.html', {
                'message': f'{mem_num} is not a valid USPSA membership number'
            }
        )

    delete_match = (
        request.POST.get('delete_match')
        if type(request.POST.get('delete_match')) == str else ''
    )

    shooter_end_date = (request.POST.get('shooter_end_date')
                        if type(request.POST.get('shooter_end_date')) ==
                        str else '')

    shooter_start_date = (request.POST.get('shooter_start_date')
                          if type(request.POST.get('shooter_start_date')) ==
                          str else '')

    login_data = {
        'username': username,
        'password': password
    }

    # Set the default date range
    match_date_range = {
        'end_date': str(dt.date.fromisoformat(str(DAY))),
        'start_date': '2019-01-01',
    }

    if (
        shooter_end_date != '' and shooter_end_date <
            str(dt.date.fromisoformat(str(dt.date.today())))
    ):
        match_date_range['end_date'] = shooter_end_date

    if (
        shooter_start_date != '' and
        shooter_start_date > match_date_range['start_date'] and
            shooter_start_date < match_date_range['end_date']
    ):
        match_date_range['start_date'] = shooter_start_date

    delete_list = []
    for ex_match in delete_match.replace(' ', '').split(','):

        if re.match(r'^(\d\d\d\d-\d\d-\d\d)$', ex_match):
            delete_list.append(ex_match)

    match_links_json = get_match_links(login_data)

    del password, login_data

    if type(match_links_json) == str:

        return render(
            request, 'error.html', {'message': match_links_json}
        )

    try:
        scores_df, shooter_fn, shooter_ln = (
            get_dataframe(
                match_links_json, match_date_range,
                delete_list, mem_num, division
            )
        )

    except ValueError:

        return render(
            request, 'error.html', {'message': get_dataframe(
                match_links_json, match_date_range,
                delete_list, mem_num, division
            )}
        )

    sys_logger('points', shooter_fn, shooter_ln, mem_num, division)

    # check if dataframe is empty
    if scores_df.empty is True:

        return render(
            request, 'error.html', {
                'message': f'no matches found for {mem_num}'
            }
        )

    graph = get_graph(
        scores_df, f'{shooter_fn} {shooter_ln}', mem_num, division
    )

    if request.method == 'POST':
        accu_stats_form2 = AccuStatsForm2(request.POST)

        if accu_stats_form2.is_valid():

            return render(
                request, 'points.html', {
                    'graph': graph, 'date': DAY,
                    'accu_stats_form2': accu_stats_form2,
                }
            )
        else:

            return HttpResponseRedirect('/')

    else:
        accu_stats_form2 = AccuStatsForm2()

    return render(
        request, 'points.html', {
            'graph': graph, 'date': DAY,
            'accu_stats_form2': accu_stats_form2,
        }
    )


def error(request):

    return render(request, 'error.html')


def corvid_da(request):

    return render(request, 'COVID-19_data_analysis.html')
