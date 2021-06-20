from typing import Dict, List
import os
import json
import ruamel.yaml
import io

yaml = ruamel.yaml.YAML()

DEFAULT_JOBS_DIR = ".action_templates/jobs"
DEFAULT_STEPS_DIR = ".action_templates/steps"
DEFAULT_EVENTS_DIR = ".action_templates/events"


def __pp(obj):
    print(json.dumps(obj, indent=4))


def _load_template_file(filename: str) -> Dict:
    with open(filename, "r") as f:
        return yaml.load(f.read())


def _get_file_path_or_default(path: str, default_path: str) -> str:
    if os.path.exists(path):
        return path
    if os.path.exists(path + ".yml"):
        return path + ".yml"
    if os.path.exists(path + ".yaml"):
        return path + ".yaml"

    default = os.path.join(default_path, path)
    if os.path.exists(default):
        return default
    if os.path.exists(default + ".yml"):
        return default + ".yml"
    if os.path.exists(default + ".yaml"):
        return default + ".yaml"
    raise ValueError("No such file: {}!".format(path))


def _load_jobs(template: Dict) -> Dict:
    job_templates = template["jobs"]
    final_jobs = []
    for job_template in job_templates:
        path = _get_file_path_or_default(job_template["template"], DEFAULT_JOBS_DIR)
        job_dict = _load_template_file(path)
        job_dict.yaml_set_start_comment(f"template: {path}", indent=2)
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
        path = _get_file_path_or_default(step_template, DEFAULT_STEPS_DIR)
        step_list = _load_template_file(path)

        for (i, s) in enumerate(step_list):
            if i == 0:
                s.yaml_set_start_comment(f"template: {path}", indent=4)

            if "if" in step:
                s["if"] = step["if"]
            final_steps.append(s)

    return final_steps


def _load_events(template: Dict) -> Dict:
    events = []
    all_events = template["events"]
    for e in all_events:
        event_template = e["template"]
        path = _get_file_path_or_default(event_template, DEFAULT_EVENTS_DIR)
        with open(path) as f:
            yaml_event = yaml.load(f.read())
            yaml_event.yaml_set_start_comment(f"template: {path}", indent=2)
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
    template = _load_template_file(template_path)
    name = template["name"]
    jobs = _load_jobs(template)
    events = _load_events(template)
    return {
        "name": name,
        "on": events,
        "jobs": jobs,
    }
