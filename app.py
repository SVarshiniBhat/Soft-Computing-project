from flask import Flask, render_template, request, session, redirect
import requests
from questions import questions
import random
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "secret123"


# 🎯 FILTER QUESTIONS
def get_filtered_questions():
    domain = (session.get("domain") or "").strip()
    language = (session.get("language") or "").strip()
    concept = (session.get("concept") or "").strip()

    filtered = []

    for q in questions:
        if q["domain"] == domain:

            if domain == "Programming":
                if q["language"] == language and q["concept"] == concept:
                    filtered.append(q)
            else:
                if q["concept"] == concept:
                    filtered.append(q)

    if len(filtered) == 0:
        return []

    return random.sample(filtered, min(10, len(filtered)))


# 🧠 LEVEL LOGIC
def get_level(score, total_questions):

    percentage = (score / total_questions) * 100

    if percentage <= 40:
        return "Beginner"

    elif percentage <= 70:
        return "Intermediate"

    else:
        return "Advanced"


# 🤖 AI RESULT FEEDBACK
def generate_ai_content(level, score):
    API_KEY = "YOUR_API_KEY"

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "AI Learning Project"
    }

    domain = session.get("domain")
    language = session.get("language") or "N/A"
    concept = session.get("concept")

    prompt = f"""
    A student took a {domain} quiz.

    Language: {language}
    Concept: {concept}
    Score: {score}
    Level: {level}

    Give:
    1. Feedback
    2. Topics to improve
    3. 3 practice questions
    """

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        return response.json()['choices'][0]['message']['content']
    except:
        return "AI response not available"


# 🤖 AI PRACTICE QUESTIONS
def generate_ai_practice():

    API_KEY = "YOUR_API_KEY"

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "AI Learning Project"
    }

    # DEFAULT QUIZ VALUES
    # IF USER CHANGES FILTERS -> USE NEW VALUES

    domain = (
        session.get("practice_domain")
        or session.get("domain")
    )

    language = (
        session.get("practice_language")
        or session.get("language")
        or "N/A"
    )

    concept = (
        session.get("practice_concept")
        or session.get("concept")
    )

    print(domain, language, concept)

    prompt = f"""
    You are an educational AI.

    Generate EXACTLY 1 MCQ question.

    STRICTLY follow the selected topic.

    Domain: {domain}
    Language: {language}
    Concept: {concept}

    IMPORTANT RULES:

    - Question MUST belong ONLY to the selected domain.
    - Do NOT mix topics from other domains.

    - If domain is UI/UX:
      ask ONLY UI/UX related questions.
      NEVER ask coding, Python, ML or Data Science questions.

    - If domain is Programming:
      ask ONLY programming questions.

    - If domain is Machine Learning:
      ask ONLY Machine Learning questions.

    - If domain is Data Science:
      ask ONLY Data Science questions.

    Generate a completely NEW and UNIQUE question.

    STRICT FORMAT:

    Question: ...

    A) ...
    B) ...
    C) ...

    Answer: A

    Explanation: ...

    Do not generate anything else.
    """

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    try:

        text = response.json()['choices'][0]['message']['content']

        lines = text.strip().split("\n")

        question = ""
        options = []
        answer = ""
        explanation = ""

        for line in lines:

            line = line.strip()

            if line.startswith("Question:"):

                question = line.replace(
                    "Question:",
                    ""
                ).strip()

            elif line.startswith(("A)", "B)", "C)")):

                options.append(line)

            elif line.startswith("Answer:"):

                answer = line.replace(
                    "Answer:",
                    ""
                ).strip()

            elif line.startswith("Explanation:"):

                explanation = line.replace(
                    "Explanation:",
                    ""
                ).strip()

        return {
            "question": question,
            "options": options,
            "answer": answer,
            "explanation": explanation
        }

    except Exception as e:

        print(e)

        return {
            "question": "AI not available",
            "options": [],
            "answer": "",
            "explanation": ""
        }


# ROUTES
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("quiz_app.db")

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["username"] = username

            return redirect("/setup")

        else:

            message = "Invalid username or password"

    return render_template(
        "login.html",
        message=message
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # PASSWORD MATCH CHECK
        if password != confirm_password:

            message = "Passwords do not match"

            return render_template(
                "register.html",
                message=message
            )

        # PASSWORD LENGTH
        if len(password) < 8:

            message = "Password must contain at least 8 characters"

            return render_template(
                "register.html",
                message=message
            )

        # UPPERCASE CHECK
        if not re.search(r"[A-Z]", password):

            message = "Password must contain an uppercase letter"

            return render_template(
                "register.html",
                message=message
            )

        # LOWERCASE CHECK
        if not re.search(r"[a-z]", password):

            message = "Password must contain a lowercase letter"

            return render_template(
                "register.html",
                message=message
            )

        # NUMBER CHECK
        if not re.search(r"[0-9]", password):

            message = "Password must contain a number"

            return render_template(
                "register.html",
                message=message
            )

        # SYMBOL CHECK
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):

            message = "Password must contain a special symbol"

            return render_template(
                "register.html",
                message=message
            )

        conn = sqlite3.connect("quiz_app.db")

        cursor = conn.cursor()

        # CHECK EXISTING USER
        cursor.execute(
            "SELECT * FROM users WHERE username=? OR email=?",
            (username, email)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            conn.close()

            message = "Username or Email already exists"

            return render_template(
                "register.html",
                message=message
            )

        # INSERT USER
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template(
        "register.html",
        message=message
    )


@app.route("/setup")
def setup():
    return render_template("setup.html")


@app.route("/quiz/<int:qno>", methods=["GET", "POST"])
def quiz_question(qno):

    if qno == 0:
        session["domain"] = request.args.get("domain")
        session["language"] = request.args.get("language")
        session["concept"] = request.args.get("concept")
        session["level"] = request.args.get("level")
        session["answers"] = []
        session["quiz_questions"] = get_filtered_questions()

    quiz_questions = session.get("quiz_questions", [])

    if request.method == "POST":
        ans = request.form.get("answer")
        answers = session.get("answers", [])
        answers.append(ans)
        session["answers"] = answers

    if qno >= len(quiz_questions):
        return redirect("/result")

    question = quiz_questions[qno]

    return render_template("quiz_single.html", question=question, qno=qno)

@app.route("/result")
def result():

    answers = session.get("answers", [])
    quiz_questions = session.get("quiz_questions", [])

    score = 0

    for i, ans in enumerate(answers):

        if i < len(quiz_questions) and ans == quiz_questions[i]["answer"]:
            score += 1

    review_data = []

    for i, ans in enumerate(answers):

        if i < len(quiz_questions):

            review_data.append({
                "question": quiz_questions[i]["question"],
                "selected": ans,
                "correct": quiz_questions[i]["answer"]
            })

    total_questions = len(quiz_questions)

    percentage = round((score / total_questions) * 100)

    level = get_level(score, total_questions)

    # STORE ANALYTICS DATA

    if "analytics_data" not in session:
        session["analytics_data"] = []

    session["analytics_data"].append({

        "domain": session.get("domain"),

        "concept": session.get("concept"),

        "score": percentage

    })

    # STORE SUMMARY

    session["last_score"] = score

    session["percentage"] = percentage

    session["current_level"] = level

    session["strong_area"] = session.get("concept")

    if percentage >= 70:

        session["weak_area"] = "Minor Improvements Needed"

    else:

        session["weak_area"] = "Needs Improvement"

    ai_output = generate_ai_content(level, score)

    return render_template(
        "result.html",
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        level=level,
        ai_output=ai_output,
        review_data=review_data
    )
    

@app.route("/practice", methods=["GET", "POST"])
def practice():

    # FILTER CHANGE / NEW QUESTION
    if request.method == "GET":

        # UPDATE SESSION VALUES
        session["practice_domain"] = request.args.get(
            "domain"
        ) or session.get("practice_domain")

        session["practice_language"] = request.args.get(
            "language"
        ) or session.get("practice_language")

        session["practice_concept"] = request.args.get(
            "concept"
        ) or session.get("practice_concept")

        # GENERATE NEW QUESTION
        ai_question = generate_ai_practice()

        session["correct_answer"] = ai_question["answer"]

        session["explanation"] = ai_question["explanation"]

        session["current_question"] = ai_question

        return render_template(
            "practice.html",
            question=ai_question,
            show_result=False
        )

    # ANSWER SUBMIT
    selected = request.form.get("selected_answer")

    correct = session.get("correct_answer")

    if selected == correct:

        feedback = "✅ Correct Answer!"

    else:

        feedback = (
            f"❌ Wrong Answer! "
            f"Correct answer is {correct}"
        )

    return render_template(
        "practice.html",
        feedback=feedback,
        explanation=session.get("explanation"),
        show_result=True,
        question=session.get("current_question")
    )

@app.route("/review")
def review():

    answers = session.get("answers", [])
    quiz_questions = session.get("quiz_questions", [])

    review_data = []

    for i, ans in enumerate(answers):

        if i < len(quiz_questions):

            review_data.append({
                "question": quiz_questions[i]["question"],
                "selected": ans,
                "correct": quiz_questions[i]["answer"]
            })

    return render_template(
        "review.html",
        review_data=review_data
    )

if __name__ == "__main__":
    app.run(debug=True)