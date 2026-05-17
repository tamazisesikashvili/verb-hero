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


# --- Helper Functions ---
def get_level(level_number):
    """Return a single level by its number (1-5)."""
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


# --- Routes ---

@app.route("/")
def home():
    """Home page."""
    return render_template("index.html", levels=LEVELS)


# ---- STUDY MODE ----

@app.route("/study/<int:level_number>")
def study(level_number):
    """Show all 10 verbs for a given level."""
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
    level_number = request.args.get("level", "all")  # Get level from URL, e.g. ?level=2

    # Build the list of verbs for this game
    if level_number == "all":
        verbs = all_verbs()
    else:
        level = get_level(int(level_number))
        if level is None:
            return redirect(url_for("game_home"))
        verbs = level["verbs"]

    # Shuffle so it's different every time
    random.shuffle(verbs)

    # Save game state in the session (session = data stored per browser tab)
    session["game_verbs"] = verbs
    session["game_index"] = 0
    session["game_score"] = 0
    session["game_total"] = len(verbs)
    session["game_level"] = level_number

    return redirect(url_for("game_question"))


@app.route("/game/question", methods=["GET", "POST"])
def game_question():
    """Show the current question, or handle the submitted answer."""

    # Check that a game is actually running
    if "game_verbs" not in session:
        return redirect(url_for("game_home"))

    index = session["game_index"]
    verbs = session["game_verbs"]
    total = session["game_total"]

    # Game over — all questions answered
    if index >= total:
        return redirect(url_for("game_result"))

    current_verb = verbs[index]

    # Decide which form to hide (randomly show base or past, user fills in the rest)
    # For simplicity: always show the BASE form, user types past + participle
    
    result = None  # Will hold "correct" or "wrong" after checking

    if request.method == "POST":
        # Player submitted an answer
        past_answer = request.form.get("past", "").strip().lower()
        participle_answer = request.form.get("participle", "").strip().lower()

        correct_past = current_verb["past"].lower()
        correct_participle = current_verb["participle"].lower()

        if past_answer == correct_past and participle_answer == correct_participle:
            result = "correct"
            session["game_score"] = session["game_score"] + 1
        else:
            result = "wrong"

        # Move to the next verb
        session["game_index"] = index + 1
        session.modified = True  # Tell Flask the session changed

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

    # GET request — show a fresh question
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

    # Clear the game from the session
    session.pop("game_verbs", None)
    session.pop("game_index", None)
    session.pop("game_score", None)
    session.pop("game_total", None)
    session.pop("game_level", None)

    return render_template("game_result.html", score=score, total=total, level=level)


# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True)  # debug=True means it auto-reloads when you save changes
