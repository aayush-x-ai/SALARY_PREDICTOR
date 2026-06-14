import os
from functools import wraps

import mysql.connector
from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from mysql.connector import Error, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from model.train_model import SalaryPredictor


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")
app.config["DB_HOST"] = os.getenv("DB_HOST", "localhost")
app.config["DB_PORT"] = int(os.getenv("DB_PORT", "3306"))
app.config["DB_USER"] = os.getenv("DB_USER", "root")
app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "root")
app.config["DB_NAME"] = os.getenv("DB_NAME", "salary_predictor")

salary_model = SalaryPredictor("model/dataset.csv")

EDUCATION_OPTIONS = ["Diploma", "B.Sc", "BCA", "B.Tech", "MCA", "M.Tech", "MBA"]
CITY_OPTIONS = ["Bangalore", "Chennai", "Delhi", "Hyderabad", "Mumbai", "Pune"]
DOMAIN_OPTIONS = [
    "Artificial Intelligence",
    "Data Science",
    "Software Development",
    "Web Development",
]
ROLE_OPTIONS = [
    "AI Engineer",
    "Data Analyst",
    "Data Scientist",
    "ML Engineer",
    "Software Developer",
    "Web Developer",
]


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=app.config["DB_HOST"],
            port=app.config["DB_PORT"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
            database=app.config["DB_NAME"],
        )
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please log in to use the salary predictor.", "info")
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


@app.context_processor
def inject_current_user():
    return {"current_user": session.get("user_name")}


@app.errorhandler(Error)
def handle_database_error(error):
    app.logger.error("Database error: %s", error)
    return (
        render_template(
            "error.html",
            title="Database unavailable",
            message=(
                "The app could not connect to MySQL. Check your database settings "
                "and run database.sql before trying again."
            ),
        ),
        500,
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("predictor"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif len(password) < 6:
            flash("Password must contain at least 6 characters.", "error")
        else:
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, generate_password_hash(password)),
                )
                db.commit()
                user_id = cursor.lastrowid
                cursor.close()
                session.clear()
                session["user_id"] = user_id
                session["user_name"] = name
                flash("Account created successfully. Welcome!", "success")
                return redirect(url_for("predictor"))
            except IntegrityError:
                flash("An account with this email already exists.", "error")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("predictor"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, name, password FROM users WHERE email = %s", (email,)
        )
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("predictor"))

        flash("Incorrect email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/predictor")
@login_required
def predictor():
    return render_template(
        "predictor.html",
        educations=EDUCATION_OPTIONS,
        cities=CITY_OPTIONS,
        domains=DOMAIN_OPTIONS,
        roles=ROLE_OPTIONS,
    )


@app.route("/result", methods=["POST"])
@login_required
def result():
    education = request.form.get("education", "").strip()
    skills = request.form.get("skills", "").strip()
    city = request.form.get("city", "").strip()
    domain = request.form.get("domain", "").strip()
    job_role = request.form.get("job_role", "").strip()

    try:
        experience_months = int(request.form.get("experience_months", "0"))
    except ValueError:
        experience_months = -1

    valid_choice = (
        education in EDUCATION_OPTIONS
        and city in CITY_OPTIONS
        and domain in DOMAIN_OPTIONS
        and job_role in ROLE_OPTIONS
    )
    if not valid_choice or not skills or not 0 <= experience_months <= 600:
        flash("Please enter valid information in every field.", "error")
        return redirect(url_for("predictor"))

    prediction = salary_model.predict(
        education=education,
        skills=skills,
        experience_months=experience_months,
        city=city,
        domain=domain,
        job_role=job_role,
    )

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO predictions
            (user_id, education, skills, experience_months, city, domain,
             job_role, predicted_salary)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            session["user_id"],
            education,
            skills,
            experience_months,
            city,
            domain,
            job_role,
            prediction["salary"],
        ),
    )
    db.commit()
    prediction_id = cursor.lastrowid
    cursor.close()

    return render_template(
        "result.html",
        prediction_id=prediction_id,
        education=education,
        skills=skills,
        experience_months=experience_months,
        city=city,
        domain=domain,
        job_role=job_role,
        prediction=prediction,
    )


@app.route("/history")
@login_required
def history():
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(
        """
        SELECT prediction_id, job_role, city, domain, experience_months,
               predicted_salary, prediction_date
        FROM predictions
        WHERE user_id = %s
        ORDER BY prediction_date DESC
        """,
        (session["user_id"],),
    )
    predictions = cursor.fetchall()
    cursor.close()
    return render_template("history.html", predictions=predictions)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1")
