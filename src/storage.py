from sqlalchemy import Column, Integer, String, Index, JSON
from sqlalchemy import create_engine, select, exc
from sqlalchemy.orm import declarative_base, Session
import xdg
import os


Base = declarative_base()


class Anchors(Base):
    __tablename__ = 'anchors'
    anchor_id = Column(Integer, primary_key=True)
    image = Column(String, unique=True)
    anchors = Column(JSON)
    Index("anchors_image_idx", image)


class Storage:
    def __init__(self):
        datadir = xdg.xdg_data_home().joinpath("gpx-race")
        os.makedirs(datadir, exist_ok=True)

        dburi = datadir.joinpath("storage.db").as_uri()
        dburi = dburi.replace("file:", "sqlite:/")
        self.engine = create_engine(dburi, echo=False, future=True)
        Base.metadata.create_all(self.engine)

    def save_anchors(self, image, anchors):
        with Session(self.engine) as session:
            try:
                stmt = select(Anchors).where(Anchors.image.is_(image))
                old_anchors = session.scalars(stmt).one()
                old_anchors.anchors = anchors
            except exc.NoResultFound:
                session.add(Anchors(image=image, anchors=anchors))
            session.commit()

    def load_anchors(self, image):
        with Session(self.engine) as session:
            try:
                stmt = select(Anchors).where(Anchors.image.is_(image))
                return session.scalars(stmt).one().anchors
            except exc.NoResultFound:
                return None
