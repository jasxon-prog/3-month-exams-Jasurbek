import sqlite3

connection = sqlite3.connect('.kurs.db')
cursor = connection.cursor()

def create_course():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Course(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name VARCHAR(200),
        course_price INTEGER,
        description TEXT,
        teacher_info TEXT
    )
    """)
    connection.commit()

def insert_course(course_name, course_price, description, teacher_info):
    cursor.execute(
        'INSERT INTO Course (course_name, course_price, description, teacher_info) VALUES (?, ?, ?, ?)', 
        (course_name, course_price, description, teacher_info)
    )
    connection.commit()  

def fetch_course_by_id():
    cursor.execute("SELECT * FROM Course")
    course = cursor.fetchall()
    connection.commit()
    return course 