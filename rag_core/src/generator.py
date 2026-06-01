import logging
import re
from groq import Groq
from rag_core.src import config

logger = logging.getLogger(__name__)

def parse_sentences(text: str) -> list:
    """
    Helper to split text into distinct sentences.
    """
    return [s.strip() for s in re.split(r'(?<=[.?!])\s+', text) if s.strip()]

def run_mock_generator(query: str, chunks: list) -> str:
    """
    A robust rule-based mock LLM generator.
    Simulates extractive reading comprehension from the retrieved ChromaDB chunks,
    returning a max of 3 sentences, and adhering to strict refusal rules.
    """
    logger.info("[Mock Mode] Simulating Groq Llama 3 generation...")
    
    if not chunks:
        return "I do not have enough information to answer this query."

    # Combine all chunk texts
    combined_context = " ".join([chunk["text"] for chunk in chunks])
    query_lower = query.lower()
    
    # Extract sentences
    sentences = parse_sentences(combined_context)
    matched_sentences = []

    # 1. Rules for Exit Load
    if "exit load" in query_lower or "redeem" in query_lower or "charge" in query_lower:
        for s in sentences:
            s_lower = s.lower()
            if "exit load" in s_lower or "redemption" in s_lower or "switch-out" in s_lower:
                if s not in matched_sentences:
                    matched_sentences.append(s)

    # 2. Rules for Minimum SIP / Initial investment
    elif "sip" in query_lower or "minimum" in query_lower or "invest" in query_lower or "purchase" in query_lower:
        for s in sentences:
            s_lower = s.lower()
            if "minimum sip" in s_lower or "minimum initial" in s_lower or "minimum subscription" in s_lower or "multiples of" in s_lower or "purchase" in s_lower:
                if s not in matched_sentences:
                    matched_sentences.append(s)

    # 3. Rules for Lock-in period
    elif "lock" in query_lower or "lock-in" in query_lower or "elss" in query_lower:
        for s in sentences:
            s_lower = s.lower()
            if "lock-in" in s_lower or "lock in" in s_lower or "3 years" in s_lower or "completion of" in s_lower:
                if s not in matched_sentences:
                    matched_sentences.append(s)

    # 4. Rules for Expense Ratio
    elif "expense" in query_lower or "ratio" in query_lower or "charge" in query_lower:
        for s in sentences:
            s_lower = s.lower()
            if "expense ratio" in s_lower or "direct plan" in s_lower or "regular plan" in s_lower:
                if s not in matched_sentences:
                    matched_sentences.append(s)

    # 5. Rules for Risk / Riskometer
    elif "risk" in query_lower or "riskometer" in query_lower or "suitable" in query_lower:
        for s in sentences:
            s_lower = s.lower()
            if "riskometer" in s_lower or "suitable" in s_lower or "risk of" in s_lower or "very high" in s_lower:
                if s not in matched_sentences:
                    matched_sentences.append(s)

    # 6. Rules for Benchmark
    elif "benchmark" in query_lower or "index" in query_lower:
        for s in sentences:
            s_lower = s.lower()
            if "benchmark" in s_lower or "index" in s_lower:
                if s not in matched_sentences:
                    matched_sentences.append(s)

    # 7. Rules for Statement or Capital Gains Download Guides
    elif "download" in query_lower or "statement" in query_lower or "report" in query_lower or "gains" in query_lower or "how to" in query_lower:
        for s in sentences:
            s_lower = s.lower()
            # Match step keywords like "Go to", "Log in", "Select", "Click", "Choose", "Download"
            if any(kw in s for kw in ["Go to", "Log in", "Select", "Click", "Choose", "Download", "SMS", "send", "Visit"]):
                if s not in matched_sentences:
                    matched_sentences.append(s)

    # 8. Refusal check if query doesn't match topics
    if not matched_sentences:
        return "I do not have enough information to answer this query."

    # Enforce strict 3-sentence limit
    final_sentences = matched_sentences[:3]
    return " ".join(final_sentences)


def generate_answer(query: str, chunks: list) -> str:
    """
    Generates a factual answer based on chunks.
    Uses Groq API if GROQ_API_KEY is configured, otherwise falls back to Mock Generator.
    """
    if not chunks:
        return "I do not have enough information to answer this query."

    # Check if API Key is set
    if not config.GROQ_API_KEY:
        logger.info("Groq API Key not found. Using Mock Generator Fallback.")
        return run_mock_generator(query, chunks)

    # Combine chunk contents to form context block
    context_text = ""
    for idx, chunk in enumerate(chunks):
        source_url = chunk.get('metadata', {}).get('source_url', '')
        context_text += f"Context Block {idx+1} (Source: {source_url}):\n{chunk['text']}\n\n"

    logger.info(f"Groq: Dispatching completion query with {len(chunks)} context blocks...")
    try:
        client = Groq(api_key=config.GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {"role": "user", "content": f"Context Blocks:\n{context_text}\nQuery: {query}"}
            ],
            temperature=config.TEMPERATURE,
            max_tokens=250
        )
        answer = chat_completion.choices[0].message.content.strip()
        logger.info("Groq: Completion successfully received.")
        return answer
    except Exception as e:
        logger.error(f"Groq API Call failed: {str(e)}. Falling back to Mock Generator.")
        return run_mock_generator(query, chunks)
