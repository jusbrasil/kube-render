import collections
import os
import sys
from subprocess import Popen, PIPE

import click
import dpath
import jinja2
import yaml

RenderedTemplate = collections.namedtuple('RenderedTemplate', ['slug', 'content'])


def merge_dicts(dicts):
    merged = {}
    for d in dicts:
        dpath.util.merge(merged, d)
    return merged

def should_render_template(template_path):
    filename = template_path.split('/')[-1]
    return not (filename.startswith('.') or filename.startswith('_'))

def render_templates(template_dir, **context):
    loader = jinja2.FileSystemLoader('.')
    env = jinja2.Environment(loader=loader)
    env.filters['dump'] = lambda o: yaml.dump(o, default_flow_style=False)

    def render(filename):
        template = env.get_template(os.path.join(template_dir, filename))
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
        dpath.util.new(obj, key.replace('.', '/'), value)
        return obj

    return list(map(parse_statement, overriden_vars))


def create_kubectl_apply_pipe():
    return Popen(['kubectl', 'apply', '-f', '-'], stdin=PIPE)


def call_kubectl_apply(t):
    if not (yaml.load(t.content) or {}).get('kind'):
        sys.stdout.write('### {} is invalid. Ignoring..\n'.format(t.slug))
        return
    pipe = create_kubectl_apply_pipe()
    pipe.communicate(t.content)


@click.command()
@click.option('--verbose', '-v', default=False, is_flag=True, help='Whether it should print generated files or not')
@click.option('--context', '-c', 'context_files', help="Yaml file path to be loaded into context. Supports merging.", multiple=True)
@click.option('--set', '-s', 'overriden_vars', help="Vars that override context files. Format: key=value", multiple=True)
@click.option('--template-dir', '-t', default='templates', help='Folder holding templates that should be rendered')
@click.option('--apply', '-A', 'should_apply', default=False, is_flag=True, help="Apply rendered files using `kubectl apply`")
def run(verbose, template_dir, should_apply, context_files, overriden_vars):
    context_data = map(load_yaml_file, context_files)

    overriden_vars = parse_overriden_vars(overriden_vars)
    context = merge_dicts(context_data + overriden_vars)
    rendered_templates = render_templates(template_dir, **context)

    if verbose:
        sys.stdout.write('### Computed variables:')
        sys.stdout.write(yaml.safe_dump(context, default_flow_style=False, indent=2))
        for t in rendered_templates:
            sys.stdout.write('\n### Rendered {}\n'.format(t.slug))
            sys.stdout.write(t.content)
            sys.stdout.write('\n')

    if should_apply:
        map(call_kubectl_apply, rendered_templates)


if __name__ == '__main__':
    run()
