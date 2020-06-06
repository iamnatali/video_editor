import unittest
from unittest import mock
import editor


red_start = "\x1b[31;40m"
red_end = "\x1b[0m"

frame1 = mock.Mock(spec=editor.Frame)


class Test(unittest.TestCase):

    @mock.patch.dict(editor.frame_dict, {'name2': "wow"})
    @mock.patch('editor.print')
    def test_adding(self, my_print):
        editor.adding_frame('name1', frame1, "CREATE", 'comment')
        my_print.assert_any_call(red_start+'CREATE'+red_end)
        my_print.assert_any_call('comment')

    @mock.patch.dict(editor.frame_dict, {'name2': "wow"})
    @mock.patch('editor.print')
    def test_wrong_adding(self, my_print):
        editor.adding_frame('name2', frame1, "CREATE", 'comment')
        my_print.assert_any_call(red_start + 'фрагмент с именем ' +
                                 'name2'+' уже существует, попробуйте снова' +
                                 red_end)
