import unittest
import editor


red_start = "\x1b[31;40m"
red_end = "\x1b[0m"


class Test(unittest.TestCase):

    def test_insert(self):
        inf1 = editor.Information(
            'name1', 0, 10, 1, 0, 0, 100, 100, 'path1', 10)
        inf2 = editor.Information(
            'name2', 0, 10, 1, 0, 0, 100, 100, 'path2', 15)
        frame1 = editor.Frame([inf1, inf2], 'video', 'audio')
        frame1.video = 'video'
        frame1.audio = 'audio'
        res_frame = editor.get_res_frame(
            frame1, 'some_subs1', 'video', 'audio', 'subs')
        res_frame = editor.get_res_frame(
            res_frame, 'some_subs2', 'video', 'audio', 'subs')
        for e in res_frame.information:
            self.assertEqual(e.subs, ['some_subs1', 'some_subs2'])
