import pytest
from typing import Dict

from ghat.template import template_github_action


@pytest.fixture(scope="module")
def template_0() -> Dict:
    yield template_github_action("tests/fixtures/template-0.yaml")


@pytest.fixture(scope="module")
def template_1() -> Dict:
    yield template_github_action("tests/fixtures/template-1.yaml")


@pytest.fixture(scope="module")
def param_template() -> Dict:
    yield template_github_action("tests/fixtures/template-param.yaml")


def test_jobs_can_be_templated(template_0: Dict):
    assert len(template_0["jobs"]) == 1

    job = template_0["jobs"]["HelloWorld"]
    assert (
            job["if"]
            == "github.event.pull_request.head.repo.full_name != 'mongodb/mongodb-kubernetes-operator' && contains(github.event.pull_request.labels.*.name, 'safe-to-test')"
    )
    assert job["runs-on"] == "ubuntu-latest"


def test_steps_can_be_templated(template_0: Dict):
    assert "steps" in template_0["jobs"]["HelloWorld"]

    steps = template_0["jobs"]["HelloWorld"]["steps"]

    assert len(steps) == 5
    assert steps[0]["name"] == "Hello World"
    assert steps[0]["run"] == 'echo "Hello World 0!"'
    assert steps[0]["if"] == "success()"

    assert steps[1]["name"] == "Hello World ls"
    assert steps[1]["run"] == 'echo "ls -la"'
    assert steps[1]["if"] == "success()"


def test_events_can_be_templated(template_0: Dict):
    assert "on" in template_0
    events = template_0["on"]
    assert len(events) == 3

    assert events["pull_request"]["branches"][0] == "master"
    assert events["push"]["branches"][0] == "master"
    assert "workflow_dispatch" in events


def test_urls_can_be_used_for_templating_jobs(template_1: Dict):
    assert len(template_1["jobs"]) == 1
    assert template_1["jobs"]["HelloWorld"]["if"] == "success()"


def test_step_can_be_parameterised(param_template: Dict):
    step = param_template["jobs"]["ParameterizedJob"]["steps"][0]

    assert step["with"]["ref"] == "${{ some/github/value }}"
    assert step["with"]["repository"] == "${{ github.repository }}"


def test_job_can_be_parameterised(param_template: Dict):
    job = param_template["jobs"]["ParameterizedJob"]

    assert job["runs-on"] == "ubuntu-latest"
    assert job["some-key"] == "some-value"


def test_event_can_be_parameterised(param_template: Dict):
    assert param_template["on"]["push"]["branches"][0] == "master"


# TODO:

# def test_urls_can_be_used_for_templating_steps
# def test_urls_can_be_used_for_templating_events
# def test_relative_paths_can_be_used
# def test_absolute_paths_can_be_used
# def test_file_name_with_yaml_extension_can_be_used
# def test_file_name_with_yml_extension_can_be_used
# def test_custom_actions_dir
# def test_exception_raised_when_file_does_not_exist
