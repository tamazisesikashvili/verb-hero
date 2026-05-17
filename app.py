from flask import Flask, render_template, request, session, redirect, url_for
import json
import random

# --- App Setup ---
app = Flask(__name__)
app.secret_key = "luka_verbs_secret_123"  # Needed to use sessions (storing data per user)

# --- Load Verbs ---
def load_verbs():
    """Read the verbs from our JSON file and return them."""
    with open("verbs.json", "r") as f:
        data = json.load(f)
    return data["levels"]

LEVELS = load_verbs()  # Load once when the app starts

# Minimum score percentage needed to unlock the next level
PASS_PERCENT = 70


# --- Helper Functions ---
def get_level(level_number):
    """Return a single level by its number."""
    for level in LEVELS:
        if level["level"] == level_number:
            return level
    return None

def all_verbs():
    """Return a flat list of all verbs from all levels."""
    verbs = []
    for level in LEVELS:
        verbs.extend(level["verbs"])
    return verbs

def get_unlocked_levels():
    """Return a list of level numbers the player has unlocked.
    Level 1 is always unlocked. Each other level unlocks when
    the previous level is completed with 70% or more."""
    if "completed_levels" not in session:
        session["completed_levels"] = []

    unlocked = [1]  # Level 1 always unlocked

    for completed in session["completed_levels"]:
        next_level = completed + 1
        if next_level not in unlocked:
            unlocked.append(next_level)

    return unlocked

def is_unlocked(level_number):
    """Check if a specific level is unlocked."""
    return level_number in get_unlocked_levels()


# --- Routes ---

@app.route("/")
def home():
    return redirect("https://lingua-hero.onrender.com")


# ---- STUDY MODE ----

@app.route("/study/<int:level_number>")
def study(level_number):
    """Show all 10 verbs for a given level."""
    if not is_unlocked(level_number):
        return redirect(url_for("home"))  # Block locked levels

    level = get_level(level_number)
    if level is None:
        return "Level not found!", 404
    return render_template("study.html", level=level, total_levels=len(LEVELS))


# ---- GAME MODE ----

@app.route("/game")
def game_home():
    """Game home — let the player choose a level or play all."""
    return render_template("game_home.html", levels=LEVELS)


@app.route("/game/play")
def game_play():
    """Start a new game session."""
    level_number = request.args.get("level", "all")

    if level_number == "all":
        verbs = all_verbs()
    else:
        level = get_level(int(level_number))
        if level is None:
            return redirect(url_for("game_home"))
        verbs = level["verbs"]

    random.shuffle(verbs)

    session["game_verbs"] = verbs
    session["game_index"] = 0
    session["game_score"] = 0
    session["game_total"] = len(verbs)
    session["game_level"] = level_number

    return redirect(url_for("game_question"))


@app.route("/game/question", methods=["GET", "POST"])
def game_question():
    """Show the current question, or handle the submitted answer."""
    if "game_verbs" not in session:
        return redirect(url_for("game_home"))

    index = session["game_index"]
    verbs = session["game_verbs"]
    total = session["game_total"]

    if index >= total:
        return redirect(url_for("game_result"))

    current_verb = verbs[index]
    result = None

    if request.method == "POST":
        past_answer = request.form.get("past", "").strip().lower()
        participle_answer = request.form.get("participle", "").strip().lower()

        correct_past = current_verb["past"].lower()
        correct_participle = current_verb["participle"].lower()

        if past_answer == correct_past and participle_answer == correct_participle:
            result = "correct"
            session["game_score"] = session["game_score"] + 1
        else:
            result = "wrong"

        session["game_index"] = index + 1
        session.modified = True

        return render_template(
            "game_question.html",
            verb=current_verb,
            result=result,
            past_answer=past_answer,
            participle_answer=participle_answer,
            index=index + 1,
            total=total,
            score=session["game_score"],
        )

    return render_template(
        "game_question.html",
        verb=current_verb,
        result=None,
        index=index + 1,
        total=total,
        score=session["game_score"],
    )


@app.route("/game/result")
def game_result():
    """Show the final score after all questions."""
    if "game_score" not in session:
        return redirect(url_for("game_home"))

    score = session["game_score"]
    total = session["game_total"]
    level = session["game_level"]
    percent = int(score / total * 100)

    # If passed 70%+, unlock the next level
    level_unlocked = False
    if level != "all":
        level_num = int(level)
        if percent >= PASS_PERCENT:
            if "completed_levels" not in session:
                session["completed_levels"] = []
            if level_num not in session["completed_levels"]:
                session["completed_levels"].append(level_num)
                session.modified = True
                level_unlocked = True

    session.pop("game_verbs", None)
    session.pop("game_index", None)
    session.pop("game_score", None)
    session.pop("game_total", None)
    session.pop("game_level", None)

    return render_template("game_result.html", score=score, total=total,
                           level=level, percent=percent, level_unlocked=level_unlocked)


# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True)