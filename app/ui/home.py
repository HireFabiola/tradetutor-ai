import streamlit as st
import streamlit.components.v1 as components
import textwrap
from pathlib import Path
import base64
import hashlib
from app.rag.llm_client import answer_question
from app.services.attempt_service import process_attempt
from app.services.transcription_service import transcribe_audio

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="TradeTutor AI",
    page_icon="📈",
    layout="wide",
)

# --------------------------------------------------
# GLOBAL STYLING
# --------------------------------------------------
styles_path = Path(__file__).with_name("styles.css")
st.markdown(
    f"<style>{styles_path.read_text()}</style>",
    unsafe_allow_html=True,
)

st.session_state.setdefault("dark_mode", False)

THEME_VARIABLES = {
    "light": {
        "app-bg": "#F7F6F1",
        "text": "#173F4A",
        "muted-text": "#52666A",
        "body-text": "#44545A",
        "surface": "#FFFFFF",
        "surface-soft": "#F5FAF8",
        "surface-teal": "#EAF4F1",
        "surface-warm": "#FFF8EE",
        "border": "#DDE5E2",
        "border-soft": "#E4E7E5",
        "button-bg": "#173F4A",
        "button-hover": "#2A7F7B",
        "button-text": "#FFFFFF",
        "accent-teal": "#2A7F7B",
        "accent-teal-strong": "#078D75",
        "accent-orange": "#D88B39",
        "accent-orange-strong": "#CB762C",
        "note-bg": "#FFF1D8",
        "note-border": "#E7A84B",
        "note-text": "#59482F",
        "price-blue-bg": "#EAF3F9",
        "price-blue-border": "#D4E5EF",
        "price-blue-text": "#14528C",
        "stop-bg": "#FFF0ED",
        "stop-border": "#F6D9D4",
        "stop-text": "#D62C43",
        "target-bg": "#EAF7F1",
        "target-border": "#CBE9DC",
        "target-text": "#078D75",
        "feedback-bg": "#E6F5EF",
        "feedback-border": "#CBE9DE",
        "input-bg": "#FFFFFF",
        "input-border": "#D8DEDC",
        "placeholder": "#78898D",
        "shadow": "rgba(0, 0, 0, 0.05)",
    },
    "dark": {
        "app-bg": "#071D22",
        "text": "#EAF7F4",
        "muted-text": "#B6CCC9",
        "body-text": "#C8D8D5",
        "surface": "#0E2A31",
        "surface-soft": "#12363E",
        "surface-teal": "#103B42",
        "surface-warm": "#332718",
        "border": "#24525A",
        "border-soft": "#1F464D",
        "button-bg": "#2A7F7B",
        "button-hover": "#70D2C5",
        "button-text": "#031D22",
        "accent-teal": "#70D2C5",
        "accent-teal-strong": "#70D2C5",
        "accent-orange": "#F3B562",
        "accent-orange-strong": "#F3B562",
        "note-bg": "#3A2A14",
        "note-border": "#F3B562",
        "note-text": "#FFE7B7",
        "price-blue-bg": "#102D43",
        "price-blue-border": "#285D79",
        "price-blue-text": "#92D5FF",
        "stop-bg": "#3B1B20",
        "stop-border": "#7A3540",
        "stop-text": "#FF9AA7",
        "target-bg": "#12372F",
        "target-border": "#2C6A5D",
        "target-text": "#85E9D7",
        "feedback-bg": "#123B33",
        "feedback-border": "#2E7567",
        "input-bg": "#08252B",
        "input-border": "#2F5E66",
        "placeholder": "#8EA6A3",
        "shadow": "rgba(0, 0, 0, 0.28)",
    },
}

selected_theme = "dark" if st.session_state["dark_mode"] else "light"
theme_css = "\n".join(
    f"    --{name}: {value};"
    for name, value in THEME_VARIABLES[selected_theme].items()
)
st.markdown(
    f"<style>.stApp {{\n{theme_css}\n}}</style>",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# TRADETUTOR BRAND
# --------------------------------------------------
spacer_col, toggle_col, brand_col = st.columns(
    [5, 1.2, 1.9],
    vertical_alignment="center",
)
with toggle_col:
    st.toggle("Light / Dark", key="dark_mode")
with brand_col:
    st.markdown(
        textwrap.dedent("""
<div class="tt-brand-bar">
    <div class="tt-brand">
        <span class="tt-brand-icon" aria-hidden="true">
            <svg viewBox="0 0 32 32" role="img" focusable="false">
                <line x1="9" y1="8" x2="9" y2="24" />
                <rect x="6" y="13" width="6" height="8" rx="1.5" />
                <line x1="16" y1="6" x2="16" y2="23" />
                <rect x="13" y="10" width="6" height="9" rx="1.5" />
                <line x1="23" y1="9" x2="23" y2="25" />
                <rect x="20" y="15" width="6" height="7" rx="1.5" />
            </svg>
        </span>
        <span class="tt-brand-name">TradeTutor</span>
        <span class="tt-brand-ai">AI</span>
    </div>
</div>
"""),
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# LESSON HERO
# --------------------------------------------------
hero_banner_path = Path(__file__).parent / "assets" / "tradetutor_hero_banner.png"
st.image(hero_banner_path, width="stretch")

# --------------------------------------------------
# LESSON VIDEOS
# --------------------------------------------------
st.markdown(
    textwrap.dedent("""
    <div class="video-section-header">
        <div class="video-label">VIDEO LESSON</div>
        <div class="video-title">🎥 Understanding Risk/Reward</div>
        <div class="video-description">
            Watch the three short lesson segments below, then use
            Ask TradeTutor if you need help with any of the concepts.
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)

video_lessons = [
    (
        "Part 1 — Understanding Ratios",
        "https://app.heygen.com/embeds/7d99c67d7fad403e874294eedd1fa0ba",
        textwrap.dedent("""
        <div class="lesson-reading-card">
            <div class="lesson-reading-header">
                <div class="watch-learn-label">READ THE LESSON</div>
                <h3>Understanding ratios</h3>
            </div>
            <div class="lesson-reading-body">
                <p>
                    A ratio is simply a comparison between two quantities. Imagine a classroom
                    where the ratio of boys to girls is 2 to 3. That means for every 2 boys in
                    the room, there are 3 girls.
                </p>
                <div class="lesson-definition">
                    <span>Key takeaway</span>
                    <strong>A ratio compares one quantity to another.</strong>
                </div>
                <p>
                    Ratios show up everywhere once you start looking for them, and trading uses
                    the same basic idea.
                </p>
                <p>
                    A risk/reward ratio compares the money you are risking on a trade to the
                    money you could potentially earn from it.
                </p>
            </div>
        </div>
        """),
    ),
    (
        "Part 2 — Understanding Risk/Reward",
        "https://app.heygen.com/embeds/8c7f9cdbe4a541db826c4005b1c87789",
        textwrap.dedent("""
        <div class="lesson-reading-card">
            <div class="lesson-reading-header">
                <div class="watch-learn-label">READ THE LESSON</div>
                <h3>What risk/reward means</h3>
            </div>
            <div class="lesson-reading-body">
                <p>
                    If a trade has a risk/reward ratio of 2 to 3, that means for every $2 you
                    are risking, you stand to potentially earn $3. The bigger the potential
                    reward compared to the risk, the more favorable the trade looks on paper.
                </p>
                <div class="lesson-definition">
                    <span>Important note</span>
                    <strong>This app calculates the ratio as reward divided by risk.</strong>
                </div>
                <p>
                    Calculating reward divided by risk tells you how much you stand to win for
                    every dollar you are putting at risk. A ratio of 2.0 means you stand to earn
                    $2 for every $1 risked.
                </p>
                <p>
                    The ratio alone is not the whole story. It only tells you what happens if
                    the trade works out, not how likely the trade is to hit its target instead
                    of its stop-loss.
                </p>
                <div class="lesson-reminder">
                    A favorable risk/reward ratio does <strong>not</strong> guarantee a
                    successful trade.
                </div>
            </div>
        </div>
        """),
    ),
    (
        "Part 3 — Calculating Risk/Reward",
        "https://app.heygen.com/embeds/9135edd4f12f44608f720cb02a3e92dd",
        textwrap.dedent("""
        <div class="lesson-reading-card">
            <div class="lesson-reading-header">
                <div class="watch-learn-label">READ THE LESSON</div>
                <h3>Calculating the ratio</h3>
            </div>
            <div class="lesson-reading-body">
                <p>
                    To calculate a risk/reward ratio, you need three numbers: your entry price,
                    your stop-loss price, and your target price.
                </p>
                <div class="lesson-formula-list">
                    <div><span>Risk</span><strong>Entry − Stop-Loss</strong></div>
                    <div><span>Reward</span><strong>Target − Entry</strong></div>
                    <div><span>Risk/Reward Ratio</span><strong>Reward ÷ Risk</strong></div>
                </div>
                <p>
                    For example, imagine you enter a trade at $40, set a stop-loss at $35, and
                    set a target of $50. Your risk is $5, and your reward is $10.
                </p>
                <p>
                    Dividing reward by risk gives a ratio of 2.0. A good ratio makes a trade
                    worth considering alongside the likelihood of the trade reaching its target.
                </p>
            </div>
        </div>
        """),
    ),
]

st.session_state.setdefault("selected_lesson_index", 0)
selected_lesson_index = st.segmented_control(
    "Select video lesson",
    options=range(len(video_lessons)),
    format_func=lambda lesson_index: video_lessons[lesson_index][0],
    key="selected_lesson_index",
    required=True,
    label_visibility="collapsed",
    width="stretch",
    wrap=True,
)
if selected_lesson_index is None:
    selected_lesson_index = 0

watch_col, read_col = st.columns(
    [1, 1],
    gap="large",
    vertical_alignment="top",
)
with watch_col:
    with st.container(key="video_viewer_card"):
        st.markdown(
            '<div class="watch-learn-label">WATCH THE LESSON</div>',
            unsafe_allow_html=True,
        )
        components.iframe(
            video_lessons[selected_lesson_index][1],
            height=460,
        )
with read_col:
    st.markdown(
        video_lessons[selected_lesson_index][2],
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# ASK TRADETUTOR
# --------------------------------------------------
st.session_state.setdefault("ask_question_input", "")
st.session_state.setdefault("ask_tutor_response", "")
st.session_state.setdefault("ask_tutor_last_question", "")

# Apply a new voice transcription before creating the text widget.
if "pending_voice_question" in st.session_state:
    st.session_state["ask_question_input"] = (
        st.session_state.pop("pending_voice_question")
    )

def clear_ask_response() -> None:
    st.session_state["ask_tutor_response"] = ""
    st.session_state["ask_tutor_last_question"] = ""

def set_suggested_question(suggested_question: str) -> None:
    st.session_state["ask_question_input"] = suggested_question
    clear_ask_response()

# Load the peeking avatar.
avatar_path = (
    Path(__file__).parent / "assets" / "ask_tutor_peek.png"
)
avatar_base64 = base64.b64encode(
    avatar_path.read_bytes()
).decode("utf-8")

with st.container(key="ask_tutor_panel"):
    # ---------- HEADER + THINKING AVATAR ----------
    st.markdown(
        textwrap.dedent(f"""
        <div class="tt-ask-hero">
            <div class="tt-ask-heading">
                <div class="ask-icon" aria-hidden="true">
                    ✦<br>AI
                </div>
                <div class="ask-header-copy">
                    <div class="ask-label">
                        YOUR AI LEARNING ASSISTANT
                    </div>
                    <div class="ask-title">
                        Ask TradeTutor
                    </div>
                    <div class="ask-description">
                        Have a question? Let's work through it together.
                    </div>
                </div>
            </div>
            <div class="tt-thinking-avatar" aria-hidden="true">
                <img
                    src="data:image/png;base64,{avatar_base64}"
                    alt=""
                >
            </div>
        </div>
        <div class="ask-suggestions-label">
            Try one of these questions:
        </div>
        """),
        unsafe_allow_html=True,
    )

    # ---------- SUGGESTED QUESTIONS ----------
    suggestion_questions = [
        "What does a 1:3 ratio mean?",
        "Can I still lose money with a good risk/reward ratio?",
        "Why is a stop-loss important?",
    ]
    suggestion_cols = st.columns(3, gap="medium")
    for index, (col, suggestion) in enumerate(
        zip(suggestion_cols, suggestion_questions)
    ):
        with col:
            st.button(
                f"◉  {suggestion}   ›",
                key=f"ask_suggestion_{index}",
                on_click=set_suggested_question,
                args=(suggestion,),
                width="stretch",
            )

    # ---------- EDITABLE QUESTION INPUT ----------
    input_col, ask_col = st.columns(
        [5, 1],
        gap="small",
        vertical_alignment="bottom",
    )
    with input_col:
        question = st.text_input(
            "Your question",
            key="ask_question_input",
            placeholder=(
                "Ask about ratios, stop-losses, "
                "or risk/reward math..."
            ),
            label_visibility="collapsed",
            on_change=clear_ask_response,
        )
    cleaned_question = question.strip()
    with ask_col:
        ask_submitted = st.button(
            "➤  Ask",
            key="ask_tutor_submit",
            disabled=not cleaned_question,
            width="stretch",
        )

    # ---------- VOICE INPUT ----------
    with st.container(key="ask_voice_panel"):
        st.markdown(
            textwrap.dedent("""
            <div class="tt-voice-heading">
                <span class="tt-voice-symbol">🎙</span>
                <div>
                    <div class="tt-voice-title">
                        Prefer to speak your question?
                    </div>
                    <div class="tt-voice-description">
                        Record your question. I'll transcribe
                        it into the box above.
                    </div>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        audio = st.audio_input(
            "Record your question",
            key="ask_voice_input",
        )
        if audio is not None:
            audio_hash = hashlib.sha256(
                audio.getvalue()
            ).hexdigest()
            if (
                st.session_state.get("last_audio_hash")
                != audio_hash
            ):
                with st.spinner("Transcribing your question..."):
                    transcription = transcribe_audio(audio)
                st.session_state["last_audio_hash"] = audio_hash
                if transcription.strip():
                    st.session_state["pending_voice_question"] = (
                        transcription.strip()
                    )
                    clear_ask_response()
                    st.rerun()
                else:
                    st.warning(
                        "No speech detected. "
                        "Please record your question again."
                    )

    # ---------- PROCESS QUESTION ----------
    if ask_submitted and cleaned_question:
        with st.spinner("TradeTutor is thinking..."):
            st.session_state["ask_tutor_response"] = (
                answer_question(cleaned_question)
            )
            st.session_state["ask_tutor_last_question"] = (
                cleaned_question
            )

    # ---------- TUTOR RESPONSE ----------
    with st.container(key="tutor_response_card"):
        st.markdown(
            textwrap.dedent("""
            <div class="tt-response-heading">
                <span class="tt-response-icon">💡</span>
                <span>TradeTutor explains</span>
            </div>
            """),
            unsafe_allow_html=True,
        )
        if st.session_state["ask_tutor_response"]:
            st.markdown(
                st.session_state["ask_tutor_response"]
            )
            st.markdown(
                textwrap.dedent("""
                <div class="response-footer">
                    Answers are grounded in
                    TradeTutor's lesson materials.
                </div>
                """),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                textwrap.dedent("""
                <div class="tt-response-placeholder">
                    Your answer will appear here.
                    I'll break it down step by step,
                    using our lesson materials.
                </div>
                """),
                unsafe_allow_html=True,
            )

# --------------------------------------------------
# PRACTICE
# --------------------------------------------------
st.markdown(
    textwrap.dedent("""
<div class="practice-header">
    <div class="practice-label">PRACTICE SCENARIO</div>
    <div class="practice-title">🧮 Meridian Robotics</div>
    <div class="practice-description">
        Test your understanding with a fictional trade setup.
        Calculate the risk/reward ratio and explain your reasoning.
    </div>
</div>
<div class="price-row">
    <div class="price-card">
        <span>ENTRY PRICE</span>
        <strong>$60</strong>
    </div>
    <div class="price-card stop-card">
        <span>STOP-LOSS PRICE</span>
        <strong>$54</strong>
    </div>
    <div class="price-card target-card">
        <span>TARGET PRICE</span>
        <strong>$78</strong>
    </div>
</div>
"""),
    unsafe_allow_html=True,
)

# --------------------------------------------------
# PRACTICE INPUTS
# --------------------------------------------------
with st.container(border=True):
    answer_col, reasoning_col = st.columns(
        [1, 2],
        gap="large",
    )
    with answer_col:
        numeric_answer = st.number_input(
            "What is the risk/reward ratio?",
            min_value=0.0,
            step=0.1,
            format="%.1f",
        )
    with reasoning_col:
        reasoning_text = st.text_area(
            "Explain your reasoning",
            placeholder=(
                "Explain how you calculated the ratio "
                "and what the result tells you about "
                "potential risk and reward."
            ),
            height=110,
        )
    submitted = st.button(
        "Submit Answer",
        type="primary",
        use_container_width=True,
    )

# --------------------------------------------------
# PROCESS PRACTICE ANSWER
# --------------------------------------------------
if submitted:
    result = process_attempt(
        scenario_id="meridian_001",
        entry_price=60,
        stop_loss_price=54,
        target_price=78,
        numeric_answer=numeric_answer,
        reasoning_text=reasoning_text,
    )
    st.session_state["practice_result"] = result

# --------------------------------------------------
# YOUR FEEDBACK
# --------------------------------------------------
if "practice_result" in st.session_state:
    result = st.session_state["practice_result"]
    st.markdown(
        textwrap.dedent("""
        <div class="feedback-header">
            <div class="feedback-title">📊 Your Feedback</div>
            <div class="feedback-description">
                Here's how you did on this practice scenario.
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )
    feedback_col, score_col, misconception_col = st.columns(
        3,
        gap="medium",
    )

    # ---------- ANSWER FEEDBACK ----------
    with feedback_col:
        with st.container(border=True):
            st.markdown("#### Your Answer")
            if result["is_correct"]:
                st.success(
                    f"Correct! The risk/reward ratio is "
                    f"{result['correct_answer']:.1f}."
                )
            else:
                st.error(
                    f"Not quite. The correct risk/reward ratio is "
                    f"{result['correct_answer']:.1f}."
                )

    # ---------- REASONING SCORE ----------
    with score_col:
        with st.container(border=True):
            st.markdown("#### Reasoning Score")
            scores = result["scores"]
            st.metric(
                "Total Score",
                f"{scores['total']:.1f} / 3.0",
            )
            st.write(
                f"Calculation Process: "
                f"{scores['calculation_process']} / 1"
            )
            st.write(
                f"Interpretation: "
                f"{scores['interpretation']} / 1"
            )
            st.write(
                f"Terminology: "
                f"{scores['terminology']} / 1"
            )

    # ---------- MISCONCEPTION CHECK ----------
    with misconception_col:
        with st.container(border=True):
            st.markdown("#### Misconception Check")
            if result["misconceptions"]:
                for misconception in result["misconceptions"]:
                    st.warning(misconception)
            else:
                st.success("No misconceptions detected.")
