from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random

app = Flask(__name__)
app.secret_key = "1085107"

data = open("words.txt", "r", encoding="utf-8").read().splitlines()
words = {}
for line in data:
    if line == "":
        continue
    word, meaning = line.split(":")
    words[word.strip()] = meaning.strip()

@app.route('/')
def index():
    if "chosen_words" not in session:
        session["chosen_words"] = []

    if "game_words" not in session:
        session["game-words"] = []

    return render_template(
        'index.html',
        words=words,
        selected_words=session["chosen_words"]
    )

@app.route('/api/toggle_word', methods=['POST'])
def toggle_word():
    data = request.get_json()

    word = data.get("word")

    if "chosen_words" not in session:
        session["chosen_words"] = []

    chosen_words = session["chosen_words"]

    if word in chosen_words:
        chosen_words.remove(word)
        added = False
    else:
        chosen_words.append(word)
        added = True

    session["chosen_words"] = chosen_words
    session.modified = True

    return jsonify({
        "success": True,
        "added": added,
        "words": chosen_words
    })

@app.route('/api/add-word', methods=['POST'])
def add_word():
    word = request.form.get('word')
    meaning = request.form.get('meaning')
    if word and meaning:
        words[word] = meaning
        with open("words.txt", "a", encoding="utf-8") as f:
            f.write(f"{word}:{meaning}\n")
    return redirect(url_for('index'))

@app.route("/api/select_all_words", methods=["POST"])
def select_all_words():

    session["chosen_words"] = list(words.keys())

    session.modified = True

    return jsonify({
        "success": True,
        "words": session["chosen_words"]
    })

@app.route("/api/clear_all_words", methods=["POST"])
def clear_all_words():

    session["chosen_words"] = []

    session.modified = True

    return jsonify({
        "success": True
    })

@app.route("/api/set-game-words", methods=['POST'])
def set_game_words():

    chosen_words = session.get("chosen_words", [])

    if len(chosen_words) < 10:

        return jsonify({
            "success": False,
            "message": "Нужно выбрать минимум 10 слов"
        })

    session["game-words"] = chosen_words.copy()

    session.modified = True

    return jsonify({
        "success": True,
        "redirect": url_for("get_random_word")
    })

@app.route('/words-game')
def get_random_word():

    game_words = session.get("game-words", [])

    if len(game_words) == 0:
        return "Кончились слова для игры"

    word = random.choice(game_words)

    game_words.remove(word)

    session["game-words"] = game_words
    session.modified = True

    right_answer = words[word]

    all_translations = list(words.values())

    all_translations.remove(right_answer)

    wrong_count = min(3, len(all_translations))

    wrong_answers = random.sample(
        all_translations,
        wrong_count
    )

    options = wrong_answers + [right_answer]

    random.shuffle(options)

    return render_template(
        "game.html",
        word=word,
        options=options,
        correct_answer=right_answer
    )

if __name__ == '__main__':
    app.run()
