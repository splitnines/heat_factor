import re
import datetime as dt
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import (
    PractiscoreUrlForm, GetUppedForm, AccuStatsForm1, AccuStatsForm2
)
from .heatfactor import get_it, run_it, graph_it
from .classificationwhatif import ClassifactionWhatIf
from .USPSA_Stats import (
    create_dataframe, get_match_links, plot_stats, check_mem_num
)
import sys


def home(request):
    """Display app home page/landing page"""

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
    """get practiscore url from form, pass it to get_it fuction then run thru
       the rest of the program"""

    url = request.POST.get('p_url')
    ps_regex = (
        re.compile(
            r'^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$'
        )
    )
    if re.search(ps_regex, url):

        match_def = get_it(url)

        if 'match_name' in match_def:
            heat_idx, match_name = run_it(match_def)
            """heat_idx is a tuple containing the Heat Factor for each
               division in the match in the following order: Production, Open,
               Carry Optics, Limited, PCC, Single Stack"""

            graphic = graph_it(heat_idx, match_name)

            return render(
                request, 'heat_factor.html', {
                    'graphic': graphic, 'date': dt.datetime.now()
                }
            )

        elif match_def == 'problem downloading aws json file.':
            return render(request, 'error.html', {'message': match_def})

    else:
        # Redirect on bad_url detection
        return redirect('/bad_url/')


def bad_url(request):
    """this page is displayed when a bad URL is entered.  I don't like it this
       way"""

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
    """Creates a ClassifactionWhatIf object and calls various methods on that
       object to produce responses."""

    mem_num = request.POST.get('mem_num')
    division = request.POST.get('division')
    DAY = dt.datetime.now()

    try:
        shooter = ClassifactionWhatIf(mem_num, division)
    except AttributeError:
        return render(
            request, 'get_upped.html',
            {
                'response_text': '<font color=\"red\">2 Mikes, 2 '
                'No-shoots:</font> No scores found for member '
                f'<font color=\"red\">{mem_num}</font> in '
                f'<font color=\"red\">{division}</font> division. If '
                'your USPSA classifier scores are set to priviate this '
                'tool won\'t work. If you don\'t have at least 3 '
                'qualifing classifier scores on record this tool '
                'won\'t work.', 'date': DAY
            }
        )
    if shooter.get_shooter_class() == 'GM':
        shtr_class = shooter.get_shooter_class()
        return render(
            request, 'get_upped.html',
            {
                'response_text': 'You\'re a <font color=\"blue\">'
                f'{shtr_class}</font>.  Nowhere to go from here.',
                'date': DAY
            }
        )
    if shooter.get_shooter_class() == 'U':
        shtr_init_class = shooter.get_initial_classifaction()
        return render(
            request, 'get_upped.html',
            {
                'response_text': 'You need a score of '
                f'<font color=\"green\">{str(shtr_init_class[0])}'
                '%</font> in your next classifier to achieve an '
                'initial classification of <font color=\"green\">'
                f'{str(shtr_init_class[1])}</font> class.',
                'date': DAY
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
        return render(
            request, 'get_upped.html',
            {
                'response_text': 'You need a score of '
                f'<font color=\"green\">{str(shooter.get_upped())}'
                '%</font> to make <font color=\"green\">'
                f'{shooter.get_next_class()}</font> class.',
                'date': DAY
            }
        )


def points(request):
    """Returns a matplotlib .png to the points.html template"""

    username = request.POST.get('username')
    password = request.POST.get('password')
    mem_num = request.POST.get('mem_num')
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
            request, 'error.html', {
                'message': match_links_json
            }
        )

    try:
        scores_df, shooter_fn, shooter_ln = (
            create_dataframe(
                match_links_json, match_date_range, delete_list, mem_num
            )
        )
    except ValueError:
        return render(
            request, 'error.html', {
                'message': create_dataframe(
                    match_links_json, match_date_range, delete_list, mem_num
                )
            }
        )

    # check if dataframe is empty
    if scores_df.empty is True:
        return render(
            request, 'error.html', {
                'message': f'no matches found for {mem_num}'
            }
        )

    graph = plot_stats(scores_df, f'{shooter_fn} {shooter_ln}', mem_num)

    def TS():
        return dt.datetime.now()

    if request.method == 'POST':
        accu_stats_form2 = AccuStatsForm2(request.POST)
        if accu_stats_form2.is_valid():
            print(f'{TS()} CALL_LOG: 1st render in views.points',
                  file=sys.stderr)
            return render(
                request, 'points.html', {
                    'graph': graph, 'date': DAY,
                    'accu_stats_form2': accu_stats_form2,
                }
            )
        else:
            print(f'{TS()} CALL_LOG: HttpResponseRedirect in views.points',
                  file=sys.stderr)
            return HttpResponseRedirect('/')
    else:
        accu_stats_form2 = AccuStatsForm2()
        print(f'{TS()} CALL_LOG: 2nd render in views.points', file=sys.stderr)
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
