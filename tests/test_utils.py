from kuberender.utils import merge_dicts, make_template_path
from os.path import expanduser


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


def test_make_template_path():
    user_home = expanduser("~")

    dir1 = make_template_path("git+ssh://git@github.com/jusbrasil/kube-templates.git"
                               "@e0f515433973a0a3bd49f6baa7d47da1bf092728")
    assert dir1 == user_home + "/.kube-render/templates/jusbrasil/kube-templates.git" \
                               "@e0f515433973a0a3bd49f6baa7d47da1bf092728"

    dir2 = make_template_path("git+https://github.com/jusbrasil/somerepo.git")
    assert dir2 == user_home + "/.kube-render/templates/jusbrasil/somerepo.git"

    dir3 = make_template_path("git+git@bitbucket.org:jusbrasil/templates.git@mybranch")
    assert dir3 == user_home + "/.kube-render/templates/jusbrasil/templates.git@mybranch"
