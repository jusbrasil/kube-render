import unittest
from functools import partial

import yaml
from dpath.util import get as get_value
from kuberender.render import render


class KubeRenderTestCase(unittest.TestCase):

    def _partial_render(self):
        return partial(
            render,
            verbose=False,
            template_dir='templates',
            should_apply=False,
            working_dir='tests/resources',
            template_url=None,
        )

    def _load_template_manifest(self, rendered_templates):
        assert 1 == len(rendered_templates)
        return yaml.load(rendered_templates[0].content)

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
            overriden_vars=['image.tag=3.0.7', 'image.repository=bitnami/redis']
        ))

        # Image and tag were overriden but pullPolicy (which is a sibling) wasn't modified
        assert 'bitnami/redis:3.0.7' == get_value(manifest, 'spec/template/spec/containers/0/image')
        assert 'Always' == get_value(manifest, 'spec/template/spec/containers/0/imagePullPolicy')


if __name__ == '__main__':
    unittest.main()
