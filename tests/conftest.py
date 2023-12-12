from .util.docker_controller import DockerController


def pytest_sessionstart(session):
    DockerController.up()


def pytest_sessionfinish(session, exitstatus):
    DockerController.down()
