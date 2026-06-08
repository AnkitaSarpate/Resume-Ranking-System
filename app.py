from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import re
import json
import matplotlib
matplotlib.use('Agg')  # Prevent backend errors
import matplotlib.pyplot as plt
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "secret_key"

# -------------------------
# Predefined Technical Skills
# -------------------------
SKILLS = [
    "Python", "Java", "C++", "SQL", "HTML", "CSS", "JavaScript",
    "Flask", "Django", "Docker", "AWS", "Kubernetes", "Machine", "Learning",
    "Data", "Analysis", "React", "Node.js", "Excel", "Power", "BI"
]

# -------------------------
# Fake login credentials
# -------------------------
users = {"admin": "password123"}

# -------------------------
# Skill Extraction Function
# -------------------------
def extract_skills(text):
    words = text.split()
    found_skills = []
    for word in words:
        clean_word = word.strip(",.()").capitalize()
        if clean_word in SKILLS:
            found_skills.append(clean_word)
    return list(set(found_skills))  # Unique skills only

# -------------------------
# Resume Ranking Function
# -------------------------
def rank_resumes(job_description, resumes):
    ranked = []
    jd_words = job_description.split()

    for idx, resume in enumerate(resumes, start=1):
        skills = extract_skills(resume["content"])
        experience_match = re.findall(r'(\d+)\s+years?', resume["content"])
        exp = int(experience_match[0]) if experience_match else 0
        
        # Fallbacks
        name = resume.get("name", "Unknown")
        email = resume.get("email", "Not provided")
        phone = resume.get("phone", "Not provided")
        skills_str = ", ".join(skills) if skills else "No skills found"
        
        score = len(set(jd_words) & set(resume["content"].split())) + exp

        ranked.append({
            "srno": idx,
            "name": name,
            "email": email,
            "phone": phone,
            "experience": f"{exp} years" if exp else "Not mentioned",
            "skills": skills_str,
            "score": score
        })

    # Sort by score
    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)
    
     # Normalize to 0–100
    if ranked:
        max_score = ranked[0]["score"]
        if max_score > 0:
            for r in ranked:
                r["score"] = int((r["score"] / max_score) * 100)
                
    # Generate Bar Chart
    names = [r["name"] for r in ranked]
    scores = [r["score"] for r in ranked]

    plt.figure(figsize=(8, 5))
    plt.bar(names, scores, color="skyblue")
    plt.title("Resume Ranking Results")
    plt.xlabel("Candidates")
    plt.ylabel("Match Score")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    chart_path = os.path.join("static", "ranking_chart.png")
    plt.savefig(chart_path)
    plt.close()
    
    print("DEBUG SCORES:", [r["score"] for r in ranked])

    return ranked

# -------------------------
# Routes
# -------------------------

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", username=session["user"])

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Load users.json
        with open("users.json", "r") as f:
            users = json.load(f)

        # Check user
        if username in users:
            stored_pw = users[username]
            # If password is encrypted, check with hash
            if stored_pw.startswith("scrypt:"):
                from werkzeug.security import check_password_hash
                if check_password_hash(stored_pw, password):
                    session["user"] = username
                    return redirect(url_for("home"))
            # If password is plain text
            elif stored_pw == password:
                session["user"] = username
                return redirect(url_for("home"))

        flash("Invalid credentials!")  # Wrong username/password
    return render_template("login.html")



@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    resumes = []
    ranked_resumes = []

    if request.method == "POST":
        job_description = request.form.get("job_description", "")

        uploaded_files = request.files.getlist("resumes")

        for file in uploaded_files:
            content = file.read().decode("utf-8")
            resumes.append({
                "name": file.filename.replace(".txt", ""),
                "content": content,
                "email": re.search(r'[\w\.-]+@[\w\.-]+', content).group(0) if re.search(r'[\w\.-]+@[\w\.-]+', content) else "N/A",
                "phone": re.search(r'\d{10}', content).group(0) if re.search(r'\d{10}', content) else "N/A"
            })

        ranked_resumes = rank_resumes(job_description, resumes)

        return render_template("results.html", resumes=ranked_resumes)

    return render_template("upload.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)

