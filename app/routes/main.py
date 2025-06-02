from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.phrase import Phrase
from app.utils.openai_helper import get_phrase_suggestions
from sqlalchemy import func
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        # 全体の統計
        total_phrases = Phrase.query.filter_by(user_id=current_user.id).count()
        memorized_phrases = Phrase.query.filter_by(user_id=current_user.id, is_memorized=True).count()
        memorization_rate = (memorized_phrases / total_phrases * 100) if total_phrases > 0 else 0
        
        # 最近追加されたフレーズ
        recent_phrases = Phrase.query.filter_by(user_id=current_user.id)\
            .order_by(Phrase.created_at.desc())\
            .limit(5).all()
        
        # 最近復習したフレーズ
        recently_reviewed = Phrase.query.filter_by(user_id=current_user.id)\
            .filter(Phrase.last_reviewed_at.isnot(None))\
            .order_by(Phrase.last_reviewed_at.desc())\
            .limit(5).all()
        
        # 未暗記のフレーズ
        unmemorized_phrases = Phrase.query.filter_by(user_id=current_user.id, is_memorized=False)\
            .order_by(func.random())\
            .limit(5).all()
        
        # 今日の学習状況
        today = datetime.utcnow().date()
        phrases_reviewed_today = Phrase.query.filter_by(user_id=current_user.id)\
            .filter(Phrase.last_reviewed_at >= today)\
            .count()
        
        return render_template('index.html',
            total_phrases=total_phrases,
            memorized_phrases=memorized_phrases,
            memorization_rate=round(memorization_rate, 1),
            recent_phrases=recent_phrases,
            recently_reviewed=recently_reviewed,
            unmemorized_phrases=unmemorized_phrases,
            phrases_reviewed_today=phrases_reviewed_today
        )
    return render_template('index.html')

@main_bp.route('/add_phrase', methods=['GET', 'POST'])
@login_required
def add_phrase():
    if request.method == 'POST':
        english = request.form.get('english')
        japanese = request.form.get('japanese')
        example = request.form.get('example')
        note = request.form.get('note')
        
        if not english or not japanese:
            flash('英語とフレーズの意味は必須です', 'error')
            return redirect(url_for('main.add_phrase'))
        
        phrase = Phrase(
            user_id=current_user.id,
            english=english,
            japanese=japanese,
            example=example,
            note=note
        )
        db.session.add(phrase)
        db.session.commit()
        
        flash('フレーズを追加しました', 'success')
        return redirect(url_for('main.list_phrases'))
    
    return render_template('phrases/add.html')

@main_bp.route('/phrases')
@login_required
def list_phrases():
    phrases = Phrase.query.filter_by(user_id=current_user.id).order_by(Phrase.created_at.desc()).all()
    return render_template('phrases/list.html', phrases=phrases)

@main_bp.route('/memorize')
@login_required
def memorize():
    return render_template('phrases/memorize.html')

@main_bp.route('/api/phrases/random')
@login_required
def get_random_phrases():
    count = int(request.args.get('count', 10))
    # 未暗記のフレーズを優先的に取得
    unmemorized = request.args.get('unmemorized', 'false') == 'true'
    
    query = Phrase.query.filter_by(user_id=current_user.id)
    if unmemorized:
        query = query.filter_by(is_memorized=False)
    
    phrases = query.order_by(db.func.random()).limit(count).all()
    return jsonify([{
        'id': p.id,
        'english': p.english,
        'japanese': p.japanese,
        'example': p.example,
        'is_memorized': p.is_memorized
    } for p in phrases])

@main_bp.route('/api/phrases/suggest', methods=['POST'])
@login_required
def suggest_phrase():
    english = request.json.get('english')
    if not english:
        return jsonify({'error': 'English phrase is required'}), 400
    
    suggestions = get_phrase_suggestions(english)
    return jsonify(suggestions)

@main_bp.route('/api/phrases/<int:phrase_id>/memorization', methods=['POST'])
@login_required
def update_memorization_status(phrase_id):
    phrase = Phrase.query.filter_by(id=phrase_id, user_id=current_user.id).first_or_404()
    is_memorized = request.json.get('is_memorized', False)
    
    phrase.update_memorization_status(is_memorized)
    db.session.commit()
    
    return jsonify({
        'id': phrase.id,
        'is_memorized': phrase.is_memorized,
        'last_reviewed_at': phrase.last_reviewed_at.isoformat() if phrase.last_reviewed_at else None
    }) 