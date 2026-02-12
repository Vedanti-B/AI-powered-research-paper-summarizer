import torch
from transformers import pipeline

@torch.no_grad()
def load_model(model_name: str = "facebook/bart-large-cnn"):
    """Faster pipeline approach - loads once, ready to use"""
    device = 0 if torch.cuda.is_available() else -1
    summarizer = pipeline(
        "summarization",
        model=model_name,
        device=device,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    return summarizer

def summarize_text(summarizer, text: str, max_len: int = 150, min_len: int = 30) -> str:
    """Faster single pipeline call"""
    return summarizer(text, max_length=max_len, min_length=min_len,
                     do_sample=False)[0]['summary_text']
