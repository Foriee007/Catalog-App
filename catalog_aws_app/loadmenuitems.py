from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database_setup import Base, User, Category, Items

engine = create_engine('postgresql://catalog123:catalog@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user

User1 = User(id=1,
              name="Chris Enchev",
              email="fori.enchev@gmail.com",
              picture="https://lh3.googleusercontent.com/-4vvdFOS93Bw/AAAAAAAAAAI/AAAAAAAAAaU/yGCAr7962wA/photo.jpg")


session.add(User1)
session.commit()

# Create a test category
category1 = Category(name="Vision",
                     id=1)

session.add(category1)
session.commit()

time1 = datetime.datetime.now()
Item1 = Items(user_id=1,
              category_id=1,
              name="Jonathan Swift",
              date=time1,
              description="True vision is the ability to see what is invisible to others.",
              picture="https://farm5.staticflickr.com/4219/35198634236_8dfd0115e5_b.jpg",
              category=category1)

session.add(Item1)
session.commit()

time2 = datetime.datetime.now()
Item2 = Items(user_id=1,
              category_id=1,
              name="Warren G. Bennis",
              date=time2,
              description="Leadership is the capacity to translate vision into realyty.",
              picture="https://farm5.staticflickr.com/4221/34594876474_dc06286daf_b.jpg",
              category=category1)

session.add(Item2)
session.commit()

category2 = Category(name="Innovation",
                     id=2)

session.add(category2)
session.commit()

time3 = datetime.datetime.now()
Item3 = Items(user_id=1,
              category_id=2,
              name="Jeanne Marie Laskas",
              date=time3,
              description="An influential leader carves a path by example for others to follow.",
              picture="https://farm5.staticflickr.com/4251/34394633744_c5b4e6bf37_b.jpg",
              category=category2)

session.add(Item3)
session.commit()


category3 = Category(name="Influence",
                     id=3)

session.add(category3)
session.commit()

time4 = datetime.datetime.now()
Item4 = Items(user_id=1,
              category_id=3,
              name="Chris Enchev",
              date=time4,
              description="The positive action of one person reverberates endlessly throughout humanity.",
              picture="https://farm5.staticflickr.com/4204/35238688665_8a55f1dfee_b.jpg",
              category=category3)

session.add(Item4)
session.commit()

category4 = Category(name="Endurance",
                     id=4)

session.add(category4)
session.commit()

time5 = datetime.datetime.now()
Item5 = Items(user_id=1,
              category_id=4,
              name="Henry Kissinger",
              date=time5,
              description="The leader does not deserve the name unless he is willing occasionally to stand alone.",
              picture="https://farm5.staticflickr.com/4196/35073249062_b50eeb9ec5_b.jpg",
              category=category4)

session.add(Item5)
session.commit()

category5 = Category(name="Graffiti Art",
                     id=5)

session.add(category5)
session.commit()

time6 = datetime.datetime.now()
Item6 = Items(user_id=1,
              category_id=5,
              name="Banksy ",
              date=time5,
              description=" ",
              picture="https://farm5.staticflickr.com/4264/35455520196_baa8e7db8c_c.jpg",
              category=category5)

session.add(Item6)
session.commit()