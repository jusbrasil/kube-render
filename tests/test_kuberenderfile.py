import unittest

from kuberender.file import run
from mock import call, patch


class KubeRenderFileTestCase(unittest.TestCase):
    @patch('kuberender.render.run')
    def test_run(self, run_render):
        # prepare
        run_render.return_value = 0
        expected_calls = [
            call(
                context_files=['base.yaml'],
                overriden_vars={'kind': 'app1'},
                should_apply=False,
                template_dir='templates',
                verbose=True,
                working_dir='tests/resources'),
            call(
                context_files=['base.yaml', 'extended.yaml'],
                overriden_vars={'kind': 'app2'},
                should_apply=False,
                template_dir='templates',
                verbose=False,
                working_dir='tests/resources'),
        ]

        # run
        run('tests/resources/kr-file.yaml')
        # assert
        assert 2 == run_render.call_count
        run_render.assert_has_calls(expected_calls)
