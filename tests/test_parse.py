import unittest
from unittest import mock
import parameterized
import editor


def my_side(str):
    yield str
    yield 'exit'


class Test(unittest.TestCase):

    @parameterized.parameterized.expand(
        [parameterized.param(['-fragment', 'main',
                              '10', '15', 'new'],
                             'fragment'),
         parameterized.param(['-copy_fragment', 'new',
                              'main'], 'copy_fragment')]
    )
    def test_parsing(self, args, name):
        parser = editor.parse_enter()
        parser = editor.add_actions(parser)
        res = parser.parse_args(args)
        d = res.__dict__
        self.assertEqual(d[name], args[1:])

    @parameterized.parameterized.expand([
        parameterized.param('-fragment main 10 15 new',
                            'editor.create_fragment'),
        parameterized.param('-result main a.mp4', 'editor.write_result'),
        parameterized.param('-speed wow 1.2', 'editor.speed_preparations'),
        parameterized.param('-crop main 1 5 20 50',
                            'editor.crop_preparations'),
        parameterized.param('-concat main child',
                            'editor.concat_preparations'),
        parameterized.param('-insert main child p.jpg 80 10',
                            'editor.insert_preparations'),
        parameterized.param('-insert_vid main child child1 80 10',
                            'editor.insert_vid_preparations'),
        parameterized.param(
            '-insert_vid main child child1 80 10 -a both',
            'editor.insert_vid_preparations'),
        parameterized.param('-subs new main p.srt 80 10',
                            'editor.subs_preparations'),
        parameterized.param('-show_all_fragments', 'editor.print'),
        parameterized.param('-show_fragment name',
                            'editor.get_frame_from_dict'),
        parameterized.param('-copy_fragment mother name',
                            'editor.get_frame_from_dict')
    ])
    def test_interaction(self, st, f):
        with mock.patch('editor.input', side_effect=my_side(st)):
            with mock.patch(f) as create_mock:
                parser = editor.parse_enter()
                parser = editor.add_actions(parser)
                editor.interactive_action(parser, False)
        create_mock.assert_called()

    def test_start(self):
        with mock.patch('editor.input', side_effect=my_side('-start')):
            parser = editor.parse_enter()
            editor.interactive_action(parser, False)
            args = parser.parse_args(['-load', 'wow.mp4', 'a'])
        self.assertEqual('load' in args.__dict__, True)
