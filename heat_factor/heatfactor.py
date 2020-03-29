import matplotlib.pyplot as plt
import random
import requests
import re
import json
from io import BytesIO
import base64



def get_it(match_link):
    """get_it is the function used to fetch the match data from practiscore/aws.  It takes the users supplied practiscore url
       and returns the uuid for the match."""

    uuid_regex = re.compile('practiscore\.com/results/new/([0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})$')
    non_uuid_regex = re.compile('practiscore\.com/results/new/(\d+)$')

    if re.search(non_uuid_regex, match_link):

        match_html_text = requests.get(match_link).text
        aws_uuid_regex = re.compile('https://s3\.amazonaws\.com/ps-scores/production/([0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/match_def.json')
        if re.search(aws_uuid_regex, match_html_text):
            match_uuid = re.search(aws_uuid_regex, match_html_text)[1]


    elif re.search(uuid_regex, match_link):
        match_uuid = re.search(uuid_regex, match_link)[1]

    try:
        match_def = json.loads(requests.get('https://s3.amazonaws.com/ps-scores/production/' + match_uuid + '/match_def.json').text)
    except:
        return 'problem downloading aws json file.'

    return match_def
    

def run_it(match_def):
    """run_it is the function used to calculate the Heat Factor for each division in a match.  It takes the match_def json file
       as its only param and returns a tuple with the heat factor numbers and the match name"""

    match_name = match_def['match_name']

    division_heat = {
        'Production'   : [0, 0, 0, 0,],
        'Limited'      : [0, 0, 0, 0,],
        'Carry Optics' : [0, 0, 0, 0,],
        'Open'         : [0, 0, 0, 0,],
        'PCC'          : [0, 0, 0, 0,],
        'Single Stack' : [0, 0, 0, 0,],
    }

    division_count = {
        'Production'   : 0,
        'Limited'      : 0,
        'Carry Optics' : 0,
        'Open'         : 0,
        'PCC'          : 0,
        'Single Stack' : 0,
    }


    for shooter in match_def['match_shooters']:

        class_weights = {
            'G' : random.randrange(95, 100),
            'M'  : random.randrange(85, 94),
            'A'  : random.randrange(75, 84),
            'B'  : random.randrange(60, 74),
        }

        for division in division_heat:

            if 'sh_dvp' in shooter and 'sh_grd' in shooter:

                if shooter['sh_dvp'] == division and shooter['sh_grd'] == 'G':
                    division_heat[division][0] += class_weights['G']
                    division_count[division]   += 1

                if shooter['sh_dvp'] == division and shooter['sh_grd'] == 'M':
                    division_heat[division][1] += class_weights['M']
                    division_count[division]   += 1

                if shooter['sh_dvp'] == division and shooter['sh_grd'] == 'A':
                    division_heat[division][2] += class_weights['A']
                    division_count[division]   += 1

                if shooter['sh_dvp'] == division and shooter['sh_grd'] == 'B':
                    division_heat[division][3] += class_weights['B']
                    division_count[division]   += 1

    heat_idx = (
        round(sum(division_heat['Production']) / division_count['Production'], 2) if division_count['Production'] > 0 else 0,
        round(sum(division_heat['Open']) / division_count['Open'], 2) if division_count['Open'] > 0 else 0,
        round(sum(division_heat['Carry Optics']) / division_count['Carry Optics'], 2) if division_count['Carry Optics'] > 0 else 0,
        round(sum(division_heat['Limited']) / division_count['Limited'], 2) if division_count['Limited'] > 0 else 0,
        round(sum(division_heat['PCC']) / division_count['PCC'], 2) if division_count['PCC'] > 0 else 0,
        round(sum(division_heat['Single Stack']) / division_count['Single Stack'], 2) if division_count['Single Stack'] > 0 else 0,
    )

    return heat_idx, match_name



def graph_it(heat_idx, match_name):
    """graph the data from practiscore, save image to memory and pass image back"""
    """Production, Open, Carry Optics, Limited, PCC, Single Stack"""

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
