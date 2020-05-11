import json
import re
import datetime as dt
import asyncio
from collections import deque, defaultdict
import base64
from io import BytesIO
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from aiohttp import ClientSession


"""The following functions where converted from the practiscore javascipt code
that decodes the AWS json files with the scores for paper targets.

Returns the human consumable scores for paper targets.

Args:
score_field -- this the coded scores for paper targets in the AWS json file"""


def num_alphas(score_field):
    A_MASK = 0x0000000F
    A_MASK2 = 0x0000000F00000000
    A_SHIFT = 0
    A_SHIFT2 = 28

    return (
        ((score_field & A_MASK) >> A_SHIFT) +
        ((score_field & A_MASK2) >> A_SHIFT2)
    )


def num_bravos(score_field):
    B_MASK = 0x000000F0
    B_MASK2 = 0x000000F000000000
    B_SHIFT = 4
    B_SHIFT2 = 32

    return (
        ((score_field & B_MASK) >> B_SHIFT) +
        ((score_field & B_MASK2) >> B_SHIFT2)
    )


def num_charlies(score_field):
    C_MASK = 0x00000F00
    C_MASK2 = 0x00000F0000000000
    C_SHIFT = 8
    C_SHIFT2 = 36

    return (
        ((score_field & C_MASK) >> C_SHIFT) +
        ((score_field & C_MASK2) >> C_SHIFT2)
    )


def num_deltas(score_field):
    D_MASK = 0x0000F000
    D_MASK2 = 0x0000F00000000000
    D_SHIFT = 12
    D_SHIFT2 = 40

    return (
        ((score_field & D_MASK) >> D_SHIFT) +
        ((score_field & D_MASK2) >> D_SHIFT2)
    )


def num_ns(score_field):
    NS_MASK = 0x000F0000
    NS_MASK2 = 0x000F000000000000
    NS_SHIFT = 16
    NS_SHIFT2 = 44

    return (
        ((score_field & NS_MASK) >> NS_SHIFT) +
        ((score_field & NS_MASK2) >> NS_SHIFT2)
    )


def num_m(score_field):
    M_MASK = 0x00F00000
    M_MASK2 = 0x00F0000000000000
    M_SHIFT = 20
    M_SHIFT2 = 48

    return (
        ((score_field & M_MASK) >> M_SHIFT) +
        ((score_field & M_MASK2) >> M_SHIFT2)
    )


def num_npm(score_field):
    NPM_MASK = 0x0F000000
    NPM_MASK2 = 0x0F00000000000000
    NPM_SHIFT = 24
    NPM_SHIFT2 = 42

    return (
        ((score_field & NPM_MASK) >> NPM_SHIFT) +
        ((score_field & NPM_MASK2) >> NPM_SHIFT2)
    )


async def http_get(url, session):
    """Returns the AWS response for each json file

    Args:  url -- the individual url from the shooters list of matches
           session -- the aiohttp session object """

    try:
        async with session.get(url) as response:
            assert response.status == 200
            return await response.text()
    except Exception:
        return f'Error downloading {url}'


async def http_sess(links):
    """Returns the AWS json files as a string object.

    Args:
    links -- the json object containing the shooters match uuids"""

    def_tasks = deque()
    scores_tasks = deque()

    async with ClientSession() as session:

        for link in links:
            url1 = (
                'https://s3.amazonaws.com/ps-scores/'
                f"production/{link['matchId']}/match_def.json"
            )
            def_tasks.append(asyncio.create_task(http_get(url1, session)))

            url2 = (
                'https://s3.amazonaws.com/ps-scores/'
                f"production/{link['matchId']}/match_scores.json"
            )
            scores_tasks.append(asyncio.create_task(http_get(url2, session)))

        return (
            (x for x in await asyncio.gather(*def_tasks)),
            (x for x in await asyncio.gather(*scores_tasks))
        )


def async_loop(json_links):
    """Return match data received from AWS in two json object

    Args: json_links - json object containing the shooters match
                       links."""

    # why do I have to use Selector???
    # loop = asyncio.get_event_loop()
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    match_def_data, match_scores_data = (
        loop.run_until_complete(http_sess(json_links))
    )
    loop.close()

    return match_def_data, match_scores_data


def calc_totals(match_scores, idx, shtr_uuid):
    """Returns a dict with totals for each target.

    Args: match_scores - json file with the shooters details from each match.
          idx - used to align the two AWS json files with the scores.
          shtr_uuid - the shooters uuid."""

    totals = defaultdict(lambda: 0)

    for score in match_scores[idx]['match_scores']:
        for stage_score in score['stage_stagescores']:

            if re.match(shtr_uuid, stage_score['shtr']):
                totals['alphas'] += stage_score['poph']
                totals['mikes'] += stage_score['popm']

                if 'ts' in stage_score:

                    for ts in stage_score['ts']:
                        totals['alphas'] += num_alphas(ts)
                        totals['bravos'] += num_bravos(ts)
                        totals['charlies'] += num_charlies(ts)
                        totals['deltas'] += num_deltas(ts)
                        totals['ns'] += num_ns(ts)
                        totals['mikes'] += num_m(ts)
                        totals['npm'] += num_npm(ts)
    return totals


def rnd_count(totals):
    """Returns total round count for all matches.

    Args: totals - dict containing points data."""

    return sum(
        (
            totals['alphas'], totals['bravos'], totals['charlies'],
            totals['deltas'], totals['ns'], totals['mikes'],
            totals['npm']
        )
    )


def pts_scored(pf, totals):
    """Returns the total points scored.

    Args: pf - str of shooters power factor (MAJOR or MINOR).
          totals - dict containing points data."""

    if pf == 'MINOR':
        points = sum(
            [
                (totals['alphas'] * 5), (totals['bravos'] * 3),
                (totals['charlies'] * 3), (totals['deltas'])
            ]
        )
        penalties = sum([(totals['ns'] * 10), (totals['mikes'] * 10)])

        return points - penalties

    points = sum(
        [
            (totals['alphas'] * 5), (totals['bravos'] * 4),
            (totals['charlies'] * 4), (totals['deltas'] * 2)
        ]
    )
    penalties = sum([(totals['ns'] * 10), (totals['mikes'] * 10)])

    return points - penalties


def create_dataframe(json_obj, match_date_range, delete_list, mem_num):
    """Returns the dataframe containing all the statistics and the shooters
       first and last name.

       Args:
       json_obj -- the json object containing the shooters match uuids
       match_date_range -- dict containing alternate start/end dates
       deleate_list -- list containing dates to be omitted from plot
       mem_num -- shooters USPSA membership number
       """

    match_def_data, match_scores_data = async_loop(json_obj)

    match_def_json = (json.loads(i) for i in match_def_data)
    match_scores_json = [json.loads(i) for i in match_scores_data]

    scores_df = pd.DataFrame(
        columns=[
            'Match Date', 'Total Alphas', 'Total Charlies', 'Total Deltas',
            'Total No-shoots', 'Total Mikes', 'Total NPM', 'Round Count',
            'Points Poss.', 'Points Scored', 'Pct Points', 'A/C Ratio',
            'Errors'
        ]
    )

    for idx, match_def in enumerate(match_def_json):
        match_date = (
            dt.date.fromisoformat(match_def['match_date'])
        )
        if str(match_date) in delete_list:
            continue
        form_end_date = (
            dt.date.fromisoformat(match_date_range['end_date'])
        )
        form_start_date = (
            dt.date.fromisoformat(match_date_range['start_date'])
        )

        if match_date <= form_end_date and match_date >= form_start_date:

            if match_def['match_subtype'] != 'uspsa':
                continue

            match_date = match_def['match_date']

            for match_info in match_def['match_shooters']:
                if (
                    'sh_id' in match_info and
                    match_info['sh_id'].upper() == mem_num.upper()
                ):
                    shooter_uuid = match_info['sh_uid']
                    shooter_fname = match_info['sh_fn']
                    shooter_lname = match_info['sh_ln']
                    shooter_pf = match_info['sh_pf'].upper()
                else:
                    continue

            totals = calc_totals(match_scores_json, idx, shooter_uuid)

            round_count = rnd_count(totals)

            points_possible = (round_count * 5)

            points_scored = pts_scored(shooter_pf, totals)

            if points_scored > 0:
                pct_points = round((points_scored / points_possible) * 100, 2)
            else:
                pct_points = 'NaN'

            if totals['alphas'] > 0 and totals['charlies'] > 0:
                alpha_charlie_ratio = (
                    round((totals['charlies'] / totals['alphas']) * 100, 2)
                )
            else:
                alpha_charlie_ratio = 'NaN'

            if sum([totals['deltas'], totals['mikes'], totals['ns']]) > 0:
                pct_errors = (
                    round((sum([totals['deltas'], totals['mikes'],
                                totals['ns']]) / round_count) * 100, 2)
                )
            else:
                pct_errors = 'NaN'

            score_list = [
                match_date, totals['alphas'],
                totals['charlies'] + totals['bravos'], totals['deltas'],
                totals['ns'], totals['mikes'], totals['npm'], round_count,
                points_possible, points_scored, pct_points,
                alpha_charlie_ratio, pct_errors
            ]

            score_series = pd.Series(score_list, index=scores_df.columns)
            scores_df = scores_df.append(score_series, ignore_index=True)

            # limit total matches to plot to 50
            if idx > 50:
                break

    scores_df['Avg Pct Scored'] = (
        round((scores_df['Points Scored'].sum() / scores_df['Points Poss.']
               .sum()) * 100, 2)
    )
    scores_df.sort_values(by=['Match Date'], inplace=True)

    return scores_df, shooter_fname, shooter_lname


def get_match_links(login_dict):
    """Returns the shooters list of matches from practiscore in the form of
    a json object.

    Args:
    login_dict - dict containing the shooters practiscore login credentials
    """

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/80.0.3987.149 Safari/537.36'
    }

    login_status_strs = {
        'bad_pass': 'Forgot Password',
        'bad_email': 'have an account with the email',
        'success': r'https://practiscore\.com/associate/step2',
    }

    with requests.Session() as sess:

        login = sess.post(
            'https://practiscore.com/login', data=login_dict, headers=headers
        )

        if re.findall(login_status_strs['bad_pass'], str(login.content)):
            sess.close
            return 'Bad password.'

        elif re.findall(login_status_strs['bad_email'], str(login.content)):
            sess.close
            return 'Bad email/username'

        elif re.findall(login_status_strs['success'], str(login.content)):
            shooter_ps_match_links = (
                sess.get(
                    'https://practiscore.com/associate/step2', headers=headers
                )
            )
            sess.get('https://practiscore.com/logout', headers=headers)
            sess.close

    match_link_re = re.compile(r'var matches = (\[.+\]);\\n\s+var selected =')

    match_link_raw_data = (
        match_link_re.search(str(shooter_ps_match_links.content))
    )

    match_links_json = deque()
    my_epoch = dt.date.fromisoformat('2019-01-01')
    raw_match_links = json.loads(match_link_raw_data.group(1))

    for match_link_info in raw_match_links:
        if dt.date.fromisoformat(match_link_info['date']) >= my_epoch:
            match_links_json.append(match_link_info)

    return match_links_json


def add_annotation(x_ax, y_ax):
    """Adds labels to plot"""

    for xx, yy in zip(x_ax, y_ax):
        label = "{:.2f}".format(yy)
        plt.annotate(
            label, (xx, yy), textcoords='offset points',
            xytext=(-5, 0), ha='right', fontsize=8
        )


def plot_stats(scores, shooter_name, mem_number):
    """Returns a matplotlib .png object saved in memory

    Args:
    scores -- pandas dataframe containing the shooters scores for all matches
    shooter_name -- the shooters first and last name as a string object
    mem_number -- the shooters USPSA membership number
    """
    x = np.arange(len(scores['Match Date']))

    plt.figure(figsize=(14.5, 8))
    plt.plot(
        x, scores['Pct Points'], label='Percent Points',
        linestyle='solid', marker='o', markersize=6, linewidth=3
    )
    plt.plot(
        x, scores['Avg Pct Scored'], label='Average Percent Points',
        color='black', linestyle='dashed',  linewidth=3
    )
    plt.plot(
        x, scores['A/C Ratio'], 'co-', label='A/C Ratio', color='c',
        linestyle='solid', marker='o', markersize=6, linewidth=3
    )
    plt.bar(
        x, scores['Errors'], label='Errors', color='rosybrown', width=0.50,
        linewidth=1.15, edgecolor='gray'
    )

    plt.title('Percent of Match Points Scored')
    plt.ylabel('Percent')
    plt.xlabel('Date of Match')
    plt.ylim([0, 100])
    plt.yticks(np.arange(0, 110, 10))
    plt.xticks(x, scores['Match Date'], rotation=90)
    plt.subplots_adjust(left=0, right=1)

    plt.legend(
        bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=2,
        borderaxespad=0.
    )
    plt.grid(linestyle='--', linewidth='0.25')
    plt.margins(x=0.01)

    add_annotation(x, scores['Pct Points'])
    add_annotation(x, scores['A/C Ratio'])

    for x_errors, y_errors in zip(x, scores['Errors']):
        label4 = "{:.2f}".format(y_errors)
        plt.annotate(
            label4, (x_errors, 1.0), textcoords='offset points',
            xytext=(0.1, 0), ha='center', fontsize=8, rotation=90
        )

    plt.annotate(
        f'Shooter Name: {shooter_name}', (1, 1), (-125, 20),
        fontsize=7, xycoords='axes fraction',
        textcoords='offset points', va='top'
    )
    plt.annotate(
        f'USPSA#: {mem_number}', (1, 1), (-125, 10), fontsize=7,
        xycoords='axes fraction', textcoords='offset points',
        va='top'
    )
    plt.annotate(
        f'Total Round Count: {str(scores["Round Count"].sum())}',
        (0, 0), (0, -92), xycoords='axes fraction',
        textcoords='offset points', va='top'
    )
    plt.annotate(
        f'Average Percent Points: {str(scores["Avg Pct Scored"].iloc[-1])}',
        (0, 0), (0, -80), xycoords='axes fraction', textcoords='offset points',
        va='top'
    )
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')

    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    return graphic
