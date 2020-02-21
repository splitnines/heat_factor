from django.shortcuts import render
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import random
from bs4 import BeautifulSoup
import requests
import re
import datetime
from io import BytesIO
import base64


def get_it(url):

    match_link_html = requests.get(url)
    bs = BeautifulSoup(match_link_html.text, 'lxml')
    match_name = bs.find('h4').get_text()
    match_breakdown_link = bs.select_one("a[href*=matchdefbreakdown]").get('href')

    match_breakdown_html = requests.get(match_breakdown_link)
    bs = BeautifulSoup(match_breakdown_html.text, 'lxml')

    # Production Division
    if bs.find(text='Production'):
        prod_class_list = []
        for i in bs.find(text='Production').parent.next_siblings:
            if str(type(i)) != "<class 'bs4.element.NavigableString'>":
                prod_class_list.append(int(i.get_text()))
        prod_dict = {'gm' : prod_class_list[6], 'm' : prod_class_list[5],
                     'a' : prod_class_list[4], 'b' : prod_class_list[3]}
    else:
        prod_dict = {'gm' : 0, 'm' : 0, 'a' : 0, 'b' : 0}

    # Open division
    if bs.find(text='Open'):
        opn_class_list = []
        for i in bs.find(text='Open').parent.next_siblings:
            if str(type(i)) != "<class 'bs4.element.NavigableString'>":
                opn_class_list.append(int(i.get_text()))
        opn_dict = {'gm' : opn_class_list[6], 'm' : opn_class_list[5],
                    'a' : opn_class_list[4], 'b' : opn_class_list[3]}
    else:
        opn_dict = {'gm' : 0, 'm' : 0, 'a' : 0, 'b' : 0}

    # CO division
    if bs.find(text='Carry Optics'):
        co_class_list = []
        for i in bs.find(text='Carry Optics').parent.next_siblings:
            if str(type(i)) != "<class 'bs4.element.NavigableString'>":
                co_class_list.append(int(i.get_text()))
        co_dict = {'gm' : co_class_list[6], 'm' : co_class_list[5],
                   'a' : co_class_list[4], 'b' : co_class_list[3]}
    else:
        co_dict = {'gm' : 0, 'm' : 0, 'a' : 0, 'b' : 0}

    # Limited division
    if bs.find(text='Limited'):
        lim_class_list = []
        for i in bs.find(text='Limited').parent.next_siblings:
            if str(type(i)) != "<class 'bs4.element.NavigableString'>":
                lim_class_list.append(int(i.get_text()))
        lim_dict = {'gm' : lim_class_list[6], 'm' : lim_class_list[5],
                    'a' : lim_class_list[4], 'b' : lim_class_list[3]}
    else:
        lim_dict = {'gm' : 0, 'm' : 0, 'a' : 0, 'b' : 0}

    # PCC division
    if bs.find(text='Limited'):
        pcc_class_list = []
        for i in bs.find(text='PCC').parent.next_siblings:
            if str(type(i)) != "<class 'bs4.element.NavigableString'>":
                pcc_class_list.append(int(i.get_text()))
        pcc_dict = {'gm' : pcc_class_list[6], 'm' : pcc_class_list[5],
                    'a' : pcc_class_list[4], 'b' : pcc_class_list[3]}
    else:
        pcc_dict = {'gm' : 0, 'm' : 0, 'a' : 0, 'b' : 0}

    # Single Stack division
    if bs.find(text='Single Stack'):
        ss_class_list = []
        for i in bs.find(text='Single Stack').parent.next_siblings:
            if str(type(i)) != "<class 'bs4.element.NavigableString'>":
                ss_class_list.append(int(i.get_text()))
        ss_dict = {'gm' : ss_class_list[6], 'm' : ss_class_list[5],
                   'a' : ss_class_list[4], 'b' : ss_class_list[3]}
    else:
        ss_dict = {'gm' : 0, 'm' : 0, 'a' : 0, 'b' : 0}

    return prod_dict, opn_dict, co_dict, lim_dict, pcc_dict, ss_dict, match_name


def run_it(prod, opn, co, lim, pcc, ss):

    # heat multiplier
    multiplier = {'gm' : random.randrange(95, 100), 'm' : random.randrange(85, 94),
                  'a' : random.randrange(75, 84), 'b' : random.randrange(60, 74)}
    # init heat counts
    prod_heat_count = 0
    opn_heat_count = 0
    co_heat_count = 0
    lim_heat_count = 0
    pcc_heat_count = 0
    ss_heat_count = 0
    # init total shooters
    prod_count = 0
    opn_count = 0
    co_count = 0
    lim_count = 0
    pcc_count = 0
    ss_count = 0
    # loop through the dicts
    for key in multiplier:
        # calc heat counts
        for num in range(0, prod[key]):
            prod_heat_count += multiplier[key]
        for num in range(0, opn[key]):
            opn_heat_count += multiplier[key]
        for num in range(0, co[key]):
            co_heat_count += multiplier[key]
        for num in range(0, lim[key]):
            lim_heat_count += multiplier[key]
        for num in range(0, pcc[key]):
            pcc_heat_count += multiplier[key]
        for num in range(0, ss[key]):
            ss_heat_count += multiplier[key]

        #calc total shooters in sample
        prod_count += prod[key]
        opn_count += opn[key]
        co_count += co[key]
        lim_count += lim[key]
        pcc_count += pcc[key]
        ss_count += ss[key]

    # factor heat index
    prod_heat_idx = round(prod_heat_count / prod_count, 2) if prod_count > 0 else 0
    opn_heat_idx = round(opn_heat_count / opn_count, 2) if opn_count > 0 else 0
    co_heat_idx = round(co_heat_count / co_count, 2) if co_count > 0 else 0
    lim_heat_idx = round(lim_heat_count / lim_count, 2) if lim_count > 0 else 0
    pcc_heat_idx = round(pcc_heat_count / pcc_count, 2) if pcc_count > 0 else 0
    ss_heat_idx = round(ss_heat_count / ss_count, 2) if ss_count > 0 else 0

    return prod_heat_idx, opn_heat_idx, co_heat_idx, lim_heat_idx, pcc_heat_idx, ss_heat_idx


def graph_it(prod_heat_idx, opn_heat_idx, co_heat_idx, lim_heat_idx, pcc_heat_idx, ss_heat_idx, match_name):
    labels = ['Production', 'Open', 'CO', 'Limited', 'PCC', 'SS']
    heat_idx = [prod_heat_idx, opn_heat_idx, co_heat_idx, lim_heat_idx, pcc_heat_idx, ss_heat_idx]

    x = np.arange(len(labels))  # the label locations
    width = 0.3  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, heat_idx, width, label='Heat Factor')
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Heat Factor')
    ax.set_title(match_name)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    #ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    fig.tight_layout()
    t_stamp =str(datetime.datetime.now()).replace(' ', '_').replace('.', '_').replace(':', '')

    # use IO BytesIO to store image in memory
    # I took this from the web and need to figure out how it works
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    return graphic

def home(request):
    return render(request, 'home.html')

def heat_factor(request):
    url = request.POST.get('p_url')
    if re.match(r'^https://practiscore.com/results/new/[0-9a-z-]+$', url):
        prod_dict, opn_dict, co_dict, lim_dict, pcc_dict, ss_dict, match_name = get_it(url)
        prod_heat_idx, opn_heat_idx, co_heat_idx, lim_heat_idx, pcc_heat_idx, ss_heat_idx = run_it(prod_dict, opn_dict, co_dict, lim_dict, pcc_dict, ss_dict)
        graphic = graph_it(prod_heat_idx, opn_heat_idx, co_heat_idx, lim_heat_idx, pcc_heat_idx, ss_heat_idx, match_name)
        return render(request, 'heat_factor.html', {'graphic':graphic})
    else:
        return render(request, 'home.html', {'error':'Not a valid Practiscore.com URL: ' + url})
