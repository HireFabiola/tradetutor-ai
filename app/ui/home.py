import streamlit as st
import streamlit.components.v1 as components
import textwrap
from pathlib import Path

from app.rag.llm_client import answer_question
from app.services.attempt_service import process_attempt


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

# --------------------------------------------------
# TRADETUTOR BRAND
# --------------------------------------------------

st.markdown(
    textwrap.dedent("""
    <div style="
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-bottom: 18px;
    ">
        <div style="
            font-size: 26px;
            font-weight: 800;
            color: #173F4A;
        ">
            📈 TradeTutor <span style="color:#2A7F7B;">AI</span>
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)

# --------------------------------------------------
# LESSON HERO
# --------------------------------------------------

st.markdown(
    textwrap.dedent("""
    <div style="
        background: linear-gradient(135deg, #173F4A 0%, #245D65 100%);
        padding: 38px 42px;
        border-radius: 22px;
        margin-bottom: 30px;
    ">
        <div style="
            color: #9FD8D2;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
        ">
            RISK MANAGEMENT FUNDAMENTALS
        </div>
        <div style="
            color: white;
            font-size: 42px;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 14px;
        ">
            Understanding Risk/Reward Ratios
        </div>
        <div style="
            color: #E5F0EF;
            font-size: 17px;
            max-width: 700px;
            line-height: 1.6;
        ">
            Learn how to calculate a risk/reward ratio, understand what
            the number means, and recognize why a favorable ratio does
            not guarantee a successful trade.
        </div>
        <div style="
            margin-top: 22px;
            color: #F3B562;
            font-size: 15px;
            font-weight: 600;
        ">
            Learn the Why. Practice the How.
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)

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

col1, col2, col3 = st.columns(3)


# ---------- PART 1 ----------

with col1:
    st.markdown(
        textwrap.dedent("""
        <div class="video-part">PART 1</div>
        <div class="video-part-title">Understanding Ratios</div>
        """),
        unsafe_allow_html=True,
    )

    components.iframe(
        "https://app.heygen.com/embeds/7d99c67d7fad403e874294eedd1fa0ba",
        height=230,
    )


# ---------- PART 2 ----------

with col2:
    st.markdown(
        textwrap.dedent("""
        <div class="video-part">PART 2</div>
        <div class="video-part-title">Understanding Risk/Reward</div>
        """),
        unsafe_allow_html=True,
    )

    components.iframe(
        "https://app.heygen.com/embeds/8c7f9cdbe4a541db826c4005b1c87789",
        height=230,
    )


# ---------- PART 3 ----------

with col3:
    st.markdown(
        textwrap.dedent("""
        <div class="video-part">PART 3</div>
        <div class="video-part-title">Calculating Risk/Reward</div>
        """),
        unsafe_allow_html=True,
    )

    components.iframe(
        "https://app.heygen.com/embeds/9135edd4f12f44608f720cb02a3e92dd",
        height=230,
    )
# --------------------------------------------------
# KEY TAKEAWAYS
# --------------------------------------------------

st.markdown(
    textwrap.dedent("""
    <div class="takeaway-card">
        <div class="takeaway-title">
            💡 Key Takeaways
        </div>
        <div class="formula-row">
            <div class="formula-box">
                <span>RISK</span>
                <strong>Entry − Stop-Loss</strong>
            </div>
            <div class="formula-box">
                <span>REWARD</span>
                <strong>Target − Entry</strong>
            </div>
            <div class="formula-box">
                <span>RATIO</span>
                <strong>Reward ÷ Risk</strong>
            </div>
        </div>
        <div class="takeaway-note">
            A favorable risk/reward ratio does
            <strong>not</strong> guarantee a successful trade.
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)

# --------------------------------------------------
# ASK TRADETUTOR
# --------------------------------------------------

st.markdown(
    textwrap.dedent("""
    <div class="ask-card-header">
        <div class="ask-label">AI TUTOR</div>
        <div class="ask-title">💬 Ask TradeTutor</div>
        <div class="ask-description">
            Have a question about anything from this lesson?
            <br>Ask TradeTutor for help understanding the concepts
            and applying what you've learned.
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)

question = st.text_input(
    "Ask about this lesson",
    placeholder=(
        "Example: Why doesn't a good risk/reward ratio "
        "guarantee a profitable trade?"
    ),
)

if st.button("Ask TradeTutor"):
    if question:
        with st.spinner("TradeTutor is thinking..."):
            answer = answer_question(question)

        st.markdown(
            '<div class="ask-label">TRADETUTOR RESPONSE</div>',
            unsafe_allow_html=True,
        )

        st.info(answer)

    else:
        st.warning("Please enter a question first.")



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
