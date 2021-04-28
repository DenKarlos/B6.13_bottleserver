import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base


DB_PATH = "sqlite:///albums.sqlite3"
# Автоматическое создание классов на основе таблиц из указанной БД
Base = automap_base()
Base.prepare(sa.create_engine(DB_PATH), reflect=True)
Album = Base.classes.album

def connect_db():
    """
    Устанавливает соединение к базе данных, создает таблицы, если их еще нет и возвращает объект сессии 
    """
    engine = sa.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    return sessionmaker(engine)()


def all():
    """
    выводит всю таблицу album из базы данных
    """
    return connect_db().query(Album).all()
    

def find(artist):
    """
    Находит все альбомы в базе данных по заданному артисту
    """
    session = connect_db()
    albums = session.query(Album).filter(Album.artist == artist).all()
    return albums


def add(alb):
    """
    Добавляет альбом
    """
    session = connect_db()
    session.add(alb)
    session.commit()
    return 'Альбом добавлен'


# if __name__ == "__main__":
    