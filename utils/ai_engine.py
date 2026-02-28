import ollama


def ask_llama(prompt: str, system: str = "") -> str:
    """Send a prompt to local LLaMA 3 and get a response."""
    messages = []

    if system:
        messages.append({"role": "system", "content": system})

    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(
        model="llama3",
        messages=messages
    )

    return response["message"]["content"]


def summarize_paper(sections: dict) -> str:
    """Generate a clean summary of the research paper."""
    text = sections.get("abstract", "") or sections.get("full_text", "")[:3000]

    system = """You are an expert academic research assistant. 
    Summarize research papers in a clear, structured way for students.
    Be concise but comprehensive."""

    prompt = f"""Summarize this research paper in exactly this format:

**Title/Topic:** (one line)
**Core Problem:** (what problem does it solve, 2-3 sentences)
**Proposed Solution:** (what did they build/propose, 2-3 sentences)  
**Key Results:** (what did they achieve, 2-3 sentences)
**Limitations:** (what could they not solve, 1-2 sentences)

Paper content:
{text}"""

    return ask_llama(prompt, system)


def detect_knowledge_gaps(sections: dict) -> str:
    """Detect research gaps and unsolved problems in the paper."""
    text = sections.get("conclusion", "") or sections.get("full_text", "")[:3000]

    system = """You are an expert research analyst helping PhD and M.Tech students 
    find research opportunities. Be specific and actionable."""

    prompt = f"""Analyze this research paper and identify:

**Unsolved Problems:** (what problems did the authors admit they couldn't fully solve?)
**Research Gaps:** (what areas are missing or underexplored?)
**Future Work Opportunities:** (list 3-5 specific things a student could research next)
**Potential Improvements:** (how could this work be extended or improved?)

Paper content:
{text}"""

    return ask_llama(prompt, system)


def extract_key_contributions(sections: dict) -> str:
    """Extract the main contributions of the paper."""
    text = sections.get("abstract", "") + "\n" + sections.get("introduction", "")
    text = text[:3000] if text.strip() else sections.get("full_text", "")[:3000]

    system = """You are an expert academic assistant helping students 
    understand research papers quickly."""

    prompt = f"""Extract the key contributions from this paper:

**Main Contributions:** (bullet list of 3-5 key contributions)
**Novelty:** (what is genuinely new about this work?)
**Technical Approach:** (what methods/techniques did they use?)
**Domain:** (what field is this paper from?)
**Keywords:** (5-7 relevant keywords)

Paper content:
{text}"""

    return ask_llama(prompt, system)


def answer_question(question: str, sections: dict) -> str:
    """Answer a specific question about the paper."""
    # Use relevant sections based on question keywords
    context = sections.get("full_text", "")[:4000]

    system = """You are a helpful research assistant. Answer questions 
    about research papers accurately based on the provided content.
    If the answer is not in the paper, say so clearly."""

    prompt = f"""Based on this research paper, answer the following question:

Question: {question}

Paper content:
{context}

Give a clear, direct answer. If the paper doesn't contain this information, say "This information is not available in the paper." """

    return ask_llama(prompt, system)


def generate_research_brief(metadata: dict, sections: dict) -> dict:
    """Generate a complete research brief for a paper."""
    print("Generating summary...")
    summary = summarize_paper(sections)

    print("Detecting knowledge gaps...")
    gaps = detect_knowledge_gaps(sections)

    print("Extracting contributions...")
    contributions = extract_key_contributions(sections)

    return {
        "title": metadata.get("title", "Unknown"),
        "author": metadata.get("author", "Unknown"),
        "summary": summary,
        "knowledge_gaps": gaps,
        "contributions": contributions
    }


# Test it directly
if __name__ == "__main__":
    print("Testing AI Engine...")
    print("Connecting to Ollama LLaMA 3...\n")

    test_sections = {
        "abstract": """This paper presents a novel deep learning approach for 
        underwater image enhancement using fusion techniques. We propose a method 
        that combines multiple image inputs to improve visibility and color accuracy 
        in underwater footage. Results show 40% improvement in image quality metrics 
        compared to existing methods. However, real-time processing on mobile devices 
        remains a challenge for future work.""",
        "full_text": ""
    }

    print("Testing summarization...")
    result = summarize_paper(test_sections)
    print(result)
    print("\n✅ AI Engine working!")