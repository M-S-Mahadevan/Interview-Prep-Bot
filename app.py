from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from llm import LLMConfig, chat_completion
from prompts import InterviewContext, build_system_prompt, mode_instruction


load_dotenv()

st.set_page_config(page_title="Interview Prep Chatbot", page_icon="🎓", layout="wide")


def require_api_key() -> bool:
    if os.getenv("OPENAI_API_KEY"):
        return True
    st.error(
        "Missing `OPENAI_API_KEY`. Set it in your environment or create a `.env` file.\n\n"
        "Example `.env`:\n"
        "OPENAI_API_KEY=your_key_here"
    )
    return False


def init_state() -> None:
    st.session_state.setdefault("history", [])


def sidebar_context() -> tuple[InterviewContext, str, float, float]:
    with st.sidebar:
        st.header("Settings")

        model = st.text_input("OpenAI model", value="gpt-4.1-mini")
        st.caption("Use any chat-capable model available in your account.")

        st.subheader("Interview context")
        role = st.text_input("Target role", value="Software Engineer (Fresher)")
        level = st.selectbox("Experience level", ["Fresher", "Intern", "0-2 years", "2-5 years"], index=0)
        interview_type = st.selectbox(
            "Interview type",
            ["HR / Behavioral", "Technical", "Mixed (HR + Technical)"],
            index=2,
        )
        focus_area = st.selectbox(
            "Focus area",
            ["General", "DSA", "Python", "Java", "Web Dev", "Data Analyst", "ML/AI Basics"],
            index=0,
        )
        language = st.selectbox("Language", ["English", "Hindi", "Tamil", "Telugu", "Malayalam"], index=0)

        st.subheader("Generation controls")
        temperature = st.slider("Temperature", 0.0, 1.2, 0.4, 0.05)
        top_p = st.slider("Top-p", 0.1, 1.0, 0.9, 0.05)

        st.divider()
        if st.button("Clear conversation", use_container_width=True):
            st.session_state["history"] = []
            st.rerun()

    ctx = InterviewContext(
        role=role.strip(),
        level=level,
        interview_type=interview_type,
        focus_area=focus_area,
        language=language,
    )
    return ctx, model.strip(), temperature, top_p


def add_to_history(role: str, content: str) -> None:
    st.session_state["history"].append({"role": role, "content": content})


def render_history() -> None:
    for m in st.session_state["history"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])


def main() -> None:
    init_state()
    st.title("Interview Prep Chatbot")
    st.caption("Domain-specific assistant for mock interviews, feedback, and practice.")

    if not require_api_key():
        st.stop()

    ctx, model, temperature, top_p = sidebar_context()
    system_prompt = build_system_prompt(ctx)
    config = LLMConfig(model=model, temperature=temperature, top_p=top_p)

    tab_mock, tab_improve, tab_questions, tab_demo = st.tabs(
        ["Mock Interview", "Answer Improvement", "Question Generator", "Temp / Top‑p Demo"]
    )

    with tab_mock:
        st.subheader("Mock Interview (one question at a time)")
        st.write("Click **Start** to receive one realistic interview question. Reply in chat to get feedback.")

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Start / Next question", use_container_width=True):
                user_msg = mode_instruction("mock")
                reply = chat_completion(
                    system_prompt=system_prompt,
                    user_message=user_msg,
                    history=st.session_state["history"],
                    config=config,
                )
                add_to_history("assistant", reply)
                st.rerun()
        with col2:
            st.info("Tip: Paste your answer in the chat box below, then press Enter.")

        render_history()
        if prompt := st.chat_input("Type your answer (or ask for a follow-up)…"):
            add_to_history("user", prompt)
            coaching_msg = (
                "The user just answered. Evaluate using the rubric and provide improvements, "
                "then ask ONE follow-up question."
            )
            reply = chat_completion(
                system_prompt=system_prompt,
                user_message=coaching_msg,
                history=st.session_state["history"],
                config=config,
            )
            add_to_history("assistant", reply)
            st.rerun()

    with tab_improve:
        st.subheader("Answer Improvement (STAR/CAR + rubric)")
        q = st.text_area("Question (optional)", height=90, placeholder="e.g., Tell me about a time you handled a conflict.")
        a = st.text_area("Your answer", height=180, placeholder="Paste your answer here…")
        if st.button("Improve my answer", type="primary"):
            if not a.strip():
                st.warning("Please paste your answer.")
            else:
                user_msg = mode_instruction("improve") + "\n\n"
                if q.strip():
                    user_msg += f"Question:\n{q.strip()}\n\n"
                user_msg += f"Answer:\n{a.strip()}"
                reply = chat_completion(
                    system_prompt=system_prompt,
                    user_message=user_msg,
                    history=None,
                    config=config,
                )
                st.markdown(reply)

    with tab_questions:
        st.subheader("Curated Question Set")
        if st.button("Generate 10 questions", type="primary"):
            user_msg = mode_instruction("questions")
            reply = chat_completion(
                system_prompt=system_prompt,
                user_message=user_msg,
                history=None,
                config=config,
            )
            st.markdown(reply)

    with tab_demo:
        st.subheader("Demonstrate temperature/top‑p differences (for your report)")
        st.write(
            "Use the same prompt with two configurations. "
            "This is the evidence section you can screenshot for evaluation."
        )
        demo_prompt = st.text_area(
            "Demo prompt",
            height=140,
            value="Generate 5 interview questions for a fresher data analyst role (mix of HR + SQL + case questions).",
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Config A (more deterministic)**")
            t1 = st.slider("A: temperature", 0.0, 1.2, 0.2, 0.05, key="tA")
            p1 = st.slider("A: top‑p", 0.1, 1.0, 0.7, 0.05, key="pA")
        with c2:
            st.markdown("**Config B (more creative/varied)**")
            t2 = st.slider("B: temperature", 0.0, 1.2, 0.9, 0.05, key="tB")
            p2 = st.slider("B: top‑p", 0.1, 1.0, 1.0, 0.05, key="pB")

        if st.button("Run comparison", type="primary"):
            cfg_a = LLMConfig(model=model, temperature=t1, top_p=p1)
            cfg_b = LLMConfig(model=model, temperature=t2, top_p=p2)

            with st.spinner("Generating A…"):
                out_a = chat_completion(
                    system_prompt=system_prompt,
                    user_message=demo_prompt,
                    history=None,
                    config=cfg_a,
                )
            with st.spinner("Generating B…"):
                out_b = chat_completion(
                    system_prompt=system_prompt,
                    user_message=demo_prompt,
                    history=None,
                    config=cfg_b,
                )

            st.divider()
            colA, colB = st.columns(2)
            with colA:
                st.markdown("### Output A")
                st.markdown(out_a)
            with colB:
                st.markdown("### Output B")
                st.markdown(out_b)


if __name__ == "__main__":
    main()

