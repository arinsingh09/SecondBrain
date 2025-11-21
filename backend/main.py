# main.py
import streamlit as st
import json
from rag_engine import ask
import re 
st.set_page_config(page_title="🧠 Second Brain", layout="wide")
st.title("🧠 Your Second Brain")

tab_ask, tab_history, tab_flash = st.tabs(["💬 Ask", "📜 History", "⚡ Flash Cards"])

# 💬 ASK TAB
with tab_ask:
    user_prompt = st.text_input("❓ Ask me anything from your S3 data:")

    if st.button("Ask"):
        if not user_prompt.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                try:
                    answer = ask(user_prompt)
                    st.markdown("**Answer:**")
                    st.write(answer)
                    st.session_state.setdefault("history", []).append({
                        "user": user_prompt, "bot": answer
                    })
                except Exception as e:
                    st.error(f"Error: {e}")

# 📜 HISTORY TAB
with tab_history:
    st.subheader("Conversation History")
    history = st.session_state.get("history", [])
    if not history:
        st.info("No questions asked yet.")
    else:
        for msg in reversed(history):
            st.markdown(f"**🧑 You:** {msg['user']}")
            st.markdown(f"**🤖 Bot:** {msg['bot']}")
            st.divider()

# ⚡ FLASHCARDS TAB
with tab_flash:
    st.subheader("Generate Flashcards from your AWS data")
    if st.button("Generate Flashcards"):
        with st.spinner("Generating flashcards..."):
            try:
                response = ask(
                    "Generate 10 flashcards as JSON array with 'question' and 'answer'."
                )
                try:
                    # Extract JSON array inside optional code fences
                    cleaned = re.search(r"\[.*\]", response, re.DOTALL)
                    if cleaned:
                        response_json = cleaned.group(0)
                    else:
                        response_json = response

                    cards = json.loads(response_json)

                except json.JSONDecodeError:
                    st.error("⚠️ Could not parse model output as JSON. Showing raw output:")
                    st.code(response)
                    st.stop()

                for i, c in enumerate(cards, start=1):
                    with st.expander(f"Card {i}: {c.get('question', '❓')}"):
                        st.write(c.get('answer', '❓'))
            except Exception as e:
                st.error(f"Error: {e}")
