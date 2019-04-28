from os import path
import sys

from . import render
from .utils import load_yaml_file, merge_dicts


def fix_keys(d):
    return dict((k.replace('-', '_'), v) for (k, v) in d.items())


def configure_working_dir(filename, base_config):
    dirname = path.dirname(filename)
    if not dirname:
        dirname = '.'
    base_config['working-dir'] = dirname
    return base_config


def ensure_apply_by_default(parameters):
    if 'should_apply' not in parameters:
        parameters['should_apply'] = True
    return parameters


def run(filename, verbose=False):
    content = load_yaml_file(filename)
    base_config = content.get('base', {})
    base_config = configure_working_dir(filename, base_config)
    all_renders = content.get('renders', [])
    for r in all_renders:
        parameters = merge_dicts([dict(base_config), r])
        parameters = fix_keys(parameters)
        parameters = ensure_apply_by_default(parameters)
        if verbose:
            parameters['verbose'] = True
            sys.stdout.write('\n\n### RENDERING FIRST ###\n')
            sys.stdout.write(str(parameters) + '\n')
        return_code = render.run(**parameters)
        if return_code != 0:
            return return_code
    return 0
