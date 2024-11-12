from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# your classes here

class Courses(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False)
    assignments = db.relationship('Assignment', cascade='all, delete-orphan', backref='course')
    students = db.relationship('Users', secondary='course_students', backref='enrolled_courses')
    instructors = db.relationship('Users', secondary='course_instructors', backref='teaching_courses')

    def __init__(self, name, code):
        if not name or not code:
            raise ValueError("Both 'name' and 'code' are required")
        self.name = name
        self.code = code

    def serialize(self):
        assignments = [a.serialize() for a in self.assignments]
        students = [s.serialize() for s in self.students]
        instructors = [i.serialize() for i in self.instructors]

        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'assignments': assignments,
            'students': students,
            'instructors': instructors
        }

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    def __init__(self, title, due_date, course_id):
        if not title or not due_date or not course_id:
            raise ValueError("Both 'title', 'due_date', and 'course_id' are required")
        self.title = title
        self.due_date = due_date
        self.course_id = course_id

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'due_date': self.due_date,
            'course_id': self.course_id
        }

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)

    def __init__(self, name, netid):
        if not name or not netid:
            raise ValueError("Both 'name' and 'netid' are required")
        self.name = name
        self.netid = netid

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid
        }

# Association table for the many-to-many relationship between Courses and Users for students
course_students = db.Table('course_students',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

# Association table for the many-to-many relationship between Courses and Users for instructors
course_instructors = db.Table('course_instructors',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

# Association table for the many-to-many relationship between Courses and Assignments
course_assignments = db.Table('course_assignments',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('assignment_id', db.Integer, db.ForeignKey('assignments.id'), primary_key=True)
)