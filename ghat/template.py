from typing import Dict, List
import os
import ruamel.yaml
yaml = ruamel.yaml.YAML()

DEFAULT_JOBS_DIR = ".action_templates/jobs"
DEFAULT_STEPS_DIR = ".action_templates/steps"
DEFAULT_EVENTS_DIR = ".action_templates/events"


def pp(obj):
    import json
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
    final_jobs = {}
    for job_template in job_templates:
        path = job_template["template"]
        with open(_get_file_path_or_default(path, DEFAULT_JOBS_DIR)) as f:
            job_dict = yaml.load(f.read())
            for job_name in job_dict:
                # we move any "if" specified in the template to all of the jobs from the templates.
                if "if" in job_template:
                    job_dict[job_name]["if"] = job_template["if"]

                # we assign directly all of the steps references in the templates.
                if "steps" in job_template:
                    job_dict[job_name]["steps"] = _get_steps(job_template)

            # add the job by name to the final result.
            final_jobs[job_name] = job_dict[job_name]
    return final_jobs


def _get_steps(job: Dict) -> List[str]:
    final_steps = []
    steps = job["steps"]
    for step in steps:
        step_template = step["template"]
        with open(_get_file_path_or_default(step_template, DEFAULT_STEPS_DIR), "r") as sf:
            step_list = yaml.load(sf.read())
            for s in step_list:
                if "if" in step:
                    s["if"] = step["if"]
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
