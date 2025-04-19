from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
import mysql.connector
import openpyxl


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS quiz_app")
db.database = "quiz_app"


cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text VARCHAR(255),
    option1 VARCHAR(100),
    option2 VARCHAR(100),
    option3 VARCHAR(100),
    option4 VARCHAR(100),
    correct_option INT,
    subject VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    score INT,
    subject VARCHAR(100)
)
""")


cursor.execute("SELECT COUNT(*) FROM questions")
if cursor.fetchone()[0] == 0:
    sample_questions = [
    
    ("What keyword is used to define a function in Python?", "func", "def", "function", "define", 2, "python"),
    ("Which of the following is a Python data type?", "integer", "real", "decimal", "character", 1, "python"),
    ("How do you start a comment in Python?", "//", "#", "--", "/*", 2, "python"),
    ("What is the output of: print(2 ** 3)?", "6", "8", "9", "5", 2, "python"),
    ("Which of the following is used to create a list?", "{}", "[]", "()", "<>", 2, "python"),

   
    ("Which keyword is used to define a class in Java?", "function", "define", "class", "new", 3, "java"),
    ("Which method is the entry point in a Java program?", "start()", "init()", "main()", "run()", 3, "java"),
    ("Which of these is not a Java keyword?", "static", "Boolean", "void", "private", 2, "java"),
    ("Which symbol is used to end a statement in Java?", ".", ":", ";", "/", 3, "java"),
    ("Which of the following is used to create an object in Java?", "make", "new", "object", "create", 2, "java"),

    
    ("Which SQL keyword is used to retrieve data?", "GET", "SELECT", "FETCH", "SHOW", 2, "sql"),
    ("Which clause is used to filter records in SQL?", "ORDER BY", "GROUP BY", "WHERE", "FILTER", 3, "sql"),
    ("What does SQL stand for?", "Simple Query Language", "Structured Query List", "Structured Query Language", "System Query Language", 3, "sql"),
    ("Which command is used to remove all records from a table?", "DELETE", "REMOVE", "ERASE", "DROP", 1, "sql"),
    ("Which SQL function returns the number of rows?", "COUNT()", "SUM()", "TOTAL()", "ROWS()", 1, "sql"),

    
    ("Which symbol is used to end a statement in C?", ".", ";", ":", "!", 2, "c"),
    ("What is the correct syntax for 'main' function in C?", "function main()", "main()", "int main()", "start main()", 3, "c"),
    ("Which header file is required for printf() in C?", "stdlib.h", "stdio.h", "conio.h", "string.h", 2, "c"),
    ("Which of the following is a valid data type in C?", "text", "string", "int", "bool", 3, "c"),
    ("How do you start a comment in C?", "//", "#", "--", "/*", 1, "c"),
]

    cursor.executemany("""
    INSERT INTO questions (question_text, option1, option2, option3, option4, correct_option, subject)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, sample_questions)
    db.commit()


root = Tk()
root.title("Subject-wise Quiz App")
root.geometry("500x450")

current_question = 0
score = 0
user_name = ""
selected_option = IntVar()
selected_subject = ""
questions = []



def display_name_screen():
    for widget in root.winfo_children():
        widget.destroy()
    
    Label(root, text="Enter Your Name", font=("Arial", 14)).pack(pady=10)
    global name_entry
    name_entry = Entry(root, font=("Arial", 12))
    name_entry.pack(pady=10)

    Label(root, text="Select Subject", font=("Arial", 14)).pack(pady=10)
    global subject_var
    subject_var = StringVar()
    subject_var.set("python")
    subjects = ["Python", "Java","Sql","C"]
    OptionMenu(root, subject_var, *subjects).pack(pady=10)

    Button(root, text="Start Quiz", command=start_quiz).pack(pady=20)

def start_quiz():
    global user_name, selected_subject, questions, current_question, score
    user_name = name_entry.get().strip()
    selected_subject = subject_var.get()
    current_question = 0
    score = 0
    if not user_name:
        messagebox.showwarning("Name Required", "Please enter your name to start the quiz.")
        return

    cursor.execute("SELECT * FROM questions WHERE subject=%s", (selected_subject,))
    questions = cursor.fetchall()
    if not questions:
        messagebox.showerror("Error", f"No questions found for subject: {selected_subject}")
        return
    display_question()

def display_question():
    global selected_option
    for widget in root.winfo_children():
        widget.destroy()

    if current_question >= len(questions):
        show_result()
        return

    q = questions[current_question]
    options = [q[2], q[3], q[4], q[5]]

    Label(root, text=f"Question {current_question + 1}", font=("Arial", 12)).pack(pady=10)
    Label(root, text=q[1], font=("Arial", 12), wraplength=400).pack(pady=10)

    selected_option.set(-1)
    for i, opt in enumerate(options, 1):
        Radiobutton(root, text=opt, variable=selected_option, value=i).pack(anchor="w", padx=50)

    Button(root, text="Next", command=check_answer).pack(pady=20)

def check_answer():
    global current_question, score
    if selected_option.get() == -1:
        messagebox.showwarning("Warning", "Please select an option!")
        return
    if selected_option.get() == questions[current_question][6]:
        score += 1
    current_question += 1
    display_question()

def show_result():
    cursor.execute("INSERT INTO results (name, score, subject) VALUES (%s, %s, %s)", (user_name, score, selected_subject))
    db.commit()
    for widget in root.winfo_children():
        widget.destroy()

    Label(root, text="Quiz Completed!", font=("Arial", 16)).pack(pady=20)
    Label(root, text=f"{user_name}, Your Score: {score}/{len(questions)} ({selected_subject.title()})").pack(pady=10)
    Button(root, text="Download Certificate", command=generate_certificate).pack(pady=10)
    Button(root, text="Show All Scores", command=show_all_scores).pack(pady=5)
    Button(root, text="Download Excel", command=download_excel).pack(pady=5)
    Button(root, text="Restart Quiz", command=restart_quiz).pack(pady=10)
    Button(root, text="Exit", command=root.destroy).pack(pady=10)

def generate_certificate():
    if score >= len(questions) // 2:
        template_path = "quiz.jpg"  
        filename = f"{user_name}_certificate.jpeg"

        image = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("BRUSHSCI.TTF", 110)
        draw.text((775, 750), user_name, fill="black", font=font)
        image.save(filename, "JPEG")
        messagebox.showinfo("Certificate", f"Certificate saved as {filename}")
    else:
        messagebox.showerror("Warning", "You need at least 50% to get a certificate.")

def show_all_scores():
    for widget in root.winfo_children():
        widget.destroy()

    Label(root, text="All Participants and Scores", font=("Arial", 14)).pack(pady=10)
    cursor.execute("SELECT name, score, subject FROM results")
    all_results = cursor.fetchall()

    for name, score_val, subject in all_results:
        Label(root, text=f"{name} ({subject.title()}): {score_val}").pack()

    Button(root, text="Download Excel", command=download_excel).pack(pady=10)
    Button(root, text="Back to Menu", command=show_result).pack(pady=10)

def download_excel():
    cursor.execute("SELECT name, score, subject FROM results")
    all_results = cursor.fetchall()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Quiz Results"

    sheet.append(["Name", "Score", "Subject"])
    for name, score_val, subject in all_results:
        sheet.append([name, score_val, subject])

    filename = "quiz_results.xlsx"
    workbook.save(filename)
    messagebox.showinfo("Excel Downloaded", f"Results saved as {filename}")

def restart_quiz():
    global current_question, score
    current_question = 0
    score = 0
    display_name_screen()


display_name_screen()
root.mainloop() 