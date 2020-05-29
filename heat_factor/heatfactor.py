import base64
import json
import random
import re
from collections import defaultdict
from io import BytesIO

import matplotlib.pyplot as plt
import requests


def get_match_def(match_link):
    """Fetches the match data from AWS in the form of a json file.

    Arguments:
        match_link {str} -- practiscore match url.

    Raises:
        ValueError: if there was a problem pulling the AWS files.

    Returns:
        [dict] -- json object with the match data from AWS.
    """
    uuid_re = re.compile(
        r'practiscore\.com/results/new/([0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-'
        r'[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})$'
    )

    non_uuid_re = re.compile(r'practiscore\.com/results/new/(\d+)$')

    if non_uuid_re.search(match_link):

        match_html_text = requests.get(match_link).text

        aws_uuid_re = re.compile(
            r'https://s3\.amazonaws\.com/ps-scores/production/([0-9a-fA-F]{8}'
            r'\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-'
            '[0-9a-fA-F]{12})/match_def.json'
        )

        if aws_uuid_re.search(match_html_text):
            match_uuid = re.search(aws_uuid_re, match_html_text)[1]

    elif uuid_re.search(match_link):
        match_uuid = re.search(uuid_re, match_link)[1]

    try:
        match_def = (
            json.loads(requests.get(
                f'https://s3.amazonaws.com/ps-scores/production/{match_uuid}/'
                'match_def.json').text)
        )

    except Exception:

        raise Exception('problem downloading aws json file.')

    return match_def


def get_heat_factor(match_def):
    """Calculates the heat index for each division and pulls the match name
       from the json object.  Assigns random heat factor to each shooter
       within a range based on the shooters classification.

    Arguments:
        match_def {dict} -- json object with the match data from AWS.

    Returns:
        [dict] -- dict containing the heat index for each division as an int.
    """
    division_heat = {
        'Production':   [0, 0, 0, 0],
        'Limited':      [0, 0, 0, 0],
        'Carry Optics': [0, 0, 0, 0],
        'Open':         [0, 0, 0, 0],
        'PCC':          [0, 0, 0, 0],
        'Single Stack': [0, 0, 0, 0],
    }

    division_count = defaultdict(int)

    for shooter in match_def['match_shooters']:

        if 'sh_grd' not in shooter or shooter['sh_dvp'] not in division_heat:
            continue

        if 'sh_dvp' in shooter and shooter['sh_grd'] == 'G':
            division_heat[shooter['sh_dvp']][0] += random.randrange(95, 100)
            division_count[shooter['sh_dvp']] += 1

        if 'sh_dvp' in shooter and shooter['sh_grd'] == 'M':
            division_heat[shooter['sh_dvp']][1] += random.randrange(85, 94)
            division_count[shooter['sh_dvp']] += 1

        if 'sh_dvp' in shooter and shooter['sh_grd'] == 'A':
            division_heat[shooter['sh_dvp']][2] += random.randrange(75, 84)
            division_count[shooter['sh_dvp']] += 1

        if 'sh_dvp' in shooter and shooter['sh_grd'] == 'B':
            division_heat[shooter['sh_dvp']][3] += random.randrange(60, 74)
            division_count[shooter['sh_dvp']] += 1

    heat_idx = defaultdict(int)

    for division in division_heat:

        if sum(division_heat[division]) > 0 and division_count[division] > 0:

            heat_idx[division] = round(
                sum(division_heat[division]) / division_count[division], 2
            )

    return heat_idx


def get_chart(match_def):
    """Configure the matplotlib image, encodes the image into a BytesIO bytes
       object.

    Arguments:
        match_def {[dict]} -- json object with the match data from AWS.

    Returns:
        [bytes object] -- the bytes encoded png matplotlib image
    """
    heat_idx = get_heat_factor(match_def)

    x = range(len(heat_idx.keys()))
    y = list(heat_idx.values())

    width = 0.3

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(9, 6))

    rects = ax.bar(x, y, width, label='Heat Factor', color='#add8e6')
    ax.set_ylabel('Heat Factor', fontsize=14)
    ax.set_title(match_def['match_name'], fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(heat_idx.keys(), fontsize=12)
    ax.grid(axis='y', alpha=0.6, linewidth=0.25)

    for rect in rects:

        height = rect.get_height()
        ax.annotate(
            f'{height}', xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 0), textcoords="offset points", ha='center', va='bottom'
        )

    fig.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')

    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    chart = base64.b64encode(image_png)
    chart = chart.decode('utf-8')

    return chart
