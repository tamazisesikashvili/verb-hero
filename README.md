# ⚡ Verb Hero

A Flask web app to learn English irregular verbs!
Built by Luka.

---

## How to Run

### 1. Install Flask
Open your terminal and type:
```
pip install flask
```

### 2. Go into the project folder
```
cd luka_verbs
```

### 3. Start the app
```
python app.py
```

### 4. Open your browser
Go to: http://127.0.0.1:5000

---

## Project Structure

```
luka_verbs/
├── app.py              ← The main Python code (Flask routes)
├── verbs.json          ← All the verb data (easy to add more!)
├── templates/
│   ├── base.html       ← The page template every page uses
│   ├── index.html      ← Home page
│   ├── study.html      ← Study mode
│   ├── game_home.html  ← Game level selector
│   ├── game_question.html  ← Game question
│   └── game_result.html    ← Final score
└── static/
    └── style.css       ← All the styling (colours, layout)
```

---

## Ideas for What to Add Next

- [ ] Add more verbs to verbs.json
- [ ] Track high scores in a file or database
- [ ] Add a timer to each question
- [ ] Multiple choice mode (show 4 options, pick the right one)
- [ ] Streak system (7 days in a row = trophy!)
- [ ] Sound effects when you get it right
