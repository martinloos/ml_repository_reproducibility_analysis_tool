#!/usr/bin/python3

import subprocess
import json
import time
from rich import print

# Modify this URL (replace IP with your URL/IP). Do not remove the '/build/gh/' part as this is the API path.
BINDERHUB_BASE_URL = '10.100.198.221/build/gh/'
# Stores the result of the analysis. Can be: 'BinderHub not reachable', 'Yes' in case the repository is buildable
# or 'No' if it is not.
result = []


def get_result():
    # No result is present (e.g. something went wrong). We assume that the repository is not buildable.
    if not result:
        result.append('No')

    return result


def call_binderhub_to_build(repo_owner, repo_name):
    """
        Firstly, tests if the specified BinderHub URL is reachable. If yes, calls this URL and tries to build the
        provided repository. Depending on the repository size, and the BinderHub resources this can take more or less
        time.

        Parameters:
            repo_owner (str): Name of the owner of the repository.
            repo_name (str): Name of the repository.
    """
    # Can happen if you use this tool in a loop to perform analysis on many repositories.
    print('If the rate limit is exceeded can take up to 1 hour ...\n')
    print('[bold green]Testing if binderhub reachable ...[/bold green]\n')

    # default value
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

    # If Dockerfile present: Binder expects very specific use of it check documentation
    # Otherwise, it's very likely that the container will crash
    # https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html
    url = BINDERHUB_BASE_URL + repo_owner + '/' + repo_name + '/HEAD'
    commands = ['curl', '-H', '"Accept: application/json"', '--connect-timeout', '120', '--max-time', '1200',
                url]

    finished_build_call = 0

    # terminates if the build call has been finished, and we got either a positive or negative result
    while (finished_build_call == 0) & (binderhub_reachable == 1):
        cmd = subprocess.Popen(commands, stdout=subprocess.PIPE)
        out, err = cmd.communicate()

        if out:
            out_json = out.decode('utf8').replace('data: ', '').replace(':keepalive', '').strip()
            string_list = out_json.split('}')
            for s in string_list:
                if 'phase' in s:
                    s = s.replace('\\n', '').replace('\n', '') + '}'
                    if (s.startswith('{')) and not ('"phase": "building"' in s):
                        # Load the JSON to a Python list & dump it back out as formatted JSON
                        data = json.loads(s)
                        if 'Rate limit exceeded.' in s:
                            # retry in 5 minutes
                            print('\n:pile_of_poo: [bold red]Rate limit for BinderHub Call exceeded. '
                                  'Retrying in 5 minutes. Please wait. This may take up to one hour.[/bold red]\n')
                            time.sleep(300)
                        else:
                            if data['phase'].lower() == 'ready':
                                url = (data['url']).replace('\n', '')
                                token = data['token'].replace('\n', '')
                                print("\n:smiley: [bold green]BinderHub build successful! [/bold green]")
                                print('Url: ' + url + ' Token: ' + token + '\n')
                                finished_build_call = 1
                                ootb_buildable = 'Yes'
                            elif data['phase'].lower() == 'failed':
                                try:
                                    msg = (data['message']).replace('\n', '')
                                except KeyError:
                                    msg = 'Failed.'
                                print('\n:pile_of_poo: [bold red]Failed with message: [/bold red]'
                                      + msg + '\n')
                                finished_build_call = 1
                                ootb_buildable = 'No'

    result.append(ootb_buildable)
