import streamlit as st
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import ExcelAnalyzer 
import pandas as pd

def main():
    # ページ設定 - アプリケーションのタイトルとレイアウトを設定
    st.set_page_config(
        page_title="医療記録分析システム",
        page_icon="🏥",
        layout="wide"  # 画面を広く使用
    )

    st.title("医療記録分析システム")

    # サイドバーの設定 - 分析に必要な基本設定を行うエリア
    with st.sidebar:
        st.header("設定")
        # LLMサーバーの設定
        llm_server_url = st.text_input(
            "LLMサーバーURL",
            value="http://localhost:8000/v1",
            help="OpenAI互換のLLMサーバーのURLを入力してください。デフォルトはローカルホストです。"
        )
        
        # テンプレートファイルの設定
        template_path = st.text_input(
            "テンプレートファイルパス",
            value="templates/prompt_templates.json",
            help="分析テンプレートのJSONファイルパスを入力してください。分析の種類や方法を定義します。"
        )

    # タブの作成 - 分析タブとテンプレート編集タブ
    tab1, tab2 = st.tabs(["分析実行", "テンプレート編集"])
    
    with tab1:
        # メインコンテンツエリア
        # Excelファイルのアップロード機能
        uploaded_file = st.file_uploader(
            "医療記録Excelファイルをアップロード", 
            type=['xlsx'],
            help="分析対象の医療記録データをExcelファイル形式でアップロードしてください。"
        )

        if uploaded_file is not None:
            # ExcelAnalyzerのインスタンスを作成 - 分析エンジンの初期化
            analyzer = ExcelAnalyzer(
                llm_server_url=llm_server_url,
                template_path=template_path
            )

            # アップロードされたファイルを一時保存して読み込む
            with open("temp.xlsx", "wb") as f:
                f.write(uploaded_file.getvalue())
            
            if analyzer.load_excel("temp.xlsx"):
                st.success("ファイルの読み込みが完了しました")

                # データプレビュー - アップロードされたデータの確認
                st.subheader("データプレビュー")
                st.write("アップロードされたデータの最初の数行を表示します")
                st.dataframe(analyzer.df.head())

                # 分析オプションの設定
                st.subheader("分析オプション")
                
                col1, col2 = st.columns(2)
                
                # 分析テンプレートの選択
                with col1:
                    selected_templates = st.multiselect(
                        "実行する分析を選択",
                        options=analyzer.templates.keys(),
                        default=list(analyzer.templates.keys()),
                        format_func=lambda x: analyzer.templates[x]["name"],
                        help="実行したい分析の種類を選択してください。複数選択可能です。"
                    )

                # 特定の患者IDの選択
                with col2:
                    sample_id = st.selectbox(
                        "サンプルIDを選択（オプション）",
                        options=["すべて"] + list(analyzer.df["ID"].unique()),
                        help="特定の患者のデータのみを分析する場合は、該当のIDを選択してください。"
                    )

                # 分析実行ボタンと処理
                if st.button("分析を実行", type="primary", help="選択した分析を開始します"):
                    with st.spinner("分析を実行中..."):
                        # 選択された各テンプレートに対して分析を実行
                        for template_key in selected_templates:
                            progress_text = f"{analyzer.templates[template_key]['name']}の分析中..."
                            st.write(progress_text)
                            analyzer.analyze_with_template(template_key)

                        # 分析結果の保存
                        analyzer.save_results("analyzed_results.xlsx")
                        
                        # 分析結果の表示
                        st.subheader("分析結果")
                        result_df = analyzer.df
                        if sample_id != "すべて":
                            result_df = result_df[result_df["ID"] == sample_id]
                        
                        st.write("分析結果の一覧を表示します")
                        st.dataframe(result_df)

                        # 結果のダウンロード機能
                        with open("analyzed_results.xlsx", "rb") as f:
                            st.download_button(
                                label="分析結果をダウンロード",
                                data=f,
                                file_name="analyzed_results.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                help="分析結果をExcelファイルとしてダウンロードできます"
                            )

                # 個別の医療記録テキスト表示
                if sample_id != "すべて":
                    st.subheader(f"ID: {sample_id} の医療記録")
                    st.write("選択された患者の医療記録の詳細を表示します")
                    combined_texts = analyzer.get_combined_texts(sample_id)
                    if combined_texts:
                        st.text_area(
                            "医療記録", 
                            combined_texts[sample_id], 
                            height=300,
                            help="選択された患者の全ての医療記録を時系列で表示します"
                        )
    
    with tab2:
        st.header("プロンプトテンプレート編集")
        
        # テンプレートファイルの読み込み
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            # テンプレートの選択
            template_keys = list(templates.keys())
            selected_template = st.selectbox(
                "編集するテンプレートを選択",
                options=template_keys,
                format_func=lambda x: templates[x]["name"],
                help="編集したいテンプレートを選択してください"
            )
            
            if selected_template:
                # 選択されたテンプレートの編集フォーム
                st.subheader(f"テンプレート: {templates[selected_template]['name']}")
                
                # テンプレートの各項目を編集するフォーム
                with st.form(key="template_edit_form"):
                    # テンプレートキー（変更不可）
                    st.text_input("テンプレートキー", value=selected_template, disabled=True)
                    
                    # 名前
                    template_name = st.text_input(
                        "名前", 
                        value=templates[selected_template]["name"],
                        help="テンプレートの表示名を入力してください"
                    )
                    
                    # 説明
                    template_description = st.text_input(
                        "説明", 
                        value=templates[selected_template].get("description", ""),
                        help="テンプレートの説明を入力してください"
                    )
                    
                    # 分析タイプ
                    template_analysis_type = st.selectbox(
                        "分析タイプ",
                        options=["extract", "classify", "summarize"],
                        index=["extract", "classify", "summarize"].index(templates[selected_template]["analysis_type"]),
                        help="分析の種類を選択してください"
                    )
                    
                    # システムプロンプト
                    template_system_prompt = st.text_area(
                        "システムプロンプト",
                        value=templates[selected_template]["system_prompt"],
                        height=300,
                        help="LLMに送信するシステムプロンプトを入力してください"
                    )
                    
                    # 保存ボタン
                    submit_button = st.form_submit_button(label="変更を保存", type="primary")
                    
                    if submit_button:
                        # テンプレートの更新
                        templates[selected_template]["name"] = template_name
                        templates[selected_template]["description"] = template_description
                        templates[selected_template]["analysis_type"] = template_analysis_type
                        templates[selected_template]["system_prompt"] = template_system_prompt
                        
                        # ファイルに保存
                        try:
                            with open(template_path, 'w', encoding='utf-8') as f:
                                json.dump(templates, f, ensure_ascii=False, indent=2)
                            st.success("テンプレートを保存しました")
                        except Exception as e:
                            st.error(f"テンプレートの保存に失敗しました: {str(e)}")
                
                # 新しいテンプレートの追加ボタン
                if st.button("新しいテンプレートを追加"):
                    st.session_state.add_new_template = True
                
                # 新しいテンプレート追加フォーム
                if st.session_state.get("add_new_template", False):
                    st.subheader("新しいテンプレートを追加")
                    with st.form(key="new_template_form"):
                        new_template_key = st.text_input(
                            "テンプレートキー（一意のID）", 
                            help="英数字とアンダースコアのみを使用してください"
                        )
                        
                        new_template_name = st.text_input(
                            "名前", 
                            help="テンプレートの表示名を入力してください"
                        )
                        
                        new_template_description = st.text_input(
                            "説明", 
                            help="テンプレートの説明を入力してください"
                        )
                        
                        new_template_analysis_type = st.selectbox(
                            "分析タイプ",
                            options=["extract", "classify", "summarize"],
                            help="分析の種類を選択してください"
                        )
                        
                        new_template_system_prompt = st.text_area(
                            "システムプロンプト",
                            height=300,
                            help="LLMに送信するシステムプロンプトを入力してください"
                        )
                        
                        add_button = st.form_submit_button(label="テンプレートを追加", type="primary")
                        
                        if add_button and new_template_key and new_template_name and new_template_system_prompt:
                            if new_template_key in templates:
                                st.error(f"テンプレートキー '{new_template_key}' は既に存在します")
                            else:
                                # 新しいテンプレートを追加
                                templates[new_template_key] = {
                                    "name": new_template_name,
                                    "description": new_template_description,
                                    "analysis_type": new_template_analysis_type,
                                    "system_prompt": new_template_system_prompt
                                }
                                
                                # ファイルに保存
                                try:
                                    with open(template_path, 'w', encoding='utf-8') as f:
                                        json.dump(templates, f, ensure_ascii=False, indent=2)
                                    st.success("新しいテンプレートを追加しました")
                                    st.session_state.add_new_template = False
                                except Exception as e:
                                    st.error(f"テンプレートの保存に失敗しました: {str(e)}")
                
                # テンプレート削除ボタン
                if st.button("このテンプレートを削除", type="secondary"):
                    st.session_state.confirm_delete = True
                    st.session_state.delete_template_key = selected_template
                
                # 削除確認ダイアログ
                if st.session_state.get("confirm_delete", False) and st.session_state.get("delete_template_key") == selected_template:
                    st.warning(f"テンプレート '{templates[selected_template]['name']}' を削除してもよろしいですか？")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("はい、削除します"):
                            # テンプレートを削除
                            del templates[selected_template]
                            
                            # ファイルに保存
                            try:
                                with open(template_path, 'w', encoding='utf-8') as f:
                                    json.dump(templates, f, ensure_ascii=False, indent=2)
                                st.success("テンプレートを削除しました")
                                st.session_state.confirm_delete = False
                                st.session_state.delete_template_key = None
                                st.rerun()  # ページを再読み込み
                            except Exception as e:
                                st.error(f"テンプレートの削除に失敗しました: {str(e)}")
                    with col2:
                        if st.button("いいえ、キャンセル"):
                            st.session_state.confirm_delete = False
                            st.session_state.delete_template_key = None
                            st.rerun()  # ページを再読み込み
                
        except FileNotFoundError:
            st.error(f"テンプレートファイル '{template_path}' が見つかりません")
        except json.JSONDecodeError:
            st.error(f"テンプレートファイルのJSON形式が不正です")
        except Exception as e:
            st.error(f"テンプレートの読み込みに失敗しました: {str(e)}")

if __name__ == "__main__":
    # セッション状態の初期化
    if "add_new_template" not in st.session_state:
        st.session_state.add_new_template = False
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False
    if "delete_template_key" not in st.session_state:
        st.session_state.delete_template_key = None
        
    main() 