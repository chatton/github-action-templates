from typing import Dict, List
import os
import json
import ruamel.yaml
import io
import requests

yaml = ruamel.yaml.YAML()

DEFAULT_JOBS_DIR = ".action_templates/jobs"
DEFAULT_STEPS_DIR = ".action_templates/steps"
DEFAULT_EVENTS_DIR = ".action_templates/events"


def __pp(obj):
    print(json.dumps(obj, indent=4))


def _load_template(template: str) -> Dict:

    # it is a link, try to fetch the yaml contents.
    if template.startswith("http"):
        resp = requests.get(template, stream=True)
        resp.raise_for_status()
        return yaml.load(resp.content)

    # a full or relative path was provided, just use it directly.
    if os.path.exists(template):
        with open(template, "r") as f:
            return yaml.load(f.read())

    # find any files that have yaml or yml extentions that match.
    for subdir, _, files in os.walk("examples"):
        for f in files:
            stripped = f.rstrip(".yml").rstrip(".yaml")
            full_file = os.path.join(subdir, stripped)
            if os.path.exists(full_file + ".yml") and template == stripped:
                with open(full_file + ".yml", "r") as f2:
                    return yaml.load(f2.read())


            if os.path.exists(full_file + ".yaml") and template == stripped:
                with open(full_file + ".yaml", "r") as f2:
                    return yaml.load(f2.read())



def _load_jobs(template: Dict) -> Dict:
    job_templates = template["jobs"]
    final_jobs = []
    for job_template in job_templates:

        template_name = job_template["template"]
        job_dict = _load_template(template_name)
        job_dict.yaml_set_start_comment(f"template: {template_name}", indent=2)
        for job_name in job_dict:
            # we move any "if" specified in the template to all of the jobs from the templates.
            if "if" in job_template:
                job_dict[job_name]["if"] = job_template["if"]

            # we assign directly all of the steps references in the templates.
            if "steps" in job_template:
                job_dict[job_name]["steps"] = _get_steps(job_template)

        final_jobs.append(job_dict)
    return _merge_yaml_lists_into_dict(final_jobs)


def _get_steps(job: Dict) -> List[Dict]:
    final_steps = []
    steps = job["steps"]
    for step in steps:
        step_template = step["template"]
        step_list = _load_template(step_template)
        for (i, s) in enumerate(step_list):
            if i == 0:
                s.yaml_set_start_comment(f"template: {step_template}", indent=4)

            if "if" in step:
                s["if"] = step["if"]
            final_steps.append(s)

    return final_steps


def _load_events(template: Dict) -> Dict:
    events = []
    all_events = template["events"]
    for e in all_events:
        event_name = e["template"]
        yaml_event = _load_template(e["template"])
        yaml_event.yaml_set_start_comment(f"template: {event_name}", indent=2)
        events.append(yaml_event)

    return _merge_yaml_lists_into_dict(events)


def _merge_yaml_lists_into_dict(yaml_elements: List[Dict]) -> Dict:
    """
    _merge_yaml_lists_into_dict converts a list of elements into a dict.
    this function preserves yaml comments.

    :param yaml_elements: a list of yaml elements
    :return: a yaml dictionary consisting of all of these elements.
    """
    string_stream = io.StringIO()
    for e in yaml_elements:
        yaml.dump(e, string_stream)
    string_stream.seek(0)
    return yaml.load(string_stream)


def template_github_action(template_path: str) -> Dict:
    template = _load_template(template_path)
    # __pp(template)
    name = template["name"]
    jobs = _load_jobs(template)
    events = _load_events(template)
    return {
        "name": name,
        "on": events,
        "jobs": jobs,
    }
