import unittest
from unittest import mock
import editor
import pathlib

f1 = mock.Mock(spec=editor.Frame)
f1.video = 'v1'
f1.audio = 'a1'
f2 = mock.Mock(spec=editor.Frame)
f2.video = 'v2'
f2.audio = 'a2'
d = {'main': f1, 'add': f2}
pre_path = pathlib.Path('.').absolute()
if pre_path.name == 'tests':
    pre_path = pre_path.parent
pre_path = pre_path/'barbara.mp4'
red_start = "\x1b[31;40m"
red_end = "\x1b[0m"


class Test(unittest.TestCase):

    @mock.patch.dict(editor.frame_dict, d)
    @mock.patch('ffmpeg.overlay')
    @mock.patch('editor.get_res_frame')
    @mock.patch('editor.adding_frame')
    def test_insert_prep(self, ad, get, over):
        args = mock.Mock()
        args.insert_vid = ['result', 'main', 'add', '30', '30']
        editor.insert_vid_preparations(args, 'main')

    @mock.patch.dict(editor.frame_dict, d)
    @mock.patch('ffmpeg.overlay')
    @mock.patch('editor.get_res_frame')
    @mock.patch('editor.adding_frame')
    @mock.patch('editor.print')
    def test_insert_wrong(self, pr, ad, get, over):
        args = mock.Mock()
        args.insert_vid = ['result', 'main', 'add', 'aaa', '30']
        editor.insert_vid_preparations(args, 'main')
        pr.assert_any_call('координаты должны быть числами больше 0')

    @mock.patch.dict(editor.frame_dict, d)
    @mock.patch('ffmpeg.overlay')
    @mock.patch('ffmpeg.input')
    @mock.patch('editor.get_res_frame')
    @mock.patch('editor.adding_frame')
    def test_insert_pic(self, ad, get, inp, over):
        args = mock.Mock()
        args.insert = ['result', 'main', str(pre_path.absolute()), '30', '30']
        editor.insert_preparations(args)

    @mock.patch.dict(editor.frame_dict, d)
    @mock.patch('ffmpeg.overlay')
    @mock.patch('ffmpeg.input')
    @mock.patch('editor.get_res_frame')
    @mock.patch('editor.adding_frame')
    @mock.patch('editor.print')
    def test_insert_wrong_pic(self, pr, ad, get, inp, over):
        args = mock.Mock()
        args.insert = ['result', 'main', 'qwertyuioasdfghja', '30', '30']
        editor.insert_preparations(args)
        pr.assert_any_call(red_start+'пожалуйста, попытайтесь снова'+red_end)
