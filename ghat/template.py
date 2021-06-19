from typing import Dict, List
import os
import ruamel.yaml

yaml = ruamel.yaml.YAML()

DEFAULT_JOBS_DIR = "action_templates/jobs"
DEFAULT_STEPS_DIR = "action_templates/steps"
DEFAULT_EVENTS_DIR = "action_templates/events"


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
    job_list = []
    jobs = template["jobs"]

    for job in jobs:
        path = job["template"]
        with open(_get_file_path_or_default(path, DEFAULT_JOBS_DIR)) as f:
            job_dict = yaml.load(f.read())
            # specified a condition in the template file.
            if "if" in job:
                job_dict["if"] = job["if"]

            # specified steps in template file.
            if "steps" in job:
                job_dict["steps"] = _get_steps(job)

            job_list.append(job_dict)

    on_obj = {}
    for e in job_list:
        for k, v in e.items():
            on_obj[k] = v
    return on_obj


def _get_steps(job: Dict) -> List[str]:
    final_steps = []
    steps = job["steps"]
    for step in steps:
        step_template = step["template"]
        with open(_get_file_path_or_default(step_template, DEFAULT_STEPS_DIR), "r") as sf:
            step_list = yaml.load(sf.read())
            for s in step_list:
                final_steps.append(s)
    return final_steps


def _load_events(template: Dict) -> Dict:
    events = []
    all_events = template["events"]
    for e in all_events:
        event_template = e["template"]
        with open(_get_file_path_or_default(event_template, DEFAULT_EVENTS_DIR)) as f:
            events.append(yaml.load(f.read()))
    on_obj = {}
    for e in events:
        for k, v in e.items():
            on_obj[k] = v
    return on_obj


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
