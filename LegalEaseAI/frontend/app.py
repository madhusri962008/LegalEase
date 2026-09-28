import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)
import os
from pathlib import Path

import requests
import streamlit as st

from dotenv import load_dotenv

from backend.services.document_formatter import (
    format_docx,
    format_pdf,
    format_txt
)

def text_to_html(text: str) -> str:
    if not text:
        return ""

    html = text.replace("&", "&amp;")
    html = html.replace("<", "&lt;")
    html = html.replace(">", "&gt;")

    html = html.replace("\n", "<br>")

    return html


load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[1]

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide"
)


# -----------------------------
# CUSTOM CSS
# -----------------------------

st.markdown(
    """
    <style>

    .hero {
        padding: 1.5rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #111827,
            #1e3a8a
        );
        color: white;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.6rem;
    }

    .hero p {
        margin-top: 0.4rem;
        opacity: 0.9;
        font-size: 1.1rem;
    }

    .preview {
        background: #111827;
        color: #f9fafb;
        padding: 1.4rem;
        border-radius: 16px;
        min-height: 420px;
        max-height: 700px;
        overflow-y: auto;
    }

    .preview h1,
    .preview h2,
    .preview h3 {
        color: #93c5fd;
    }

    .preview p,
    .preview li {
        line-height: 1.6;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# HEADER
# -----------------------------

st.markdown(
    """
    <div class="hero">

        <h1>⚖️ LegalEase</h1>

        <p>
            AI-Powered Legal Document Generator
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


st.info(
    "LegalEase is an AI-assisted drafting tool. "
    "Review generated documents with a qualified "
    "legal professional before relying on them."
)


# -----------------------------
# SESSION STATE
# -----------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


if "document_type" not in st.session_state:

    st.session_state.document_type = ""


# -----------------------------
# LAYOUT
# -----------------------------

left, right = st.columns(
    [1, 1.25],
    gap="large"
)


# =====================================================
# LEFT SIDE
# =====================================================

with left:

    st.subheader(
        "Document Details"
    )

    document_type = st.text_input(

        "Document Type",

        placeholder=(
            "e.g. "
            "Non-Disclosure Agreement"
        )
    )

    parties = st.text_area(

        "Parties Involved",

        placeholder=(
            "Jane Doe "
            "(Service Provider), "
            "TechNova Inc. (Client)"
        ),

        height=120
    )

    terms = st.text_area(

        "Terms & Conditions",

        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with "
            "15 days notice"
        ),

        height=180,

        help=(
            "Use semicolons to separate "
            "different terms."
        )
    )

    effective_date = st.text_input(

        "Effective Date",

        placeholder="April 10, 2026"
    )


    # -----------------------------
    # GENERATE BUTTON
    # -----------------------------

    if st.button(
        "Generate Document",
        type="primary",
        use_container_width=True
    ):

        if not all(
            [
                document_type.strip(),
                parties.strip(),
                terms.strip(),
                effective_date.strip(),
            ]
        ):

            st.error(
                "Please complete all four fields."
            )

        else:

            payload = {

                "document_type":
                    document_type.strip(),

                "parties":
                    parties.strip(),

                "terms":
                    terms.strip(),

                "effective_date":
                    effective_date.strip(),
            }


            with st.spinner(
                "Generating document with Gemini..."
            ):

                try:

                    response = requests.post(

                        f"{BACKEND_URL}/api/generate",

                        json=payload,

                        timeout=180
                    )


                    if response.ok:

                        data = response.json()

                        st.session_state.document = (
                            data["content"]
                        )

                        st.session_state.document_type = (
                            data["document_type"]
                        )

                        st.success(
                            "Document generated successfully."
                        )

                    else:

                        try:

                            detail = (
                                response.json()
                                .get(
                                    "detail",
                                    response.text
                                )
                            )

                        except Exception:

                            detail = response.text


                        st.error(
                            f"Backend error "
                            f"({response.status_code}): "
                            f"{detail}"
                        )


                except requests.RequestException as exc:

                    st.error(
                        "Could not connect to FastAPI. "
                        "Make sure the backend is running."
                    )

                    st.caption(
                        str(exc)
                    )


# =====================================================
# RIGHT SIDE
# =====================================================

with right:

    st.subheader(
        "Editable Document"
    )


    edited = st.text_area(

        "Edit the generated document",

        value=st.session_state.document,

        height=500,

        label_visibility="collapsed",

        placeholder=(
            "Your generated document "
            "will appear here."
        )
    )


    st.session_state.document = edited


    # -----------------------------
    # PREVIEW
    # -----------------------------

    if edited.strip():

        st.markdown(
            "### Preview"
        )

        html_preview = text_to_html(
            edited
        )

        st.markdown(

            f"""
            <div class="preview">
                {html_preview}
            </div>
            """,

            unsafe_allow_html=True
        )


        # -----------------------------
        # DOWNLOAD
        # -----------------------------

        st.markdown(
            "### Download"
        )


        col1, col2, col3 = st.columns(3)


        safe_name = (
            "legalease_document"
        )


        with col1:

            st.download_button(

                "Download TXT",

                format_txt(edited),

                f"{safe_name}.txt",

                "text/plain",

                use_container_width=True
            )


        with col2:

            st.download_button(

                "Download DOCX",

                format_docx(

                    edited,

                    st.session_state.document_type
                    or "Legal Document"
                ),

                f"{safe_name}.docx",

                (
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),

                use_container_width=True
            )


        with col3:

            st.download_button(

                "Download PDF",

                format_pdf(

                    edited,

                    st.session_state.document_type
                    or "Legal Document"
                ),

                f"{safe_name}.pdf",

                "application/pdf",

                use_container_width=True
            )


# -----------------------------
# FOOTER
# -----------------------------

st.divider()

st.caption(
    "LegalEase | FastAPI + Streamlit + Google Gemini "
    "| AI-generated text should be reviewed before legal use."
)