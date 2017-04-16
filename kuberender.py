import collections
import os
import shutil
import sys
import tempfile
from subprocess import call

import click
import dpath
import jinja2
import yaml

RenderedTemplate = collections.namedtuple('RenderedTemplate', ['slug', 'content'])


def save_rendered_templates(rendered_templates, output_dir):
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)
    for t in rendered_templates:
        with tempfile.NamedTemporaryFile(prefix='rendered', suffix=t.slug, dir=output_dir, delete=False) as temp:
            temp.write(t.content)
            temp.flush()


def merge_dicts(dicts):
    merged = {}
    for d in dicts:
        dpath.util.merge(merged, d)
    return merged


def render_templates(template_dir, **context):
    loader = jinja2.FileSystemLoader('.')
    env = jinja2.Environment(loader=loader)
    return map(
        lambda filename: RenderedTemplate(
            filename,
            env.get_template(os.path.join(template_dir, filename)).render(
                yaml=yaml,
                **context)),
        os.listdir(template_dir)
    )


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


@click.command()
@click.option('--verbose', '-v', default=False, is_flag=True, help='Whether it should print generated files or not')
@click.option('--context', '-c', 'context_files', help="Yaml file path to be loaded into context. Supports merging.", multiple=True)
@click.option('--set', '-s', 'overriden_vars', help="Vars that override context files. Format: key=value", multiple=True)
@click.option('--template-dir', '-t', default='templates', help='Folder holding templates that should be rendered')
@click.option('--output-dir', '-o', default='gen', help='Folder that rendered templates should be put in')
@click.option('--no-save', default=False, is_flag=True, help="Only prints templates. Doesn't create files")
@click.option('--apply', '-A', 'should_apply', default=False, is_flag=True, help="Apply rendered files using `kubectl apply`")
def run(verbose, template_dir, no_save, should_apply, context_files, output_dir, overriden_vars):
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

    if not no_save:
        save_rendered_templates(rendered_templates, output_dir)
        if should_apply:
            call(['kubectl', 'apply', '-f', output_dir])


if __name__ == '__main__':
    run()
