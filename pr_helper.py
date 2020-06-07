# This script is used as part of the "pr-helper" task from the Dispatchfile

import os
import requests
import sys
import logging
import json

logging.basicConfig(level=logging.DEBUG)

help_message = """## Deploy these changes to the cluster

1. Check [opened pull requests](https://github.com/mesosphere/konvoy-soak/pulls) and make sure there are no PRs with a `Deployed` label. If there are, they must be merged before you proceed here, otherwise this will cause issues on the cluster.

2. If this PR is not about upgrading the Konvoy version, skip this step.  
Download that new Konvoy release, run `konvoy init`, take the generated cluster.yaml and merge it with the existing cluster.yaml in the repo by manually comparing the two. It's possible there is nothing to merge. Once you are done, contribute the changes (if any) to this pull request and merge it.

3. Once this pull request is merged into master, give some time for the pipeline to run, then [look for the status check next to your commit](https://github.com/mesosphere/konvoy-soak/commits/master) in master. If there is a red check mark, report the issue in #devprod. If the check is green, a new commit titled "Deploy soak update" should also have been merged automatically in master.

4. Go to [ArgoCD](https://konvoy-staging.production.d2iq.cloud/dispatch/argo-cd/applications/konvoy-soak). Click "SYNC", then "SYNCHRONIZE". This will start the update process and notify #eng-konvoy-soak.
"""

pr_number = sys.argv[1].split('-')[1]
gh_token = os.environ['GITHUB_TOKEN']
url = 'https://api.github.com/repos/cprovencher/cicd-hello-world/issues/{}/comments'.format(pr_number)

headers = {'Authorization':  'token ' + gh_token}
data = json.dumps({'body': help_message}).encode('utf-8')
r = requests.post(url, data=data, headers=headers)
print(r.json())
r.raise_for_status()
