from typing import Dict, List, Tuple
import os
import json
import ruamel.yaml
import io
import requests

yaml = ruamel.yaml.YAML()

def __pp(obj):
    print(json.dumps(obj, indent=4))


def _load_template(template: str, actions_dir: str) -> Tuple[Dict, str]:
    # it is a link, try to fetch the yaml contents.
    if template.startswith("http"):
        resp = requests.get(template, stream=True)
        resp.raise_for_status()
        return yaml.load(resp.content), template

    # find any files that have yaml or yml extentions that match.
    for subdir, _, files in os.walk(actions_dir):
        for f in files:
            stripped = f.rstrip(".yml").rstrip(".yaml")
            full_file = os.path.join(subdir, stripped)
            if os.path.exists(full_file + ".yml") and template == stripped:
                with open(full_file + ".yml", "r") as f2:
                    return yaml.load(f2.read()), full_file + ".yml" 

            if os.path.exists(full_file + ".yaml") and template == stripped:
                with open(full_file + ".yaml", "r") as f2:
                    return yaml.load(f2.read()), full_file + ".yaml"

    # TOOD: this will also find a file that is in the root of the directory if not under the actions dir!
    # a full or relative path was provided, just use it directly.
    if os.path.exists(template):
        with open(template, "r") as f:
            return yaml.load(f.read()), template

    raise ValueError("Unable to find template for {}".format(template))



def _load_jobs(template: Dict, actions_dir: str) -> Dict:
    job_templates = template["jobs"]
    final_jobs = []
    for job_template in job_templates:
        job_dict, job_template_path = _load_template(job_template["template"], actions_dir)
        job_dict.yaml_set_start_comment(f"template: {job_template_path}", indent=2)
        for job_name in job_dict:
            # we move any "if" specified in the template to all of the jobs from the templates.
            if "if" in job_template:
                job_dict[job_name]["if"] = job_template["if"]

            # we assign directly all of the steps references in the templates.
            if "steps" in job_template:
                job_dict[job_name]["steps"] = _get_steps(job_template, actions_dir)

        final_jobs.append(job_dict)
    return _merge_yaml_lists_into_dict(final_jobs)


def _get_steps(job: Dict, actions_dir: str) -> List[Dict]:
    final_steps = []
    steps = job["steps"]
    for step in steps:
        step_list, step_template_path = _load_template(step["template"], actions_dir)
        for (i, s) in enumerate(step_list):
            if i == 0:
                s.yaml_set_start_comment(f"template: {step_template_path}", indent=4)

            if "if" in step:
                s["if"] = step["if"]
            final_steps.append(s)

    return final_steps


def _load_events(template: Dict, actions_dir: str) -> Dict:
    events = []
    all_events = template["events"]
    for e in all_events:
        yaml_event, event_template_path = _load_template(e["template"], actions_dir)
        yaml_event.yaml_set_start_comment(f"template: {event_template_path}", indent=2)
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


def template_github_action(template_path: str, actions_dir=".action_templates") -> Dict:
    template, _ = _load_template(template_path, actions_dir)
    name = template["name"]
    jobs = _load_jobs(template, actions_dir)
    events = _load_events(template, actions_dir)
    return {
        "name": name,
        "on": events,
        "jobs": jobs,
    }
