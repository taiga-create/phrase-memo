from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import Phrase
from . import db
from openai import OpenAI
from config import Config
import json

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    # 最近追加されたフレーズを取得（最新5件）
    recent_phrases = Phrase.query.order_by(Phrase.id.desc()).limit(5).all()
    
    # 総フレーズ数を取得
    total_phrases = Phrase.query.count()
    
    # LocalStorageから覚えたフレーズの数を取得する関数をJavaScriptで実装
    memorized_phrases = 0  # この値はJavaScriptで更新
    memorization_rate = 0  # この値はJavaScriptで更新
    
    return render_template(
        "index.html",
        recent_phrases=recent_phrases,
        total_phrases=total_phrases,
        memorized_phrases=memorized_phrases,
        memorization_rate=memorization_rate
    )

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        phrase = request.form["phrase"]
        meaning = request.form["meaning"]
        example = request.form["example"]
        example_meaning = request.form["example_meaning"]

        new_phrase = Phrase(
            phrase=phrase,
            meaning=meaning,
            example=example,
            example_meaning=example_meaning
        )
        db.session.add(new_phrase)
        db.session.commit()
        return redirect(url_for("main.index"))

    return render_template("register.html")

@bp.route("/list")
def list_phrases():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10  # 1ページに表示する件数

    query = Phrase.query
    if q:
        query = query.filter(Phrase.phrase.contains(q) | Phrase.meaning.contains(q))

    phrases = query.order_by(Phrase.id.desc()).paginate(page=page, per_page=per_page)

    return render_template("list.html", phrases=phrases, q=q)


@bp.route("/memorize")
def memorize():
    mode = request.args.get("mode", "full")  # "full", "english", "japanese", "example"など
    phrases = Phrase.query.all()
    return render_template("memorize.html", phrases=phrases, mode=mode)

@bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_phrase(id):
    phrase = Phrase.query.get_or_404(id)
    if request.method == "POST":
        phrase.phrase = request.form["phrase"]
        phrase.meaning = request.form["meaning"]
        phrase.example = request.form["example"]
        phrase.example_meaning = request.form["example_meaning"]
        db.session.commit()
        flash("更新しました")
        return redirect(url_for("main.list_phrases"))
    return render_template("edit.html", phrase=phrase)

@bp.route("/delete/<int:id>", methods=["POST"])
def delete_phrase(id):
    phrase = Phrase.query.get_or_404(id)
    db.session.delete(phrase)
    db.session.commit()
    flash("削除しました")
    return redirect(url_for("main.list_phrases"))

@bp.route('/add_phrase')
def add_phrase():
    return render_template('add_phrase.html')

@bp.route('/api/suggest', methods=['POST'])
def suggest_translation():
    data = request.get_json()
    phrase = data.get('phrase')
    
    if not phrase:
        return jsonify({'error': 'Phrase is required'}), 400

    try:
        # ChatGPT APIを使用して翻訳と例文を生成
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        prompt = f"""
以下の英語フレーズについて、以下の形式で日本語の意味と例文を生成してください：

フレーズ: {phrase}

以下の形式でJSON形式で出力してください：
{{
    "meaning": "日本語の意味",
    "example": "英語の例文",
    "example_meaning": "例文の日本語訳"
}}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは英語学習のための翻訳アシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # ChatGPTの応答からJSONを抽出
        try:
            content = response.choices[0].message.content
            # JSON文字列を探して抽出
            import json
            import re
            json_str = re.search(r'\{.*\}', content, re.DOTALL).group()
            result = json.loads(json_str)
            return jsonify(result)
        except Exception as e:
            print(f"Error parsing ChatGPT response: {e}")
            return jsonify({
                'error': 'Failed to parse suggestion'
            }), 500

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return jsonify({
            'error': 'Failed to get suggestion'
        }), 500

@bp.route('/api/phrases', methods=['POST'])
def save_phrase():
    data = request.get_json()
    
    required_fields = ['phrase', 'meaning']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        phrase = Phrase(
            phrase=data['phrase'],
            meaning=data['meaning'],
            example=data.get('example', ''),
            example_meaning=data.get('example_meaning', '')
        )
        db.session.add(phrase)
        db.session.commit()
        return jsonify({'message': 'Phrase saved successfully'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return jsonify({'error': 'Failed to save phrase'}), 500
