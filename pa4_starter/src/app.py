from db import db
from flask import Flask, request
import json
from db import Courses, Users, Assignment

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# your routes here

# get all courses
@app.route("/api/courses/", methods=["GET"])
def get_courses():
    courses = [c.serialize() for c in Courses.query.all()]

    for course in courses:
        if not course['assignments']:
            course['assignments'] = None
        if not course['instructors']:
            course['instructors'] = None
        if not course['students']:
            course['students'] = None

    response = {
        'courses': courses
    }

    return success_response(response)

# create a course
@app.route("/api/courses/", methods=["POST"])
def create_course():
    post_body = json.loads(request.data)
    name = post_body.get('name', '')
    code = post_body.get('code', '')
    if not name or not code:
        return failure_response("Name and code are required", 400)
    
    course = Courses(name=name, code=code)
    db.session.add(course)
    db.session.commit()

    response = course.serialize()

    return success_response(response, 201)

# get a course by a specific id
@app.route("/api/courses/<int:course_id>/", methods=["GET"])
def get_course(course_id):
    course = Courses.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    
    course_serialized = course.serialize()

    response = {
        'id': course_serialized['id'],
        'name': course_serialized['name'],
        'code': course_serialized['code'],
        'assignments': course_serialized['assignments'],
        'students': course_serialized['students'],
        'instructors': course_serialized['instructors']
    }

    return success_response(response)

# delete a specific course by id
@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    course = Courses.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    
    db.session.delete(course)
    db.session.commit()

    response = course.serialize()

    return success_response(response)

# create a user
@app.route("/api/users/", methods=["POST"])
def create_user():
    post_body = json.loads(request.data)
    name = post_body.get('name', '')
    netid = post_body.get('netid', '')
    if not name or not netid:
        return failure_response("Name and netid are required", 400)
    
    user = Users(name=name, netid=netid)
    db.session.add(user)
    db.session.commit()

    user_serialized = user.serialize()

    courses = [c.serialize() for c in user.enrolled_courses + user.teaching_courses]

    response = {
        'id': user_serialized['id'],
        'name': user_serialized['name'],
        'netid': user_serialized['netid'],
        'courses': courses
    }

    return success_response(response, 201)

# get a specific user by id
@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    
    courses = [c.serialize() for c in user.enrolled_courses + user.teaching_courses]

    for course in courses:
            course['assignments'] = None
            course['instructors'] = None
            course['students'] = None

    response = {
        'id': user.id,
        'name': user.name,
        'netid': user.netid,
        'courses': courses
    }

    return success_response(response)

# add a user to a course
@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    post_body = json.loads(request.data)
    user_id = post_body.get('user_id', '')
    type = post_body.get('type', '')
   
    if not user_id or not type:
        return failure_response("User id and role are required")
    
    course = Courses.query.filter_by(id=course_id).first()
    user = Users.query.filter_by(id=user_id).first()
    
    if course is None or user is None:
        return failure_response("Course or user not found")
    
    if type == 'student':
        if user in course.students:
            return failure_response("User is already in course")
        course.students.append(user)
    elif type == 'instructor':
        if user in course.instructors:
            return failure_response("User is already in course")
        course.instructors.append(user)
    else:
        return failure_response("Type must be student or instructor")
    
    db.session.commit()

    course = Courses.query.filter_by(id=course_id).first()
    course = course.serialize()

    assignments = course['assignments']
    instructors = course['instructors']
    students = course['students']

    response = {
        "id": user_id,
        "code": course['code'],
        "name": course['name'],
        "assignments":  assignments,
        "instructors":  instructors,
        "students":  students
    }

    return success_response(response, 200)

# create an assignment for a course
@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    post_body = json.loads(request.data)
    title = post_body.get('title', '')
    due_date = post_body.get('due_date', '')
    if not title or not due_date:
        return failure_response("Title and due_date are required", 400)
    
    course = Courses.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    
    assignment = Assignment(title=title, due_date=due_date, course_id=course_id)
    db.session.add(assignment)
    db.session.commit()

    response = {
        'id': assignment.id,
        'title': assignment.title,
        'due_date': assignment.due_date,
        'course': {
            'id': course.id,
            'code': course.code,
            'name': course.name
        }
    }

    return success_response(response, 201)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)