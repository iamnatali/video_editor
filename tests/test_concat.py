import unittest
from unittest import mock
import editor


class Test(unittest.TestCase):

    @mock.patch('ffmpeg.concat')
    @mock.patch('ffmpeg.filter')
    def test_adding(self, filter, concat):
        inf1 = editor.Information(
            'name1', 0, 10, 1, 0, 0, 100, 100, 'path1', 10)
        inf2 = editor.Information(
            'name2', 0, 10, 1, 0, 0, 100, 100, 'path2', 15)
        frame1 = editor.Frame([inf1, inf2], 'video', 'audio')
        frame1.video = 'video1'
        frame1.audio = 'audio1'
        frame2 = editor.Frame([inf1, inf2], 'video', 'audio')
        frame2.video = 'video2'
        frame2.audio = 'audio2'
        editor.concat([frame1, frame2])
        concat.assert_any_call('video1', 'video2', n=2, v=1, a=0, unsafe=1)
        concat.assert_any_call('audio1', 'audio2', n=2, v=0, a=1, unsafe=1)
