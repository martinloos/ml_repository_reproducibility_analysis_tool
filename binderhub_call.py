#!/usr/bin/python3

# TODO: doc

import subprocess
import json
import time
from rich import print

# Change IP/URL at front to use
BINDERHUB_BASE_URL = '10.108.224.55/build/gh/'

result = []


def get_result():
    if not result:
        result.append('No')

    return result


def call_binderhub_to_build(repo_owner, repo_name):
    print('If the rate limit is exceeded can take up to 1 hour ...\n')

    print('[bold green]Testing if binderhub reachable ...[/bold green]\n')

    ootb_buildable = 'No'

    if 'http' in BINDERHUB_BASE_URL:
        binderhub_url = BINDERHUB_BASE_URL.split('/', 3)[2]
    else:
        binderhub_url = BINDERHUB_BASE_URL.split('/')[0]

    binderhub_reachable = 0

    commands = ['curl', '-H', '"Accept: application/json"', '--connect-timeout', '20', '--max-time', '60',
                binderhub_url]
    cmd = subprocess.Popen(commands, stdout=subprocess.PIPE)
    out, err = cmd.communicate()
    reachable = out.decode('utf8').replace("'", '"').strip()

    if reachable:
        binderhub_reachable = 1
        print('\n[bold green]Binderhub reachable. Starting build call.[/bold green]\n')
    else:
        print('\n:pile_of_poo: [bold red]Binderhub not reachable. Check base url: [/bold red]' + binderhub_url + '\n')
        ootb_buildable = 'BinderHub not reachable'

    # if Dockerfile present: Binder expects very specific use of it check documentation
    # otherwise it's very likely that the container will crash
    # https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html
    url = BINDERHUB_BASE_URL + repo_owner + '/' + repo_name + '/HEAD'
    commands = ['curl', '-H', '"Accept: application/json"', '--connect-timeout', '120', '--max-time', '1200',
                url]

    rate_limit_exceeded = 0

    while (rate_limit_exceeded == 0) & (binderhub_reachable == 1):
        cmd = subprocess.Popen(commands, stdout=subprocess.PIPE)
        out, err = cmd.communicate()

        if out:
            # Decode UTF-8 bytes to Unicode, and convert single quotes
            # to double quotes to make it valid JSON
            out_json = out.decode('utf8').replace("'", '"').replace('data: ', '').replace(':keepalive', '').strip()
            string_list = out_json.split('}')
            for s in string_list:
                if 'phase' in s:
                    s = s.replace('\n', '') + '}'
                    # Load the JSON to a Python list & dump it back out as formatted JSON
                    data = json.loads(s)
                    if 'Rate limit exceeded.' in s:
                        # retry in 5 minutes
                        print('\n:pile_of_poo: [bold red]Rate limit for BinderHub Call exceeded. '
                              'Retrying in 5 minutes. Please wait. This may take up to one hour.[/bold red]\n')
                        time.sleep(300)
                    else:
                        if data['phase'] == 'ready':
                            url = (data['url']).replace('\n', '')
                            token = data['token'].replace('\n', '')
                            print("\n:smiley: [bold green]BinderHub build successful! [/bold green]")
                            print('Url: ' + url + ' Token: ' + token + '\n')
                            rate_limit_exceeded = 1
                            build_successful = 1
                            ootb_buildable = 'Yes'
                        elif data['phase'] == 'failed':
                            msg = (data['message']).replace('\n', '')
                            print('\n:pile_of_poo: [bold red]Failed with message: [/bold red]'
                                  + msg + '\n')
                            rate_limit_exceeded = 1
                            ootb_buildable = 'No'

    result.append(ootb_buildable)
