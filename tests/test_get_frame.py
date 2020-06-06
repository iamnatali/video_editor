import unittest
from unittest import mock
import editor

red_start = "\x1b[31;40m"
red_end = "\x1b[0m"
test_dict = {'name1': 'frame1'}


class Test(unittest.TestCase):

    @mock.patch.dict(editor.frame_dict, test_dict)
    def test_get(self):
        fr = editor.get_frame_from_dict('name1')
        self.assertEqual(fr, 'frame1')

    def test_cancel(self):
        fr = editor.get_frame_from_dict('cancel')
        self.assertEqual(fr, 'cancel')

    @mock.patch('editor.input', return_value='exit')
    @mock.patch('editor.print')
    def test_no(self, my_print, inp):
        fr = editor.get_frame_from_dict('name2')
        my_print.assert_any_call(red_start +
                                 'фрагмента с именем ' + 'name2' +
                                 ' не существует' + red_end)
