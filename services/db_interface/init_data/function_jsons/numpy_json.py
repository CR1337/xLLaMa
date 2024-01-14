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
        info["name"] = "numpy." + match.group(1)
        info["url"] = f"https://numpy.org/doc/stable/reference/generated/{info['name']}.html"

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
@array_function_dispatch(_digitize_dispatcher)
def digitize(x, bins, right=False):
    
    x = _nx.asarray(x)
    bins = _nx.asarray(bins)

    # here for compatibility, searchsorted below is happy to take this
    if np.issubdtype(x.dtype, _nx.complexfloating):
        raise TypeError("x may not be complex")

    mono = _monotonicity(bins)
    if mono == 0:
        raise ValueError("bins must be monotonically increasing or decreasing")

    # this is backwards because the arguments below are swapped
    side = 'left' if right else 'right'
    if mono == -1:
        # reverse the bins, and invert the results
        return len(bins) - _nx.searchsorted(bins[::-1], x, side=side)
    else:
        return _nx.searchsorted(bins, x, side=side)
"""

doc_str = """
    Return the indices of the bins to which each value in input array belongs.

    =========  =============  ============================
    `right`    order of bins  returned index `i` satisfies
    =========  =============  ============================
    ``False``  increasing     ``bins[i-1] <= x < bins[i]``
    ``True``   increasing     ``bins[i-1] < x <= bins[i]``
    ``False``  decreasing     ``bins[i-1] > x >= bins[i]``
    ``True``   decreasing     ``bins[i-1] >= x > bins[i]``
    =========  =============  ============================

    If values in `x` are beyond the bounds of `bins`, 0 or ``len(bins)`` is
    returned as appropriate.

    Parameters
    ----------
    x : array_like
        Input array to be binned. Prior to NumPy 1.10.0, this array had to
        be 1-dimensional, but can now have any shape.
    bins : array_like
        Array of bins. It has to be 1-dimensional and monotonic.
    right : bool, optional
        Indicating whether the intervals include the right or the left bin
        edge. Default behavior is (right==False) indicating that the interval
        does not include the right edge. The left bin end is open in this
        case, i.e., bins[i-1] <= x < bins[i] is the default behavior for
        monotonically increasing bins.

    Returns
    -------
    indices : ndarray of ints
        Output array of indices, of same shape as `x`.

    Raises
    ------
    ValueError
        If `bins` is not monotonic.
    TypeError
        If the type of the input is complex.

    See Also
    --------
    bincount, histogram, unique, searchsorted

    Notes
    -----
    If values in `x` are such that they fall outside the bin range,
    attempting to index `bins` with the indices that `digitize` returns
    will result in an IndexError.

    .. versionadded:: 1.10.0

    `np.digitize` is  implemented in terms of `np.searchsorted`. This means
    that a binary search is used to bin the values, which scales much better
    for larger number of bins than the previous linear search. It also removes
    the requirement for the input array to be 1-dimensional.

    For monotonically _increasing_ `bins`, the following are equivalent::

        np.digitize(x, bins, right=True)
        np.searchsorted(bins, x, side='left')

    Note that as the order of the arguments are reversed, the side must be too.
    The `searchsorted` call is marginally faster, as it does not do any
    monotonicity checks. Perhaps more importantly, it supports all dtypes.

    Examples
    --------
    >>> x = np.array([0.2, 6.4, 3.0, 1.6])
    >>> bins = np.array([0.0, 1.0, 2.5, 4.0, 10.0])
    >>> inds = np.digitize(x, bins)
    >>> inds
    array([1, 4, 3, 2])
    >>> for n in range(x.size):
    ...   print(bins[inds[n]-1], "<=", x[n], "<", bins[inds[n]])
    ...
    0.0 <= 0.2 < 1.0
    4.0 <= 6.4 < 10.0
    2.5 <= 3.0 < 4.0
    1.0 <= 1.6 < 2.5

    >>> x = np.array([1.2, 10.0, 12.4, 15.5, 20.])
    >>> bins = np.array([0, 5, 10, 15, 20])
    >>> np.digitize(x,bins,right=True)
    array([1, 2, 3, 4, 4])
    >>> np.digitize(x,bins,right=False)
    array([1, 3, 3, 4, 5])
    """

# Extracting information
function_info = extract_function_info(func_str, doc_str)

# Appending to the existing JSON file
json_filename = "numpy_info.json"
append_to_json_file(function_info, json_filename)
print(f"Information appended to '{json_filename}' successfully.")
