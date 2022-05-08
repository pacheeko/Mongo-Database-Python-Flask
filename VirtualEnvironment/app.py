from flask import Flask, render_template, url_for, redirect
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo



app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'Degree_Builder'
app.config['MONGO_URI'] = 'mongodb+srv://Sean:XI8C0a174x0IbIG3@cluster0.ejiha.mongodb.net/Degree_Builder?retryWrites=true&w=majority'
mongo = PyMongo(app)
FLASK_ENV = 'development'
mongo.init_app(app)

# Returns the homepage, which contains links to other endpoints
@app.route('/')
def index():
    return render_template('index.html')

# Returns a jsonified version of every course in the database
@app.route('/courseList', methods=['GET'])
def get_courselist():
    courses = mongo.db.Course
    output = []
    for c in courses.find():
        output.append({'Code' : c['department_code'], 'course_number' : c['course_number']})
    return jsonify({'result' : output})

# Returns the course HTML document. Allows the user to search for a course.
@app.route('/course', methods=['GET', 'POST'])
def course():
    return render_template('course.html')

# Allows the user to find a course by course code
@app.route('/findCourse', methods=['GET', 'POST'])
def find_course():
    if request.method=='POST':
        depCode = request.form['depCode']
        courseCode = request.form['courseCode']
        return get_course(depCode,courseCode)
    return render_template('findCourse.html')

# Allows the user to find all courses by department
@app.route('/findDepartmentCourses', methods=['GET', 'POST'])
def find_dep_courses():
    if request.method=='POST':
        depCode = request.form['depCode']
        return get_department_courses(depCode)
    return render_template('findDepCourse.html')


# Returns a jsonified version of every course in the database
# of the department given
@app.route("/course/<dcode>", methods=['GET'])
def get_department_courses(dcode):
    courses = mongo.db.Course
    d_courses = courses.find({"department_code": dcode})
    output = []
    for c in d_courses:
        output.append({'Code' : c['department_code'], 'course_number' : c['course_number']})
    return jsonify({dcode + ' courses' : output})

# Returns a jsonified version of a certain course in the database,
# with much more detail than when listed with other courses
@app.route("/course/<dcode>/<cnum>", methods=['GET'])
def get_course(dcode,cnum):
    courses = mongo.db.Course
    c = courses.find_one({"department_code": dcode, "course_number": cnum})
    if c:
        output = {'Deparment code' : c['department_code'],
                       'Department name' : c['department_name'],
                       'Course number' : c['course_number'],
                       'Course name' : c['course_name'],
                       'Description' : c['course_description'],
                       'Hours' : c['course_hours'],
                       'Prerequisites' : c['prerequisites'],
                       'Antirequisites' : c['antirequisites'],
                       'Corequisites' : c['corequisites'],
                       'Notes' : c['notes']}

    else:
        output = "Course not found"
    return jsonify({'result' : output})

# Allows the user to select how they want to find a program
@app.route("/program")
def program():
    return render_template('program.html')

# Returns a jsonified version of a list of all programs
@app.route("/programList")
def get_programlist():
    programs = mongo.db.Program
    output = []
    for p in programs.find():
        output.append({'Faculty' : p['faculty_name'],
                       'Program name': p['program_name'],
                       'Accreditation type': p['accreditation_type']})
    return jsonify({'Program List': output})

# Allows the user to search all programs in a specific faculty
@app.route("/facultyPrograms", methods=['POST', 'GET'])
def faculty_programs():
    if request.method=='POST':
        faculty = request.form['faculty']
        return get_faculty_programs(faculty)
    return render_template('facultyPrograms.html')

# Allows the user to search for all accreditations of a 
# specific program
@app.route("/programAccreditations", methods=['POST', 'GET'])
def program_accreditations():
    if request.method=='POST':
        faculty = request.form['faculty']
        program = request.form['program'].replace(" ", "")
        return get_program_accreditations(faculty, program)
    return render_template('programAccreditations.html')


# Returns all programs of a specific faculty
@app.route("/program/<fname>")
def get_faculty_programs(fname):
    programs = mongo.db.Program.find({'faculty_name' : fname})
    output = []
    for p in programs:
        output.append({'Faculty' : p['faculty_name'],
                      'Program name' : p['program_name'],
                      'Accreditation' : p['accreditation_type']})
    return jsonify({'Programs in ' + fname : output})

# Returns all accreditations with the program name given
# in the faculty given
@app.route("/program/<fname>/<pname>")
def get_program_accreditations(fname, pname):
    programs = mongo.db.Program.find()
    output = []
    for p in programs:
        if p['faculty_name'].replace(" ", "") == fname and p['program_name'].replace(" ", "") == pname:
            output.append({'Faculty' : p['faculty_name'],
                      'Program Name' : p['program_name'],
                      'Accreditation' : p['accreditation_type'],
                      'Core Courses' : p['core_courses'],
                      'Outside Faculty Courses' : p['outside_faculty_courses'],
                      'Outisde Major courses' : p['outside_major_courses'],
                      'Option Courses' : p['option_courses'],
                      'Alternative Courses' : p['alternative_courses'],})
    return jsonify({"Accreditations for " + pname : output})

# Returns all details about a specific program
@app.route("/program/<fname>/<pname>/<accred>")
def get_program(fname, pname, accred):
    programs = mongo.db.Program.find()
    output = "program not found"
    for p in programs:
        if p['faculty_name'].replace(" ", "") == fname and p['program_name'].replace(" ", "") == pname and p['accreditation_type'].replace(" ", "") == accred:
            output = {'Faculty' : p['faculty_name'],
                      'Program name' : p['program_name'],
                      'Accreditation' : p['accreditation_type'],
                      'Core courses' : p['core_courses'],
                      'Outside faculty courses' : p['outside_faculty_courses'],
                      'Outside major courses' : p['outside_major_courses'],
                      'Option_courses' : p['option_courses'],
                      'Alternative courses' : p['alternative_courses']}
    return jsonify(output)

# Adds Past course information into the database
@app.route("/<int:ucid>/addNonUofCEducation", methods=['POST', 'GET'])
def add_previous_education(ucid):
    if request.method=='POST':
        prevEd = request.form['prevEd']
        mongo.db.PreviousEducation.insert_one({'ucid' : ucid, 'Previous Education' : prevEd})
    return render_template('addNonUofCEducation.html')

# Takes the user to the logged in screen
@app.route("/<int:ucid>", methods=["POST", "GET"])
def logged_in(ucid):
    if request.method=='POST':
        url = request.url
        value = request.form['loggedIn']
        return redirect(url + '/' + value)
    return render_template('loggedIn.html')

# Takes the user to the logged in screen
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form['ucid']
        return redirect(url_for('logged_in', ucid=user))
    else:
        return render_template('login.html')

# Adds past UofC courses to the database
@app.route("/<int:ucid>/addUofCCourse", methods=['POST', 'GET'])
def add_uofc_course(ucid):
    if request.method=='POST':
        depCode = request.form['depCode']
        courseCode = request.form['courseCode']
        grade = request.form['grade']
        season = request.form['season']
        year = request.form['year']
        mongo.db.StudentTakesCourse.insert_one({'ucid' : ucid, 
                                                'department_code' : depCode, 
                                                'course_code' : courseCode,
                                                'grade' : grade,
                                                'season' : season,
                                                'year' : year})
    return render_template('addUofCCourse.html')

# Display past courses taken
@app.route("/<int:ucid>/displayPastUofCCourses", methods=['GET'])
def display_past_uofc_courses(ucid):
    courses = mongo.db.StudentTakesCourse.find({'ucid' : ucid})
    output = []
    for c in courses:
        output.append({'Department code' : c['department_code'],
                       'Course code': c['course_code'],
                       'Grade' : c['grade'],
                       'Season' : c['season'],
                       'Year' : c['year']})
    return jsonify({"Courses" : output})

# Delete past course from the database
@app.route("/<int:ucid>/deleteCourse", methods=['GET', 'POST'])
def delete_course(ucid):
    if request.method=='POST':
        depCode = request.form['depCode']
        courseCode = request.form['courseCode']
        mongo.db.StudentTakesCourse.delete_one({'ucid' : ucid, 'department_code' : depCode, 'course_code' : courseCode})
    return render_template('deleteCourse.html')

# Returns the scheduler HTML document
@app.route('/<int:ucid>/scheduler', methods=['GET', 'POST'])
def scheduler(ucid):
    if request.method=='POST':
        if request.form['scheduler'] == "makeNewSchedule":
            scheduleName = request.form['newSchedule']
            return make_schedule(ucid, scheduleName)
        if request.form['scheduler'] == 'existingSchedule':
            scheduleName = request.form['existingSchedule']
            if mongo.db.Schedule.find_one({'ucid' : ucid, 'schedule_name' : scheduleName}):
                url = request.url
                return redirect(url + '/' + scheduleName)
            else:
                return "Schedule not found"
    return render_template('scheduler.html')

# Creates a new schedule and inserts it into the database
@app.route('/<int:ucid>/scheduler/<string:scheduleName>/createSchedule')
def make_schedule(ucid, scheduleName):
    schedule = mongo.db.Schedule.find_one({'ucid' : ucid, 'schedule_name' : scheduleName})
    if schedule:
        return "Schedule already exists"
    else:
        mongo.db.Schedule.insert_one({'ucid' : ucid, 'schedule_name' : scheduleName})
        output = []
        schedule = mongo.db.Schedule.find_one({'ucid' : ucid, 'schedule_name' : scheduleName})
        output.append({'UCID:' : schedule['ucid'],
                    'Schedule name:' : schedule['schedule_name']})
    return jsonify({'Schedule' : output})

# Allows a user to Edit a schedule
@app.route('/<int:ucid>/scheduler/<string:scheduleName>', methods=['GET','POST'])
def edit_schedule(ucid, scheduleName):
    if request.method=='POST':
        url = request.url
        if request.form['modifySchedule'] == 'displaySchedule':
            return display_schedule(ucid, scheduleName)
        elif request.form['modifySchedule'] == 'deleteSchedule':
            mongo.db.Schedule.delete_one({'ucid' : ucid, 'schedule_name' : scheduleName})
            return scheduleName + " has been deleted"
        elif request.form['modifySchedule'] == 'addCourse':
            return redirect(url + '/addCourse')
        elif request.form['modifySchedule'] == 'deleteCourse':
            return redirect(url + '/deleteCourse')
        elif request.form['modifySchedule'] == 'displayGUI':
            return redirect(url + '/GUI')
    return render_template('editSchedule.html')

# Display the schedule
@app.route('/<int:ucid>/scheduler/<string:scheduleName>/display', methods=['GET', 'POST'])
def display_schedule(ucid, scheduleName):
    schedule = mongo.db.Schedule.find_one({'ucid' : ucid, 'schedule_name' : scheduleName})
    output = []
    output.append({'UCID:' : schedule['ucid'],
                   'Name:' : schedule['schedule_name']})
    courses = mongo.db.CoursesForSemester.find({'ucid' : ucid, 'schedule_name' : scheduleName})
    for c in courses:
        output.append({'Department Code:' : c['department_code'],
                'Course Code:' : c['course_code'],
                'Section Number:' : c['section_number'],
                'Season:' : c['season'],
                'Year' : c['year']})
    return jsonify({'Schedule' : output})

@app.route('/<int:ucid>/scheduler/<string:scheduleName>/addCourse', methods=['GET','POST'])
def add_course_to_schedule(ucid, scheduleName):
    if request.method=='POST':
        depCode = request.form['depCode']
        courseCode = request.form['courseCode']
        secNum = request.form['sectionNumber']
        season = request.form['season']
        year = request.form['year']
        mongo.db.CoursesForSemester.insert_one({'department_code' : depCode,
                                               'course_code' : courseCode,
                                               'section_number' : secNum,
                                               'season' : season,
                                               'year' : year,
                                               'schedule_name' : scheduleName,
                                               'ucid' : ucid})
        output = []
        course = mongo.db.CoursesForSemester.find_one({'department_code' : depCode,
                                                        'course_code' : courseCode,
                                                        'section_number' : secNum,
                                                        'schedule_name' : scheduleName,
                                                        'ucid' : ucid})
        output.append({'Department Code:' : course['department_code'],
                       'Course Code:' : course['course_code'],
                       'Section Number:' : course['section_number'],
                       'Season:' : course['season'],
                       'Year' : course['year']})
        return jsonify({'Course has been added' : output})
    return render_template('addCourseInstance.html')

@app.route('/<int:ucid>/scheduler/<string:scheduleName>/deleteCourse', methods=['GET','POST'])
def delete_course_from_schedule(ucid, scheduleName):
    if request.method=='POST':
        depCode = request.form['depCode']
        courseCode = request.form['courseCode']
        secNum = request.form['sectionNumber']
        course = mongo.db.CoursesForSemester.find_one({'department_code' : depCode,
                                                    'course_code' : courseCode,
                                                    'section_number' : secNum,
                                                    'schedule_name' : scheduleName,
                                                    'ucid' : ucid})
        if course:
            mongo.db.CoursesForSemester.delete_one({'ucid' : ucid,
                                                    'schedule_name' : scheduleName,
                                                    'department_code' : depCode,
                                                    'course_code' : courseCode,
                                                    'section_number' : secNum})
            return "Course has been deleted"
        else:
            return "Course not found"
    return render_template('deleteCourseFromSchedule.html')

@app.route('/<int:ucid>/scheduler/<string:scheduleName>/GUI', methods=['GET','POST'])
def display_schedule_gui(ucid, scheduleName):
    return render_template('schedulerGUI.html')

if __name__ == "__main__":

    app.run(debug=True)

