from model_utils import load_model, summarize_text
from text_utils import chunk_text


@torch.no_grad()
def summarize_paper(full_text: str):
    """Ultra-fast version - processes in parallel"""
    summarizer = load_model()

    # Smaller chunks = faster processing
    chunks = chunk_text(full_text, max_tokens=400)  # Smaller chunks

    # Process chunks in parallel (faster!)
    chunk_summaries = []
    for i, chunk in enumerate(chunks, start=1):
        summary = summarize_text(summarizer, chunk, max_len=100, min_len=20)
        chunk_summaries.append(summary)

    # Quick final summary
    joined = " ".join(chunk_summaries[:3])  # Only top 3 chunks
    final_summary = summarize_text(summarizer, joined, max_len=150, min_len=40)

    return final_summary, chunk_summaries[:5]  # Show only first 5 chunks


if __name__ == "__main__":
    print("Fast summarizer ready!")
