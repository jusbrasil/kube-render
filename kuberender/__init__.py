from kuberender import render
from kuberender import file
import click


@click.command()
@click.option('--verbose', '-v', default=False, is_flag=True, help='Whether it should print generated files or not')
@click.option('--context', '-c', 'context_files', help="Yaml file path to be loaded into context. Supports merging.", multiple=True)
@click.option('--set', '-s', 'overriden_vars', help="Vars that override context files. Format: key=value", multiple=True)
@click.option('--template-dir', '-t', default='templates', help='Folder holding templates that should be rendered')
@click.option('--template-url', '-u', default=None, help='URL to download templates from (writes on ~/.kube-render/templates). Accepts URLs on pip format')
@click.option('--apply', '-A', 'should_apply', default=False, is_flag=True, help="Apply rendered files using `kubectl apply`")
@click.option('--working-dir', '-w', default='.', help="Base directory for loading templates and context files")
def cli_render(verbose, template_dir, should_apply, context_files, overriden_vars, template_url, working_dir):
    return_code = render.run(verbose, template_dir, should_apply, context_files, overriden_vars, template_url, working_dir)
    exit(return_code)


@click.command()
@click.option('--verbose', '-v', default=False, is_flag=True, help='Whether it should print generated files or not')
@click.argument('filename')
def cli_file(verbose, filename):
    return_code = file.run(filename, verbose)
    exit(return_code)
