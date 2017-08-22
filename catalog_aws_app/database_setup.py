from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name'          : self.name,
            'id'            : self.id,
        }

# Add DateTime?? in order to figure out the most recent items?
class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String(250))
    picture = Column(String(400), nullable=True)
    # Try to use a category with the backref to find all items associated
    # with that category
    # (session.query(Category, Items).join(Category.items).all()
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, backref="items")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref="items",  foreign_keys=[user_id])

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name'          : self.name,
            'id'            : self.id,
            'description'   : self.description,
            'picture'       : self.picture,
            'category'      : self.category.name
        }


engine = create_engine('postgresql://catalog123:catalog@localhost/catalog')
Base.metadata.create_all(engine)