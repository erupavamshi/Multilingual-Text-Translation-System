
import streamlit as st  # type: ignore[import-not-found]
from streamlit_option_menu import option_menu  # type: ignore[import-not-found]

import language_detect
from translator import translate_text
from evaluation import calculate_bleu


st.set_page_config(
    page_title="AI Translator",
    page_icon="🌍",
    layout="wide"
)


LANGUAGES = [
    "English",
    "Tamil",
    "Hindi",
    "Telugu",
    "Malayalam",
    "French",
    "Spanish",
    "German",
    "Arabic",
    "Chinese"
]

COMPARISON_LANGUAGES = ["Tamil", "Hindi", "Telugu"]

MENU_OPTIONS = [
    "Dashboard",
    "Text Translation",
    "File Translation",
    "Model Comparison",
    "Analytics",
    "History"
]

MENU_ICONS = [
    "house",
    "translate",
    "file-earmark-text",
    "columns",
    "graph-up",
    "clock-history"
]


def initialize_session():
    default_values = {
        "main_output": "",
        "history": [],
        "last_result": "",
        "comparison_results": None,
        "bleu_results": [],
        "latest_bleu_evaluation": None
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_history_entry(original, source, target, translated, entry_type):
    entry = {
        "Input": original,
        "Source": source,
        "Target": target,
        "Translation": translated,
        "Type": entry_type
    }

    st.session_state.history.append(entry)


def apply_page_style():
    st.markdown("""
    <style>
    .stApp {
        background-color: #f5f7fb;
    }

    .main-title {
        font-size: 36px;
        font-weight: 800;
        color: #243b64;
    }

    .subtitle {
        color: #68758b;
        font-size: 16px;
    }

    div.stButton > button {
        background-color: #315efb;
        color: white;
        border-radius: 10px;
        border: none;
        height: 45px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #2448c7;
        color: white;
    }

    [data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e4e9f2;
    }
    </style>
    """, unsafe_allow_html=True)


def show_header():
    st.markdown(
        '<div class="main-title">AI-Powered Multilingual Translator</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Translate, compare and evaluate languages using AI models.</div>',
        unsafe_allow_html=True
    )

    st.divider()


def show_navigation():
    with st.sidebar:
        st.markdown("## 🌍 AI Translator")
        st.caption("Multilingual Translation System")

        selected_page = option_menu(
            "Navigation",
            MENU_OPTIONS,
            icons=MENU_ICONS,
            default_index=0,
            styles={
                "container": {"padding": "5px"},
                "icon": {
                    "color": "#315efb",
                    "font-size": "18px"
                },
                "nav-link-selected": {
                    "background-color": "#315efb",
                    "color": "white"
                }
            }
        )

    return selected_page


def show_dashboard():
    st.subheader("Project Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Supported Languages", len(LANGUAGES))

    with col2:
        st.metric("AI Translation Models", 2)

    with col3:
        st.metric(
            "Translations Completed",
            len(st.session_state.history)
        )

    st.divider()
    st.subheader("Available Features")

    col1, col2 = st.columns(2)

    with col1:
        st.info("🌐 Automatic language detection")
        st.info("📝 Text and file translation")
        st.info("📚 Translation history")

    with col2:
        st.info("🤖 NLLB-200 and M2M100")
        st.info("📊 BLEU score evaluation")
        st.info("📈 Translation analytics")


def show_text_translation():
    st.subheader("Text Translation")

    original_text = st.text_area(
        "Enter your text",
        height=180,
        key="main_text"
    )

    target_language = st.selectbox(
        "Target Language",
        LANGUAGES
    )

    if st.button("Translate Text", use_container_width=True):
        if not original_text.strip():
            st.warning("Please enter some text.")

        else:
            source_language = language_detect.detect_language(
                original_text
            )

            if source_language not in LANGUAGES:
                st.error(
                    "Unable to detect the language. Enter a longer sentence."
                )

            elif source_language == target_language:
                st.info("Source and target languages are the same.")

            else:
                try:
                    with st.spinner("Translating..."):
                        translated_text = translate_text(
                            original_text,
                            source_language,
                            target_language
                        )

                    st.session_state.last_result = translated_text
                    st.session_state.main_output = translated_text

                    add_history_entry(
                        original_text,
                        source_language,
                        target_language,
                        translated_text,
                        "Text"
                    )

                    st.success("Translation completed!")
                    st.write("Detected Language:", source_language)

                except Exception as error:
                    st.error(f"Translation failed: {error}")

    if st.session_state.last_result:
        st.text_area(
            "Translated Output",
            height=180,
            key="main_output"
        )

        st.download_button(
            "Download Translation",
            st.session_state.last_result,
            file_name="translation.txt",
            mime="text/plain"
        )

        if st.button("Copy Translation"):
            st.code(st.session_state.last_result)


def show_file_translation():
    st.subheader("TXT File Translation")

    uploaded_file = st.file_uploader(
        "Upload a text file",
        type=["txt"]
    )

    target_language = st.selectbox(
        "Target Language",
        LANGUAGES
    )

    if uploaded_file is None:
        return

    try:
        file_text = uploaded_file.getvalue().decode("utf-8")

        st.text_area(
            "File Content",
            file_text,
            height=150
        )

        if st.button("Translate File"):
            if not file_text.strip():
                st.warning("File is empty.")
                return

            source_language = language_detect.detect_language(
                file_text
            )

            if source_language not in LANGUAGES:
                st.error("Unable to detect the language.")

            elif source_language == target_language:
                st.info("File is already in the selected language.")

            else:
                with st.spinner("Translating file..."):
                    translated_text = translate_text(
                        file_text,
                        source_language,
                        target_language
                    )

                add_history_entry(
                    file_text,
                    source_language,
                    target_language,
                    translated_text,
                    "File"
                )

                st.success("File translated successfully!")

                st.text_area(
                    "Translated File",
                    translated_text,
                    height=150,
                    key="translated_file_output"
                )

                st.download_button(
                    "Download Translated File",
                    translated_text,
                    file_name="translated_file.txt",
                    mime="text/plain"
                )

    except UnicodeDecodeError:
        st.error("Please upload a UTF-8 encoded TXT file.")

    except Exception as error:
        st.error(f"File translation failed: {error}")


def show_model_comparison():
    st.subheader("AI Model Comparison")

    st.info(
        "Compare NLLB-200 and M2M100 for Tamil and Hindi. "
        "Telugu is evaluated using NLLB-200."
    )

    original_text = st.text_area(
        "Enter English text",
        height=150,
        key="comparison_text"
    )

    target_language = st.selectbox(
        "Target Language",
        COMPARISON_LANGUAGES,
        key="comparison_target"
    )

    if st.button("Compare Models", use_container_width=True):
        if not original_text.strip():
            st.warning("Please enter some text.")

        elif language_detect.detect_language(original_text) != "English":
            st.warning("Please enter English text.")

        else:
            try:
                with st.spinner("Comparing models..."):
                    from comparison import compare_models

                    nllb_result, m2m_result = compare_models(
                        original_text,
                        target_language
                    )

                st.session_state.comparison_results = {
                    "input": original_text,
                    "target": target_language,
                    "nllb": nllb_result,
                    "m2m": m2m_result
                }

                st.session_state.latest_bleu_evaluation = None

            except Exception as error:
                st.error(f"Comparison failed: {error}")

    comparison = st.session_state.comparison_results

    if comparison is None:
        return

    st.markdown(f"### English → {comparison['target']}")

    col1, col2 = st.columns(2)

    comparison_key = (
        f"{comparison['target']}_{abs(hash(comparison['input']))}"
    )

    with col1:
        st.markdown("### NLLB-200")

        st.text_area(
            "NLLB Translation",
            comparison["nllb"],
            height=150,
            key=f"nllb_result_{comparison_key}",
            disabled=True
        )

    with col2:
        st.markdown("### M2M100")

        if comparison["m2m"] is not None:
            st.text_area(
                "M2M100 Translation",
                comparison["m2m"],
                height=150,
                key=f"m2m_result_{comparison_key}",
                disabled=True
            )
        else:
            st.info(
                "M2M100 does not support Telugu. "
                "NLLB-200 is used for Telugu translation."
            )

    st.divider()
    st.markdown("### BLEU Score Evaluation")

    reference_text = st.text_area(
        f"Enter the correct {comparison['target']} reference translation",
        key="model_reference"
    )

    if st.button("Evaluate Models"):
        if not reference_text.strip():
            st.warning("Enter a reference translation.")

        else:
            try:
                nllb_score = calculate_bleu(
                    reference_text,
                    comparison["nllb"]
                )

                m2m_score = None

                if comparison["m2m"] is not None:
                    m2m_score = calculate_bleu(
                        reference_text,
                        comparison["m2m"]
                    )

                evaluation = {
                    "Target": comparison["target"],
                    "NLLB-200": nllb_score,
                    "M2M100": m2m_score
                }

                st.session_state.bleu_results.append(evaluation)
                st.session_state.latest_bleu_evaluation = evaluation

            except Exception as error:
                st.error(f"BLEU evaluation failed: {error}")

    latest_evaluation = st.session_state.latest_bleu_evaluation

    if (
        latest_evaluation is not None
        and latest_evaluation["Target"] == comparison["target"]
    ):
        st.success("BLEU evaluation completed!")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "NLLB-200 BLEU Score",
                f"{latest_evaluation['NLLB-200']}/100"
            )

        with col2:
            if latest_evaluation["M2M100"] is not None:
                st.metric(
                    "M2M100 BLEU Score",
                    f"{latest_evaluation['M2M100']}/100"
                )
            else:
                st.info("M2M100 is unavailable for this language.")


def show_analytics():
    st.subheader("Translation Quality Analysis")

    if not st.session_state.bleu_results:
        st.info(
            "Compare and evaluate models first to see BLEU analysis."
        )
        return

    available_targets = sorted({
        item["Target"]
        for item in st.session_state.bleu_results
    })

    selected_target = st.selectbox(
        "Select language for BLEU analysis",
        available_targets,
        key="analytics_bleu_target"
    )

    target_results = [
        item
        for item in st.session_state.bleu_results
        if item["Target"] == selected_target
    ]

    nllb_scores = [
        item["NLLB-200"]
        for item in target_results
    ]

    m2m_scores = [
        item["M2M100"]
        for item in target_results
        if item["M2M100"] is not None
    ]

    average_nllb = sum(nllb_scores) / len(nllb_scores)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Average NLLB-200 BLEU",
            f"{average_nllb:.2f}/100"
        )

    with col2:
        if m2m_scores:
            average_m2m = sum(m2m_scores) / len(m2m_scores)

            st.metric(
                "Average M2M100 BLEU",
                f"{average_m2m:.2f}/100"
            )
        else:
            average_m2m = None
            st.info("M2M100 scores are not available for Telugu.")

    st.markdown(
        f"### English → {selected_target} Model Performance"
    )

    chart_data = {
        "NLLB-200": [average_nllb]
    }

    if average_m2m is not None:
        chart_data["M2M100"] = [average_m2m]

    st.bar_chart(chart_data)

    st.write(
        "Number of evaluations:",
        len(target_results)
    )


def show_history():
    st.subheader("Translation History")

    history = st.session_state.history

    if not history:
        st.info("No translations available yet.")
        return

    for item in reversed(history):
        with st.expander(
            f'{item["Source"]} → {item["Target"]}'
        ):
            st.write("Type:", item.get("Type", "Text"))
            st.write("Original:", item["Input"])
            st.write("Translation:", item["Translation"])

    history_text = "\n\n".join(
        f'Original: {item["Input"]}\n'
        f'Source: {item["Source"]}\n'
        f'Target: {item["Target"]}\n'
        f'Type: {item.get("Type", "Text")}\n'
        f'Translation: {item["Translation"]}'
        for item in history
    )

    st.download_button(
        "Download History",
        history_text,
        file_name="translation_history.txt"
    )

    if st.button("Clear History"):
        st.session_state.history = []
        st.session_state.last_result = ""
        st.session_state.main_output = ""
        st.session_state.comparison_results = None
        st.session_state.bleu_results = []
        st.session_state.latest_bleu_evaluation = None

        st.rerun()


def main():
    initialize_session()
    apply_page_style()

    selected_page = show_navigation()

    show_header()

    pages = {
        "Dashboard": show_dashboard,
        "Text Translation": show_text_translation,
        "File Translation": show_file_translation,
        "Model Comparison": show_model_comparison,
        "Analytics": show_analytics,
        "History": show_history
    }

    pages[selected_page]()

    st.divider()

    st.caption(
        "AI-Powered Multilingual Text Translation System | NLP Project"
    )


if __name__ == "__main__":
    main()
