from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.phrase import Phrase
from app.models.quiz import QuizResult
from app.utils.openai_helper import evaluate_quiz_answer
from sqlalchemy.sql import func
import random

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz')
@login_required
def quiz_home():
    return render_template('quiz/home.html')

@quiz_bp.route('/api/quiz/start', methods=['POST'])
@login_required
def start_quiz():
    quiz_type = request.json.get('type', 'english_to_japanese')
    count = request.json.get('count', 10)
    
    # ユーザーのフレーズからランダムに選択
    phrases = Phrase.query.filter_by(user_id=current_user.id)\
        .order_by(func.random())\
        .limit(count).all()
    
    if not phrases:
        return jsonify({
            'error': 'フレーズが登録されていません'
        }), 400
    
    # クイズ問題を生成
    questions = []
    for phrase in phrases:
        if quiz_type == 'english_to_japanese':
            question = phrase.english
            answer = phrase.japanese
        else:
            question = phrase.japanese
            answer = phrase.english
        
        questions.append({
            'id': phrase.id,
            'question': question,
            'answer': answer
        })
    
    return jsonify({
        'questions': questions,
        'quiz_type': quiz_type
    })

@quiz_bp.route('/api/quiz/check', methods=['POST'])
@login_required
def check_answer():
    data = request.json
    user_answer = data.get('answer', '')
    correct_answer = data.get('correct_answer', '')
    quiz_type = data.get('quiz_type', 'english_to_japanese')
    
    # 回答を評価
    result = evaluate_quiz_answer(user_answer, correct_answer, quiz_type)
    
    return jsonify(result)

@quiz_bp.route('/api/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    data = request.json
    score = data.get('score', 0)
    total_questions = data.get('total_questions', 0)
    quiz_type = data.get('quiz_type', 'english_to_japanese')
    
    # 結果を保存
    result = QuizResult(
        user_id=current_user.id,
        score=score,
        total_questions=total_questions,
        quiz_type=quiz_type
    )
    db.session.add(result)
    db.session.commit()
    
    return jsonify({
        'score': score,
        'total_questions': total_questions,
        'accuracy': round((score / total_questions * 100), 1) if total_questions > 0 else 0
    }) 