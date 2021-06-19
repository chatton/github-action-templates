# Github Action Templates

Github Action Templates is a tool that allows for templating of yaml files to compose a github action.
This allows for re-use of jobs, steps and events.


### Quick Start

Create a new directory for your templates.

```bash
mkdir -p .action_templates/{jobs,steps,events}
```

####Templated jobs should go in the `jobs` directory.

```yaml
# .action_templates/jobs/hello-world.yaml
HelloWorld:
  if: success()
  runs-on: ubuntu-latest
```

*Note*: 
* `steps` can be ommited if you are also providing a additional steps templates.
* There should be a **single job** per file.
####Templated steps go under the `steps` directory.

The contents of this file should be a yaml array with the step items to be templated.

```yaml
# .action_templates/steps/python-setup.yaml
- uses: actions/setup-python@v2
  with:
    python-version: '3.6'
- run: pip install -r requirements.txt
- run: python my-script.py
```

*Note* 
  * The `steps` key is ommited, we just provide the contents.

####Templated events go in the `events` directory

```yaml
# .action_templates/events/on-pull-request-master.yaml
pull_request:
  branches:
    - master
```

####Create the Template file to pull everything together

```yaml
# .action_templates/my-github-action.yaml
name: "My Github Action"
jobs:
  - template: hello-world
    if: success()
    steps:
    - template: python-setup
      if: always()
events:
  - template: on-pull-request-master
```


#### Generate the template

```bash
python main.py -t .action_templates/my-github-action.yaml
```


The generated contents will be

```yaml
name: My Github Action
on:
  pull_request:
    branches:
    - master
jobs:
  HelloWorld:
    if: success()
    runs-on: ubuntu-latest
    steps:
    # template: python-setup
    - uses: actions/setup-python@v2
      with:
        python-version: '3.6'
      if: always()
    - run: pip install -r requirements.txt
      if: always()
    - run: python my-script.py
      if: always()
```

Alternatively, install the python package and use the provided library in your applications.

```bash
pip install .

python

>>> from ghat.template import template_github_action
>>> template_github_action(".action_templates/my-github-action.yaml")
{'name': 'My Github Action', 'on': {'pull_request': ordereddict([('branches', ['master'])])}, 'jobs': {'HelloWorld': ordereddict([('if', 'success()'), ('runs-on', 'ubuntu-latest'), ('steps', [ordereddict([('uses', 'actions/setup-python@v2'), ('with', ordereddict([('python-version', '3.6')])), ('if', 'always()')]), ordereddict([('run', 'pip install -r requirements.txt'), ('if', 'always()')]), ordereddict([('run', 'python my-script.py'), ('if', 'always()')])])])}}
>>>
```


#### Structure of the template file

   | Field | Type| Description |  Sample Value |
   |----|----|----|---|
   | name | String | Name of the GitHub Action. | `My Github Action` |
   | jobs | Array |Array of jobs which the Github Action will contain |
   | jobs[*].template |String| Full or relative path to the template file. Can be just the name if the default location (.action_templates/jobs) is used. | `.action_templates/jobs/hello-world.yaml` |
   | jobs[*].if |String| Contents of the `if:` condition that will be used for this job. | `github.event.pull_request.head.repo.full_name == '<some-value>'`|
   | jobs[*].steps |Array| Array of step template objects |||
   | jobs[*].steps[*].template |String| Full or relative path to the template file. Can be just the name if the default location (.action_templates/steps) is used.| `python-setup`|
   | jobs[*].steps[*].if |String|  Contents of the `if:` condition that will be used for **all steps** in this template. | `always()`|
   | events |Array| Array of events, these correspond to the `on` section of a workflow file. | 
   | events[*].template |String| Full or relative path to the template file. Can be just the name if the default location (.action_templates/events) is used.| `on-pull-request-master` | 
