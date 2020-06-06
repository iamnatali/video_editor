import unittest
from unittest import mock
import editor
import pathlib
import parameterized

red_start = "\x1b[31;40m"
red_end = "\x1b[0m"
test_dict = {'name1': 'frame1'}


class Test(unittest.TestCase):

    @parameterized.parameterized.expand([
        parameterized.param(int, '10', True),
        parameterized.param(int, 'er', False),
        parameterized.param(int, '4.5', False),
        parameterized.param(float, 'er', False),
        parameterized.param(float, '4.5', True),
        parameterized.param(float, '-4.5', False)
    ])
    def test_one(self, f, coords, result):
        res = editor.check_coord(f, 'error', coords)
        self.assertEqual(res[0], result)

    @parameterized.parameterized.expand([
        parameterized.param(float, ['6.2', '4'], True),
        parameterized.param(float, ['1.3', '0.03', '8', '10'], True),
        parameterized.param(float, ['ow', '3'], False)
    ])
    def test_params(self, f, coords, result):
        res = editor.check_coord(f, 'error', *coords)
        self.assertEqual(res[0], result)
