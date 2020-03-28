import re
import datetime
import requests
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from .forms import PractiscoreUrlForm, GetUppedForm, AccuStatsForm1, AccuStatsForm2
from .heatfactor import get_it, run_it, graph_it
from .classificationwhatif import ClassifactionWhatIf
from .USPSA_Stats import create_dataframe, get_match_links, plot_stats




def home(request):
    """display app home page/landing page"""

    if request.method == 'POST':

        practiscore_url_form = PractiscoreUrlForm(request.POST)
        get_upped_form = GetUppedForm(request.POST)
        accu_stats_form1 = AccuStatsForm1(request.POST)

        if practiscore_url_form.is_valid():
            return HttpResponseRedirect('/')
        elif get_upped_form.is_valid():
            return HttpResponseRedirect('/')
        elif accu_stats_form1.is_valid():
            return HttpResponseRedirect('/')

    else:

        practiscore_url_form = PractiscoreUrlForm()
        get_upped_form = GetUppedForm()
        accu_stats_form1 = AccuStatsForm1()


    return render(request, 'home.html', {
        'practiscore_url_form': practiscore_url_form,
        'get_upped_form'      : get_upped_form,
        'accu_stats_form1'    : accu_stats_form1,
        }
    )



def heat_factor(request):
    """get practiscore url from form, pass it to get_it fuction then run thru the rest of the program"""

    url = request.POST.get('p_url')
    if re.match(r'^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$', url):

        match_uuid = get_it(url)
        try:
            match_def = json.loads(requests.get('https://s3.amazonaws.com/ps-scores/production/' + match_uuid + '/match_def.json').text)
        except:
            return render(request, 'error.html', {'message': 'problem downloading aws json file.'})

        heat_idx, match_name = run_it(match_def)
        """heat_idx is a tuple containing the Heat Factor for each division in the match if the following order:
           Production, Open, Carry Optics, Limited, PCC, Single Stack"""

        graphic = graph_it(heat_idx, match_name)

        return render(request, 'heat_factor.html', {'graphic':graphic, 'date':datetime.datetime.now()})
    else:

        # redirect on bad_url detection
        return redirect('/bad_url/')



def bad_url(request):
    """this page is displayed when a bad URL is entered.  I don't like it this way"""

    if request.method == 'POST':
        practiscore_url_form = PractiscoreUrlForm(request.POST)
        if practiscore_url_form.is_valid():
            return HttpResponseRedirect('/')
    else:
        practiscore_url_form = PractiscoreUrlForm()

    return render(request, 'bad_url.html', {'practiscore_url_form': practiscore_url_form})



def get_upped(request):
    """Creates a ClassifactionWhatIf object and calls various methods on that object to produce responses."""

    mem_num = request.POST.get('mem_num')
    division = request.POST.get('division')

    try:
        shooter = ClassifactionWhatIf(mem_num, division)
    except:
        return render(request, 'get_upped.html', {'response_text':
                                                  '<font color=\"red\">2 Mikes, 2 No-shoots:</font> No scores found for memeber {} in {} division.  If your USPSA classifier scores are set to priviate this tool won\'t.  If you don\'t have at least 3 qualifing classifier scores on record this tool won\'t work.'.format(mem_num, division), 'date': datetime.datetime.now()})

    if shooter.get_shooter_class() == 'GM':
        return render(request, 'get_upped.html', {'response_text':
                                                  'You\'re a <font color=\"blue\">{}</font>.  Nowhere to go from here.'.format(shooter.get_shooter_class()), 'date': datetime.datetime.now()})

    if shooter.get_shooter_class() == 'U':
        return render(request, 'get_upped.html', {'response_text':
                                                  'You need a score of <font color=\"green\">{}%</font> in your next classifier to achieve an initial classification of <font color=\"green\">{}</font> class.'.format(str(shooter.get_initial_classifaction()[0]), shooter.get_initial_classifaction()[1]), 'date': datetime.datetime.now()})

    if shooter.get_upped() > 100:
        return render(request, 'get_upped.html', {'response_text':
                                                  'You can not move up in your next classifier because you need a score greater than <font color=\"red\">100%</font>. Enjoy {} class'.format(shooter.get_shooter_class()), 'date': datetime.datetime.now()})
    else:
        return render(request, 'get_upped.html', {'response_text':
                                                  'You need a score of <font color=\"green\">{}%</font> to make <font color=\"green\">{}</font> class.'.format(str(shooter.get_upped()), shooter.get_next_class()), 'date': datetime.datetime.now()})



def points(request):

    username           = request.POST.get('username')
    password           = request.POST.get('password')
    mem_num            = request.POST.get('mem_num')
    delete_match       = request.POST.get('delete_match') if type(request.POST.get('delete_match')) == str else ''
    shooter_end_date   = request.POST.get('shooter_end_date') if type(request.POST.get('shooter_end_date')) == str else ''
    shooter_start_date = request.POST.get('shooter_start_date') if type(request.POST.get('shooter_start_date')) == str else ''


    login_data = {
        'username': username,
        'password': password
    }

    match_date_range = {
        # set the default date range
        'end_date': str(datetime.date.fromisoformat(str(datetime.date.today()))),
        'start_date': '2019-01-01',

    }


    if shooter_end_date != '' and shooter_end_date < str(datetime.date.fromisoformat(str(datetime.date.today()))):
        match_date_range['end_date'] = shooter_end_date

    if shooter_start_date != '' and shooter_start_date > match_date_range['start_date'] and shooter_start_date < match_date_range['end_date']:
        match_date_range['start_date'] = shooter_start_date


    delete_list = []
    for ex_match in delete_match.replace(' ', '').split(','):
        if re.match('^(\d\d\d\d-\d\d-\d\d)$', ex_match):
            delete_list.append(ex_match)


    match_links_json = get_match_links(login_data)
    if type(match_links_json) == str:
        return render(request, 'error.html', {'message': match_links_json})

    del password, login_data


    try:
        scores_df, shooter_fn, shooter_ln = create_dataframe(match_links_json, match_date_range, delete_list, mem_num)
    except:
        return render(request, 'error.html', {'message': create_dataframe(match_links_json, match_date_range, delete_list, mem_num)})


    graph = plot_stats(scores_df, shooter_fn + ' ' + shooter_ln, mem_num)

    return render(
        request, 'points.html', { 'graph': graph, 'date': datetime.datetime.now(), 'accu_stats_form2': AccuStatsForm2() })



def error(request):

    return render(request, 'error.html')
