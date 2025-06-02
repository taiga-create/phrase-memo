from openai import OpenAI
from flask import current_app

def get_phrase_suggestions(english_phrase):
    """OpenAI APIを使用して、英語フレーズの日本語訳と例文を生成します"""
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
    
    prompt = f"""
以下の英語フレーズについて、以下の形式で情報を提供してください：

英語フレーズ：{english_phrase}

必要な情報：
1. 日本語の意味（簡潔に）
2. 自然な例文（英語）

回答は以下の形式で：
{{
    "japanese": "日本語の意味",
    "example": "Example sentence using the phrase."
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは英語学習のエキスパートアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # レスポンスから必要な情報を抽出
        content = response.choices[0].message.content
        
        # 文字列をPythonの辞書形式に変換
        import json
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            # JSONのパースに失敗した場合のフォールバック
            return {
                "japanese": "翻訳を生成できませんでした",
                "example": "Could not generate an example"
            }
            
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        return {
            "japanese": "翻訳を生成できませんでした",
            "example": "Could not generate an example"
        }

def generate_quiz_choices(correct_answer, quiz_type='english_to_japanese'):
    """クイズの選択肢を生成します"""
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
    
    if quiz_type == 'english_to_japanese':
        prompt = f"""
以下の日本語の意味に対して、明確に異なる意味の選択肢を3つ生成してください：

正解：{correct_answer}

条件：
1. 完全に異なる意味の選択肢を生成すること
2. 自然な日本語であること
3. 長さは正解と同程度にすること
4. 以下のような選択肢を生成してください：
   - 反対の意味
   - 全く異なる文脈の意味
   - 同じ品詞だが異なる意味

回答は以下の形式で：
{{
    "choices": [
        "選択肢1（反対の意味）",
        "選択肢2（異なる文脈）",
        "選択肢3（同じ品詞で異なる意味）"
    ]
}}
"""
    else:  # japanese_to_english
        prompt = f"""
以下の英語フレーズに対して、明確に異なる意味の選択肢を3つ生成してください：

正解：{correct_answer}

条件：
1. 完全に異なる意味の選択肢を生成すること
2. 自然な英語であること
3. 長さは正解と同程度にすること
4. 以下のような選択肢を生成してください：
   - 反対の意味
   - 全く異なる文脈の意味
   - 同じ品詞だが異なる意味

回答は以下の形式で：
{{
    "choices": [
        "opposite meaning",
        "different context",
        "same part of speech but different meaning"
    ]
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは英語学習のエキスパートアシスタントです。与えられた単語やフレーズに対して、明確に異なる意味の選択肢を生成してください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        content = response.choices[0].message.content
        
        import json
        try:
            result = json.loads(content)
            choices = result['choices']
            # 正解を含めてシャッフル
            import random
            all_choices = choices + [correct_answer]
            random.shuffle(all_choices)
            return {
                'choices': all_choices,
                'correct_index': all_choices.index(correct_answer)
            }
        except (json.JSONDecodeError, KeyError):
            # フォールバックの選択肢を生成
            return {
                'choices': [
                    "選択肢1",
                    "選択肢2",
                    "選択肢3",
                    correct_answer
                ],
                'correct_index': 3
            }
            
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        return {
            'choices': [
                "選択肢1",
                "選択肢2",
                "選択肢3",
                correct_answer
            ],
            'correct_index': 3
        } 