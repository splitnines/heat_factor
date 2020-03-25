import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
import re
import datetime
import base64
from getpass import getpass
from io import BytesIO



"""The following functions where converted from the practiscore javascipt code that decodes the AWS
   json files with the scores"""

def num_alphas(score_field):
    A_MASK = 0x0000000F
    A_MASK2 = 0x0000000F00000000
    A_SHIFT = 0
    A_SHIFT2 = 28

    return ((score_field & A_MASK) >> A_SHIFT) + ((score_field & A_MASK2) >> A_SHIFT2)

def num_bravos(score_field):
    B_MASK = 0x000000F0
    B_MASK2 = 0x000000F000000000
    B_SHIFT = 4
    B_SHIFT2 = 32

    return ((score_field & B_MASK) >> B_SHIFT) + ((score_field & B_MASK2) >> B_SHIFT2)

def num_charlies(score_field):
    C_MASK = 0x00000F00
    C_MASK2 = 0x00000F0000000000
    C_SHIFT = 8
    C_SHIFT2 = 36

    return ((score_field & C_MASK) >> C_SHIFT) + ((score_field & C_MASK2) >> C_SHIFT2)

def num_deltas(score_field):
    D_MASK = 0x0000F000
    D_MASK2 = 0x0000F00000000000
    D_SHIFT = 12
    D_SHIFT2 = 40

    return ((score_field & D_MASK) >> D_SHIFT) + ((score_field & D_MASK2) >> D_SHIFT2)

def num_ns(score_field):
    NS_MASK = 0x000F0000
    NS_MASK2 = 0x000F000000000000
    NS_SHIFT = 16
    NS_SHIFT2 = 44

    return ((score_field & NS_MASK) >> NS_SHIFT) + ((score_field & NS_MASK2) >> NS_SHIFT2)

def num_m(score_field):
    M_MASK = 0x00F00000
    M_MASK2 = 0x00F0000000000000
    M_SHIFT = 20
    M_SHIFT2 = 48

    return ((score_field & M_MASK) >> M_SHIFT) + ((score_field & M_MASK2) >> M_SHIFT2)

def num_npm(score_field):
    NPM_MASK = 0x0F000000
    NPM_MASK2 = 0x0F00000000000000
    NPM_SHIFT = 24
    NPM_SHIFT2 = 42

    return ((score_field & NPM_MASK) >> NPM_SHIFT) + ((score_field & NPM_MASK2) >> NPM_SHIFT2)

"""End javascript converted functions"""



def create_dataframe(json_obj, match_start_end, delete_list, mem_num):
    """This is were the magic happens.  Performs the calculations on the data pulled from the Practiscore AWS API.
       Params are the json object with match uuids, dict with start and end data filters, a list with dates
       to exclude from the report and the shooters membership number.
       Returns a pandas dataframe to be processed by the plot function"""

    scores_df = pd.DataFrame(
        columns = [
            'Match Date', 'Total Alphas', 'Total Charlies', 'Total Deltas', 'Total No-shoots', 'Total Mikes', 'Total NPM',
            'Round Count', 'Points Poss.', 'Points Scored', 'Pct Points', 'A/C Ratio', 'Errors'
        ]
    )

    # count is used to limit the number of matches that can be plotted
    count = 0
    for match_link_info in json_obj:
        match_link_date = datetime.date.fromisoformat(match_link_info['date'])
        if match_link_info['date'] in delete_list:
            continue
        if match_link_date <= datetime.date.fromisoformat(match_start_end['start_date']) and match_link_date >= datetime.date.fromisoformat(match_start_end['end_date']):
            match_uuid = match_link_info['matchId']
            try:
                match_def = json.loads(requests.get('https://s3.amazonaws.com/ps-scores/production/' + match_uuid + '/match_def.json').text)
                match_scores = json.loads(requests.get('https://s3.amazonaws.com/ps-scores/production/' + match_uuid + '/match_scores.json').text)
                #match_results = json.loads(requests.get('https://s3.amazonaws.com/ps-scores/production/' + match_uuid + '/    results.json').text)
            except:
                print('error downloading aws json files')

            if match_def['match_type'] != 'uspsa_p':
                continue

            match_date = match_def['match_date']
            match_name = match_def['match_name']


            for match_info in match_def['match_shooters']:
                if 'sh_id' in match_info and re.match(mem_num, match_info['sh_id']):
                    shooter_uuid  = match_info['sh_uid']
                    shooter_fname = match_info['sh_fn']
                    shooter_lname = match_info['sh_ln']
                    shooter_pf    = match_info['sh_pf'].upper()
                    shooter_div   = match_info['sh_dvp']
                    shooter_class = match_info['sh_grd']

            total_alphas   = 0
            total_bravos   = 0
            total_charlies = 0
            total_deltas   = 0
            total_ns       = 0
            total_mikes    = 0
            total_npm      = 0

            for score in match_scores['match_scores']:
                for stage_score in score['stage_stagescores']:
                    if re.match(shooter_uuid, stage_score['shtr']):
                        total_alphas += stage_score['poph']
                        total_mikes  += stage_score['popm']

                        if 'ts' in stage_score:
                            for ts in stage_score['ts']:
                                total_alphas   += num_alphas(ts)
                                total_bravos   += num_bravos(ts)
                                total_charlies += num_charlies(ts)
                                total_deltas   += num_deltas(ts)
                                total_ns       += num_ns(ts)
                                total_mikes    += num_m(ts)
                                total_npm      += num_npm(ts)

            round_count = sum((total_alphas, total_bravos, total_charlies, total_deltas, total_ns, total_mikes, total_npm))
            points_possible = (round_count * 5)

            if shooter_pf == 'MINOR':
                points_scored = (((total_alphas * 5) + ((total_bravos + total_charlies) * 3 + (total_deltas * 1)))) - ((total_ns *     10) +         (total_mikes *10))
            else:
                points_scored = (((total_alphas * 5) + ((total_bravos + total_charlies) * 4 + (total_deltas * 2)))) - ((total_ns *     10) +         (total_mikes *10))

            if points_scored > 0:
                pct_points = round((points_scored / points_possible) * 100, 2)
            else:
                pct_points = 'NaN'

            if total_alphas > 0 and total_charlies > 0:
                alpha_charlie_ratio = round((total_charlies / total_alphas) * 100, 2)
            else:
                alpha_charlie_ratio = 'NaN'

            if sum([total_deltas, total_mikes, total_ns]) > 0:
                pct_errors = round((sum([total_deltas, total_mikes, total_ns]) / round_count) * 100, 2)
            else:
                pct_errors = 'NaN'


            score_list = [
                match_date, total_alphas, total_charlies + total_bravos, total_deltas, total_ns, total_mikes, total_npm, round_count, points_possible, points_scored, pct_points, alpha_charlie_ratio, pct_errors
            ]

            score_series = pd.Series(score_list, index=scores_df.columns)
            scores_df = scores_df.append(score_series, ignore_index=True)

            # count is used to limit the number of matches that can be plotted
            count += 1
            if count > 50:
                break

    scores_df['Avg Pct Scored'] = round((scores_df['Points Scored'].sum() / scores_df['Points Poss.'].sum()) * 100, 2)
    scores_df.sort_values(by=['Match Date'], inplace=True)
    return scores_df, shooter_fname, shooter_lname




def get_match_links(login_dict):
    """Performs Practiscore.com login and retrieval of match url uuids.  Param is a dict with login creds.
       Returns errors on bad credentials.  Returns a json object with the match url data on success"""

    headers = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149     Safari/537.36' }


    login_status_strs = {
        'bad_pass' : 'Forgot Password',
        'bad_email': 'have an account with the email',
        'success'  : 'https://practiscore\.com/associate/step2',
    }

    with requests.Session() as sess:
        login = sess.post('https://practiscore.com/login', data=login_dict, headers=headers)
        if re.findall(login_status_strs['bad_pass'], str(login.content)):
            sess.close
            return 'Bad password.'
        elif re.findall(login_status_strs['bad_email'], str(login.content)):
            sess.close
            return 'Bad email/username'
        elif re.findall(login_status_strs['success'], str(login.content)):
            shooter_ps_match_links = sess.get('https://practiscore.com/associate/step2', headers=headers)
            sess.get('https://practiscore.com/logout', headers=headers)
            sess.close

    match_link_raw_data = re.search(r'var matches = (\[.+\]);\\n\s+var selected =', str(shooter_ps_match_links.content))

    match_links_json = []
    for match_link_info in json.loads(match_link_raw_data.group(1)):
        if datetime.date.fromisoformat(match_link_info['date']) >= datetime.date.fromisoformat('2019-01-01'):
            match_links_json.append(match_link_info)

    return match_links_json




def add_annotation(x_ax, y_ax):
    """adds labels to plot"""
    for xx, yy in zip(x_ax, y_ax):
        label = "{:.2f}".format(yy)
        plt.annotate(label, (xx, yy), textcoords='offset points', xytext=(-5,0), ha='right', fontsize=8)
    return

def plot_stats(scores, shooter_name, mem_number):
    """Plots stats in graph.  Params are pandas dataframe, shooters full name and shooters membership number.
       Returns graph saved in memory"""

    x = np.arange(len(scores['Match Date']))

    plt.figure(figsize=[14.5, 8])


    plt.plot(x, scores['Pct Points'], label='Percent Points', linestyle='solid', marker='o', markersize=6, linewidth=3)
    plt.plot(x, scores['Avg Pct Scored'], label='Average Percent Points', color='black', linestyle='dashed',  linewidth=3)
    plt.plot(x, scores['A/C Ratio'], 'co-', label='A/C Ratio', color='c', linestyle='solid', marker='o', markersize=6, linewidth=3)
    plt.bar(x, scores['Errors'], label='Errors', color='rosybrown', width=0.45, linewidth=1.15, edgecolor='gray')

    plt.title('Percent of Match Points Scored')
    plt.ylabel('Percent')
    plt.xlabel('Date of Match')
    plt.ylim([0, 100])
    plt.yticks(np.arange(0, 110, 10))
    plt.xticks(x, scores['Match Date'], rotation=90)
    plt.subplots_adjust(left=0, right=1)

    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=2, borderaxespad=0.)
    plt.grid(linestyle='--', linewidth='0.25')
    plt.margins(x=0.01)

    add_annotation(x, scores['Pct Points'])
    add_annotation(x, scores['A/C Ratio'])

    for x_errors, y_errors in zip(x, scores['Errors']):
        label4 = "{:.2f}".format(y_errors)
        plt.annotate(label4, (x_errors, 1.0), textcoords='offset points', xytext=(0.1,0), ha='right', fontsize=8, rotation=90)


    plt.annotate('Shooter Name: %s' % shooter_name, (1, 1), (-125, 20), fontsize=7, xycoords='axes fraction', textcoords='offset points', va='top')
    plt.annotate('USPSA#: %s' % mem_number, (1, 1), (-125, 10), fontsize=7, xycoords='axes fraction', textcoords='offset points', va='top')
    plt.annotate('Total Round Count: ' + str(scores['Round Count'].sum()), (0,0), (0, -92), xycoords='axes fraction',     textcoords='offset points', va='top')
    plt.annotate('Average Percent Points: ' + str(scores['Avg Pct Scored'].iloc[-1]), (0,0), (0, -80), xycoords='axes     fraction', textcoords='offset points', va='top')

    plt.tight_layout()
    # comment out plt.show() for production testing/deployment
    #plt.show()

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
