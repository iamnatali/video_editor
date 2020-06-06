import ffmpeg
import argparse
import sys
import pathlib
import colorama
import functools


_old_excepthook = sys.excepthook
get_h = "используйте -h/--help, чтобы получить справку"


def myexcepthook(exctype, value, traceback):
    if exctype == KeyboardInterrupt:
        print("Программа была прервана Ctrl+C.\n" +
              red_start +
              "Спасибо за использование нашего продукта!" + red_end)
    elif exctype == EOFError:
        print("Найден знак конца файла(Ctrl+Z или Ctrl+D).\n" +
              red_start +
              "Спасибо за использование нашего продукта!" + red_end)
    elif exctype == ffmpeg._run.Error:
        print(red_start + "Произошла ошибка в ffmpeg\n"+red_end +
              "возможно были переданы неверные аргументы\n"
              "или у вас не установлена утилита ffmpeg")
    else:
        _old_excepthook(exctype, value, traceback)


def speed(video, audio, arg):
    video = ffmpeg.setpts(video, '{}*PTS'.format(arg))
    if arg < 0.5:
        video = ffmpeg.filter(video,
                              'minterpolate', mi_mode='mci',
                              mc_mode='aobmc', vsbmc=1, fps=120)
    audio = ffmpeg.filter(audio, 'asetpts', '{}*PTS'.format(arg))
    return video, audio


def crop(video, audio,  x, y, width, height):
    video = ffmpeg.crop(video, x, y, width, height)
    return video, audio


def cut(video, audio, arg):
    st, end = arg
    video = ffmpeg.trim(video, start=st, end=end)
    video = ffmpeg.setpts(video, 'PTS-STARTPTS')
    audio = ffmpeg.filter(audio, 'atrim', start=st, end=end)
    audio = ffmpeg.filter(audio, 'asetpts', 'PTS-STARTPTS')
    return video, audio


def parse_enter():
    parser = argparse.\
        ArgumentParser(add_help=False,
                       epilog='NB: введите '
                              'exit для выхода\n'
                              '(после ошибки '
                              'или вывода '
                              'справки сначала enter)',
                       formatter_class=argparse.RawTextHelpFormatter,
                       description='NB:'
                                   'желательно '
                                   'использовать '
                                   'команды по отдельности,\n'
                                   'если в описании '
                                   'не указана иная возможность')
    parser.add_argument('-h', '--help', action='help',
                        default=argparse.SUPPRESS,
                        help='Показать это сообщение и выйти')
    parser.add_argument("-start", action='store_true',
                        help='для начала работы программы')
    return parser


class Information:
    def __init__(self, name, start,
                 end, speed, x, y, width, height, path, duration):
        self.pictures = []
        self.inside_videos = []
        self.subs = []
        self.name = name
        self.start = start
        self.end = end
        self.speed = speed
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.path = path
        self.duration = duration

    def get_copy(self):
        new_inf = Information(self.name,
                              self.start,
                              self.end,
                              self.speed,
                              self.x,
                              self.y,
                              self.width,
                              self.height,
                              self.path,
                              self.duration)
        new_inf.subs = []
        for e in self.subs:
            new_inf.subs.append(e)
        new_inf.pictures = []
        for e in self.pictures:
            new_inf.pictures.append(e)
        new_inf.inside_videos = []
        for e in self.inside_videos:
            new_inf.inside_videos.append(e)
        return new_inf

    def print_information(self):
        d = self.__dict__
        for k, v in d.items():
            print_list(k, v, 'pictures')
            print_list(k, v, 'inside_videos')
            print_list(k, v, 'subs')
            if k != 'name' and k != 'pictures'\
                    and k != 'inside_videos' and k != 'subs':
                print(red_start+str(k)+red_end+" "+str(v))


def print_list(k, v, name):
    if k == name and v:
        print(red_start + k + red_end)
        for e in v:
            print("   " + str(e))


class Frame:
    def __init__(self, inform_list, video, audio):
        self.information = []
        for inf in inform_list:
            self.information.append(inf)
        self.video = video
        self.audio = audio

    def get_copy(self):
        new_information = []
        for e in self.information:
            new_information.append(e.get_copy())
        return Frame(new_information, self.video, self.audio)

    def print_frame(self):
        if len(self.information) > 1:
            print(red_start + "Этот фрагмент"
                              " - конкатенация нескольких.\n" + red_end +
                  "Сейчас будет выведенена"
                  " информация о них, в порядке конкатенации")
            durat = 0
            for e in self.information:
                durat += e.duration
            print(red_start +
                  'общая продолжительность фрагмента '+red_end+str(durat))
        num = 0
        for e in self.information:
            num += 1
            print("Часть фрагмента номер {}"
                  .format(red_start+str(num)+red_end))
            print("===========")
            e.print_information()
            print("===========")


frame_dict = {}
red_start = "\x1b[31;40m"
red_end = "\x1b[0m"


def path_is_correct(path, new, suf):
    path = pathlib.Path(path)
    if not path.exists() and not new:
        print(red_start +
              'путь к файлу ' +
              str(path.absolute()) +
              ' неверен'+red_end)
        print(red_start+'пожалуйста, попытайтесь снова'+red_end)
        return False
    elif not path.suffix == suf:
        print(red_start+'расширение должно быть '+suf+red_end)
        print(red_start+'пожалуйста, попытайтесь снова'+red_end)
        return False
    else:
        return True


def probe(path):
    inf = ffmpeg.probe(str(path.absolute()),
                       show_entries='stream=codec_type, width, height,'
                                    ':format=duration'
                                    ':disposition='
                                    ':tags=')
    width = inf['streams'][0]['width']
    height = inf['streams'][0]['height']
    duration = inf['format']['duration']
    return width, height, duration


def load(path, name):
    if path_is_correct(path, False, '.mp4'):
        path = pathlib.Path(path)
        stream = ffmpeg.input(str(path.absolute()))
        width, height, duration = probe(path)
        duration = float(duration)
        video = stream.video
        audio = stream.audio
        inf = Information(name, 0, duration,
                          1, 0, 0, width, height,
                          str(path.absolute()), duration)
        frame = Frame([inf], video, audio)
        adding_frame(name, frame, "CREATE", 'вы создали следующий фрагмент:')


def adding_frame(name, frame, operation, comment):
    if name not in frame_dict:
        frame_dict[name] = frame.get_copy()
        print(red_start + operation + red_end)
        print(comment)
        frame.print_frame()
    else:
        print(red_start +
              'фрагмент с именем ' +
              name +
              ' уже существует, попробуйте снова' +
              red_end)


def get_frame_from_dict(name):
    global frame_dict
    no_right_answer = True
    parent = None
    while no_right_answer:
        if name == "cancel" or name == 'exit':
            return name
        elif name not in frame_dict:
            print(red_start +
                  'фрагмента с именем ' + name +
                  ' не существует' + red_end)
            name = input('попробуйте ввести:\n'
                         'имя снова,\n'
                         'cancel, чтобы отменить\n'
                         'exit, чтобы выйти\n'
                         '>')
        else:
            parent = frame_dict[name]
            no_right_answer = False
    return parent


def create_fragment(name, start, end, child_name):
    parent = get_frame_from_dict(name)
    if parent != "exit" and parent != 'cancel':
        coord = check_coord(
            int, 'начало и '
                 'конец должны '
                 'быть целыми '
                 'числами больше 0',
            start, end)
        if coord[0]:
            start = coord[1][0]
            end = coord[1][1]
            if start >= parent.information[0].start\
                    and end <= parent.information[0].end and start < end:
                child = parent.get_copy()
                for e in child.information:
                    e.start = start
                    e.end = end
                    e.duration = end-start
                child.video, child.audio = cut(parent.video,
                                               parent.audio, [start, end])
                adding_frame(child_name, child, "CREATE",
                             'вы создали следующий фрагмент:')
            else:
                print(red_start+'начало или конец'
                                ' желаемого объекта'
                                ' выходят за границы родительского\n'
                      'или начало дальше конца' +
                      red_end)
                print(get_h)
    elif parent == "exit":
        return "exit"


def analyze_frame(name, func):
    frame = get_frame_from_dict(name)
    if frame != "exit" and frame != 'cancel':
        func(frame)
    elif frame == "exit":
        return "exit"


def write_result(name, path):
    write_f = functools.partial(write_res, path=path)
    analyze_frame(name, write_f)


def write_res(frame, path):
    stream = ffmpeg.output(frame.video, frame.audio, path)
    try:
        ffmpeg.run(stream)
        print(red_start + 'результат был сохранен в {}'.
              format(pathlib.Path(path).absolute()) + red_end)
        print("лучше переименовать этот файл,"
              " чтобы он случайно не был переписан")
    except ValueError:
        print('неудачное наложение фильтров\n'
              'попробуйте записать'
              ' результат в промежутке '
              'между первого действия '
              'с видео\n'
              'а затем загрузите для второго')


def add_actions(parser):
    parser.add_argument('-fragment', type=str, nargs=4, metavar=('PARENT',
                                                                 'START',
                                                                 'END',
                                                                 'CHILD'),
                        help='передайте имя фрагмента-родителя,'
                             ' начало и конец нового фрагмента,'
                             ' имя фрагмента, который будет получен')
    parser.add_argument('-copy_fragment', type=str, nargs=2, metavar=('PARENT',
                                                                      'CHILD'),
                        help='передайте имя фрагмента-родителя'
                             ' и имя нового фрагмента')
    parser.add_argument('-show_all_fragments', action='store_true',
                        help='показать характеристики'
                             ' всех доступных фрагментов')
    parser.add_argument('-show_fragment', type=str, nargs=1,  metavar='NAME',
                        help='передайте имя фрагмента,'
                             ' информацию о котором хотите вывести')
    parser.add_argument('-result', type=str, nargs=2, metavar=('NAME',
                                                               'PATH'),
                        help='передайте имя фрагмента и путь,'
                             ' по которому вы хотите сохранить фрагмент')
    parser.add_argument('-speed', type=str, nargs=2, metavar=('NAME',
                                                              'SPEED'),
                        help='Чтобы изменить скорость фрагмента,\n'
                             'передайте имя фрагмента, желаемое ускорение'
                             '(0<число<1) '
                             'или замедление'
                             '(число>1).\n' +
                             red_start +
                             'NB'+red_end+':передаваемое число '
                             'должно быть  в диапазоне от 0.3 до 2')
    parser.add_argument('-crop', type=str, nargs=5, action='append',
                        metavar=('NAME', 'X', 'Y', 'WIDTH', 'HEIGHT'),
                        help='Чтобы обрезать изображение фргамента,\n'
                             'передайте имя фрагмента, x и y  левого'
                             ' верхнего угла фрагмента,\n'
                             'его ширину и высоту.\n'
                             'NB:x+width и y+height должны быть'
                             ' < реальных ширины и высоты видео')
    parser.add_argument('-concat', type=str, nargs='+', action='append',
                        metavar=('CHILD', 'PARENTS_NAMES'),
                        help='Передайте имя нового фрагмента,'
                             ' полученного в результате слияния,\n'
                             'а также имена фрагментов видео,'
                             'которые вы хотите соединить\n' +
                             red_start+'NB' +
                             red_end+':фрагменты, использовавшиеся'
                             ' для слияния, продолжают существовать\n' +
                             red_start+'NB1'+red_end +
                             ':при конкатенации размер всех фрагментов\n' +
                             'сводится к наибольшим длине и ширине')
    parser.add_argument('-insert', type=str, nargs=5,
                        metavar=('CHILD', 'PARENT', 'PIC_PATH', 'X', 'Y'),
                        help='передайте имя нового фрагмента,'
                             ' фрагмента видео, путь к изображению,\n'
                             'которое хотите вставить,'
                             ' x и y верхнего левого угла изображения')
    parser.add_argument('-insert_vid', type=str, nargs=5,
                        metavar=('CHILD', 'MAIN_PARENT',
                                 'OTHER_PARENT', 'X', 'Y'),
                        help='передайте имя нового фрагмента,'
                             ' основного фрагмента видео,'
                             ' дополнительного фрагмента,\n'
                             'который хотите вставить,'
                             ' x и y верхнего левого угла изображения\n'
                             'дополнительного фрагмента '
                             'относительно основного\n' + red_start+'NB' +
                             red_end +
                             ':контролируйте '
                             'выход изображения '
                             'за границы видео!'
                        )
    parser.add_argument('-a', type=str,
                        metavar='CHOICE',
                        choices=['main', 'added', 'both'], nargs=1,
                        help='регуляция '
                             'оставшихся аудиодорожек в insert_vid\n'
                             '(по умолчанию'
                             ' остается только дорожка главного видео)')
    parser.add_argument('-subs', type=str, nargs=5,
                        metavar=('CHILD', 'PARENT',
                                 'SUBS_PATH', 'X', 'Y'),
                        help='для отображения субтитров поверх'
                             ' видео передайте'
                             ' имя нового и исходного фрагментов,\n'
                             'путь к файлу с субтитрами и'
                             ' расширением .srt,'
                             ' x и y положения субтитров\n'+red_start +
                             'NB'+red_end+':учитывайте наложение текста,'
                             ' если у фрагмента уже имеются '
                             'субтитры на тех же координатах\n'+red_start +
                             'NB1'+red_end +
                             ':котролируйте'
                             ' выход текста за границы видео\n'
                             'лучше придерживаться координат меньше 300')
    parser.add_argument('-resize', type=str, nargs=4,
                        metavar=('CHILD', 'PARENT', 'WIDTH', 'HEIGHT'),
                        help='изменение размеров фрагмента\n'
                             'без обрезания частей изображения\n'
                             'передайте'
                             ' имя нового фрагмента,'
                             ' основного фрагмента и\n'
                             'желаемые ширину и высоту')
    return parser


def interactive_action(parser, first_call, wrd=""):
    colorama.init()
    while True:
        if first_call:
            args = parser.parse_args()
            first_call = False
        else:
            no_right_answer = True
            while no_right_answer:
                fake_args = wrd.split()
                try:
                    args = parser.parse_args(fake_args)
                    no_right_answer = False
                except:
                    wrd = input()
        my_dict = args.__dict__
        if args.start and 'load' not in my_dict:
            parser.add_argument('-load', type=str, nargs=2,
                                metavar=('PATH', 'NAME'),
                                help='передайте путь'
                                     ' для загрузки видео,'
                                     ' имя фрагмента, который будет получен')
            parser.print_help()
        if 'load' in my_dict and args.load:
            v_path = args.load[0]
            name = args.load[1]
            load(v_path, name)
            if 'fragment' not in my_dict:
                add_actions(parser)
            print(get_h)
            print('NB:после первого вызова load больше функций доступно')
        if 'fragment' in my_dict and args.fragment:
            p_name = args.fragment[0]
            start = args.fragment[1]
            end = args.fragment[2]
            new_name = args.fragment[3]
            if create_fragment(p_name, start, end, new_name) == 'exit':
                break
        if 'show_all_fragments' in my_dict and args.show_all_fragments:
            for k, v in frame_dict.items():
                print(red_start+k+red_end)
                v.print_frame()
                print()
            print(get_h)
        if 'show_fragment' in my_dict and args.show_fragment:
            name = args.show_fragment[0]
            frame = get_frame_from_dict(name)
            if frame != "exit" and frame != 'cancel':
                frame.print_frame()
                print(get_h)
            elif frame == "exit":
                break
        if 'copy_fragment' in my_dict and args.copy_fragment:
            p_name = args.copy_fragment[0]
            n_name = args.copy_fragment[1]
            frame = get_frame_from_dict(p_name)
            if frame != "exit" and frame != 'cancel':
                adding_frame(n_name, frame, "COPY",
                             'копия фрагмента '+p_name+' успешно создана')
                print(get_h)
            elif frame == "exit":
                break
        if 'result' in my_dict and args.result:
            name = args.result[0]
            path = args.result[1]
            if path_is_correct(path, True, '.mp4'):
                write_result(name, path)
            print(get_h)
        if 'speed' in my_dict and args.speed:
            res_sp = speed_preparations(args)
            if res_sp == 'exit':
                break
            print(get_h)
        if 'crop' in my_dict and args.crop:
            res = crop_preparations(args)
            if res == 'exit':
                break
            print(get_h)
        if 'concat' in my_dict and args.concat:
            concat_preparations(args)
            print(get_h)
        if 'insert' in my_dict and args.insert:
            insert_preparations(args)
            print(get_h)
        if 'insert_vid' in my_dict and args.insert_vid:
            if 'a' in my_dict and args.a:
                audi = args.a[0]
                print(audi)
                insert_vid_preparations(args, audi)
            else:
                insert_vid_preparations(args, 'main')
            print(get_h)
        if 'subs' in my_dict and args.subs:
            s = subs_preparations(args)
            if s == 'exit':
                break
            print(get_h)
        if 'resize' in my_dict and args.resize:
            resize_preparations(args)
        wrd = input('>>')
        if wrd == 'exit':
            print(red_start +
                  "Спасибо за использование нашего продукта!"+red_end)
            break


def resize_preparations(args):
    new_name = args.resize[0]
    name = args.resize[1]
    x0 = args.resize[2]
    y0 = args.resize[3]
    coord = check_coord(
        int, 'width и height должны быть целыми числами больше 0', x0, y0)
    if coord[0]:
        x = coord[1][0]
        y = coord[1][1]
        sub_f = functools.partial(resize_prep, new_name, x, y)
        analyze_frame(name, sub_f)


def resize_prep(new_name, width, height, frame):
    v, a = resize(frame.video, frame.audio, width, height)
    new_i = []
    for i in frame.information:
        inf = i.get_copy()
        inf.width = width
        inf.height = height
        new_i.append(inf)
    res_frame = Frame(new_i, v, a)
    adding_frame(new_name, res_frame,
                 "RESIZE",
                 'изменение размеров'
                 ' прошло успешно'
                 ' и был создан фрагмент:')


def resize(vid, aud, width, height):
    v = ffmpeg.filter(vid, 'scale', width=width, height=height)
    return v, aud


def subs_preparations(args):
    new_name = args.subs[0]
    name = args.subs[1]
    sub_path = args.subs[2]
    x0 = args.subs[3]
    y0 = args.subs[4]
    if path_is_correct(sub_path, False, '.srt'):
        coord = check_coord(
            int, 'координаты должны быть числами больше 0', x0, y0)
        if coord[0]:
            x = coord[1][0]
            y = coord[1][1]
            sub_f = functools.partial(
                subs_prep, new_name, x0, y0, x, y, sub_path)
            analyze_frame(name, sub_f)


def get_res_frame(frame, str, v, a, dest):
    new_i = []
    for i in frame.information:
        inf = i.get_copy()
        d = inf.__dict__
        d[dest].append(str)
        new_i.append(inf)
    res_frame = Frame(new_i, v, a)
    return res_frame


def subs_prep(new_name, x0, y0, x, y, sub_path, frame):
    if x < frame.information[0].width \
            and y < frame.information[0].height:
        v, a = subs(frame.video, frame.audio, sub_path, x, y)
        res_frame = get_res_frame(
            frame, sub_path + " x " + x0 + " y " + y0, v, a, 'subs')
        adding_frame(new_name, res_frame,
                     "SUBS",
                     'вставка субтитров '
                     'прошла успешно и '
                     'был создан фрагмент:')
    else:
        print(red_start +
              'координаты субтитров выходят за границы видео' +
              red_end)


def subs(video, audio, path, x, y):
    vid = ffmpeg.filter(video, 'subtitles', path,
                        force_style='Alignment=0,'
                                    ' Outline=1, Shadow=0,'
                                    ' Fontsize=18, MarginL={x},MarginV={y}'
                        .format(x=x, y=y))
    return vid, audio


def insert_vid_preparations(args, aud):
    result_name = args.insert_vid[0]
    name1 = args.insert_vid[1]
    frame1 = get_frame_from_dict(name1)
    name2 = args.insert_vid[2]
    frame2 = get_frame_from_dict(name2)
    if frame1 != "exit" \
            and frame1 != 'cancel' \
            and frame2 != "exit" and frame2 != 'cancel':
        x0 = args.insert_vid[3]
        y0 = args.insert_vid[4]
        coord = check_coord(
            int, 'координаты должны быть числами больше 0', x0, y0)
        if coord[0]:
            x = coord[1][0]
            y = coord[1][1]
            v, a = insert_vid(frame1.video, frame1.audio,
                              frame2.video, frame2.audio, x, y, aud)
            res_frame = get_res_frame(frame1, name2, v, a, 'inside_videos')
            adding_frame(result_name, res_frame,
                         "INSERT",
                         'вставка видео прошла'
                         ' успешно и был создан'
                         ' фрагмент:')
    elif frame1 == "exit" or frame2 == "exit":
        return 'exit'


def insert_vid(video, audio, video1, audio1,  x, y, aud):
    video = ffmpeg.overlay(video, video1, x=x, y=y)
    if aud == 'main':
        return video, audio
    elif aud == 'added':
        return video, audio1
    elif aud == 'both':
        au = ffmpeg.filter([audio, audio1], 'amix')
        return video, au


def insert_preparations(args):
    result_name = args.insert[0]
    name = args.insert[1]
    path = args.insert[2]
    insert_f = functools.partial(insert_prep, path, args, result_name)
    analyze_frame(name, insert_f)


def insert_prep(path, args, result_name, frame):
    if path_is_correct(path, False, '.jpg'):
        x0 = args.insert[3]
        y0 = args.insert[4]
        coord = check_coord(
            int, 'координаты должны быть числами больше 0', x0, y0)
        if coord[0]:
            x = coord[1][0]
            y = coord[1][1]
            v, a = insert_pic(frame.video,
                              frame.audio,
                              path, x, y)
            res_frame = get_res_frame(
                frame, path +
                " x " + str(x) +
                " y " + str(y),
                v, a, 'pictures')
            adding_frame(result_name, res_frame,
                         "INSERT",
                         'вставка изображения '
                         'прошла успешно и был '
                         'создан фрагмент:')


def insert_pic(video, audio, path, x, y):
    f = ffmpeg.input(str(pathlib.Path(path).absolute()))
    pic_vid = f.video
    video = ffmpeg.overlay(video, pic_vid, x=x, y=y)
    return video, audio


def check_coord(func, str, *args):
    right_coord = True
    result = []
    for e in args:
        try:
            x = func(e)
            if x < 0:
                right_coord = False
            result.append(x)
        except ValueError:
            right_coord = False
    if not right_coord:
        print(str)
    return right_coord, result


def speed_preparations(args):
    name = args.speed[0]
    coord = check_coord(
        float, 'скорость должна быть вещественным числом', args.speed[1])
    if coord[0]:
        sp_list = coord[1]
        sp = sp_list[0]
        speed_f = functools.partial(speed_prep, sp, name)
        analyze_frame(name, speed_f)


def speed_prep(sp, name, frame):
    if sp < 0.3 or sp > 2:
        print(red_start +
              'скорость должна быть в диапазоне от 0.3 до 2' + red_end)
    else:
        frame.video, frame.audio = speed(frame.video, frame.audio, sp)
        for e in frame.information:
            e.speed = e.speed * sp
            e.duration = e.duration * sp
        print(red_start + "SPEED" + red_end)
        print("видео успешно ускорено")
        print("фрагмент " + name + " изменен следующим образом:")
        frame.print_frame()


def crop_preparations(args):
    crop_args = args.crop[0]
    name = crop_args[0]
    crop_f = functools.partial(crop_prep, crop_args, name)
    analyze_frame(name, crop_f)


def crop_prep(crop_args, name, frame):
    coord = check_coord(float,
                        'координаты должны '
                        'быть вещественными числами больше 0',
                        crop_args[1],
                        crop_args[2],
                        crop_args[3], crop_args[4])
    if coord[0]:
        coord_list = coord[1]
        frame.x = x = coord_list[0]
        frame.y = y = coord_list[1]
        width = coord_list[2]
        height = coord_list[3]
        if x + width > frame.information[0].width \
                or y + height > frame.information[0].height:
            print(red_start +
                  'x+width и y+height должны быть'
                  ' < реальных ширины и высоты видео' + red_end)
        else:
            for e in frame.information:
                e.width = width
                e.height = height
                e.x = x
                e.y = y
            frame.video, frame.audio = crop(frame.video,
                                            frame.audio, x, y, width, height)
            print(red_start + "CROP" + red_end)
            print("видео успешно обрезано")
            print("фрагмент " + name + " изменен следующим образом:")
            frame.print_frame()


def concat_preparations(args):
    our_args = args.concat[0]
    result_name = our_args[0]
    frame_names = our_args[1:]
    frames = []
    information_frames = []
    talking_flag = True
    for e in frame_names:
        f = get_frame_from_dict(e)
        if f != "exit" and f != 'cancel':
            frames.append(f)
            information_frames.append(f.information[0])
        elif f == "exit":
            break
        else:
            talking_flag = False
    if talking_flag:
        video, audio = concat(frames)
        res_frame = Frame(information_frames, video, audio)
        adding_frame(result_name, res_frame, "CONCAT",
                     'конкатенация прошла успешно и был создан фрагмент:')


def concat(frames):
    video = []
    audio = []
    same_size = True
    width = frames[0].information[0].width
    height = frames[0].information[0].height
    for f in frames:
        same_size = same_size \
            and f.information[0].width == width\
            and f.information[0].height == height
        video.append(f.video)
        audio.append(f.audio)
    if not same_size:
        x_min = float('inf')
        y_min = float('inf')
        h_max = 0
        w_max = 0
        for f in frames:
            if f.information[0].x < x_min:
                x_min = f.information[0].x
            if f.information[0].y < y_min:
                y_min = f.information[0].y
            if f.information[0].height > h_max:
                h_max = f.information[0].height
            if f.information[0].width > w_max:
                w_max = f.information[0].width
        mywidth = w_max-x_min
        myheight = h_max-y_min
        vid = []
        for v in video:
            v = ffmpeg.filter(v, 'scale', width=mywidth, height=myheight)
            vid.append(v)
    else:
        vid = video
    number = len(frames)
    video = ffmpeg.concat(*vid, n=number, v=1, a=0, unsafe=1)
    audio = ffmpeg.concat(*audio, n=number, v=0, a=1, unsafe=1)
    video = ffmpeg.filter(video, 'mpdecimate')
    video = ffmpeg.filter(video, 'framerate', fps=30000/1001)
    return video, audio


def main():
    sys.excepthook = myexcepthook
    if len(sys.argv) == 1:
        print("используйте -h/--help, чтобы получить справку")
    else:
        parser = parse_enter()
        interactive_action(parser, True)


if __name__ == '__main__':
    main()
