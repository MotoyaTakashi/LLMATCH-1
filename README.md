# 医療テキスト分析システム

## 概要
このシステムは、医療記録の時系列テキストデータを分析し、がん診療に関する重要な医療情報を自動抽出するツールです。vLLMベースのローカルLLMサーバーを使用して、高速な分析を実現します。

## 主な機能

### 1. データ生成機能 (`src/data/data_generator.py`)
- がん診療に特化したダミーデータの生成
- 以下の情報を含むテキストデータを生成：
  - がん診断名（複数の表記揺れに対応）
  - ステージ情報
  - 診断検査情報
  - 手術記録
  - 化学療法情報
  - 特記事項

### 2. テキスト分析機能 (`src/analyzer/excel_analyzer.py`)
- Excel形式の医療記録からの情報抽出
- 患者IDごとの時系列データの統合
- カスタマイズ可能なプロンプトテンプレートによる分析
- 以下の情報を自動抽出：
  - がん診断名
  - ステージ情報
  - 診断検査情報
  - 初回治療内容
  - 化学療法情報
  - 手術術式
  - 特記事項

## セットアップ

### 1. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

### 2. vLLMサーバーの準備
- GPUが必要です
- vLLMサーバーを起動し、OpenAI互換のエンドポイントを提供する必要があります

## 使用方法

### 1. ダミーデータの生成
```bash
python examples/test_data_generator.py
```
- 50人分のダミー医療記録が `sample_data.xlsx` に生成されます

### 2. テキスト分析の実行
```bash
python analyze_medical_records.py
```
- 分析結果は `analyzed_results.xlsx` に保存されます

## データ形式

### 入力データ（必須列）
- `ID`: 患者ID
- `day`: 記録日（YYYY-MM-DD形式）
- `text`: 医療記録テキスト

| ID | day | text |
|----|-----|------|
| 1 | 2023-01-01 | "初診時所見：子宮体部類内膜癌 Stage IA。内膜生検の病理結果では、類内膜癌 Grade 1。MRIにて筋層浸潤は認めず。開腹子宮全摘術の方針とする。" |
| 1 | 2023-01-15 | "術前検査：胸部CT、腹部造影CTにて遠隔転移なし。血液検査にて貧血（Hb 9.8）あり、術前に貧血改善を要する。" |
| 1 | 2023-02-01 | "手術記録：腹腔鏡下子宮全摘+両側付属器切除術施行。手術時間2時間45分、出血量150ml。腹腔内に播種なし。術中合併症なし。" |

## プロンプトテンプレート
`templates/prompt_templates.json` で各分析タスクのプロンプトをカスタマイズできます。

## ファイル構成
```
.
├── src/
│   ├── analyzer/
│   │   ├── __init__.py
│   │   └── excel_analyzer.py
│   └── data/
│       ├── __init__.py
│       └── data_generator.py
├── examples/
│   ├── test_data_generator.py
│   └── test_excel_analyzer.py
├── templates/
│   └── prompt_templates.json
├── analyze_medical_records.py
├── setup.py
├── requirements.txt
└── README.md
```

## 制限事項
- テキストの最大長は4000文字（超過分は切り捨て）
- vLLMサーバーの実行にはGPUが必要
- 日本語医療テキストの分析に特化

## ライセンス
MIT License

