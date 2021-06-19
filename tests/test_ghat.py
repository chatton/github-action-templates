import pytest
from typing import Dict

from ghat.template import template_github_action


@pytest.fixture(scope="module")
def template_0() -> Dict:
    yield template_github_action("tests/fixtures/template-0.yaml")


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
