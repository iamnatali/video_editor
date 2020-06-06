import unittest
from unittest import mock
import editor


red_start = "\x1b[31;40m"
red_end = "\x1b[0m"


def init_inf():
    my_inf = editor.Information(
        'main', 10, 20, 1, 30, 30, 100, 100, 'path.mp4', 90)
    my_inf.inside_videos.append('child')
    my_inf.inside_videos.append('other')
    my_inf.pictures.append('pp.jpg')
    my_inf.pictures.append('pic.ipg')
    my_inf.subs.append('rus.srt')
    my_inf.subs.append('eng.srt')
    return my_inf


class Test(unittest.TestCase):

    def test_get_copy(self):
        my_inf = init_inf()
        copy = my_inf.get_copy()
        self.assertEqual(copy.path, my_inf.path)
        copy.path = 'test.mp4'
        self.assertNotEqual(copy.path, my_inf.path)
        copy.subs.append('test.srt')
        self.assertNotEqual(copy.subs, my_inf.subs)

    @mock.patch('editor.print')
    def test_print(self, my_print):
        my_inf = init_inf()
        my_inf.print_information()
        my_print.assert_any_call(red_start + 'pictures' + red_end)

    def test_frame(self):
        inf1 = init_inf()
        inf2 = init_inf()
        frame = editor.Frame([inf1, inf2], 'video', 'audio')
        copy = frame.get_copy()
        self.assertEqual(len(copy.information), len(frame.information))
        self.assertEqual(
            copy.information[0].__dict__, frame.information[0].__dict__)
        copy.information[0].pictures[0] = 'another.jpg'
        self.assertNotEqual(
            copy.information[0].__dict__, frame.information[0].__dict__)

    @mock.patch('editor.print')
    def test_print_frame(self, my_print):
        inf1 = init_inf()
        inf2 = init_inf()
        frame = editor.Frame([inf1, inf2], 'video', 'audio')
        print()
        frame.print_frame()
        my_print.assert_any_call(red_start + "Этот фрагмент"
                                 " - конкатенация нескольких.\n" + red_end +
                                 "Сейчас будет выведенена"
                                 " информация о них, в порядке конкатенации")
        my_print.assert_any_call(red_start +
                                 'общая продолжительность фрагмента ' +
                                 red_end+str(180))
