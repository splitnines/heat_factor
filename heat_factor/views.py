import re
import datetime

from django.shortcuts import render, redirect
from .forms import PractiscoreUrlForm, GetUppedForm
from .heatfactor import fix_g_class, division_counts, get_it, run_it, graph_it
from .classificationwhatif import ClassifactionWhatIf



def home(request):
    """display app home page/landing page"""

    if request.method == 'POST':
        practiscore_url_form = PractiscoreUrlForm(request.POST)
        get_upped_form = GetUppedForm(request.POST)
        if practiscore_url_form.is_valid() and get_upped_form.is_valid():
            return HttpResponseRedirect('/')
    else:
        practiscore_url_form = PractiscoreUrlForm()
        get_upped_form = GetUppedForm()

    return render(request, 'home.html', {'practiscore_url_form':practiscore_url_form, 'get_upped_form':get_upped_form})



def heat_factor(request):
    """get practiscore url from form, pass it to get_it fuction then run thru the rest of the program"""

    url = request.POST.get('p_url')
    if re.match(r'^https://[w]*.*practiscore.com/results/new/[0-9a-z-]+$', url):
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
        form = PractiscoreUrlForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/')
    else:
        form = PractiscoreUrlForm()

    return render(request, 'bad_url.html', {'form': form})



def get_upped(request):
    """Creates a ClassifactionWhatIf object and calls various methods on that object to produce responses."""

    mem_num = request.POST.get('mem_num')
    division = request.POST.get('division')

    try:
        shooter = ClassifactionWhatIf(mem_num, division)
    except:
        return render(request, 'get_upped.html', {'response_text':'2 Mikes, 2 No-shoots.  An error occured.'})

    if shooter.get_shooter_class() == 'GM':
        return render(request, 'get_upped.html', {'response_text':'You are a ' + shooter.get_shooter_class() + ' already.  Nowhere to go from here.'})

    if shooter.get_shooter_class() == 'U':
        return render(request, 'get_upped.html', {'response_text':'You need a ' + str(shooter.get_initial_classifaction()[0]) + '% in your next classifier to make ' + shooter.get_initial_classifaction()[1] + ' class.'})

    if shooter.get_upped() > 100:
        return render(request, 'get_upped.html', {'response_text':'You can not move up in your next classifier, you need a score greater that 100%'})
    else:
        return render(request, 'get_upped.html', {'response_text':'You need a score of ' + str(shooter.get_upped()) + '% to make ' + shooter.get_next_class() + ' class.'})
