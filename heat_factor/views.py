import matplotlib.pyplot as plt
import random
from bs4 import BeautifulSoup
import re
from io import BytesIO
import base64
import datetime

from django.shortcuts import render, redirect
from .forms import PractiscoreUrlForm
from .heatfactor import fix_g_class, division_counts, get_it, run_it, graph_it




def home(request):
    """display app home page/landing page"""
    if request.method == 'POST':
        form = PractiscoreUrlForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/')
    else:
        form = PractiscoreUrlForm()

    return render(request, 'home.html', {'form': form})

def heat_factor(request):
    """get practiscore url from form, pass it to get_it fuction then run thru the rest of the program"""
    url = request.POST.get('p_url')
    if re.match(r'^https://practiscore.com/results/new/[0-9a-z-]+$', url):
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
