from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import DAL.db_config as config
from contextlib import contextmanager
import copy


class BaseRepository:

    def __init__(self, db_object):
        self.engine = create_engine(config.connection_string)
        self.db_object = db_object
        self.Session = sessionmaker(bind=self.engine)

    def get_all(self):
        try:
            with self.session_scope() as session:
                query = session.query(self.db_object)
                return query.all(), None
        except SQLAlchemyError as e:
            return None, "Error occured: " + str(e)

    # def where(self,**kwargs):
    #     try:
    #         with self.session_scope() as session:
    #             query = session.query(self.db_object).filter_by(**kwargs)
    #             return query.all(), None
    #     except SQLAlchemyError as e:
    #         return None, "Error occured: " + str(e)

    def where(self,*criterion):
        try:
            with self.session_scope() as session:
                query = session.query(self.db_object).filter(*criterion)
                return query.all(), None
        except SQLAlchemyError as e:
            return None, "Error occured: " + str(e)

    def get(self, **kwargs):
        try:
            with self.session_scope() as session:
                query = session.query(self.db_object).filter_by(**kwargs)
                return query.one_or_none(), None
        except SQLAlchemyError as e:
            return None, "Error occured: " + str(e)

    def add(self, *new_objects):
        try:
            with self.session_scope(commit_needed=True) as session:
                session.add_all(new_objects)
            return True, None
        except SQLAlchemyError as e:
            return False, "Error occured: " + str(e)

    @contextmanager
    def session_scope(self, commit_needed=False):
        session = self.Session()
        try:
            yield session
            if commit_needed:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

