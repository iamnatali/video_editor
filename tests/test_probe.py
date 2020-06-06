import unittest
from unittest import mock
import editor
import pathlib

red_start = "\x1b[31;40m"
red_end = "\x1b[0m"
test_dict1 = {}
test_dict2 = {'name1': ''}
stream_mock = mock.Mock()
stream_mock.video = 'video'
stream_mock.audio = 'audio'


class Test(unittest.TestCase):

    def setUp(self):
        global test_dict1
        test_dict1 = {}

    @mock.patch.dict(editor.frame_dict, test_dict1)
    @mock.patch('ffmpeg.input', return_value=stream_mock)
    @mock.patch('editor.probe', return_value=(100, 100, 20))
    @mock.patch('editor.path_is_correct', return_value=True)
    def test_load(self, inp, pr, cor):
        print(editor.frame_dict)
        with mock.patch('editor.print') as my_print:
            editor.load('some/path', 'name1')
            my_print.assert_any_call(red_start + "CREATE" + red_end)

    @mock.patch.dict(editor.frame_dict, test_dict2)
    @mock.patch('ffmpeg.input', return_value=stream_mock)
    @mock.patch('editor.probe', return_value=(100, 100, 20))
    @mock.patch('editor.path_is_correct', return_value=True)
    def test_load_twice(self, inp, pr, cor):
        print("DICT")
        print(editor.frame_dict)
        with mock.patch('editor.print') as my_print:
            editor.load('some/path', 'name1')
            my_print.assert_any_call(red_start +
                                     'фрагмент с именем ' +
                                     'name1' +
                                     ' уже существует, попробуйте снова' +
                                     red_end)

    def test_probe(self):
        pre_path = pathlib.Path('.').absolute()
        if pre_path.name == 'tests':
            pre_path = pre_path.parent
        pr_res = editor.probe(pre_path/'barbara.mp4')
        self.assertEqual(pr_res, (1280, 720, '99.845800'))
