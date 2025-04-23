from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

# Load data from JSON file
def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)

# Routes
@app.route('/')
def home():
    return render_template('home.html', title="The Souls of Cars")

@app.route('/learn/<int:lesson_id>')
def learn(lesson_id):
    data = load_data()
    
    # Check if lesson exists
    if lesson_id <= 0 or lesson_id > len(data['lessons']):
        return redirect(url_for('home'))
    
    # Get the current lesson
    lesson = data['lessons'][lesson_id - 1]
    
    # Record user progress in session
    if 'progress' not in session:
        session['progress'] = {'lessons_viewed': []}
    
    if lesson_id not in session['progress']['lessons_viewed']:
        session['progress']['lessons_viewed'].append(lesson_id)
    
    # Determine if there's a next lesson
    next_lesson = lesson_id + 1 if lesson_id < len(data['lessons']) else None
    
    return render_template('learn.html', 
                          lesson=lesson, 
                          lesson_id=lesson_id,
                          next_lesson=next_lesson,
                          title=lesson['title'])

@app.route('/quiz/<int:question_id>', methods=['GET', 'POST'])
def quiz(question_id):
    data = load_data()
    quiz_length = len(data['quiz'])
    
    # Make sure we don't go out of bounds
    if question_id < 1:
        question_id = 1
    elif question_id > quiz_length:
        return redirect(url_for('quiz_results'))
    
    # Get the current question
    question = data['quiz'][question_id - 1]
    
    # Check if this is the first question and it's a GET request (new quiz)
    if question_id == 1 and request.method == 'GET' and 'from_reset' not in session:
        # Auto-reset the quiz when starting from question 1
        if 'quiz' in session:
            session.pop('quiz')
    
    # Initialize quiz in session if needed
    if 'quiz' not in session:
        session['quiz'] = {'answers': {}, 'score': 0, 'correct_answers': []}
    
    # Remove the from_reset flag if it exists
    if 'from_reset' in session:
        session.pop('from_reset')
        session.modified = True
    
    # Variables for feedback
    feedback_given = False
    user_answer = None
    
    # Handle form submission
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        if user_answer:  # Check that we actually got an answer
            # Record answer
            session['quiz']['answers'][str(question_id)] = user_answer
            
            # Check if correct and add to score
            if user_answer == question['correct']:
                # Only add to score if this is the first time answering correctly
                if str(question_id) not in session['quiz'].get('correct_answers', []):
                    session['quiz']['score'] += 1
                    if 'correct_answers' not in session['quiz']:
                        session['quiz']['correct_answers'] = []
                    session['quiz']['correct_answers'].append(str(question_id))
            
            # Explicitly save the session to ensure changes persist
            session.modified = True
            
            # Show feedback
            feedback_given = True
    else:
        # Check if we already have an answer for this question (coming back)
        if str(question_id) in session['quiz'].get('answers', {}):
            user_answer = session['quiz']['answers'][str(question_id)]
            feedback_given = True
    
    return render_template('quiz.html', 
                          question=question, 
                          question_id=question_id,
                          quiz_length=quiz_length,
                          score=session['quiz'].get('score', 0),
                          feedback_given=feedback_given,
                          user_answer=user_answer,
                          title=f"Quiz Question {question_id}")

@app.route('/quiz_results')
def quiz_results():
    if 'quiz' not in session:
        return redirect(url_for('home'))
    
    data = load_data()
    total = len(data['quiz'])
    
    # Make sure we have the correct score
    score = session['quiz'].get('score', 0)
    
    # For debugging, add some session info to ensure score is correct
    print(f"Final score: {score}, Correct answers: {session['quiz'].get('correct_answers', [])}")
    
    return render_template('quiz_results.html', 
                          score=score,
                          total=total,
                          title="Quiz Results")

@app.route('/take_quiz')
def take_quiz():
    # Clear only quiz-related data from the session
    if 'quiz' in session:
        session.pop('quiz')
    # Set a flag to indicate we're coming from a reset
    session['from_reset'] = True
    return redirect(url_for('quiz', question_id=1))

if __name__ == '__main__':
    app.run(debug=True)