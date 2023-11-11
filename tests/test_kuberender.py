import unittest
from functools import partial

import yaml
from dpath.util import get as get_value
from mock import patch, Mock

from kuberender.render import render, run
from kuberender.utils import load_yaml_file


class KubeRenderTestCase(unittest.TestCase):

    def _pipe_mock(self, returncode=0):
        pipe = Mock()
        pipe.communicate.return_value = (b'output', None)
        pipe.wait.return_value = returncode
        return pipe

    def _partial_render(self, template_folder='test-basic-manifest'):
        return partial(
            render,
            verbose=False,
            template_dir=template_folder,
            should_apply=False,
            working_dir='tests/resources',
            template_url=None,
        )

    def _load_template_manifest(self, rendered_templates):
        assert 1 == len(rendered_templates)
        return yaml.load(rendered_templates[0].content)

    @patch('subprocess.Popen')
    def test_applying_multiple_deploy_in_same_file(self, popen_mock):
        context_files = ('base.yaml', 'extended.yaml')

        popen_mock.side_effect = processes = [self._pipe_mock(), self._pipe_mock()]
        assert run(
            template_dir='test-multi-file-manifest',
            should_apply=True,
            context_files=context_files,
            working_dir='tests/resources'
        ) == 0

        assert popen_mock.call_count == 2

        first_deploy_content = yaml.load(processes[0].communicate.call_args[0][0])
        assert first_deploy_content['metadata']['name'] == 'redis-news-page-cache'

        second_deploy_content = yaml.load(processes[1].communicate.call_args[0][0])
        assert second_deploy_content['metadata']['name'] == 'redis-news-page-cache-2'

    def test_generate_files(self):
        context_files = ('base.yaml', 'extended.yaml')

        assert run(
            template_dir='test-basic-manifest',
            generate_files=True,
            context_files=context_files,
            working_dir='tests/resources'
        ) == 0

        deploy_content = load_yaml_file('generated/deployment.yaml')
        assert deploy_content['metadata']['name'] == 'redis-news-page-cache'

    @patch('subprocess.Popen')
    def test_return_first_non_zero_exit_code_on_failure(self, popen_mock):
        context_files = ('base.yaml', 'extended.yaml')

        popen_mock.side_effect = processes = [self._pipe_mock(1), self._pipe_mock()]
        assert run(
            template_dir='test-multi-file-manifest',
            should_apply=True,
            context_files=context_files,
            working_dir='tests/resources'
        ) == 1

        assert popen_mock.call_count == 1

        first_deploy_content = yaml.load(processes[0].communicate.call_args[0][0])
        assert first_deploy_content['metadata']['name'] == 'redis-news-page-cache'

    @patch('subprocess.Popen')
    def test_applying_empty_dir_template(self, popen_mock):
        context_files = ('base.yaml', 'extended.yaml')

        popen_mock.side_effect = []
        assert run(
            template_dir='test-empty-dir',
            should_apply=True,
            context_files=context_files,
            working_dir='tests/resources'
        ) == 0

        assert popen_mock.call_count == 0

    def test_merging_context_values(self):
        context_files = ('base.yaml',)
        manifest = self._load_template_manifest(self._partial_render()(
            context_files=context_files,
            overriden_vars=[]
        ))
        assert '32M' == get_value(manifest, 'spec/template/spec/containers/0/resources/limits/memory')
        assert 0.3 == get_value(manifest, 'spec/template/spec/containers/0/resources/limits/cpu')

        context_files = ('base.yaml', 'extended.yaml')
        manifest = self._load_template_manifest(self._partial_render()(
            context_files=context_files,
            overriden_vars=[]
        ))
        # Memory got overriden, but it preserved sibling keys (cpu)
        assert '64M' == get_value(manifest, 'spec/template/spec/containers/0/resources/limits/memory')
        assert 0.3 == get_value(manifest, 'spec/template/spec/containers/0/resources/limits/cpu')

    def test_overriding_vars(self):
        manifest = self._load_template_manifest(self._partial_render()(
            context_files=['base.yaml'],
            overriden_vars=[]
        ))
        assert 'redis:latest' == get_value(manifest, 'spec/template/spec/containers/0/image')
        assert 'Always' == get_value(manifest, 'spec/template/spec/containers/0/imagePullPolicy')

        manifest = self._load_template_manifest(self._partial_render()(
            context_files=['base.yaml'],
            overriden_vars=['image.tag=3.0.7', 'image.repository=bitnami/redis', 'other.key=test=']
        ))

        # Image and tag were overriden but pullPolicy (which is a sibling) wasn't modified
        assert 'bitnami/redis:3.0.7' == get_value(manifest, 'spec/template/spec/containers/0/image')
        assert 'Always' == get_value(manifest, 'spec/template/spec/containers/0/imagePullPolicy')

    def test_overriding_vars_with_eq(self):
        manifest = self._load_template_manifest(self._partial_render()(
            context_files=['base.yaml'],
            overriden_vars=[]
        ))
        assert 'redis:latest' == get_value(manifest, 'spec/template/spec/containers/0/image')
        assert 'Always' == get_value(manifest, 'spec/template/spec/containers/0/imagePullPolicy')

        manifest = self._load_template_manifest(self._partial_render()(
            context_files=['base.yaml'],
            overriden_vars=['image.tag=3.0.7', 'image.repository=bitnami/redis', 'image.pullPolicy=test=']
        ))

        # Image and tag were overriden but pullPolicy (which is a sibling) wasn't modified
        assert 'bitnami/redis:3.0.7' == get_value(manifest, 'spec/template/spec/containers/0/image')
        assert 'test=' == get_value(manifest, 'spec/template/spec/containers/0/imagePullPolicy')


if __name__ == '__main__':
    unittest.main()
