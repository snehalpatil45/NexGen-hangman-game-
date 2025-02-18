import random
import requests
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# API to fetch random words and their meanings
def get_random_word():
    while True:
        try:
            response = requests.get("https://random-word-api.herokuapp.com/word").json()
            word = response[0]
            dict_response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}").json()
            meaning = dict_response[0]['meanings'][0]['definitions'][0]['definition']
            return word, meaning
        except (KeyError, IndexError):
            continue

# Hangman stages
hangman_stages = [
    r"""
      -----
      |   |
          |
          |
          |
          |
    =========
    """,
    r"""
      -----
      |   |
      O   |
          |
          |
          |
    =========
    """,
    r"""
      -----
      |   |
      O   |
      |   |
          |
          |
    =========
    """,
    r"""
      -----
      |   |
      O   |
     /|   |
          |
          |
    =========
    """,
    r"""
      -----
      |   |
      O   |
     /|\  |
          |
          |
    =========
    """,
    r"""
      -----
      |   |
      O   |
     /|\  |
     /    |
          |
    =========
    """,
    r"""
      -----
      |   |
      O   |
     /|\  |
     / \  |
          |
    =========
    """  
]

# Dancing Hangman Frames (for animation)
dancing_hangman = [
    r"""
      \O/
       |
      / \
    """,
    r"""
       O
      /|\
      / \
    """,
    r"""
      O/
      |\
      / \
    """,
]

def start_game():
    word, hint = get_random_word()
    session['word'] = word
    session['hint'] = hint
    session['word_length'] = len(word)
    session['guessed_letters'] = []
    session['wrong_guesses'] = 0
    session['max_attempts'] = 6
    session['dancing_index'] = 0  # Track animation frame index

@app.route('/')
def index():
    if 'word' not in session:
        start_game()

    word = session['word']
    guessed_letters = session['guessed_letters']
    wrong_guesses = session['wrong_guesses']
    hidden_word = " ".join([letter if letter in guessed_letters else "_" for letter in word])
    hangman_stage = hangman_stages[min(wrong_guesses, len(hangman_stages) - 1)]
    hint = session['hint']
    remaining_attempts = session['max_attempts'] - wrong_guesses
    word_length = session['word_length']

    # Check if the game is won
    won = all(letter in guessed_letters for letter in word)

    # Check if the game is lost
    lost = wrong_guesses >= session['max_attempts']

    return render_template(
        'index.html',
        hidden_word=hidden_word,
        hangman_stage=hangman_stage,
        hint=hint,
        remaining_attempts=remaining_attempts,
        word_length=word_length,
        won=won,
        lost=lost,  # Pass the lost variable
        word=word if lost else None  # Show correct word if lost
    )


@app.route('/guess', methods=['POST'])
def guess():
    if 'word' not in session:
        start_game()

    guess = request.form['guess'].lower()
    word = session['word']
    guessed_letters = session['guessed_letters']
    wrong_guesses = session['wrong_guesses']
    max_attempts = session['max_attempts']

    if len(guess) != 1 or not guess.isalpha() or guess in guessed_letters:
        return redirect(url_for('index'))

    guessed_letters.append(guess)

    if guess not in word:
        session['wrong_guesses'] += 1

    session['guessed_letters'] = guessed_letters

    return redirect(url_for('index'))

@app.route('/animate')
def animate():
    if 'word' not in session:
        return jsonify({"frame": ""})

    if all(letter in session['guessed_letters'] for letter in session['word']):
        session['dancing_index'] = (session['dancing_index'] + 1) % len(dancing_hangman)
        return jsonify({"frame": dancing_hangman[session['dancing_index']]})

    return jsonify({"frame": ""})

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

























