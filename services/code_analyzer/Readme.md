# Code Analyzer

This service provides code analysis for defined symbols and eferences to them. It also provides different code metrics.

## Endpoints

### `GET /`
This endpoint only exists for debugging purposes. It doesn't take any further parameters and always returns
```json
{"message": "Hello, world!\n This is 'code_analyzer'."}
```

### `GET /analyze`
This endpoint analyzes a given code snippet and returns defined symbols and references to them. It expects a JSON body with a code field:
```json
{
    "code": <CODE>
}
```
where `<CODE>` is the code to analyze. Here we will use this example code:
```python
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
```
For this code snippet the endpoint returns the following JSON object:
```json
{
    "error": null,
    "analysis": {
        "imports": [
            {
                "id": "json",
                "defined_at": [
                    {
                        "start_line_number": 1,
                        "start_column_number": 0,
                        "end_line_number": 1,
                        "end_column_number": 11
                    }
                ],
                "references": [
                    {
                        "start_line_number": 38,
                        "start_column_number": 15,
                        "end_line_number": 38,
                        "end_column_number": 19
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "product",
                "defined_at": [
                    {
                        "start_line_number": 2,
                        "start_column_number": 0,
                        "end_line_number": 2,
                        "end_column_number": 29
                    }
                ],
                "references": [
                    {
                        "start_line_number": 30,
                        "start_column_number": 20,
                        "end_line_number": 30,
                        "end_column_number": 27
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "print",
                "defined_at": [
                    {
                        "start_line_number": null,
                        "start_column_number": null,
                        "end_line_number": null,
                        "end_column_number": null
                    }
                ],
                "references": [
                    {
                        "start_line_number": 21,
                        "start_column_number": 8,
                        "end_line_number": 21,
                        "end_column_number": 13
                    },
                    {
                        "start_line_number": 31,
                        "start_column_number": 12,
                        "end_line_number": 31,
                        "end_column_number": 17
                    },
                    {
                        "start_line_number": 17,
                        "start_column_number": 8,
                        "end_line_number": 17,
                        "end_column_number": 13
                    },
                    {
                        "start_line_number": 6,
                        "start_column_number": 4,
                        "end_line_number": 6,
                        "end_column_number": 9
                    }
                ],
                "is_builtin": true
            },
            {
                "id": "property",
                "defined_at": [
                    {
                        "start_line_number": null,
                        "start_column_number": null,
                        "end_line_number": null,
                        "end_column_number": null
                    }
                ],
                "references": [
                    {
                        "start_line_number": 23,
                        "start_column_number": 5,
                        "end_line_number": 23,
                        "end_column_number": 13
                    }
                ],
                "is_builtin": true
            },
            {
                "id": "int",
                "defined_at": [
                    {
                        "start_line_number": null,
                        "start_column_number": null,
                        "end_line_number": null,
                        "end_column_number": null
                    }
                ],
                "references": [
                    {
                        "start_line_number": 16,
                        "start_column_number": 26,
                        "end_line_number": 16,
                        "end_column_number": 29
                    }
                ],
                "is_builtin": true
            },
            {
                "id": "range",
                "defined_at": [
                    {
                        "start_line_number": null,
                        "start_column_number": null,
                        "end_line_number": null,
                        "end_column_number": null
                    }
                ],
                "references": [
                    {
                        "start_line_number": 30,
                        "start_column_number": 28,
                        "end_line_number": 30,
                        "end_column_number": 33
                    },
                    {
                        "start_line_number": 30,
                        "start_column_number": 44,
                        "end_line_number": 30,
                        "end_column_number": 49
                    }
                ],
                "is_builtin": true
            }
        ],
        "functions": [
            {
                "id": "__init__",
                "defined_at": [
                    {
                        "start_line_number": 16,
                        "start_column_number": 4,
                        "end_line_number": 18,
                        "end_column_number": 19
                    }
                ],
                "references": [],
                "is_builtin": false
            },
            {
                "id": "hello",
                "defined_at": [
                    {
                        "start_line_number": 20,
                        "start_column_number": 4,
                        "end_line_number": 21,
                        "end_column_number": 29
                    }
                ],
                "references": [
                    {
                        "start_line_number": 34,
                        "start_column_number": 8,
                        "end_line_number": 34,
                        "end_column_number": 18
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "x",
                "defined_at": [
                    {
                        "start_line_number": 24,
                        "start_column_number": 4,
                        "end_line_number": 27,
                        "end_column_number": 22
                    }
                ],
                "references": [],
                "is_builtin": false
            },
            {
                "id": "x_cross_x",
                "defined_at": [
                    {
                        "start_line_number": 29,
                        "start_column_number": 4,
                        "end_line_number": 31,
                        "end_column_number": 24
                    }
                ],
                "references": [
                    {
                        "start_line_number": 35,
                        "start_column_number": 8,
                        "end_line_number": 35,
                        "end_column_number": 22
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "hello_cross_x",
                "defined_at": [
                    {
                        "start_line_number": 33,
                        "start_column_number": 4,
                        "end_line_number": 35,
                        "end_column_number": 24
                    }
                ],
                "references": [],
                "is_builtin": false
            },
            {
                "id": "to_json",
                "defined_at": [
                    {
                        "start_line_number": 37,
                        "start_column_number": 4,
                        "end_line_number": 38,
                        "end_column_number": 41
                    }
                ],
                "references": [],
                "is_builtin": false
            },
            {
                "id": "global_func",
                "defined_at": [
                    {
                        "start_line_number": 5,
                        "start_column_number": 0,
                        "end_line_number": 6,
                        "end_column_number": 24
                    }
                ],
                "references": [
                    {
                        "start_line_number": 17,
                        "start_column_number": 14,
                        "end_line_number": 17,
                        "end_column_number": 25
                    }
                ],
                "is_builtin": false
            }
        ],
        "classes": [
            {
                "id": "Test",
                "defined_at": [
                    {
                        "start_line_number": 12,
                        "start_column_number": 0,
                        "end_line_number": 38,
                        "end_column_number": 41
                    }
                ],
                "references": [
                    {
                        "start_line_number": 41,
                        "start_column_number": 4,
                        "end_line_number": 41,
                        "end_column_number": 8
                    }
                ],
                "is_builtin": false
            }
        ],
        "variables": [
            {
                "id": "self",
                "defined_at": [
                    {
                        "start_line_number": 16,
                        "start_column_number": 4,
                        "end_line_number": 18,
                        "end_column_number": 19
                    }
                ],
                "references": [
                    {
                        "start_line_number": 18,
                        "start_column_number": 8,
                        "end_line_number": 18,
                        "end_column_number": 12
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "x",
                "defined_at": [
                    {
                        "start_line_number": 16,
                        "start_column_number": 4,
                        "end_line_number": 18,
                        "end_column_number": 19
                    }
                ],
                "references": [
                    {
                        "start_line_number": 18,
                        "start_column_number": 18,
                        "end_line_number": 18,
                        "end_column_number": 19
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "self",
                "defined_at": [
                    {
                        "start_line_number": 20,
                        "start_column_number": 4,
                        "end_line_number": 21,
                        "end_column_number": 29
                    }
                ],
                "references": [],
                "is_builtin": false
            },
            {
                "id": "self",
                "defined_at": [
                    {
                        "start_line_number": 24,
                        "start_column_number": 4,
                        "end_line_number": 27,
                        "end_column_number": 22
                    }
                ],
                "references": [
                    {
                        "start_line_number": 27,
                        "start_column_number": 15,
                        "end_line_number": 27,
                        "end_column_number": 19
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "self",
                "defined_at": [
                    {
                        "start_line_number": 29,
                        "start_column_number": 4,
                        "end_line_number": 31,
                        "end_column_number": 24
                    }
                ],
                "references": [
                    {
                        "start_line_number": 30,
                        "start_column_number": 50,
                        "end_line_number": 30,
                        "end_column_number": 54
                    },
                    {
                        "start_line_number": 30,
                        "start_column_number": 34,
                        "end_line_number": 30,
                        "end_column_number": 38
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "i",
                "defined_at": [
                    {
                        "start_line_number": 30,
                        "start_column_number": 12,
                        "end_line_number": 30,
                        "end_column_number": 13
                    }
                ],
                "references": [
                    {
                        "start_line_number": 31,
                        "start_column_number": 18,
                        "end_line_number": 31,
                        "end_column_number": 19
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "j",
                "defined_at": [
                    {
                        "start_line_number": 30,
                        "start_column_number": 15,
                        "end_line_number": 30,
                        "end_column_number": 16
                    }
                ],
                "references": [
                    {
                        "start_line_number": 31,
                        "start_column_number": 22,
                        "end_line_number": 31,
                        "end_column_number": 23
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "self",
                "defined_at": [
                    {
                        "start_line_number": 33,
                        "start_column_number": 4,
                        "end_line_number": 35,
                        "end_column_number": 24
                    }
                ],
                "references": [
                    {
                        "start_line_number": 34,
                        "start_column_number": 8,
                        "end_line_number": 34,
                        "end_column_number": 12
                    },
                    {
                        "start_line_number": 35,
                        "start_column_number": 8,
                        "end_line_number": 35,
                        "end_column_number": 12
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "self",
                "defined_at": [
                    {
                        "start_line_number": 37,
                        "start_column_number": 4,
                        "end_line_number": 38,
                        "end_column_number": 41
                    }
                ],
                "references": [
                    {
                        "start_line_number": 38,
                        "start_column_number": 32,
                        "end_line_number": 38,
                        "end_column_number": 36
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "_x",
                "defined_at": [
                    {
                        "start_line_number": 14,
                        "start_column_number": 4,
                        "end_line_number": 14,
                        "end_column_number": 6
                    }
                ],
                "references": [],
                "is_builtin": false
            },
            {
                "id": "z",
                "defined_at": [
                    {
                        "start_line_number": 9,
                        "start_column_number": 0,
                        "end_line_number": 9,
                        "end_column_number": 1
                    }
                ],
                "references": [
                    {
                        "start_line_number": 26,
                        "start_column_number": 8,
                        "end_line_number": 26,
                        "end_column_number": 9
                    }
                ],
                "is_builtin": false
            },
            {
                "id": "t",
                "defined_at": [
                    {
                        "start_line_number": 41,
                        "start_column_number": 0,
                        "end_line_number": 41,
                        "end_column_number": 1
                    }
                ],
                "references": [],
                "is_builtin": false
            }
        ],
        "assigned_self_members": [],
        "assigned_class_members": [],
        "undefined_references": [
            {
                "id": "u",
                "line_number": 26,
                "column_number": 12
            }
        ]
    },
    "metrics": {
        "raw": {
            "loc": 41,
            "lloc": 28,
            "sloc": 26,
            "comments": 0,
            "multi": 0,
            "single_comments": 0,
            "blank": 15
        },
        "halsted": {
            "h1": 1,
            "h2": 2,
            "N1": 1,
            "N2": 2,
            "calculated_length": 2.0,
            "volume": 4.754887502163469,
            "difficulty": 0.5,
            "effort": 2.3774437510817346,
            "time": 0.1320802083934297,
            "bugs": 0.0015849625007211565
        },
        "cyclomatic_complexity": {
            "score": 1.25,
            "rank": "A"
        },
        "maintainability_index": {
            "score": 64.22434870897446,
            "rank": "A"
        }
    }
}
```

It consists if the fields `error`, `analysis` and `metrics`.

#### `error`

This is `null` if no error occurred. If an error occurred this field contains a string describing the error. This can eiter be `syntax_error` if the parser detected invalid syntax or `value_error` if the code contains a null character. In case of a syntax error the position of the error inside the code is also returned. If an error occurred the `analysis` and `metrics` fields are not present.

#### `analysis`

##### `imports`

This are the symbols imported in the code snipped. This also contains all builtin symbols that were used in the snippet.

##### `functions`

This are the functions and methods defined in the code snippet.

##### `classes`

This are the classes defined in the code snippet.

##### `variables`

This are the variables defined in the code snippet.

##### `assigned_self_members`

This are the members of all `self` objects that a value was assigned to but only if that member was not defined in the class.

##### `assigned_class_members`

This are the members of all `cls` objects that a value was assigned to but only if that member was not defined in the class.

##### `undefined_references`

This are all references to symbols that were not defined in the code snippet.

Each of these fields contains a list of objects. Each object has the following fields:

##### `id`

This is the string representation of the symbol.

##### `defined_at`

This describes where the symbol was defined. It contains where the definition starts and where it ends. If it is a builtin symbol the positions are `null`. This field contains a list because a symbol could be defined in multiple places.

##### `references`

This describes where the symbol was referenced. It contains where the reference starts and where it ends. This field contains a list because a symbol can be referenced in multiple places.

##### `is_builtin`

This is a boolean that is `true` if the symbol is a builtin symbol.

#### `metrics`

##### `raw`

This contains purely text based metrics that are desribed in the follwing table:

|Metric|Description|
|------|-----------|
|`loc`|The amount of lines of code.|
|`lloc`|The amount of logical lines of code.|
|`sloc`|The amount of source lines of code.|
|`comments`|The amount of comments.|
|`multi`|The amount of multi line comments.|
|`single_comments`|The amount of single line comments.|
|`blank`|The amount of blank lines.|

##### `halsted`

This contains the Halsted metrics that are described in the follwing table:

|Metric|Description|
|------|-----------|
|`h1`|The amount of distinct operators.|
|`h2`|The amount of distinct operands.|
|`N1`|The total amount of operators.|
|`N2`|The total amount of operands.|
|`calculated_length`|The calculated length of the program. ($L=h_1\cdot log_2~h_1 + h_2\cdot log_2~h_2$)|
|`volume`|The volume of the program. ($V=N\cdot log_2~(h1 + h1)$)|
|`difficulty`|The difficulty of the program. ($D=\frac{h1}{2}\cdot \frac{N2}{h2}$)|
|`effort`|The effort of the program. ($E=V\cdot D$)|
|`time`|The time required to program the program. ($T=\frac{E}{18~s}$)|
|`bugs`|The amount of bugs in the program. ($B=\frac{V}{3000}$)|

##### `cyclomatic_complexity`

This contains the cyclomatic complexity metrics that are described in the follwing table:

|Metric|Description|
|------|-----------|
|`score`|The cyclomatic complexity score.|
|`rank`|The cyclomatic complexity rank. (A to F)|

##### `maintainability_index`

This contains the maintainability index metrics that are described in the follwing table:

|Metric|Description|
|------|-----------|
|`score`|The maintainability index score.|
|`rank`|The maintainability index rank. (A to C)|
