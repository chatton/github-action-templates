#!/usr/bin/env python

import sys
import argparse
from typing import Dict, List

import yaml


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Template Github Actions')
    parser.add_argument("--template", "-t", type=str)
    return parser.parse_args()


def _load_template_file(filename: str) -> Dict:
    with open(filename, "r") as f:
        return yaml.safe_load(f.read())


def _load_jobs(template: Dict) -> List:
    job_dicts = []
    jobs = template["jobs"]

    for job in jobs:
        path = job["path"]
        with open(path) as f:

            job_dict = yaml.safe_load(f.read())

            if "steps" in job:
                job_dict["steps"] = []
                steps = job["steps"]
                for step in steps:
                    with open(step, "r") as sf:
                        step_list = yaml.safe_load(sf.read())
                        for s in step_list:
                            job_dict["steps"].append(s)

            job_dicts.append(job_dict)

    return job_dicts


def _load_events(template: Dict) -> Dict:
    events = []
    event_filepaths = template["events"]
    for filepath in event_filepaths:
        with open(filepath) as f:
            events.append(yaml.safe_load(f.read()))
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

    print(yaml.dump(github_action))

    return 0


if __name__ == '__main__':
    sys.exit(main())
