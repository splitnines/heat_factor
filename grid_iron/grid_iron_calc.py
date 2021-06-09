import json
import re

import pandas as pd
import requests


def grid_iron_calc(grid_iron_url):
    match_def, match_results = get_match_def(grid_iron_url)
    df_grid_iron = get_dataframes(match_def, match_results)

    return get_team_totals(api_get(), df_grid_iron)


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
    """Creates one dataframe from the AWS JSON files.

    Args:
        match_def (JSON): match data definations
        match_results (JSON): match results

    Returns:
        dataframe: combined data from the two JSON files.
    """
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
    """Grabs gridiron database rows from REST framework API

    Returns:
        JSON/dict: gridiron database rows
    """
    HEADERS = {'Content-type': 'application/json'}

    api_resp = requests.get(
        'https://www.alphamikenoshoot.com/gridiron.json',
        headers=HEADERS
    )
    return api_resp.json()


def get_team_totals(team_db, df_grid_iron):
    """Calculates the team results for gridiron.

    Args:
        team_db (dict): database rows from the gridiron team DB
        df_grid_iron (dataframe): gridiron match df with definations and
                                  results

    Returns:
        dict: team results dataframe in the form of a dict
    """
    results_cols = [
        'Team_Name', 'Team_Member1', 'Team_Member2', 'Team_Member3',
        'Member_Score1', 'Member_Score2', 'Member_Score3',
    ]
    df_grid_team_results = pd.DataFrame(columns=results_cols)

    for team_dict in team_db:
        df_grid_team_results = df_grid_team_results.append({
            'Team_Name': team_dict['team_name'],
            'Team_Member1': (
                df_grid_iron[df_grid_iron['sh_uuid'] == team_dict['team_mem1']]
                ['sh_fn'].values[0] + ' ' +
                df_grid_iron[
                    df_grid_iron['sh_uuid'] == team_dict['team_mem1']]['sh_ln']
                .values[0]
            ),
            'Team_Member2': (
                df_grid_iron[df_grid_iron['sh_uuid'] == team_dict['team_mem2']]
                ['sh_fn'].values[0] + ' ' +
                df_grid_iron[
                    df_grid_iron['sh_uuid'] == team_dict['team_mem2']]['sh_ln']
                .values[0]
            ),
            'Team_Member3': (
                df_grid_iron[df_grid_iron['sh_uuid'] == team_dict['team_mem3']]
                ['sh_fn'].values[0] + ' ' +
                df_grid_iron[
                    df_grid_iron['sh_uuid'] == team_dict['team_mem3']]['sh_ln']
                .values[0]
            ),
            'Member_Score1': (
                float(df_grid_iron[
                    df_grid_iron['sh_uuid'] == team_dict['team_mem1']]
                        ['matchPoints'].values[0])
            ),
            'Member_Score2': (
                float(df_grid_iron[
                    df_grid_iron['sh_uuid'] == team_dict['team_mem2']]
                        ['matchPoints'].values[0])
            ),
            'Member_Score3': (
                float(df_grid_iron[
                    df_grid_iron['sh_uuid'] == team_dict['team_mem3']]
                        ['matchPoints'].values[0])
            ),
        }, ignore_index=True)

    df_grid_team_results['Team_Score'] = (
        df_grid_team_results.iloc[:, -3:].sum(axis=1)
    )
    df_grid_team_results.sort_values(
        by='Team_Score', ascending=False, inplace=True, ignore_index=True
    )

    return df_grid_team_results.to_dict(orient='records')
