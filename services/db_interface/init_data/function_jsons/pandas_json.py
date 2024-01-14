import json
import re

def extract_function_info(func_str, doc_str):
    info = {
        "name": "",
        "url": "",
        "description": "",
        "source": ""
    }

    # Extracting name and url using regular expressions
    match = re.search(r'def\s+(\w+)\s*\(', func_str)
    if match:
        info["name"] = "DataFrame." + match.group(1)
        info["url"] = f"https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.{info['name']}.html"

    # Extracting docstring
    docstring = doc_str.strip()

    # Extracting source code (outside of docstring)
    source_code = func_str.strip()

    info["source"] = source_code

    # Splitting docstring into lines
    lines = [line.strip() for line in docstring.split('\n')]
    info["description"] = ' '.join(lines)

    return info

def append_to_json_file(info, filename):
    try:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = []

    data.append(info)

    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Given function string
func_str = """
def pop(self, item: Hashable) -> Series:
        
        return super().pop(item=item)

"""

doc_str = """
        Return item and drop from frame. Raise KeyError if not found.

        Parameters
        ----------
        item : label
            Label of column to be popped.

        Returns
        -------
        Series

        Examples
        --------
        >>> df = pd.DataFrame([('falcon', 'bird', 389.0),
        ...                    ('parrot', 'bird', 24.0),
        ...                    ('lion', 'mammal', 80.5),
        ...                    ('monkey', 'mammal', np.nan)],
        ...                   columns=('name', 'class', 'max_speed'))
        >>> df
             name   class  max_speed
        0  falcon    bird      389.0
        1  parrot    bird       24.0
        2    lion  mammal       80.5
        3  monkey  mammal        NaN

        >>> df.pop('class')
        0      bird
        1      bird
        2    mammal
        3    mammal
        Name: class, dtype: object

        >>> df
             name  max_speed
        0  falcon      389.0
        1  parrot       24.0
        2    lion       80.5
        3  monkey        NaN
        """



# Extracting information
function_info = extract_function_info(func_str, doc_str)

# Appending to the existing JSON file
json_filename = "pandas_info.json"
append_to_json_file(function_info, json_filename)
print(f"Information appended to '{json_filename}' successfully.")
