from kuberender.utils import merge_dicts


# https://github.com/akesterson/dpath-python/issues/59
def test_dpath_merge_infinite_loop_bug():
    src = {"l": [1]}
    p1 = {"l": [2], "v": 1}
    p2 = {"v": 2}
    dst1 = {}

    dst1 = merge_dicts([src, p1])
    dst2 = merge_dicts([src, p2])
    dst3 = merge_dicts([src, p2])

    assert dst1["l"] == [1, 2]
    assert dst2["l"] == [1]
    assert dst3["l"] == [1]


# https://github.com/akesterson/dpath-python/issues/58
def test_dpath_merge_side_effect_bug():
    src = {"l": [1]}
    p1 = {"l": [2], "v": 1}
    p2 = {"v": 2}

    dst1 = merge_dicts([src, p1])
    dst2 = merge_dicts([src, p2])

    assert dst1["l"] == [1, 2]
    assert dst2["l"] == [1]
