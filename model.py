from peewee import *
import ast
import nodes
import datetime

db = SqliteDatabase("drills.db", threadlocals=True)

class Base(Model):
    class Meta:
        database = db

class User(Base):
    name = CharField(unique = True)

    def get_latest_drill(self):
        try:
            unsolved = Drill.get(Drill.user == self, Drill.solved == False)
        except DoesNotExist, e:
            unsolved = Drill.create(user = self,
                                    date = datetime.date.today())
            unsolved.generate()
            unsolved.save()

        return unsolved

    def num_solved(self):
        return Drill.select().where(Drill.user == self).\
                where(Drill.date == datetime.date.today()).\
                where(Drill.solved == True).count()

    @staticmethod
    def get_by_name(name):
        try:
            user = User.create(name = name)
            user.save()
        except IntegrityError, e:
            user = User.get(User.name == name)

        return user

class Drill(Base):
    user = ForeignKeyField(User, related_name="drills")
    prompt = TextField(null = True)
    seed = CharField(null = True)
    solution = TextField(null = True)
    answer_key = TextField(null = True)
    solved = BooleanField(default=False)
    date = DateField()

    def compare(self):
        if not self.solution.strip():
            return False

        try:
            root = ast.parse(self.solution)
        except:
            return False

        soln_nodes = [ type(n).__name__ for n in ast.walk(root) ]
        key_nodes = [ type(n).__name__ for n in ast.walk(ast.parse(self.answer_key)) ]
        
        return soln_nodes == key_nodes

    def generate(self):
        problem = nodes.generate()
        self.prompt = problem.sentence()
        self.answer_key = problem.code()

if __name__ == "__main__":
    db.connect()
    db.create_tables([User, Drill])
