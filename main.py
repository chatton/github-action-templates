#!/usr/bin/env python3

import sys
import argparse
from ghat.template import template_github_action
import ruamel.yaml
yaml = ruamel.yaml.YAML()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Template Github Actions')
    parser.add_argument("--template", "-t", type=str)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    github_action = template_github_action(args.template)
    yaml.dump(github_action, sys.stdout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
