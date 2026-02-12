# import streamlit as st
# import pdfplumber
# import io
# import torch
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
#
#
# # ----------------------- WORKING MODEL (manual loading) -----------------------
# @st.cache_resource
# def load_model():
#     """Manual model loading - WORKS EVERYWHERE"""
#     model_name = "facebook/bart-large-cnn"
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#     model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
#
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     model.to(device)
#     return tokenizer, model, device
#
#
# # ----------------------- PDF TEXT EXTRACTION -----------------------
# def extract_text_from_pdf(file_bytes: bytes) -> str:
#     text = ""
#     with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text
#
#
# # ----------------------- FAST CHUNKING -----------------------
# def chunk_text(text: str, max_tokens: int = 400):
#     sentences = text.split(". ")
#     chunks = []
#     current = ""
#     for s in sentences:
#         if len(current.split()) + len(s.split()) > max_tokens:
#             if current.strip():
#                 chunks.append(current.strip())
#             current = s + ". "
#         else:
#             current += s + ". "
#     if current.strip():
#         chunks.append(current.strip())
#     return chunks
#
#
# # ----------------------- FAST SUMMARIZATION -----------------------
# @torch.no_grad()
# def summarize_chunk(tokenizer, model, device, text: str, max_len: int = 100, min_len: int = 20):
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
#
#     summary_ids = model.generate(
#         inputs.input_ids,
#         max_length=max_len,
#         min_length=min_len,
#         length_penalty=2.0,
#         num_beams=4,
#         early_stopping=True
#     )
#     return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
#
#
# # ----------------------- COMPLETE SUMMARIZER -----------------------
# def summarize_paper(full_text: str):
#     tokenizer, model, device = load_model()
#     chunks = chunk_text(full_text)
#
#     # Fast chunk summaries
#     chunk_summaries = []
#     progress_bar = st.progress(0)
#
#     for i, chunk in enumerate(chunks[:8], 1):  # Limit to 8 chunks
#         with st.spinner(f"Summarizing chunk {i}/{min(8, len(chunks))}"):
#             summary = summarize_chunk(tokenizer, model, device, chunk)
#             chunk_summaries.append(summary)
#
#         progress_bar.progress(i / min(8, len(chunks)))
#
#     # Final summary
#     joined = " ".join(chunk_summaries[:4])
#     final_summary = summarize_chunk(tokenizer, model, device, joined, max_len=150, min_len=40)
#
#     return final_summary, chunk_summaries
#
#
# # ----------------------- STREAMLIT UI -----------------------
# def main():
#     st.set_page_config(page_title="Research Paper Summarizer", layout="wide")
#     st.title("🚀 Research Paper Summarizer")
#     st.markdown("Upload PDF → Get summary")
#
#     uploaded_file = st.file_uploader("📄 Upload Research Paper (PDF)", type=["pdf"])
#
#     if uploaded_file is not None:
#         if st.button("🔥 SUMMARIZE PAPER", type="primary", use_container_width=True):
#             with st.spinner("Extracting text from PDF..."):
#                 file_bytes = uploaded_file.read()
#                 raw_text = extract_text_from_pdf(file_bytes)
#
#             if not raw_text.strip():
#                 st.error("❌ No text found in PDF!")
#                 st.stop()
#
#             word_count = len(raw_text.split())
#             st.success(f"✅ Extracted {word_count:,} words")
#
#             st.info("🔄 Generating summary...")
#             final_summary, chunk_summaries = summarize_paper(raw_text)
#
#             # Results
#             st.markdown("---")
#             st.subheader("📋 **Final Summary**")
#             st.markdown(final_summary)
#
#             st.markdown("---")
#             with st.expander(f"🔍 View {len(chunk_summaries)} chunk summaries"):
#                 for i, summary in enumerate(chunk_summaries, 1):
#                     st.markdown(f"**Chunk {i}:**")
#                     st.write(summary)
#                     st.markdown("─" * 50)
#
#
# if __name__ == "__main__":
#     main()
import streamlit as st
import pdfplumber
import io
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ----------------------- Pastel CSS Styling (ALL BLACK TEXT) -----------------------
# ----------------------- NUCLEAR CSS - DRAG BOX FIXED -----------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* FORCE EVERYTHING BLACK */
    * { 
        color: #2d3436 !important; 
        font-family: 'Poppins', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* DRAG & DROP - MULTIPLE SELECTORS */
    div[data-testid="stFileUploader"] *,
    div[data-testid="stFileUploader"] label *,
    div[data-testid="stFileUploader"] div *,
    .stFileUploader *,
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] div,
    div[style*="background-color"] span,
    div[style*="rgba"] span {
        color: #2d3436 !important;
        background-color: transparent !important;
    }

    /* ULTIMATE DRAG BOX OVERRIDE */
    div[data-testid="stFileUploader"] label > div:first-child,
    div[data-testid="stFileUploader"] > label > div,
    .stFileUploader > label > div {
        color: #2d3436 !important;
        background: rgba(255, 255, 255, 0.9) !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border: 3px dashed #a8edea !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 { color: #2d3436 !important; font-weight: 600; }

    /* Status messages */
    div[data-testid="stStatusMessage"],
    .stSpinner,
    .stProgress > div > div {
        color: #2d3436 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #ff9a9e, #fecfef) !important;
        color: #2d3436 !important;
        border-radius: 25px;
        border: none;
        padding: 12px 30px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(255, 154, 158, 0.4);
    }

    .stButton > button:hover {
        background: linear-gradient(45deg, #ff758c, #ff7eb3) !important;
        color: #2d3436 !important;
        transform: translateY(-2px);
    }

    /* Sidebar ONLY - white text */
    section[data-testid="stSidebar"] * { 
        color: white !important; 
        background: linear-gradient(180deg, #f093fb 0%, #f5576c 100%) !important;
    }

    /* Success/Error */
    .stSuccess { 
        background-color: #d1f2a5 !important; 
        color: #2d3436 !important; 
        border-radius: 15px; 
        padding: 15px; 
        border-left: 5px solid #4ecdc4; 
    }

    .stError { 
        background-color: #ffafbd !important; 
        color: #2d3436 !important; 
        border-radius: 15px; 
        padding: 15px; 
        border-left: 5px solid #ff6b6b; 
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #a8edea, #fed6e3) !important;
    }

    /* Expanders */
    .stExpander { 
        background: rgba(255, 255, 255, 0.95) !important; 
        border-radius: 15px; 
        border: 2px solid #a8edea; 
    }
    /* REMOVE DOTTED DRAG BOX BORDER */
div[data-testid="stFileUploader"] label {
    border: none !important;
    box-shadow: none !important;
}

div[data-testid="stFileUploader"] div[style*="dashed"] {
    border: none !important;
    border-radius: 0 !important;
}

.stFileUploader label {
    border: 2px solid transparent !important;
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 15px !important;
    box-shadow: 0 4px 15px rgba(168, 237, 234, 0.3) !important;
}

</style>
""", unsafe_allow_html=True)


# ----------------------- MODEL (same as before) -----------------------
@st.cache_resource
def load_model():
    model_name = "facebook/bart-large-cnn"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return tokenizer, model, device


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def chunk_text(text: str, max_tokens: int = 400):
    sentences = text.split(". ")
    chunks = []
    current = ""
    for s in sentences:
        if len(current.split()) + len(s.split()) > max_tokens:
            if current.strip():
                chunks.append(current.strip())
            current = s + ". "
        else:
            current += s + ". "
    if current.strip():
        chunks.append(current.strip())
    return chunks


@torch.no_grad()
def summarize_chunk(tokenizer, model, device, text: str, max_len: int = 100, min_len: int = 20):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    summary_ids = model.generate(
        inputs.input_ids,
        max_length=max_len,
        min_length=min_len,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def summarize_paper(full_text: str):
    tokenizer, model, device = load_model()
    chunks = chunk_text(full_text)

    chunk_summaries = []
    progress_bar = st.progress(0)

    for i, chunk in enumerate(chunks[:8], 1):
        with st.spinner(f"✨ Summarizing chunk {i}/{min(8, len(chunks))}"):
            summary = summarize_chunk(tokenizer, model, device, chunk)
            chunk_summaries.append(summary)
        progress_bar.progress(i / min(8, len(chunks)))

    joined = " ".join(chunk_summaries[:4])
    final_summary = summarize_chunk(tokenizer, model, device, joined, max_len=150, min_len=40)
    return final_summary, chunk_summaries


# ----------------------- PASTEL UI -----------------------
def main():
    st.set_page_config(page_title="Pastel Paper Summarizer", layout="wide")

    # Pastel header
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(45deg, #ffecd2 0%, #fcb69f 100%); border-radius: 25px; margin-bottom: 2rem;'>
        <h1 style='color: #5f27cd; font-size: 3rem; margin: 0;'>📚 Pastel Paper Summarizer</h1>
        <p style='color: #6c5ce7; font-size: 1.3rem;'>Upload PDF → ✨ Magic Summary ✨</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        uploaded_file = st.file_uploader("📁 PDF", type=["pdf"])

    with col2:
        st.markdown("### 🎨 Features")
        st.markdown("""
        - 🌈 **Pastel design**
        - ⚡ **Fast processing**  
        - 📊 **Progress tracking**  
        - 🔍 **Chunk-by-chunk summaries**
        - 💾 **Model caching**
        """, unsafe_allow_html=True)

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎀 **SUMMARIZE MAGICALLY** 🎀", type="primary",
                         use_container_width=True, key="summarize"):
                with st.spinner("🌺 Extracting text..."):
                    file_bytes = uploaded_file.read()
                    raw_text = extract_text_from_pdf(file_bytes)

                if not raw_text.strip():
                    st.error("❌ No text found in PDF!")
                    st.stop()

                word_count = len(raw_text.split())
                st.success(f"✅ Extracted **{word_count:,}** words ✨")

                st.info("🎪 Generating your pastel summary...")
                final_summary, chunk_summaries = summarize_paper(raw_text)

                # Pastel Results
                st.markdown("─" * 80)
                st.markdown("""
                <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                           padding: 2rem; border-radius: 20px; margin: 1rem 0;'>
                    <h2 style='color: #5f27cd; text-align: center;'>📋 Final Summary ✨</h2>
                    <div style='background: rgba(255,255,255,0.8); padding: 1.5rem; 
                               border-radius: 15px; font-size: 1.1rem; line-height: 1.6;'>
                        """ + final_summary.replace("\n", "</br>") + """
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f" View {len(chunk_summaries)} **chunk summaries**", expanded=False):
                    for i, summary in enumerate(chunk_summaries, 1):
                        pastel_colors = ["#ffecd2", "#fcb69f", "#a8edea", "#d1f2a5", "#ffafbd", "#ff9a9e"]
                        color = pastel_colors[i % len(pastel_colors)]
                        st.markdown(f"""
                        <div style='background: {color}; padding: 1rem; 
                                   border-radius: 15px; margin: 0.5rem 0;'>
                            <h4 style='color: #5f27cd; margin: 0;'>Chunk {i}</h4>
                            <p style='margin: 0.5rem 0 0 0; line-height: 1.5;'>{summary}</p>
                        </div>
                        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
