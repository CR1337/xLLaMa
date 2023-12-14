from .util.docker_controller import DockerController
import time


def pytest_sessionstart(session):
    DockerController.up()
    time.sleep(1)


def pytest_sessionfinish(session, exitstatus):
    DockerController.down()
