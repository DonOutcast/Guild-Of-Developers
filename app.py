import asyncio
import json

import aioredis
from sqlalchemy import (
    Column,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session, sessionmaker

engine = create_engine(
    "postgresql+psycopg2://username:secret@db:5432/database",
    echo=True,
    json_serializer=json.dumps,
)

Base = declarative_base()
session = sessionmaker(bind=engine)
s_ = Session(bind=engine)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<User(name='{}',>".format(self.name)


user_one = User(name="Shamil")


class CustomJSONEncoder(json.JSONEncoder):
    """
    Override Flask's `JSONEncoder.default`, which is called
    when the encoder doesn't handle a type.
    """

    def default(self, o):
        if isinstance(o, User):
            return o.id, o.name
        else:
            pass
            return json.JSONEncoder.default(self, o)


def init_db():
    Base.metadata.create_all(engine)
    for i in range(5):
        user_one = User(name="Shamil" + str(i))
        with session.begin() as s:
            s.add(user_one)
            s.commit()


async def request():
    redis = aioredis.from_url("redis://redis_db:6379")
    result = None
    for i in range(5):
        value = await redis.get("my-friends" + str(i))
        if value is not None:
            result = json.loads(value)
            print("RESTUL of redis: ", result)

        result = s_.query(User).all()
        await redis.set(
            "my-friends" + str(i), json.dumps(result, cls=CustomJSONEncoder)
        )
    print("RESULT of psql: ", result)


async def main():
    init_db()
    aioredis.from_url("redis://localhost:6379")
    await request()
    await request()


if __name__ == "__main__":
    asyncio.run(main())
