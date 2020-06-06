import unittest
from unittest import mock
import editor


red_start = "\x1b[31;40m"
red_end = "\x1b[0m"
frame = mock.Mock(spec=editor.Frame)
frame.video = 'video'
frame.audio = 'audio'


class Test(unittest.TestCase):

    def setUp(self):
        self.d = {}

    @mock.patch('editor.get_frame_from_dict', return_value='frame')
    def test_analyze(self, get):
        func = mock.Mock(side_effect=str.upper)
        editor.analyze_frame('name1', func)
        func.assert_any_call('frame')

    @mock.patch('editor.get_frame_from_dict', return_value='exit')
    def test_exit(self, get):
        func = mock.Mock(side_effect=str.upper)
        res = editor.analyze_frame('name1', func)
        self.assertEqual(res, 'exit')

    @mock.patch('editor.get_frame_from_dict', return_value='cancel')
    def test_cancel(self, get):
        func = mock.Mock(side_effect=str.upper)
        res = editor.analyze_frame('name1', func)
        self.assertEqual(res, None)

    @mock.patch('editor.get_frame_from_dict', return_value=frame)
    @mock.patch('ffmpeg.output', return_value='stream')
    @mock.patch('ffmpeg.run')
    def test_write_result(self, run, out, get):
        editor.write_result('name1', 'some/path')
        get.assert_any_call('name1')
        out.assert_any_call('video', 'audio', 'some/path')
        run.assert_any_call('stream')

    @mock.patch('ffmpeg.filter', return_value='new_video')
    @mock.patch('editor.Frame.print_frame')
    def test_subs_prep(self, print_f, filt):
        with mock.patch.dict(editor.frame_dict, self.d):
            inf1 = editor.Information(
                'name1', 0, 10, 1, 0, 0, 100, 100, 'path1', 10)
            inf2 = editor.Information(
                'name2', 0, 10, 1, 0, 0, 100, 100, 'path2', 15)
            frame1 = editor.Frame([inf1, inf2], 'video', 'audio')
            frame1.video = 'video'
            frame1.audio = 'audio'
            editor.subs_prep('new_name', 'x0', 'y0', 10, 10, 'path', frame1)
            print(editor.frame_dict['new_name'])
