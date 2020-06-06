import unittest
from unittest import mock
import editor
import pathlib


class Test(unittest.TestCase):

    def test_not_correct(self):
        with mock.patch('editor.print') as my_print:
            red_start = "\x1b[31;40m"
            red_end = "\x1b[0m"
            res = editor.path_is_correct('asdfghjkl', False, '.mp4')
            self.assertEqual(res, False)
            my_print.assert_any_call(
                red_start+'пожалуйста, попытайтесь снова'+red_end)

    def test_correct(self):
        pre_path = pathlib.Path('.').absolute()
        if pre_path.name == 'tests':
            pre_path = pre_path.parent
        res = editor.path_is_correct(pre_path/'barbara.mp4', False, '.mp4')
        self.assertEqual(res, True)

    @mock.patch('editor.print')
    def test_extention(self, my_print):
        red_start = "\x1b[31;40m"
        red_end = "\x1b[0m"
        pre_path = pathlib.Path('.').absolute()
        if pre_path.name == 'tests':
            pre_path = pre_path.parent
        res = editor.path_is_correct(
            pre_path/'requirements.txt', False, '.srt')
        self.assertEqual(res, False)
        my_print.assert_any_call(
            red_start+'расширение должно быть .srt'+red_end)
