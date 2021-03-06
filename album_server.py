from bottle import route
from bottle import run
from bottle import HTTPError
from bottle import request
from datetime import datetime

import album


def table_tag(inf):
    """
    Заключает информацию inf в тэг <table> 
    """
    return '<table>{}</table>\n'.format(inf)


def rw_tag(*inf, hd=False):
    """
    список inf заключается в строку таблицы,
    где значение hd определяет является ли строка заголовком
    """
    rw_tag = 'td'
    if hd:
        rw_tag = 'th'
    rows = ['<{0}>{1}</{0}>'.format(rw_tag, i) for i in inf]
    return '<tr>{}</tr>\n'.format(''.join(rows))


def rus_num(num, choice):
    """
    в зависимости от числа ставит существительное в нужный падеж
    """
    if (num // 10) % 10 == 1 or num % 10 == 0 or num % 10 >= 5:
        return '{} {}'.format(num, choice[2])
    elif num % 10 == 1:
        return '{} {}'.format(num, choice[0])
    else:
        return '{} {}'.format(num, choice[1])


@route('/albums/<artist>')
def albums(artist):
    """
    выводит информацию в виде таблицы о найденных альбомах по названию исполнителя
    в заголовке таблицы указывается информация о количестве найденных альбомов
    """
    albums_list = album.find(artist)
    if not albums_list:
        result = HTTPError(404, 'Альбомов {} не найдено'.format(artist))
    else:
        album_names = [rw_tag(a.album) for a in albums_list]
        count = len(album_names)
        result = table_tag(rw_tag('Найдено {} исполнителя "{}"'.
                                  format(rus_num(count, ('альбом', 'альбома', 'альбомов')), artist), hd=True) + ''.join(album_names))
    return result


@route('/all')
def all():
    """
    выводит в виде таблицы всю информацию о таблице album в БД albums.sqlite3
    """
    all_list = album.all()
    album_rows = [rw_tag(n.artist, n.album, n.genre, n.year) for n in all_list]
    result = table_tag(rw_tag('Исполнитель', 'Название альбома',
                       'Жанр', "Год", hd=True) + ''.join(album_rows))
    return result


@route('/albums', method='POST')
def add_album():
    """
    по информации из POST запроса формирует информацию о альбоме и добавляет в БД
    Информация проходит необходимую валидацию
    """
    artist = request.forms.get('artist')
    alb = request.forms.get('album')
    genre = request.forms.get('genre')
    year = request.forms.get('year')

    artist_list = album.find(artist)
    result = ''
    if artist_list:
        albums_names = [a.album for a in artist_list]
        if alb in albums_names:
            result = HTTPError(409, 'Такой альбом уже существует')

    if not result:  # если альбома со схожим именем не было найдено, то данные проходят валидацию
        try:
            year = datetime.strptime(year, '%Y').year
            if not (1900 <= year <= datetime.today().year):
                raise Exception('Невозможно, что в этот год вышел альбом')
        except Exception as ex:
            print(ex)
            result = 'Введён некорректный год выпуска альбома\n'
            year = None

        try:
            album_whole = album.Album(
                artist=artist,
                album=alb,
                genre=genre,
                year=year
            )
            result += album.add(album_whole)
        except Exception as ex:
            print(ex)
    return result


if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
