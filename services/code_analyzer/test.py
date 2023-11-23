import json
from itertools import product


def global_func():
    print("Global func")


z = 0


class Test:

    _x: int

    def __init__(self, x: int):
        print(global_func())
        self._x = x

    def hello(self):
        print("Hello world!")

    @property
    def x(self):
        global z
        z = u
        return self._x

    def x_cross_x(self):
        for i, j in product(range(self._x), range(self._x)):
            print(i * j)

    def hello_cross_x(self):
        self.hello()
        self.x_cross_x()

    def to_json(self):
        return json.dumps({"x": self._x})


t = Test(5)
