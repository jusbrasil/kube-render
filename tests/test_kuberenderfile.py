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
        assert run('tests/resources/kr-file.yaml') == 0
        # assert
        assert 2 == run_render.call_count
        run_render.assert_has_calls(expected_calls)

    @patch('kuberender.render.run')
    def test_run_return_first_non_zero_exit_code(self, run_render):
        # prepare
        run_render.return_value = 1
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
        assert run('tests/resources/kr-file.yaml') == 1
        # assert
        assert 1 == run_render.call_count
        run_render.assert_has_calls([expected_calls[0]])
