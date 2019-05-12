import collections
import os
import subprocess
import sys
from functools import partial
from subprocess import CalledProcessError

import dpath
import jinja2
import yaml
from libvcs.shortcuts import create_repo_from_pip_url

from .utils import load_yaml_file, make_template_path, merge_dicts

RenderedTemplate = collections.namedtuple('RenderedTemplate', ['slug', 'content'])


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


def parse_overriden_vars(overriden_vars):
    def parse_statement(override_statement):
        key, value = override_statement.split('=')
        obj = {}
        dpath.util.new(obj, key, value, separator='.')
        return obj

    if isinstance(overriden_vars, dict):
        return [overriden_vars]
    return list(map(parse_statement, overriden_vars))


def update_templates(template_url, dump_dir):
    repo = create_repo_from_pip_url(pip_url=template_url, repo_dir=dump_dir)
    repo.update_repo()


def render(verbose, template_dir, should_apply, context_files, overriden_vars, template_url, working_dir):
    change_working_dir = partial(os.path.join, working_dir)
    context_data = map(load_yaml_file, map(change_working_dir, context_files))

    overriden_vars = parse_overriden_vars(overriden_vars)
    context = merge_dicts(list(context_data) + list(overriden_vars))

    if template_url is not None:
        template_dir = make_template_path(template_url)
        update_templates(template_url, template_dir)
    else:
        template_dir = change_working_dir(template_dir)

    rendered_templates = render_templates(template_dir, working_dir, **context)

    if verbose:
        sys.stdout.write('### Computed context:\n')
        sys.stdout.write(yaml.safe_dump(context, default_flow_style=False, indent=2))
        for t in rendered_templates:
            sys.stdout.write('\n### Rendered {}\n'.format(t.slug))
            sys.stdout.write(t.content)
            sys.stdout.write('\n')
    return rendered_templates


def create_kubectl_apply_pipe():
    return subprocess.Popen(
        ['kubectl', 'apply', '-f', '-'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )


def call_kubectl_apply(template):
    def apply_template(content):
        pipe = create_kubectl_apply_pipe()
        str_content = yaml.safe_dump(content, default_flow_style=False, indent=2)
        output, _ = pipe.communicate(str_content)
        sys.stdout.write(output)
        return_code = abs(pipe.wait())
        if return_code != 0:
            raise CalledProcessError(return_code, pipe.args)
    for t in yaml.load_all(template.content):
        apply_template(t)


def apply_templates(rendered_templates):
    for t in rendered_templates:
        call_kubectl_apply(t)


def run(verbose=False, template_dir='templates', should_apply=False, context_files=None, overriden_vars=None, template_url=None, working_dir='.'):
    context_files = context_files or []
    overriden_vars = overriden_vars or {}
    return_code = 0
    rendered_templates = render(verbose, template_dir, should_apply, context_files, overriden_vars, template_url, working_dir)
    if should_apply:
        try:
            apply_templates(rendered_templates)
        except CalledProcessError as e:
            return_code = e.returncode
    return return_code
