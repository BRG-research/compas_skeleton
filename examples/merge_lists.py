import compas
from compas.datastructures import Mesh
from compas.utilities import flatten
# from compas_rhino.artists import MeshArtist
# list1 = [[[0, 1], [2, 3]], [[0, 1], [2, 3]]]
# # list1 = [[0, 1], [2, 3]]
# print(list(flatten(list(flatten(list1)))))

list1 = [
    ['w', 'u'],
    ['y', 'v', 'z'],
    ['u', 'v', 'w', 'x'],
    ['v', 'u', 'y'],
    ['x', 'u'],
    ['a', 'b'],
    ['b', 'a'],
]

def _merge_lists(list_origion):
    seen = []
    merged = []
    for n in list_origion:
        if n in seen:
            continue
        for m in list_origion[1:]:
            if m in seen:
                continue
            if set(n) & set(m):
                n = list(set(n) | set(m))
                seen.append(m)

        merged.append(n)
    return merged

def merge_lists(list_origion):
    """ merge all lists which have intersection.
    
    Attributes
    ----------
    list_origion : a list of lists

    Return
    --------
    list : a list of merged lists

    Examples
    --------
    >>> from compas.utilities import flatten
    >>>
    >>> example_list = [
    >>> ['b', 'a'],
    >>> ['w', 'u'],
    >>> ['y', 'v', 'z'],
    >>> ['u', 'v', 'w', 'x'],
    >>> ['v', 'u', 'y'],
    >>> ['x', 'u'],
    >>> ['a', 'b'],
    >>> ]
    >>> merge_lists(example_list)
    >>> [['b', 'a'], ['y', 'x', 'z', 'u', 'w', 'v']]
    """

    target_len = len(list(set(flatten(list_origion))))
    merged = list_origion
    result_len = len(list(flatten(merged)))

    while result_len <> target_len:
        merged = _merge_lists(merged)
        result_len = len(list(flatten(merged)))

    return merged

merged = merge_lists(list1)
print(merged)
