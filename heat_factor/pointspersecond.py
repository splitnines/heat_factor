import asyncio
import base64
import datetime as dt
import json
import re
import sys
from collections import defaultdict, deque, OrderedDict
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import requests
from aiohttp import ClientSession
from requests.adapters import Response


def pointspersec(form_dict):
    """Takes the HTML form data passed from views.py and calls the functions
       to produce an image file to be rendered back to the HTML template via
       views.py.
       This is the main function/interface for the module.
    Arguments:
        form_dict {dict} -- contains the form data passed from the HTML form
                            to views.py
    Raises:
        Exception: USPSA membership number not found.
        Exception: Passes Exception message from get_match_links(),
                   3 possible Exceptions.
        Exception: Dataframe creation failed.
        Exception: Image creation failed.
    Returns:
        BytesIO -- a matplotlib image file in a BytesIO data stream
    """
    try:
        check_mem_num(form_dict['mem_num'])
    except Exception:
        raise Exception('USPSA membership number not found.')
    try:
        match_links = get_match_links(form_dict)
    except Exception as e:
        raise Exception(e)
    try:
        match_defs, match_results = event_loop(http_sess, match_links)
    except Exception:
        raise Exception('A problem occured downloading match data.')
    try:
        pps_dict, fn, ln = (
            get_pps(
                match_defs, match_results, form_dict['mem_num'],
                form_dict['division']
            )
        )
    except Exception as e:
        raise Exception(e.args[0])
    try:
        return pps_plot(pps_dict, fn, ln, form_dict)
    except Exception:
        raise Exception('Image creation failed.')


def check_mem_num(mem_num):
    """Checks that mem_num is a valid uspsa number.
    Arguments:
        mem_num {str} -- the users USPSA membership number (alphanumeric).
    Raises:
        Exception: if membership number is not found.
    """
    uspsa_org_response = requests.get(
        f'https://uspsa.org/classification/{mem_num}'
    ).text

    oops_re = re.compile('Oops!')
    if oops_re.search(uspsa_org_response):
        raise Exception


def get_match_links(form_dict):
    """Logs into Practicescore.com and scrapes the links to each match the
       shooter participated in.  These links are scraped from javascript
       code in the HTML of the users Practiscore home page.
    Arguments:
        form_dict {dict} -- dict containing username and password used to log
                            in to Practiscore.com
    Returns:
        [deque] -- list of json object containing the match link uuids for
                   pulling match json files from AWS.
    """
    shooter_ps_match_links = Response
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/83.0.4103.61 Safari/537.36'
    }
    login_status_strs = {
        'bad_pass': 'Forgot Password',
        'bad_email': 'have an account with the email',
        'success': r'<a href=\"([\w:/\.\d]+)\"\sid=\"viewAllButton\"'
    }
    login_dict = {
        'username': form_dict['username'],
        'password': form_dict['password'],
    }
    with requests.Session() as sess:
        login = sess.post(
            'https://practiscore.com/login', data=login_dict, headers=headers
        )
        if re.findall(login_status_strs['bad_pass'], str(login.content)):
            sess.close
            raise Exception('Bad password.')
        if re.findall(login_status_strs['bad_email'], str(login.content)):
            sess.close
            raise Exception('Bad email/username')
        if not re.findall(login_status_strs['success'], str(login.content)):
            sess.close
            raise Exception('"ViewAll" link not found.')
        if re.search(login_status_strs['success'], str(login.content)):
            view_all_link = (
                re.search(login_status_strs['success'], str(login.content))
            )
            shooter_ps_match_links = (
                sess.get(view_all_link.group(1), headers=headers)
            )
            sess.get('https://practiscore.com/logout', headers=headers)
            sess.close

    match_link_re = re.compile(r'var matches = (\[.+\]);\\n\s+var selected =')
    match_link_raw_data = (
        match_link_re.search(str(shooter_ps_match_links.content))
    )
    match_links_json = deque()
    # epoch = dt.date.fromisoformat('2017-01-01')
    raw_match_links = json.loads(
        match_link_raw_data.group(1).replace('\\\\"', '').replace('\\\'', '')
    )
    today = dt.date.today()
    match_date_range = {
        'end_date': str(dt.date.fromisoformat(str(today))),
        'start_date': '2017-01-01',
    }
    if (
        form_dict['end_date'] != '' and
        form_dict['end_date'] < str(dt.date.fromisoformat(str(today)))
    ):
        match_date_range['end_date'] = form_dict['end_date']
    if (
        form_dict['start_date'] != '' and
        form_dict['start_date'] > match_date_range['start_date'] and
        form_dict['start_date'] < match_date_range['end_date']
    ):
        match_date_range['start_date'] = form_dict['start_date']

    delete_list = []
    for delete in form_dict['delete_match'].replace(' ', '').split(','):
        if re.match(r'^(\d\d\d\d-\d\d-\d\d)$', delete):
            delete_list.append(delete)

    for match_link_info in raw_match_links:
        if (
            dt.date.fromisoformat(match_link_info['date']) >=
            dt.date.fromisoformat(match_date_range['start_date']) and
            dt.date.fromisoformat(match_link_info['date']) <=
            dt.date.fromisoformat(match_date_range['end_date']) and
            str(dt.date.fromisoformat(match_link_info['date'])) not in
            delete_list and
            # added 09/30/2020 because steel challenge matches broke shit
            'Steel Challenge' not in match_link_info['name']
        ):
            match_links_json.append(match_link_info)

    return match_links_json


async def http_get(url, session):
    """Perform the HTTP get request to the AWS server.
    Arguments:
        url {str} -- the individual url from the shooters list of matches
        session {object} -- the aiohttp session object
    Returns:
        [json object] -- the AWS response for each json file
    """
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://practiscore.com/',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'X-CSRF-TOKEN': '2ml0QNDDNyYOr9MtxKRdXGV9WGeGh68xtnf3hcBH'
    }
    try:
        async with session.get(url, headers=headers) as response:
            assert response.status == 200
            return await response.text()
    except Exception:
        raise Exception(f'Error downloading {url}')


async def http_sess(links):
    """Creates the async coroutines to fetch the match details from AWS
    Arguments:
        links {json object} -- contains the PS AWS uuid for each match
    Returns:
        {str} -- the AWS json files as a string objects.
    """
    def_tasks = deque()
    results_tasks = deque()

    async with ClientSession() as session:
        for link in links:
            url1 = (
                'https://s3.amazonaws.com/ps-scores/'
                f"production/{link['matchId']}/match_def.json"
            )
            def_tasks.append(asyncio.create_task(http_get(url1, session)))
            url2 = (
                'https://s3.amazonaws.com/ps-scores/'
                f"production/{link['matchId']}/results.json"
            )
            results_tasks.append(asyncio.create_task(http_get(url2, session)))
        return (
            (x for x in await asyncio.gather(*def_tasks)),
            (x for x in await asyncio.gather(*results_tasks))
        )


def event_loop(func, *args):
    """Calls the specified function with list of args.
    Arguments:
        func {function} -- name of async function to call and "place on the
                           loop.
    Returns:
        [object] -- returns whatever is received from the called function.
    """
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)
    response = (loop.run_until_complete(func(*args)))
    loop.close()
    return response


def results_gopher(match, shooter_id):
    pps_dict = {
        'time': 0.,
        'points': 0,
    }
    for a in match:
        if 'Match' not in a:
            for b in a.values():
                for c in b:
                    if 'Overall' in c:
                        for d in c['Overall']:
                            if d['shooter'] == shooter_id:
                                pps_dict['time'] += float(d['stageTimeSecs'])
                                pps_dict['points'] += int(d['points'])

    if pps_dict['time'] > 0 and pps_dict['points'] > 0:
        pps = pps_dict['points'] / pps_dict['time']
        return float(f'{pps:.2f}')

    elif pps_dict['time'] <= 0 and pps_dict['points'] <= 0:
        pps = 0
        return float(f'{pps:.2f}')

    else:
        raise Exception('A problem occured with function results_gopher().')


def get_pps(match_defs, match_results, mem_num, division):
    pps_dict = defaultdict(float)
    shooter_fn = str()
    shooter_ln = str()

    for match_def, match_result in zip(match_defs, match_results):
        match_def = json.loads(match_def)
        match_result = json.loads(match_result)
        uspsa_re = re.compile(r'uspsa')
        match_type = match_def.get('match_type')
        if match_type is not None and not uspsa_re.search(match_type.lower()):
            continue
        # match_date = dt.date.fromisoformat(match_def['match_date'])
        match_date = match_def['match_date']

        for shooter in match_def['match_shooters']:
            if division.lower() != shooter['sh_dvp'].lower():
                continue
            if (
                'sh_id' in shooter and
                mem_num.upper() == shooter['sh_id'].upper()
            ):
                try:
                    pps_dict[match_date] = (
                        results_gopher(match_result, shooter['sh_uid'])
                    )
                except Exception:
                    raise Exception('Received exception from results_gopher.')
                if pps_dict[match_date] == 0:
                    del pps_dict[match_date]
                shooter_fn = shooter['sh_fn']
                shooter_ln = shooter['sh_ln']
            else:
                continue

    if len(pps_dict) > 0:
        return (
            OrderedDict(sorted(pps_dict.items(), reverse=False)),
            shooter_fn, shooter_ln
        )
    else:
        raise Exception(f'No data found for shooter {mem_num}')


def pps_plot(pps_dict, fn, ln, form_dict):

    pps = np.array(list(pps_dict.values()))
    dates = np.array(list(pps_dict.keys()))

    x = np.arange(len(pps))
    # this is a bug workaround
    # it may only be present in my dev env
    try:
        trend = np.poly1d(np.polyfit(x, pps, 2))
    except Exception:
        print(
            'SYS_LOGGER: np.poly1d(np.polyfit()) bug fix triggered',
            file=sys.stderr
        )
        trend = np.poly1d(np.polyfit(x, pps, 2))

    avg = sum(pps) / len(pps)
    avg = np.full(shape=(len(x),), fill_value=avg)

    plt.style.use('dark_background')
    plt.subplots(figsize=(14.5, 8))
    plt.title('Points/Sec per Match', fontsize=16)
    plt.ylabel('Points/Sec')
    plt.xlabel('Match Date')
    plt.xticks(x, dates, rotation=90, fontsize=8)
    plt.plot(
        x, pps, linewidth=2, marker='o', color='cornflowerblue', label='PPS'
    )
    plt.plot(
        x, trend(x), linewidth=2, color='#9a1f40', label='Trend'
    )
    plt.plot(
        x, avg, linewidth=2, linestyle='--', color='whitesmoke',
        label='Average'
    )
    plt.grid(linestyle=':', linewidth=0.3)
    plt.margins(x=0.01, y=0.03)
    plt.annotate(
        f'Shooter Name: {fn} {ln}', (1, 1), (-125, 30),
        fontsize=7, xycoords='axes fraction',
        textcoords='offset points', va='top'
    )
    plt.annotate(
        f'USPSA#: {form_dict["mem_num"]}', (1, 1), (-125, 20), fontsize=7,
        xycoords='axes fraction', textcoords='offset points',
        va='top'
    )
    plt.annotate(
        f'Division: {form_dict["division"]}', (1, 1), (-125, 10), fontsize=7,
        xycoords='axes fraction', textcoords='offset points',
        va='top'
    )
    plt.annotate(
        f'Average PP/S: {sum(pps_dict.values()) / len(pps_dict.values()):.2f}',
        (0, 0), (0, -80), xycoords='axes fraction',
        textcoords='offset points', va='top'
    )
    plt.annotate(
        f'Total Matchs: {len(dates)}',
        (0, 0), (0, -92), xycoords='axes fraction',
        textcoords='offset points', va='top'
    )
    plt.legend(
        bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=3,
        borderaxespad=0., fontsize=8
    )
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    image = base64.b64encode(image_png)
    image = image.decode('utf-8')

    return image
