import re
import datetime

from django.shortcuts import render, redirect

from .forms import PractiscoreUrlForm, GetUppedForm, AccuStatsForm1, AccuStatsForm2
from .heatfactor import fix_g_class, division_counts, get_it, run_it, graph_it
from .classificationwhatif import ClassifactionWhatIf
from . USPSA_Stats import create_dataframe, get_match_links, plot_stats




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
        prod_dict, opn_dict, co_dict, lim_dict, pcc_dict, ss_dict, match_name = get_it(url)
        heat_idx_list = run_it(prod_dict, opn_dict, co_dict, lim_dict, pcc_dict, ss_dict)
        graphic = graph_it(heat_idx_list, match_name)

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
                                                  '<font color=\"red\">2 Mikes, 2 No-shoots:</font> No scores found for memeber {} in {} division.  If your USPSA classifier scores are set to priviate this tool won\'t.  If you don\'t have at least 3 qualifing classifier scores on record this tool won\'t work.'.format(mem_num, division)})

    if shooter.get_shooter_class() == 'GM':
        return render(request, 'get_upped.html', {'response_text':
                                                  'You\'re a <font color=\"blue\">{}</font>.  Nowhere to go from here.'.format(shooter.get_shooter_class())})

    if shooter.get_shooter_class() == 'U':
        return render(request, 'get_upped.html', {'response_text':
                                                  'You need a score of <font color=\"green\">{}%</font> in your next classifier to achieve an initial classification of <font color=\"green\">{}</font> class.'.format(str(shooter.get_initial_classifaction()[0]), shooter.get_initial_classifaction()[1])})

    if shooter.get_upped() > 100:
        return render(request, 'get_upped.html', {'response_text':
                                                  'You can not move up in your next classifier because you need a score greater than <font color=\"red\">100%</font>. Enjoy {} class'.format(shooter.get_shooter_class())})
    else:
        return render(request, 'get_upped.html', {'response_text':
                                                  'You need a score of <font color=\"green\">{}%</font> to make <font color=\"green\">{}</font> class.'.format(str(shooter.get_upped()), shooter.get_next_class())})



def points(request):

    username = request.POST.get('username')
    password = request.POST.get('password')
    mem_num  = request.POST.get('mem_num')

    login_data = {
        'username': username,
        'password': password
    }

    match_start_end = {
        'start_date': str(datetime.date.fromisoformat(str(datetime.date.today()))),
        'end_date': '2019-01-01', # I can probably get rid of this
    }

    user_start_date = ''
    user_end_date = ''
    if user_start_date != '' and user_start_date < str(datetime.date.fromisoformat(str(datetime.date.today()))):
        match_start_end['start_date'] = user_start_date
    if user_end_date != '' and user_end_date >= match_start_end['end_date'] and user_end_date < match_start_end['start_date']:
        match_start_end['end_date'] = user_end_date

    delete_list = []

    match_links_json = get_match_links(login_data)
    if type(get_match_links(login_data)) == str:
        # in production this will dump to an error page url
        print(get_match_links(login_data))
        exit()
    del password, login_data

    scores_df, shooter_fn, shooter_ln = create_dataframe(match_links_json, match_start_end, delete_list, mem_num)

    graph = plot_stats(scores_df, shooter_fn + ' ' + shooter_ln, mem_num)

    return render(request, 'points.html', {'graph': graph, 'date': datetime.datetime.now()})
