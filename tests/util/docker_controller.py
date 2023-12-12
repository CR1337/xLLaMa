import subprocess
import os


class DockerController:

    @staticmethod
    def up():
        environment = os.environ.copy()
        environment["TEST"] = "1"
        process = subprocess.Popen(
            [
                'docker', 'compose', 'up', '-d', '--wait',
                '--scale', 'db=0', '--scale', 'frontend=0'
            ],
            stdout=subprocess.PIPE,
            env=environment
        )
        process.wait()
        for line in process.stdout:
            print(line.decode('utf-8'), end='', flush=True)

    @staticmethod
    def down():
        process = subprocess.Popen(
            ['docker', 'compose', 'down'],
            stdout=subprocess.PIPE,
        )
        process.wait()
        for line in process.stdout:
            print(line.decode('utf-8'), end='', flush=True)
