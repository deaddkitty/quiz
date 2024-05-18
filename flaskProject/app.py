from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('quiz.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM questions WHERE id = ?', (question_id,)).fetchone()
    conn.close()

    if question is None:
        return redirect(url_for('result'))

    if request.method == 'POST':
        user_answer = request.form.get('answer')  # Получаем значение выбранного радиокнопки
        if user_answer:
            user_answer = user_answer.strip().lower()  # Приведение к нижнему регистру для проверки
            if 'answers' not in session:
                session['answers'] = {}
            session['answers'][str(question_id)] = user_answer
            session.modified = True  # Явно указываем, что сессия была изменена
            print("User Answers (after POST):", session['answers'])  # Отладочный вывод
        return redirect(url_for('question', question_id=question_id + 1))

    print("User Answers (GET):", session.get('answers', {}))  # Отладочный вывод
    return render_template('question.html', question=question)

@app.route('/result')
def result():
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions').fetchall()
    conn.close()

    correct_answers = 0
    total_questions = len(questions)
    user_answers = session.get('answers', {})

    print("User Answers at result page:", user_answers)  # Отладочный вывод

    for question in questions:
        question_id = str(question['id'])
        correct_answer = question['answer'].strip().lower()
        user_answer = user_answers.get(question_id, '')
        if user_answer == correct_answer:
            correct_answers += 1
        print(f"Question ID: {question_id}, User Answer: {user_answer}, Correct Answer: {correct_answer}")

    return render_template('result.html', correct_answers=correct_answers, total_questions=total_questions)

if __name__ == '__main__':
    app.run(debug=True)
