from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DATABASE = "college.db"


# ==========================================
# CREATE DATABASE AND TABLES
# ==========================================
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create Students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            StudentID INTEGER PRIMARY KEY,
            Name TEXT,
            Program TEXT,
            Department TEXT,
            Semester INTEGER,
            Email TEXT,
            CGPA REAL
        )
    ''')

    # Create Courses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Courses (
            CourseID TEXT PRIMARY KEY,
            CourseName TEXT,
            CreditHours INTEGER
        )
    ''')

    # Create Faculty table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Faculty (
            FacultyID INTEGER PRIMARY KEY,
            Name TEXT,
            Designation TEXT,
            Department TEXT
        )
    ''')

    # Create Programs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Programs (
            ProgramID INTEGER PRIMARY KEY,
            ProgramName TEXT,
            Duration TEXT
        )
    ''')

    # Create Admissions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Admissions (
            AdmissionID INTEGER PRIMARY KEY,
            Program TEXT,
            Fee INTEGER,
            Duration TEXT,
            Eligibility TEXT,
            LastDate TEXT
        )
    ''')

    # NEW: Create StudentCourses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS StudentCourses (
            StudentID INTEGER,
            CourseID TEXT,
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
            FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
        )
    ''')

    # Clear old data and insert fresh data
    c.execute("DELETE FROM Students")
    c.execute("DELETE FROM Courses")
    c.execute("DELETE FROM Faculty")
    c.execute("DELETE FROM Programs")
    c.execute("DELETE FROM Admissions")
    c.execute("DELETE FROM StudentCourses")

    # Insert sample Students
    students = [
        (1, "Ali", "BSCS", "Computer Science", 4, "ali@iqra.edu", 3.5),
        (2, "Ahmed", "BBA", "Business", 3, "ahmed@iqra.edu", 3.2),
        (3, "Sara", "BSSE", "Software Engineering", 5, "sara@iqra.edu", 3.8),
        (4, "Bilal", "BSCS", "Computer Science", 2, "bilal@iqra.edu", 2.9),
        (5, "Hina", "BBA", "Business", 6, "hina@iqra.edu", 3.6),
        (6, "Usman", "BSIT", "IT", 4, "usman@iqra.edu", 3.1),
        (7, "Ayesha", "BSCS", "Computer Science", 7, "ayesha@iqra.edu", 3.9),
        (8, "Farhan", "BSSE", "Software Engineering", 3, "farhan@iqra.edu", 2.8),
        (9, "Maria", "BBA", "Business", 5, "maria@iqra.edu", 3.4),
        (10, "Kamran", "BSIT", "IT", 6, "kamran@iqra.edu", 3.0)
    ]

    # Insert sample Courses
    courses = [
        ("CS101", "Database Systems", 3),
        ("CS102", "Programming", 3),
        ("CS103", "Web Development", 3),
        ("BA101", "Accounting", 3),
        ("SE101", "Software Engineering", 3),
        ("IT101", "Networking", 3),
        ("CS104", "Data Structures", 3),
        ("BA102", "Marketing", 3),
        ("SE102", "Human Computer Interaction", 3),
        ("IT102", "Operating System", 3)
    ]

    # Insert sample Faculty
    faculty = [
        (1, "Sir Khan", "Professor", "Computer Science"),
        (2, "Sir Ahmed", "Lecturer", "Business"),
        (3, "Mam Fatima", "Professor", "Software Engineering"),
        (4, "Sir Raza", "Lecturer", "IT"),
        (5, "Mam Aisha", "Professor", "Computer Science")
    ]

    # Insert sample Programs
    programs = [
        (1, "BSCS", "4 Years"),
        (2, "BBA", "4 Years"),
        (3, "BSSE", "4 Years"),
        (4, "BSIT", "4 Years"),
        (5, "MBA", "2 Years")
    ]

    # Insert sample Admissions
    admissions = [
        (1, "BSCS", 5000, "4 Years", "Intermediate with Math", "30-Aug"),
        (2, "BBA", 4500, "4 Years", "Intermediate", "25-Aug"),
        (3, "BSSE", 5200, "4 Years", "Intermediate with Math", "28-Aug"),
        (4, "BSIT", 4800, "4 Years", "Intermediate", "22-Aug"),
        (5, "MBA", 8000, "2 Years", "Graduation", "15-Sep")
    ]

    # NEW: Insert sample StudentCourses
    student_courses = [
        (1, "CS101"), (1, "CS102"),
        (2, "BA101"), (2, "BA102"),
        (3, "SE101"), (3, "CS101"),
        (4, "CS102"), (4, "CS104"),
        (5, "BA101"),
        (6, "IT101"),
        (7, "CS101"), (7, "CS103"),
        (8, "SE101"), (8, "SE102"),
        (9, "BA102"),
        (10, "IT101"), (10, "IT102")
    ]

    c.executemany("INSERT INTO Students VALUES (?,?,?,?,?,?,?)", students)
    c.executemany("INSERT INTO Courses VALUES (?,?,?)", courses)
    c.executemany("INSERT INTO Faculty VALUES (?,?,?,?)", faculty)
    c.executemany("INSERT INTO Programs VALUES (?,?,?)", programs)
    c.executemany("INSERT INTO Admissions VALUES (?,?,?,?,?,?)", admissions)
    c.executemany("INSERT INTO StudentCourses VALUES (?,?)", student_courses)

    conn.commit()
    conn.close()


# Helper function to get database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# HOME PAGE
# ==========================================
@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# CHATBOT - Returns plain text for JavaScript
# ==========================================
@app.route("/chat", methods=["POST"])
def chat():
    msg = request.form.get("message", "").lower()
    conn = get_db()
    c = conn.cursor()
    answer = "Sorry, I don't understand. Try asking about fee, admissions, courses, faculty, students, or programs."

    # Question 1: Admission fee
    if "fee" in msg or "admission fee" in msg:
        program = None
        for p in ["bscs", "bba", "bsse", "bsit", "mba"]:
            if p in msg:
                program = p.upper()
                break
        if program:
            c.execute("SELECT Fee FROM Admissions WHERE Program = ?", (program,))
            row = c.fetchone()
            if row:
                answer = f"The admission fee for {program} is {row['Fee']}."

    # Question 2: Show all admissions
    elif "admission" in msg:
        c.execute("SELECT * FROM Admissions")
        rows = c.fetchall()
        if rows:
            answer = "Admissions information:\n\n"
            for r in rows:
                answer += f"{r['Program']}: Fee {r['Fee']}, Last Date {r['LastDate']}\n"

    # NEW Question 3: Courses of a specific student
    elif "course of" in msg or "courses of" in msg:
        words = msg.replace("?", "").replace(".", "").split()
        if "of" in words and len(words) > words.index("of") + 1:
            student_name = words[words.index("of") + 1].capitalize()
            c.execute('''
                SELECT Courses.CourseName 
                FROM Students 
                JOIN StudentCourses ON Students.StudentID = StudentCourses.StudentID
                JOIN Courses ON StudentCourses.CourseID = Courses.CourseID
                WHERE Students.Name = ?
            ''', (student_name,))
            rows = c.fetchall()
            if rows:
                answer = f"Courses of {student_name}:\n\n"
                for r in rows:
                    answer += f"- {r['CourseName']}\n"
            else:
                answer = f"No courses found for {student_name}."

    # Question 4: Show all courses
    elif "course" in msg:
        c.execute("SELECT * FROM Courses")
        rows = c.fetchall()
        answer = "Available Courses:\n\n"
        for r in rows:
            answer += f"{r['CourseID']}: {r['CourseName']}\n"

    # Question 5: Show faculty
    elif "faculty" in msg or "teacher" in msg:
        c.execute("SELECT * FROM Faculty")
        rows = c.fetchall()
        answer = "Faculty Members:\n\n"
        for r in rows:
            answer += f"{r['Name']} - {r['Designation']} ({r['Department']})\n"

    # Question 6: Show students
    elif "student" in msg:
        c.execute("SELECT * FROM Students")
        rows = c.fetchall()
        answer = "Students List:\n\n"
        for r in rows:
            answer += f"{r['StudentID']} - {r['Name']} ({r['Program']})\n"

    # Question 7: Programs
    elif "program" in msg:
        c.execute("SELECT * FROM Programs")
        rows = c.fetchall()
        answer = "Programs Offered:\n\n"
        for r in rows:
            answer += f"{r['ProgramName']} - {r['Duration']}\n"

    conn.close()
    return answer


# ==========================================
# ADMIN PANEL
# ==========================================
@app.route("/admin")
def admin():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM Students")
    students = c.fetchall()
    c.execute("SELECT * FROM Admissions")
    admissions = c.fetchall()
    conn.close()
    return render_template("admin.html", students=students, admissions=admissions)


# Add Student
@app.route("/add_student", methods=["POST"])
def add_student():
    sid = request.form["sid"]
    name = request.form["name"]
    program = request.form["program"]
    dept = request.form["dept"]
    semester = request.form["semester"]
    email = request.form["email"]
    cgpa = request.form["cgpa"]

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO Students VALUES (?,?,?,?,?,?,?)", 
              (sid, name, program, dept, semester, email, cgpa))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# Update Student
@app.route("/update_student", methods=["POST"])
def update_student():
    sid = request.form["sid"]
    name = request.form["name"]
    program = request.form["program"]
    dept = request.form["dept"]
    semester = request.form["semester"]
    email = request.form["email"]
    cgpa = request.form["cgpa"]

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        UPDATE Students 
        SET Name=?, Program=?, Department=?, Semester=?, Email=?, CGPA=?
        WHERE StudentID=?
    ''', (name, program, dept, semester, email, cgpa, sid))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# Delete Student
@app.route("/delete_student/<int:sid>")
def delete_student(sid):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM Students WHERE StudentID = ?", (sid,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# Search Student
@app.route("/search_student", methods=["POST"])
def search_student():
    name = request.form["name"]
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM Students WHERE Name LIKE ?", ('%' + name + '%',))
    results = c.fetchall()
    c.execute("SELECT * FROM Admissions")
    admissions = c.fetchall()
    conn.close()
    return render_template("admin.html", students=results, admissions=admissions)


# Add Admission
@app.route("/add_admission", methods=["POST"])
def add_admission():
    aid = request.form["aid"]
    program = request.form["program"]
    fee = request.form["fee"]
    duration = request.form["duration"]
    eligibility = request.form["eligibility"]
    lastdate = request.form["lastdate"]

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO Admissions VALUES (?,?,?,?,?,?)", 
              (aid, program, fee, duration, eligibility, lastdate))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# Update Admission
@app.route("/update_admission", methods=["POST"])
def update_admission():
    aid = request.form["aid"]
    program = request.form["program"]
    fee = request.form["fee"]
    duration = request.form["duration"]
    eligibility = request.form["eligibility"]
    lastdate = request.form["lastdate"]

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        UPDATE Admissions 
        SET Program=?, Fee=?, Duration=?, Eligibility=?, LastDate=?
        WHERE AdmissionID=?
    ''', (program, fee, duration, eligibility, lastdate, aid))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# Delete Admission
@app.route("/delete_admission/<int:aid>")
def delete_admission(aid):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM Admissions WHERE AdmissionID = ?", (aid,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# ==========================================
# OTHER PAGES
# ==========================================
@app.route("/database")
def database():
    conn = get_db()
    c = conn.cursor()

    # Get all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()

    data = {}
    for table in tables:
        table_name = table["name"]
        c.execute(f"SELECT * FROM {table_name}")
        data[table_name] = c.fetchall()

    conn.close()
    return render_template("database.html", tables=tables, data=data)


@app.route("/admissions")
def admissions():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM Admissions")
    rows = c.fetchall()
    conn.close()
    return render_template("admissions.html", admissions=rows)


@app.route("/students")
def students():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM Students")
    rows = c.fetchall()
    conn.close()
    return render_template("students.html", students=rows)


@app.route("/queries")
def queries():
    return render_template("queries.html")


# ==========================================
# RUN THE APP
# ==========================================
# Initialize database when app starts (needed for Render)
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)