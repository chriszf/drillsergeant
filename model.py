from peewee import *
import ast

db = SqliteDatabase("drills.db", threadlocals=True)

class Base(Model):
    class Meta:
        database = db

class User(Base):
    email = CharField(unique = True)

class Drill(Base):
    user = ForeignKeyField(User, related_name="drills")
    prompt = TextField(null = True)
    seed = CharField(null = True)
    solution = TextField(null = True)
    answer_key = TextField(null = True)

    def compare(self):
        if not self.solution.strip():
            return False

        try:
            ast.parse(self.solution)
        except:
            return False

        return True

    def generate(self):
        problem = nodes.generate()
        self.prompt = str(problem)
        self.answer_key = problem.code()

if __name__ == "__main__":
    db.connect()
    db.create_tables([User, Drill])
