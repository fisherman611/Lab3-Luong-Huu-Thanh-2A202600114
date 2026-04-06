import os
import sys
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.agent.agent import ReActAgent
from src.tools.registry import TOOLS
from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip()
    return v if v else default


def _build_llm(provider: str, model_name: str):
    if provider == "openai":
        api_key = _get_env("NVIDIA_API_KEY") or _get_env("OPENAI_API_KEY")
        base_url = _get_env("NVIDIA_BASE_URL") or _get_env("OPENAI_BASE_URL")
        if not api_key:
            raise ValueError("Thiếu API key. Hãy set NVIDIA_API_KEY hoặc OPENAI_API_KEY trong .env")
        # NVIDIA integrate endpoints are OpenAI-compatible but require NVIDIA model ids
        if base_url and "integrate.api.nvidia.com" in base_url and "/" not in model_name:
            raise ValueError(
                "Model không hợp lệ cho NVIDIA_BASE_URL. "
                "Hãy dùng model id dạng 'openai/gpt-oss-20b' (không phải 'gpt-4o')."
            )
        return OpenAIProvider(model_name=model_name, api_key=api_key, base_url=base_url)

    if provider == "google":
        api_key = _get_env("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Thiếu GEMINI_API_KEY trong .env")
        return GeminiProvider(model_name=model_name, api_key=api_key)

    raise ValueError(f"Provider không hỗ trợ trong UI: {provider}")


def main():
    load_dotenv()

    st.set_page_config(page_title="ReAct Agent UI", layout="wide")
    st.title("ReAct Travel Agent UI")
    st.caption("Nhập câu hỏi, agent sẽ dùng tools (calculate/search/weather) để trả lời.")

    with st.sidebar:
        st.subheader("Cấu hình")
        provider = st.selectbox("Provider", options=["openai", "google"], index=0)
        if provider == "openai":
            # If user is pointing to NVIDIA integrate, default to NVIDIA model id.
            nvidia_base_url = _get_env("NVIDIA_BASE_URL")
            if nvidia_base_url:
                default_model = _get_env("DEFAULT_MODEL", "openai/gpt-oss-20b")
                if "/" not in default_model:
                    default_model = "openai/gpt-oss-20b"
            else:
                default_model = _get_env("DEFAULT_MODEL", "gpt-4o")
        else:
            default_model = _get_env("DEFAULT_MODEL", "gemini-1.5-flash")
        model_name = st.text_input("Model", value=default_model)
        max_steps = st.slider("Max steps", min_value=1, max_value=12, value=8)
        show_trace = st.checkbox("Hiển thị trace", value=True)

        st.divider()
        st.subheader("Tools đang có")
        for t in TOOLS:
            st.markdown(f"- **{t['name']}**: {t['description']}")

    user_q = st.text_area(
        "Câu hỏi",
        value="Tôi có 5 triệu đồng, muốn đi du lịch 3 ngày. Nên đi Hà Nội hay Đà Nẵng? Chi phí mỗi ngày khoảng bao nhiêu?",
        height=120,
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        run_btn = st.button("Chạy agent", type="primary", use_container_width=True)
    with col2:
        st.info("Tip: Hỏi câu cần tool như thời tiết/chi phí/ngân sách để agent có lý do dựa trên dữ liệu.")

    if run_btn:
        try:
            llm = _build_llm(provider=provider, model_name=model_name)
            agent = ReActAgent(llm=llm, tools=TOOLS, max_steps=max_steps)
        except Exception as e:
            st.error(str(e))
            return

        with st.spinner("Đang chạy..."):
            answer, trace = agent.run_with_trace(user_q)

        st.subheader("Final Answer")
        st.write(answer)

        if show_trace:
            st.subheader("Trace (Thought/Action/Observation)")
            for step in trace:
                step_no = step.get("step", "?")
                title = f"Step {step_no}"
                if step.get("tool"):
                    title += f" • {step.get('tool')}({step.get('args', '')})"
                with st.expander(title, expanded=False):
                    st.code(step.get("llm_output", ""), language="text")
                    obs = step.get("observation")
                    if obs is not None:
                        st.markdown("**Observation**")
                        st.code(str(obs), language="text")


if __name__ == "__main__":
    main()

