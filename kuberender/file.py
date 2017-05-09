from os import path
import sys

from . import render
from .utils import load_yaml_file, merge_dicts


def fix_keys(d):
    return dict((k.replace('-', '_'), v) for (k, v) in d.items())


def configure_working_dir(filename, base_config):
    dirname = path.dirname(filename)
    base_config['working-dir'] = dirname
    return base_config


def run(filename, verbose=False):
    content = load_yaml_file(filename)
    base_config = content.get('base', {})
    base_config = configure_working_dir(filename, base_config)
    all_renders = content.get('renders', [])
    return_codes = set()
    for r in all_renders:
        parameters = merge_dicts([dict(base_config), r])
        parameters = fix_keys(parameters)
        if verbose:
            sys.stdout.write('\n\n### RENDERING FIRST ###\n')
        return_code = render.run(**parameters)
        return_codes.add(return_code)
    return all(return_codes)
