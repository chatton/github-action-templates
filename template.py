#!/usr/bin/env python

import sys
import argparse
from typing import Dict, List

import ruamel.yaml
yaml = ruamel.yaml.YAML()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Template Github Actions')
    parser.add_argument("--template", "-t", type=str)
    return parser.parse_args()


def _load_template_file(filename: str) -> Dict:
    with open(filename, "r") as f:
        return yaml.load(f.read())


def _load_jobs(template: Dict) -> List:
    job_dicts = []
    jobs = template["jobs"]

    for job in jobs:
        path = job["path"]
        with open(path) as f:

            job_dict = yaml.load(f.read())

            if "steps" in job:
                job_dict["steps"] = _get_states(job)

            job_dicts.append(job_dict)

    return job_dicts


def _get_states(job: Dict) -> List[str]:
    final_steps = []
    steps = job["steps"]
    for step in steps:
        with open(step, "r") as sf:
            step_list = yaml.load(sf.read())
            for s in step_list:
                final_steps.append(s)
    return final_steps


def _load_events(template: Dict) -> Dict:
    events = []
    event_filepaths = template["events"]
    for filepath in event_filepaths:
        with open(filepath) as f:
            events.append(yaml.load(f.read()))
    on_obj = {}
    for e in events:
        for k, v in e.items():
            on_obj[k] = v
    return on_obj


def main() -> int:
    args = _parse_args()

    template = _load_template_file(args.template)

    name = template["name"]
    jobs = _load_jobs(template)
    events = _load_events(template)

    github_action = {
        "name": name,
        "on": events,
        "jobs": jobs,
    }

    yaml.dump(github_action, sys.stdout)

    return 0


if __name__ == '__main__':
    sys.exit(main())
