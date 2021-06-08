import json
import re
from collections import defaultdict

import pandas as pd
import requests


def grid_iron_calc():
    pass


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

        match_results = (
            json.loads(requests.get(
                f'https://s3.amazonaws.com/ps-scores/production/{match_uuid}/'
                'results.json').text)
        )

    except Exception:
        raise Exception('Error downloading AWS S3 json file.')

    return match_def, match_results


def get_dataframes(match_def, match_results):
    """"""
    df_match_def = pd.DataFrame(match_def['match_shooters'])

    df_match_results = pd.DataFrame(match_results[0]['Match'][2]['Production'])
    df_match_results = (
        df_match_results.append(pd.DataFrame(
            match_results[0]['Match'][3]['Single Stack']
        ), ignore_index=True)
    )

    df_grid_iron = (
        pd.merge(df_match_def, df_match_results, how='left', left_on='sh_uuid',
                 right_on='shooter')
    )

    cols = ['sh_uuid', 'sh_ln', 'sh_fn', 'sh_id', 'sh_dvp', 'matchPoints']
    df_grid_iron = df_grid_iron[cols]

    return df_grid_iron


def api_get():
    HEADERS = {'Content-type': 'application/json'}

    api_resp = requests.get(
        'https://www.alphamikenoshoot.com/gridiron.json',
        headers=HEADERS
    )
    return api_resp.json()
