from config import db_url_object
import sqlalchemy as sq
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session, declarative_base, sessionmaker


metadata = MetaData()
Base = declarative_base()


class Rightpeople(Base):
    __tablename__ = 'rightpeople'
    user_id = sq.Column(sq.Integer, primary_key=True)
    partner_id = sq.Column(sq.Integer, primary_key=True)

    def create_db(self):
        engine = create_engine(db_url_object)
        Base.metadata.create_all(engine)

    def add_in_db(self, user_id, partner_id):
        engine = create_engine(db_url_object)
        with Session(engine) as session:
            to_bd = Rightpeople(user_id=user_id, partner_id=partner_id)
            session.add(to_bd)
            session.commit()
        return f'Запись добавлена в БД'

    def extract_from_db(self, user_id, partner_id):
        engine = create_engine(db_url_object)
        with Session(engine) as session:
            from_bd = session.query(Rightpeople).filter(Rightpeople.user_id == user_id).all()
            for item in from_bd:
                if item.partner_id == partner_id:
                    return False
        return f'Запись извлечена из БД'

    def people_in_db(self):
        engine = create_engine(db_url_object)
        sessionmaker(bind=engine)
        session = Session()
        found = session.query(Rightpeople).filter_by(
            user_id=self.user_id,
            partner_id=self.partner_id
        )
        return found is not None


if __name__ == '__main__':
    one = Rightpeople()
    one.create_db()
