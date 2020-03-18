import matplotlib.pyplot as plt
import random
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import re
from io import BytesIO
import base64



def fix_g_class(class_list, class_cnt):
    """this fixes practiscores use of both 'G' and 'GM' class"""

    gm_cnts = 0
    for i in class_list:
        if (i == 'g'):
            gm_cnts += class_cnt[class_list.index('g')]
        if (i == 'gm'):
            gm_cnts += class_cnt[class_list.index('gm')]

    return gm_cnts



def division_counts(bs, class_order_list, division):
    """Internal function not called from client code.  Params: beautifulsoup object, class_oder_list and division name text
    and return a dict with number of shooters per class"""

    if bs.find(text=division):
        division_class_list = []
        for i in bs.find(text=division).parent.next_siblings:
            if str(type(i)) != "<class 'bs4.element.NavigableString'>":
                division_class_list.append(int(i.get_text()))

        division_gm_cnt = fix_g_class(class_order_list, division_class_list) # call fix_g_class function
        division_dict = {'gm' : division_gm_cnt,
                         'm' : division_class_list[class_order_list.index('m')],
                         'a' : division_class_list[class_order_list.index('a')],
                         'b' : division_class_list[class_order_list.index('b')]
                        }
    else:
        division_dict = {'gm' : 0, 'm' : 0, 'a' : 0, 'b' : 0}

    return division_dict



def get_it(url):
    """scrape the practiscore url provided by the user"""

    match_link_html = urlopen(Request(url, headers={'User-Agent': 'Chrome/80.0.3987.132'}))
    bs = BeautifulSoup(match_link_html.read(), 'lxml')
    match_name = bs.find('h4').get_text()
    match_breakdown_link = bs.select_one("a[href*=matchdefbreakdown]").get('href')

    match_breakdown_html = urlopen(Request(match_breakdown_link, headers={'User-Agent': 'Chrome/80.0.3987.132'}))
    bs = BeautifulSoup(match_breakdown_html.read(), 'lxml')

    # get the order of the classes
    class_order_list = []
    if bs.find(text='Division'):
        for i in bs.find(text='Division').parent.next_siblings:
            if str(type(i)) != "<class 'bs4.element.NavigableString'>":
                class_order_list.append(i.get_text().lower())

    # Production Division
    prod_dict = division_counts(bs, class_order_list, 'Production')

    # Open division
    opn_dict = division_counts(bs, class_order_list, 'Open')

    # CO division
    co_dict = division_counts(bs, class_order_list, 'Carry Optics')

    # Limited division
    lim_dict = division_counts(bs, class_order_list, 'Limited')

    # PCC division
    pcc_dict = division_counts(bs, class_order_list, 'PCC')

    # Single Stack division
    ss_dict = division_counts(bs, class_order_list, 'Single Stack')

    return prod_dict, opn_dict, co_dict, lim_dict, pcc_dict, ss_dict, match_name



def run_it(prod_dict, opn_dict, co_dict, lim_dict, pcc_dict, ss_dict):

    multiplier = {'gm' : random.randrange(95, 100),
                  'm' : random.randrange(85, 94),
                  'a' : random.randrange(75, 84),
                  'b' : random.randrange(60, 74)
                 }

    prod_heat_count = 0
    opn_heat_count = 0
    co_heat_count = 0
    lim_heat_count = 0
    pcc_heat_count = 0
    ss_heat_count = 0

    prod_count = 0
    opn_count = 0
    co_count = 0
    lim_count = 0
    pcc_count = 0
    ss_count = 0

    for key in multiplier:
        for num in range(0, prod_dict[key]):
            prod_heat_count += multiplier[key]
        for num in range(0, opn_dict[key]):
            opn_heat_count += multiplier[key]
        for num in range(0, co_dict[key]):
            co_heat_count += multiplier[key]
        for num in range(0, lim_dict[key]):
            lim_heat_count += multiplier[key]
        for num in range(0, pcc_dict[key]):
            pcc_heat_count += multiplier[key]
        for num in range(0, ss_dict[key]):
            ss_heat_count += multiplier[key]

        prod_count += prod_dict[key]
        opn_count += opn_dict[key]
        co_count += co_dict[key]
        lim_count += lim_dict[key]
        pcc_count += pcc_dict[key]
        ss_count += ss_dict[key]

        prod_heat_idx = round(prod_heat_count / prod_count, 2) if prod_count > 0 else 0
        opn_heat_idx = round(opn_heat_count / opn_count, 2) if opn_count > 0 else 0
        co_heat_idx = round(co_heat_count / co_count, 2) if co_count > 0 else 0
        lim_heat_idx = round(lim_heat_count / lim_count, 2) if lim_count > 0 else 0
        pcc_heat_idx = round(pcc_heat_count / pcc_count, 2) if pcc_count > 0 else 0
        ss_heat_idx = round(ss_heat_count / ss_count, 2) if ss_count > 0 else 0

    heat_idx_list = [ prod_heat_idx, opn_heat_idx, co_heat_idx, lim_heat_idx, pcc_heat_idx, ss_heat_idx ]

    return heat_idx_list



def graph_it(heat_idx, match_name):
    """graph the data from practiscore, save image to memory and pass image back"""

    labels = [ 'Production', 'Open', 'CO', 'Limited', 'PCC', 'SS' ]

    x = range(len(labels))
    width = 0.3

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, heat_idx, width, label='Heat Factor')
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
