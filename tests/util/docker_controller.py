import subprocess
import os
from tests.util.environment import environment


class DockerController:

    @staticmethod
    def up():
        environ = os.environ.copy()
        environ["TEST"] = "1"
        command = 'run-local' if environment['LOCAL'] == '1' else 'run'
        process = subprocess.Popen(
            [
                'sh', '-c', f'bin/{command}'
            ],
            stdout=subprocess.PIPE,
            env=environ
        )
        process.wait()
        for line in process.stdout:
            print(line.decode('utf-8'), end='', flush=True)

    @staticmethod
    def down():
        environ = os.environ.copy()
        environ["TEST"] = "1"
        command = 'stop-local' if environment['LOCAL'] == '1' else 'stop'
        process = subprocess.Popen(
            ['sh', '-c', f'bin/{command}'],
            stdout=subprocess.PIPE,
            env=environ
        )
        process.wait()
        for line in process.stdout:
            print(line.decode('utf-8'), end='', flush=True)
