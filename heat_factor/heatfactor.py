import random
import re
import json
from io import BytesIO
import base64
import requests
import matplotlib.pyplot as plt


def get_it(match_link):
    """Returns a json object with the match info.

    Args:
    match_link -- user provided url as a sting object
    """

    uuid_regex = re.compile(
        r'practiscore\.com/results/new/([0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-'
        r'[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})$')
    non_uuid_regex = re.compile(r'practiscore\.com/results/new/(\d+)$')

    if re.search(non_uuid_regex, match_link):

        match_html_text = requests.get(match_link).text
        aws_uuid_regex = re.compile(
            r'https://s3\.amazonaws\.com/ps-scores/production/([0-9a-fA-F]{8}'
            r'\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-'
            '[0-9a-fA-F]{12})/match_def.json')
        if re.search(aws_uuid_regex, match_html_text):
            match_uuid = re.search(aws_uuid_regex, match_html_text)[1]

    elif re.search(uuid_regex, match_link):
        match_uuid = re.search(uuid_regex, match_link)[1]

    try:
        match_def = json.loads(requests.get(
            f'https://s3.amazonaws.com/ps-scores/production/{match_uuid}/'
            'match_def.json').text)
    except ValueError:
        return 'problem downloading aws json file.'

    return match_def


def run_it(match_def):
    """Returns a list of floats and match_name string.

    Args:
    match_def -- json object
    """

    match_name = match_def['match_name']
    division_heat = {
        'Production': [0, 0, 0, 0, ],
        'Limited': [0, 0, 0, 0, ],
        'Carry Optics': [0, 0, 0, 0, ],
        'Open': [0, 0, 0, 0, ],
        'PCC': [0, 0, 0, 0, ],
        'Single Stack': [0, 0, 0, 0, ],
    }
    division_count = {
        'Production': 0,
        'Limited': 0,
        'Carry Optics': 0,
        'Open': 0,
        'PCC': 0,
        'Single Stack': 0,
    }
    for shooter in match_def['match_shooters']:
        class_weights = {
            'G': random.randrange(95, 100),
            'M': random.randrange(85, 94),
            'A': random.randrange(75, 84),
            'B': random.randrange(60, 74),
        }
        for division in division_heat:
            if 'sh_dvp' in shooter and 'sh_grd' in shooter:
                if shooter['sh_dvp'] == division and shooter['sh_grd'] == 'G':
                    division_heat[division][0] += class_weights['G']
                    division_count[division] += 1
                if shooter['sh_dvp'] == division and shooter['sh_grd'] == 'M':
                    division_heat[division][1] += class_weights['M']
                    division_count[division] += 1
                if shooter['sh_dvp'] == division and shooter['sh_grd'] == 'A':
                    division_heat[division][2] += class_weights['A']
                    division_count[division] += 1
                if shooter['sh_dvp'] == division and shooter['sh_grd'] == 'B':
                    division_heat[division][3] += class_weights['B']
                    division_count[division] += 1

    heat_idx = (
        round(sum(division_heat['Production']) /
              division_count['Production'], 2)
        if division_count['Production'] > 0 else 0,
        round(sum(division_heat['Open']) /
              division_count['Open'], 2) if division_count['Open'] > 0 else 0,
        round(sum(division_heat['Carry Optics']) /
              division_count['Carry Optics'], 2)
        if division_count['Carry Optics'] > 0 else 0,
        round(sum(division_heat['Limited']) /
              division_count['Limited'], 2)
        if division_count['Limited'] > 0 else 0,
        round(sum(division_heat['PCC']) /
              division_count['PCC'], 2) if division_count['PCC'] > 0 else 0,
        round(sum(division_heat['Single Stack']) /
              division_count['Single Stack'], 2)
        if division_count['Single Stack'] > 0 else 0,
    )

    return heat_idx, match_name


def graph_it(heat_idx, match_name):
    """Returns as matplotlib graph saved as a BytesIO object

    Args:
    heat_idx -- a list of floats
    match_name -- sting
    """

    labels = ['Production', 'Open', 'CO', 'Limited', 'PCC', 'SS']

    x = range(len(labels))
    width = 0.3

    fig, ax = plt.subplots()
    rects = ax.bar(x, heat_idx, width, label='Heat Factor')
    ax.set_ylabel('Heat Factor')
    ax.set_title(match_name)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}', xy=(rect.get_x() + rect.get_width() / 2,
                                     height), xytext=(0, 0),
                    textcoords="offset points", ha='center',
                    va='bottom')

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
