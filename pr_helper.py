# This script is used as part of the "pr-helper" task from the Dispatchfile

import os
import requests
import sys
import logging
import json
import tarfile
import subprocess

logging.basicConfig(level=logging.DEBUG)

title = '## Deploy these changes to the cluster'
check_open_prs = 'Check [opened pull requests](https://github.com/mesosphere/konvoy-soak/pulls) and make sure there are no PRs with a `aws/deployed` label. If there are, they must be merged before you proceed here, otherwise this will cause issues on the cluster.'
konvoy_init = "Download the generated cluster.yaml [here](REPLACE_WITH_URL) and merge it with the existing cluster.yaml in the repo by manually comparing the two. It's possible there is nothing to merge. Once you are done, contribute the changes (if any) to this pull request and merge it."
check_commit = 'Once this pull request is merged into master, give some time for the pipeline to run, then [look for the status check next to your commit](https://github.com/mesosphere/konvoy-soak/commits/master) in master. If there is a red check mark, report the issue in #devprod. If the check is green, a new commit titled "Deploy soak update" should also have been merged automatically in master.'
argo = 'Go to [ArgoCD](https://konvoy-staging.production.d2iq.cloud/dispatch/argo-cd/applications/konvoy-soak). Click "SYNC", then "SYNCHRONIZE". This will start the update process and notify #eng-konvoy-soak.'

help_message = """{title}

1. {check_open_prs}

2. {check_commit}

3. {argo}
""".format(title=title, check_open_prs=check_open_prs, check_commit=check_commit, argo=argo)

help_message_upgrade = """{title}

1. {check_open_prs}

2. {konvoy_init}

3. {check_commit}

4. {argo}
""".format(title=title, check_open_prs=check_open_prs, konvoy_init=konvoy_init, check_commit=check_commit, argo=argo)



pr_number = sys.argv[1].split('-')[1]
gh_repo = 'cicd-hello-world'
gh_owner = 'cprovencher'
bot_name = 'cprovencher'
gh_token = os.environ['GITHUB_TOKEN']
headers = {'Authorization': 'token ' + gh_token}

def generate_cluster_yaml(version):
    gh_token = os.environ['GITHUB_TOKEN']
    headers = {'Authorization': 'token ' + gh_token}
    url = 'https://downloads.mesosphere.io/konvoy/konvoy_{version}_linux.tar.bz2'.format(version=version)
    r = requests.get(url, stream = True)
    print(r.json())
    r.raise_for_status()
    with open("konvoy.tar.bz2", "wb") as konvoy_file:
        for chunk in r.iter_content(chunk_size = 1024):
            if chunk:
                konvoy_file.write(chunk)

    tar = tarfile.open('konvoy.tar.bz2', 'r:bz2')
    tar.extractall('konvoy_dir')
    tar.close()
    konvoy_sub_dir = 'konvoy_dir/konvoy_' + version
    subprocess.run(['./konvoy', 'init'], cwd=konvoy_sub_dir, check=True)
    konvoy_yaml = 'konvoy_{}_cluster.yaml'.format(version)

    with open(konvoy_sub_dir + '/cluster.yaml', 'r') as f:
        content = f.read()

    input = {
        'description': 'Temp gist used for the pr-helper in konvoy-soak repo',
        'files': {
            konvoy_yaml: {
                'content': content
            }
        }
    }
    data = json.dumps(input).encode('utf-8')
    r = requests.post('https://api.github.com/gists', data=data, headers=headers)
    r_json = r.json()
    print(r_json)
    r.raise_for_status()
    return r_json['files'][konvoy_yaml]['raw_url']


url = 'https://api.github.com/repos/{}/{}/pulls/{}'.format(gh_owner, gh_repo, pr_number)
r = requests.get(url, headers=headers)
r_json = r.json()
print(r_json)
r.raise_for_status()

if r_json['user']['login'] == bot_name:
    if r_json['body'] == '':
        konvoy_version = r_json['title'].split()[-1]
        cluster_yaml_url = generate_cluster_yaml(konvoy_version)
        help_message_upgrade.replace('REPLACE_WITH_URL', cluster_yaml_url)
        data = json.dumps({'body': help_message_upgrade}).encode('utf-8')
        r = requests.patch(url, data=data, headers=headers)
        print(r.json())
        r.raise_for_status()
else:
    url = 'https://api.github.com/repos/{}/{}/issues/{}/comments'.format(gh_owner, gh_repo, pr_number)

    r = requests.get(url, headers=headers)
    r_json = r.json()
    print(r_json)
    r.raise_for_status()

    for comment in r_json:
        if comment['user']['login'] == bot_name:
            exit(0)

    data = json.dumps({'body': help_message}).encode('utf-8')
    r = requests.post(url, data=data, headers=headers)
    print(r.json())
    r.raise_for_status()
