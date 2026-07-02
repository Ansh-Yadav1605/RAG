"""
Prompt Builder Module — Mutual Fund FAQ Assistant

Constructs system prompts combining strict behavioural rules and retrieved context.
"""

def build_prompt(query: str, retrieved_chunks: list[dict]) -> tuple[str, str]:
    """
    Returns (system_prompt, user_prompt)
    """
    
    # 1. Format context
    context_str = ""
    for i, chunk in enumerate(retrieved_chunks):
        meta = chunk['metadata']
        context_str += f"\n--- Source {i+1} ---\n"
        context_str += f"Scheme: {meta.get('scheme_name')}\n"
        context_str += f"URL: {meta.get('source_url')}\n"
        context_str += f"Content: {chunk['text']}\n"
        
    # 2. Build system prompt with STRICT rules
    system_prompt = f"""You are a Facts-Only FAQ Assistant for Mutual Funds.
You help retail investors by answering objective questions based STRICTLY on the provided context.

YOUR RULES:
1. NO INVESTMENT ADVICE. You cannot recommend, compare performance for advice, or tell the user what they "should" do.
2. FACTS ONLY. Answer only using the context provided below.
3. CONCISE. Your answer MUST be 3 sentences or fewer.
4. CITE SOURCE. If you answer, you must end with a single citation link from the context metadata.
5. NO HALLUCINATION. If the context does not contain the answer, say exactly: "I'm sorry, but I don't have that information in my verified sources."

CONTEXT:
{context_str}
"""

    return system_prompt, query
