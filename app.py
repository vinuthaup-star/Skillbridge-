from flask import Flask, render_template, request, redirect, session
import sqlite3
from urllib.parse import quote

app = Flask(__name__)

app.secret_key = "skillbridge-secret-key"


# -------------------------------------------------
# DATABASE
# -------------------------------------------------

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_db()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            education TEXT,
            skills TEXT,
            phone TEXT,
            location TEXT,
            bio TEXT
        )
    """)

    # Resume table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            full_name TEXT,
            phone TEXT,
            email TEXT,
            education TEXT,
            skills TEXT,
            experience TEXT,
            projects TEXT,
            achievements TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Saved jobs table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            job_id INTEGER,
            UNIQUE(user_id, job_id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# DEMO JOB DATA
# -------------------------------------------------

JOBS = [

    {
        "id": 1,
        "company": "SkillBridge Demo Company",
        "role": "Python Developer Intern",
        "location": "Remote",
        "skills": "Python, Flask, SQL",
        "type": "Internship",
        "description": "Sample internship opportunity for students learning Python.",
        "url": "https://www.linkedin.com/jobs/"
    },

    {
        "id": 2,
        "company": "Tech Demo Solutions",
        "role": "Web Development Intern",
        "location": "Bengaluru, India",
        "skills": "HTML, CSS, JavaScript",
        "type": "Internship",
        "description": "Sample web development opportunity for beginners.",
        "url": "https://www.linkedin.com/jobs/"
    },

    {
        "id": 3,
        "company": "Digital Skills Demo",
        "role": "Junior Java Developer",
        "location": "Hyderabad, India",
        "skills": "Java, SQL, Git",
        "type": "Entry Level",
        "description": "Sample entry-level Java opportunity.",
        "url": "https://www.linkedin.com/jobs/"
    },

    {
        "id": 4,
        "company": "Data Demo Labs",
        "role": "Data Analyst Intern",
        "location": "Remote",
        "skills": "Python, Excel, SQL",
        "type": "Internship",
        "description": "Sample data analytics opportunity.",
        "url": "https://www.linkedin.com/jobs/"
    },

    {
        "id": 5,
        "company": "Creative Web Demo",
        "role": "Frontend Developer Intern",
        "location": "Mumbai, India",
        "skills": "HTML, CSS, JavaScript",
        "type": "Internship",
        "description": "Sample frontend development opportunity.",
        "url": "https://www.linkedin.com/jobs/"
    }

]


# -------------------------------------------------
# HOME
# -------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -------------------------------------------------
# REGISTER
# -------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        education = request.form.get("education", "").strip()
        skills = request.form.get("skills", "").strip()

        if not name or not email or not password:

            return "Please fill in all required fields."

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO users
                (name, email, password, education, skills)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    password,
                    education,
                    skills
                )
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            conn.close()

            return "This email is already registered."


    return render_template("register.html")


# -------------------------------------------------
# LOGIN
# -------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ? AND password = ?
            """,
            (email, password)
        ).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect("/dashboard")

        return "Invalid email or password."


    return render_template("login.html")


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )


# -------------------------------------------------
# SEARCH
# -------------------------------------------------

@app.route("/search")
def search():

    if "user_id" not in session:

        return redirect("/login")

    query = request.args.get("q", "").strip()

    return render_template(
        "search.html",
        query=query
    )


# -------------------------------------------------
# SKILLS
# -------------------------------------------------

@app.route("/skills")
def skills():

    if "user_id" not in session:

        return redirect("/login")

    skill = request.args.get("skill", "").strip()

    resources = []

    if skill:

        encoded_skill = quote(skill)

        resources = [

            {
                "title": f"Learn {skill} - Beginner",
                "description": f"Start learning the basics of {skill}.",
                "url":
                    f"https://www.youtube.com/results?search_query="
                    f"{encoded_skill}+for+beginners"
            },

            {
                "title": f"{skill} Tutorial",
                "description": f"Find tutorials and practical lessons about {skill}.",
                "url":
                    f"https://www.youtube.com/results?search_query="
                    f"{encoded_skill}+tutorial"
            },

            {
                "title": f"{skill} Projects",
                "description": f"Practice {skill} by building projects.",
                "url":
                    f"https://www.youtube.com/results?search_query="
                    f"{encoded_skill}+projects"
            }

        ]

    return render_template(
        "skills.html",
        skill=skill,
        resources=resources
    )


# -------------------------------------------------
# YOUTUBE
# -------------------------------------------------

@app.route("/youtube")
def youtube():

    if "user_id" not in session:

        return redirect("/login")

    query = request.args.get("q", "").strip()

    video_url = ""

    if query:

        video_url = (
            "https://www.youtube.com/results?search_query="
            + quote(query)
        )

    return render_template(
        "youtube.html",
        query=query,
        video_url=video_url
    )


# -------------------------------------------------
# JOBS
# -------------------------------------------------

@app.route("/jobs")
def jobs():

    if "user_id" not in session:

        return redirect("/login")

    query = request.args.get("q", "").strip().lower()

    if query:

        filtered_jobs = []

        for job in JOBS:

            searchable_text = (
                job["company"]
                + " "
                + job["role"]
                + " "
                + job["location"]
                + " "
                + job["skills"]
                + " "
                + job["type"]
            ).lower()

            if query in searchable_text:

                filtered_jobs.append(job)

    else:

        filtered_jobs = JOBS


    return render_template(
        "jobs.html",
        jobs=filtered_jobs,
        query=query
    )


# -------------------------------------------------
# SAVE JOB
# -------------------------------------------------

@app.route("/save-job/<int:job_id>")
def save_job(job_id):

    if "user_id" not in session:

        return redirect("/login")

    user_id = session["user_id"]

    valid_job = None

    for job in JOBS:

        if job["id"] == job_id:

            valid_job = job
            break

    if valid_job:

        conn = get_db()

        conn.execute(
            """
            INSERT OR IGNORE INTO saved_jobs
            (user_id, job_id)
            VALUES (?, ?)
            """,
            (user_id, job_id)
        )

        conn.commit()
        conn.close()

    return redirect(request.referrer or "/jobs")


# -------------------------------------------------
# REMOVE SAVED JOB
# -------------------------------------------------

@app.route("/remove-saved-job/<int:job_id>")
def remove_saved_job(job_id):

    if "user_id" not in session:

        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db()

    conn.execute(
        """
        DELETE FROM saved_jobs
        WHERE user_id = ? AND job_id = ?
        """,
        (user_id, job_id)
    )

    conn.commit()
    conn.close()

    return redirect(request.referrer or "/saved-jobs")


# -------------------------------------------------
# SAVED JOBS
# -------------------------------------------------

@app.route("/saved-jobs")
def saved_jobs():

    if "user_id" not in session:

        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db()

    saved_rows = conn.execute(
        """
        SELECT job_id
        FROM saved_jobs
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    saved_ids = [row["job_id"] for row in saved_rows]

    saved_jobs_list = []

    for job in JOBS:

        if job["id"] in saved_ids:

            saved_jobs_list.append(job)

    return render_template(
        "saved_jobs.html",
        jobs=saved_jobs_list
    )


# -------------------------------------------------
# PROFILE
# -------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:

        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        education = request.form.get("education", "").strip()
        skills = request.form.get("skills", "").strip()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()
        bio = request.form.get("bio", "").strip()

        conn.execute(
            """
            UPDATE users
            SET name = ?,
                education = ?,
                skills = ?,
                phone = ?,
                location = ?,
                bio = ?
            WHERE id = ?
            """,
            (
                name,
                education,
                skills,
                phone,
                location,
                bio,
                user_id
            )
        )

        conn.commit()

        session["user_name"] = name

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )


# -------------------------------------------------
# RESUME
# -------------------------------------------------

@app.route("/resume", methods=["GET", "POST"])
def resume():

    if "user_id" not in session:

        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db()

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        education = request.form.get("education", "").strip()
        skills = request.form.get("skills", "").strip()
        experience = request.form.get("experience", "").strip()
        projects = request.form.get("projects", "").strip()
        achievements = request.form.get("achievements", "").strip()

        conn.execute(
            """
            INSERT INTO resumes
            (
                user_id,
                full_name,
                phone,
                email,
                education,
                skills,
                experience,
                projects,
                achievements
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                full_name = excluded.full_name,
                phone = excluded.phone,
                email = excluded.email,
                education = excluded.education,
                skills = excluded.skills,
                experience = excluded.experience,
                projects = excluded.projects,
                achievements = excluded.achievements
            """,
            (
                user_id,
                full_name,
                phone,
                email,
                education,
                skills,
                experience,
                projects,
                achievements
            )
        )

        conn.commit()

    resume_data = conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "resume.html",
        resume=resume_data
    )


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# -------------------------------------------------
# START APPLICATION
# -------------------------------------------------

if __name__ == "__main__":

    create_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
