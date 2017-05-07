import collections
import os
from os.path import expanduser
import sys
from subprocess import Popen, PIPE
from functools import partial

import click
import dpath
import jinja2
import yaml
from libvcs.shortcuts import create_repo_from_pip_url

RenderedTemplate = collections.namedtuple('RenderedTemplate', ['slug', 'content'])


def merge_dicts(dicts):
    merged = {}
    for d in dicts:
        dpath.util.merge(merged, d)
    return merged


def should_render_template(template_path):
    filename = template_path.split('/')[-1]
    return not (filename.startswith('.') or filename.startswith('_'))


def render_templates(template_dir, working_dir, **context):
    loader = jinja2.FileSystemLoader([working_dir, template_dir])
    env = jinja2.Environment(loader=loader)
    env.filters['dump'] = lambda o: yaml.dump(o, default_flow_style=False)

    def render(filename):
        template = env.get_template(filename)

        rendered = template.render(yaml=yaml, **context)
        return RenderedTemplate(filename, rendered)
    return map(render, filter(should_render_template, os.listdir(template_dir)))


def load_yaml_file(path):
    with open(path) as f:
        return yaml.load(f.read())


def parse_overriden_vars(overriden_vars):
    def parse_statement(override_statement):
        key, value = override_statement.split('=')
        obj = {}
        dpath.util.new(obj, key, value, separator='.')
        return obj

    return list(map(parse_statement, overriden_vars))


def create_kubectl_apply_pipe():
    return Popen(['kubectl', 'apply', '-f', '-'], stdin=PIPE)


def call_kubectl_apply(template):
    if not (yaml.load(template.content) or {}).get('kind'):
        return
    pipe = create_kubectl_apply_pipe()
    pipe.communicate(template.content)


def update_templates(template_url, dump_dir):
    repo = create_repo_from_pip_url(pip_url=template_url, repo_dir=dump_dir)
    repo.update_repo()

def render(verbose, template_dir, should_apply, context_files, overriden_vars, template_url, working_dir):
    change_working_dir = partial(os.path.join, working_dir)
    context_data = map(load_yaml_file, map(change_working_dir, context_files))

    overriden_vars = parse_overriden_vars(overriden_vars)
    context = merge_dicts(context_data + overriden_vars)

    if template_url is not None:
        template_dir = os.path.join(expanduser("~"), '.kube-render/templates')
        update_templates(template_url, template_dir)
    else:
        template_dir = change_working_dir(template_dir)

    rendered_templates = render_templates(template_dir, working_dir, **context)

    if verbose:
        sys.stdout.write('### Computed variables:')
        sys.stdout.write(yaml.safe_dump(context, default_flow_style=False, indent=2))
        for t in rendered_templates:
            sys.stdout.write('\n### Rendered {}\n'.format(t.slug))
            sys.stdout.write(t.content)
            sys.stdout.write('\n')

    if should_apply:
        map(call_kubectl_apply, rendered_templates)
    return rendered_templates


@click.command()
@click.option('--verbose', '-v', default=False, is_flag=True, help='Whether it should print generated files or not')
@click.option('--context', '-c', 'context_files', help="Yaml file path to be loaded into context. Supports merging.", multiple=True)
@click.option('--set', '-s', 'overriden_vars', help="Vars that override context files. Format: key=value", multiple=True)
@click.option('--template-dir', '-t', default='templates', help='Folder holding templates that should be rendered')
@click.option('--template-url', '-u', default=None, help='URL to download templates from (writes on ~/.kube-render/templates). Accepts URLs on pip format')
@click.option('--apply', '-A', 'should_apply', default=False, is_flag=True, help="Apply rendered files using `kubectl apply`")
@click.option('--working-dir', '-w', default='.', help="Directory where jinja will find all files")
def run(verbose, template_dir, should_apply, context_files, overriden_vars, template_url, working_dir):
    return render(verbose, template_dir, should_apply, context_files, overriden_vars, template_url, working_dir)