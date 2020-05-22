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
    uuid_regex = re.compile(
        r'practiscore\.com/results/new/([0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-'
        r'[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})$'
    )
    non_uuid_regex = re.compile(r'practiscore\.com/results/new/(\d+)$')

    if non_uuid_regex.search(match_link):

        match_html_text = requests.get(match_link).text

        aws_uuid_regex = re.compile(
            r'https://s3\.amazonaws\.com/ps-scores/production/([0-9a-fA-F]{8}'
            r'\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-'
            '[0-9a-fA-F]{12})/match_def.json'
        )

        if aws_uuid_regex.search(match_html_text):
            match_uuid = re.search(aws_uuid_regex, match_html_text)[1]

    elif uuid_regex.search(match_link):
        match_uuid = re.search(uuid_regex, match_link)[1]

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
       from the json object.

    Arguments:
        match_def {dict} -- json object with the match data from AWS.

    Returns:
        [dict] -- dict containing the heat index for each division as an int.
    """
    division_heat = {
        'Production': [0, 0, 0, 0, ],
        'Limited': [0, 0, 0, 0, ],
        'Carry Optics': [0, 0, 0, 0, ],
        'Open': [0, 0, 0, 0, ],
        'PCC': [0, 0, 0, 0, ],
        'Single Stack': [0, 0, 0, 0, ],
    }

    division_count = defaultdict(lambda: 0)

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

    heat_idx = {
        'Production': 0, 'Limited': 0, 'Carry Optics': 0,
        'Open': 0, 'PCC': 0, 'Single Stack': 0,
    }

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
        heat_idx {tuple} -- contains the heat factor number for each division.
        match_name {str} -- the match name

    Returns:
        [bytes object] -- the bytes encoded png matplotlib image
    """
    heat_idx = get_heat_factor(match_def)

    match_name = match_def['match_name']

    labels = list(heat_idx.keys())

    x = range(len(labels))
    y = list(heat_idx.values())

    width = 0.3

    fig, ax = plt.subplots(figsize=(9, 6))

    rects = ax.bar(x, y, width, label='Heat Factor')
    ax.set_ylabel('Heat Factor')
    ax.set_title(match_name)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

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
