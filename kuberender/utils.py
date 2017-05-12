import yaml
import os
from os.path import expanduser
from urlparse import urlparse


def load_yaml_file(path):
    with open(path) as f:
        return yaml.load(f.read())


def merge_dicts(dicts):
    merged = {}
    for d in dicts:
        merged = deep_merge(merged, d, always_concat_list=True)
    return merged


def deep_merge(lhs, rhs, always_concat_list=False):
    def merge_values(k, v_lhs, v_rhs):
        if isinstance(v_lhs, dict) and isinstance(v_rhs, dict):
            return k, deep_merge(v_lhs, v_rhs, always_concat_list)
        elif isinstance(v_lhs, list) and isinstance(v_rhs, list):
            if always_concat_list:
                return k, v_lhs + v_rhs
            else:
                return k, v_rhs
        else:
            return k, v_rhs

    lhs_keys = set(lhs.keys())
    rhs_keys = set(rhs.keys())

    pairs = [merge_values(k, lhs[k], rhs[k]) for k in lhs_keys & rhs_keys] \
        + [(k, lhs[k]) for k in lhs_keys - rhs_keys] \
        + [(k, rhs[k]) for k in rhs_keys - lhs_keys]
    return dict(pairs)


def create_template_dir(repo_url):
    path = urlparse(repo_url).path[1:]
    template_dir = os.path.join(expanduser("~"), '.kube-render/templates', path)
    return template_dir
