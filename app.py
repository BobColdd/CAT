from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import random
from collections import Counter
import statistics

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///word_cat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.relationship('TestResult', backref='student', lazy=True)

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer)  # in seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    responses = db.Column(db.Text)  # JSON string of responses

# Load test questions
with open('test_questions.json', 'r') as f:
    QUESTIONS = json.load(f)

# Admin credentials (for demo purposes)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "wordteacher123"

@app.route('/')
def index():
    """Home page for student registration"""
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """Register student for the test"""
    student_id = request.form.get('student_id')
    name = request.form.get('name')
    class_name = request.form.get('class_name')
    
    # Check if student already exists
    existing_student = Student.query.filter_by(student_id=student_id).first()
    if existing_student:
        student = existing_student
    else:
        # Create new student
        student = Student(student_id=student_id, name=name, class_name=class_name)
        db.session.add(student)
        db.session.commit()
    
    # Store student ID in session
    session['student_id'] = student.id
    session['student_info'] = {
        'student_id': student_id,
        'name': name,
        'class_name': class_name
    }
    
    return redirect(url_for('take_test'))

@app.route('/test')
def take_test():
    """Render the test page"""
    if 'student_id' not in session:
        return redirect(url_for('index'))
    
    # Select 30 random questions for the test
    test_questions = random.sample(QUESTIONS, min(30, len(QUESTIONS)))
    return render_template('test.html', questions=test_questions)

@app.route('/submit-test', methods=['POST'])
def submit_test():
    """Evaluate test results"""
    if 'student_id' not in session:
        return redirect(url_for('index'))
    
    data = request.json
    responses = data.get('responses', [])
    time_taken = data.get('time_taken', 0)
    
    # Calculate score
    correct_answers = 0
    total_questions = len(responses)
    
    for response in responses:
        question_id = response['question_id']
        selected_answer = response['selected_answer']
        
        # Find the question
        question = next((q for q in QUESTIONS if q['id'] == question_id), None)
        if question and selected_answer == question['correct_answer']:
            correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Save result to database
    result = TestResult(
        student_id=session['student_id'],
        score=score,
        total_questions=total_questions,
        correct_answers=correct_answers,
        time_taken=time_taken,
        responses=json.dumps(responses)
    )
    db.session.add(result)
    db.session.commit()
    
    # Return the result ID for redirection
    return jsonify({
        'score': round(score, 2),
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'time_taken': time_taken,
        'result_id': result.id
    })

@app.route('/result/<int:result_id>')
def show_result(result_id):
    """Display individual test result"""
    result = TestResult.query.get_or_404(result_id)
    return render_template('result.html', result=result)

@app.route('/my-result')
def my_result():
    """Show latest result for current student"""
    if 'student_id' not in session:
        return redirect(url_for('index'))
    
    result = TestResult.query.filter_by(student_id=session['student_id'])\
        .order_by(TestResult.completed_at.desc()).first()
    
    if not result:
        return render_template('no_results.html')
    
    return render_template('result.html', result=result)

@app.route('/detailed-result/<int:result_id>')
def detailed_result(result_id):
    """Display detailed test result with questions and answers"""
    result = TestResult.query.get_or_404(result_id)
    
    # Load student responses
    responses = json.loads(result.responses)
    
    # Get question details for each response
    detailed_questions = []
    for response in responses:
        question_id = response['question_id']
        selected_answer = response['selected_answer']
        
        # Find the question in QUESTIONS
        question = next((q for q in QUESTIONS if q['id'] == question_id), None)
        if question:
            is_correct = selected_answer == question['correct_answer']
            detailed_questions.append({
                'question': question['question'],
                'options': question['options'],
                'selected_answer': selected_answer,
                'correct_answer': question['correct_answer'],
                'explanation': question.get('explanation', ''),
                'is_correct': is_correct
            })
    
    return render_template('detailed_result.html', 
                         result=result,
                         questions=detailed_questions)

@app.route('/my-results')
def my_results():
    """Show all test results for current student"""
    if 'student_id' not in session:
        return redirect(url_for('index'))
    
    results = TestResult.query.filter_by(student_id=session['student_id'])\
        .order_by(TestResult.completed_at.desc()).all()
    
    return render_template('my_results.html', results=results)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin.html', error='Invalid credentials')
    
    return render_template('admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with all results"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get all results with student information
    results = db.session.query(TestResult, Student).join(Student).order_by(TestResult.completed_at.desc()).all()
    
    # Calculate statistics
    total_students = Student.query.count()
    total_tests = TestResult.query.count()
    avg_score = db.session.query(db.func.avg(TestResult.score)).scalar() or 0
    
    return render_template('admin_dashboard.html', 
                         results=results, 
                         total_students=total_students,
                         total_tests=total_tests,
                         avg_score=round(avg_score, 2))


# Add these imports at the top if not already present


# ... after the existing routes in app.py, add these new ones:

@app.route('/admin/question-analysis')
def admin_question_analysis():
    """Admin page showing question difficulty and common mistakes"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get all test results
    all_results = TestResult.query.all()
    
    # Analyze question performance
    question_stats = {}
    total_responses = 0
    
    for result in all_results:
        responses = json.loads(result.responses)
        total_responses += len(responses)
        
        for response in responses:
            question_id = response['question_id']
            selected_answer = response['selected_answer']
            
            # Find the question
            question = next((q for q in QUESTIONS if q['id'] == question_id), None)
            if question:
                is_correct = selected_answer == question['correct_answer']
                
                if question_id not in question_stats:
                    question_stats[question_id] = {
                        'question_text': question['question'],
                        'category': question['category'],
                        'total_attempts': 0,
                        'correct_attempts': 0,
                        'incorrect_attempts': 0,
                        'common_wrong_answers': Counter(),
                        'correct_answer': question['correct_answer'],
                        'explanation': question.get('explanation', '')
                    }
                
                question_stats[question_id]['total_attempts'] += 1
                if is_correct:
                    question_stats[question_id]['correct_attempts'] += 1
                else:
                    question_stats[question_id]['incorrect_attempts'] += 1
                    question_stats[question_id]['common_wrong_answers'][selected_answer] += 1
    
    # Calculate percentages and sort by difficulty
    for question_id, stats in question_stats.items():
        if stats['total_attempts'] > 0:
            stats['success_rate'] = (stats['correct_attempts'] / stats['total_attempts']) * 100
            stats['failure_rate'] = 100 - stats['success_rate']
            # Get most common wrong answers
            stats['top_wrong_answers'] = stats['common_wrong_answers'].most_common(3)
        else:
            stats['success_rate'] = 0
            stats['failure_rate'] = 0
            stats['top_wrong_answers'] = []
    
    # Sort questions by failure rate (highest first)
    sorted_questions = sorted(
        question_stats.items(),
        key=lambda x: x[1]['failure_rate'],
        reverse=True
    )
    
    # Calculate overall statistics
    total_questions = len(QUESTIONS)
    questions_with_data = len(question_stats)
    overall_success_rate = statistics.mean(
        [stats['success_rate'] for stats in question_stats.values()]
    ) if question_stats else 0
    
    return render_template('admin_question_analysis.html',
                         questions=sorted_questions,
                         total_questions=total_questions,
                         questions_with_data=questions_with_data,
                         total_responses=total_responses,
                         overall_success_rate=overall_success_rate)

@app.route('/admin/student-analysis')
def admin_student_analysis():
    """Admin page showing student performance by category"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get all students with their results
    students = Student.query.all()
    student_performance = []
    
    for student in students:
        results = TestResult.query.filter_by(student_id=student.id).all()
        if results:
            # Calculate average score
            avg_score = statistics.mean([r.score for r in results]) if results else 0
            best_score = max([r.score for r in results]) if results else 0
            worst_score = min([r.score for r in results]) if results else 0
            total_tests = len(results)
            
            # Analyze by category
            category_scores = {}
            for result in results:
                responses = json.loads(result.responses)
                for response in responses:
                    question_id = response['question_id']
                    selected_answer = response['selected_answer']
                    
                    question = next((q for q in QUESTIONS if q['id'] == question_id), None)
                    if question:
                        category = question['category']
                        is_correct = selected_answer == question['correct_answer']
                        
                        if category not in category_scores:
                            category_scores[category] = {'correct': 0, 'total': 0}
                        
                        category_scores[category]['total'] += 1
                        if is_correct:
                            category_scores[category]['correct'] += 1
            
            # Calculate category percentages
            category_performance = {}
            for category, scores in category_scores.items():
                category_performance[category] = (scores['correct'] / scores['total']) * 100
            
            student_performance.append({
                'student': student,
                'avg_score': avg_score,
                'best_score': best_score,
                'worst_score': worst_score,
                'total_tests': total_tests,
                'category_performance': category_performance,
                'weakest_category': min(category_performance.items(), key=lambda x: x[1])[0] if category_performance else None,
                'strongest_category': max(category_performance.items(), key=lambda x: x[1])[0] if category_performance else None
            })
    
    # Sort by average score (highest first)
    student_performance.sort(key=lambda x: x['avg_score'], reverse=True)
    
    return render_template('admin_student_analysis.html',
                         student_performance=student_performance)

@app.route('/admin/failed-questions/<int:question_id>')
def admin_failed_questions_detail(question_id):
    """Show detailed analysis for a specific question"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Find the question
    question = next((q for q in QUESTIONS if q['id'] == question_id), None)
    if not question:
        return "Question not found", 404
    
    # Get all responses for this question
    all_results = TestResult.query.all()
    students_wrong = []
    answer_distribution = Counter()
    
    for result in all_results:
        responses = json.loads(result.responses)
        for response in responses:
            if response['question_id'] == question_id:
                selected_answer = response['selected_answer']
                answer_distribution[selected_answer] += 1
                
                if selected_answer != question['correct_answer']:
                    students_wrong.append({
                        'student': result.student,
                        'selected_answer': selected_answer,
                        'test_date': result.completed_at,
                        'score': result.score
                    })
    
    # Calculate statistics
    total_attempts = sum(answer_distribution.values())
    correct_attempts = answer_distribution.get(question['correct_answer'], 0)
    success_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get most common wrong answers
    wrong_answers = [(answer, count) for answer, count in answer_distribution.items() 
                     if answer != question['correct_answer']]
    wrong_answers.sort(key=lambda x: x[1], reverse=True)
    
    return render_template('admin_question_detail.html',
                         question=question,
                         students_wrong=students_wrong,
                         answer_distribution=dict(answer_distribution),
                         wrong_answers=wrong_answers,
                         total_attempts=total_attempts,
                         correct_attempts=correct_attempts,
                         success_rate=success_rate)

@app.route('/admin/category-analysis')
def admin_category_analysis():
    """Show performance analysis by question category"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Initialize category statistics
    category_stats = {}
    
    # Get all results
    all_results = TestResult.query.all()
    
    for result in all_results:
        responses = json.loads(result.responses)
        for response in responses:
            question_id = response['question_id']
            selected_answer = response['selected_answer']
            
            question = next((q for q in QUESTIONS if q['id'] == question_id), None)
            if question:
                category = question['category']
                is_correct = selected_answer == question['correct_answer']
                
                if category not in category_stats:
                    category_stats[category] = {
                        'total_questions': 0,
                        'correct_answers': 0,
                        'incorrect_answers': 0,
                        'questions': set()
                    }
                
                category_stats[category]['total_questions'] += 1
                category_stats[category]['questions'].add(question_id)
                if is_correct:
                    category_stats[category]['correct_answers'] += 1
                else:
                    category_stats[category]['incorrect_answers'] += 1
    
    # Calculate percentages and prepare data for template
    analysis_data = []
    for category, stats in category_stats.items():
        success_rate = (stats['correct_answers'] / stats['total_questions'] * 100) if stats['total_questions'] > 0 else 0
        unique_questions = len(stats['questions'])
        
        analysis_data.append({
            'category': category,
            'total_questions': stats['total_questions'],
            'correct_answers': stats['correct_answers'],
            'incorrect_answers': stats['incorrect_answers'],
            'success_rate': success_rate,
            'unique_questions': unique_questions,
            'avg_per_question': stats['total_questions'] / unique_questions if unique_questions > 0 else 0
        })
    
    # Sort by success rate (lowest first - hardest categories)
    analysis_data.sort(key=lambda x: x['success_rate'])
    
    # Overall statistics
    total_attempts = sum(item['total_questions'] for item in analysis_data)
    overall_success_rate = statistics.mean(item['success_rate'] for item in analysis_data) if analysis_data else 0
    
    return render_template('admin_category_analysis.html',
                         categories=analysis_data,
                         total_attempts=total_attempts,
                         overall_success_rate=overall_success_rate)

@app.route('/admin/export-data')
def admin_export_data():
    """Export test data for analysis"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get all data
    results = TestResult.query.all()
    
    # Prepare CSV data
    csv_data = "Student ID,Student Name,Class,Test Date,Score,Correct Answers,Total Questions,Time Taken\n"
    
    for result in results:
        csv_data += f"{result.student.student_id},{result.student.name},{result.student.class_name},"
        csv_data += f"{result.completed_at},{result.score},{result.correct_answers},"
        csv_data += f"{result.total_questions},{result.time_taken}\n"
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=test_results.csv"}
    )                        

@app.route('/admin/logout')
def admin_logout():
    """Logout admin"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)