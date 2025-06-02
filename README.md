# PhraseMemo

英語フレーズを効率的に暗記するためのWebアプリケーション

## 機能

- フレーズの登録と管理
- ChatGPT APIを使用した自動翻訳・例文生成
- カードベースの暗記モード
- 進捗管理機能
- レスポンシブデザイン

## 技術スタック

- Backend: Python/Flask
- Frontend: HTML/CSS/JavaScript
- Database: SQLite
- API: OpenAI API (ChatGPT)

## セットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/phrase-memo.git
cd phrase-memo
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
venv\Scripts\activate     # Windowsの場合
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集してOpenAI APIキーを設定
```

5. アプリケーションの起動
```bash
flask run
```

## 使い方

1. フレーズの追加
   - 「フレーズを追加」から新しい英語フレーズを登録
   - ChatGPT APIにより自動で翻訳と例文が生成

2. 暗記モード
   - カードベースのインターフェースで効率的に学習
   - 進捗状況を確認可能

3. フレーズ一覧
   - 登録したフレーズの管理と編集
   - 検索機能で素早くフレーズを見つける

## ライセンス

MIT License

## 作者

Taiga Bando 