# src/generator.py
# Uses Groq API with Llama 3.1 8B
# Prompt uses cautious language — avoids overconfident legal conclusions

# src/generator.py
import json
import re
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


def generate_analysis(retrieved: dict) -> dict:

    # Build context — label each chunk clearly with its article number
    context_parts = []

    if retrieved["fundamental_rights"]:
        context_parts.append("RETRIEVED CONSTITUTIONAL TEXT (use ONLY this text):")
        for i, item in enumerate(retrieved["fundamental_rights"], 1):
            art_num = item.get("article_number", "")
            art_title = item.get("article_title", "")
            header = f"[CHUNK {i} — Article {art_num}: {art_title}]" if art_num else f"[CHUNK {i}]"
            context_parts.append(f"{header}\n{item['text']}\n")

    if retrieved["state_duties"]:
        context_parts.append("ADDITIONAL CONSTITUTIONAL PROVISIONS:")
        for item in retrieved["state_duties"]:
            art_num = item.get("article_number", "")
            art_title = item.get("article_title", "")
            header = f"[Article {art_num}: {art_title}]" if art_num else "[Provision]"
            context_parts.append(f"{header}\n{item['text']}\n")

    if retrieved["remedies"]:
        context_parts.append("CONSTITUTIONAL REMEDIES AVAILABLE:")
        for item in retrieved["remedies"]:
            art_num = item.get("article_number", "")
            context_parts.append(f"[Article {art_num}]\n{item['text']}\n")

    context = "\n".join(context_parts)

    prompt = f"""You are a careful constitutional law assistant for Indian citizens.

CITIZEN'S SITUATION: "{retrieved['situation']}"

RETRIEVED CONSTITUTIONAL TEXT:
{context}

===== STRICT RULES — READ CAREFULLY =====

RULE 1 — USE ONLY THE TEXT ABOVE:
Read each chunk's actual text carefully before mentioning any article.
DO NOT use your own memory of what an article says.
The chunk header tells you the article number and title — trust that.
If the chunk text does not clearly apply to this situation, do not include that article.

RULE 2 — DESCRIBE ARTICLES ACCURATELY:
The "title" field must match what the chunk header says.
The "explanation" must be based on what the chunk TEXT actually says — not what you think the article says from memory.

RULE 3 — CAUTIOUS LANGUAGE:
Never say a right was "violated." Use: "may apply", "could be relevant", "if the facts show."
Acknowledge missing facts — e.g. "This depends on whether a rental agreement existed."

RULE 4 — CORRECT WRIT SELECTION:
Habeas Corpus — only for unlawful detention or imprisonment of a person.
Mandamus — to compel a government authority to perform its legal duty.
Certiorari — to quash an illegal order passed by a lower court or tribunal.
Prohibition — to stop a lower court from exceeding its jurisdiction.
Quo Warranto — to challenge someone's right to hold public office.
For property/eviction disputes involving a private landlord, the remedy is usually civil court or rent tribunal — NOT a constitutional writ. If no writ clearly applies, say so honestly.

RULE 5 — ONLY INCLUDE RELEVANT ARTICLES:
If an article is about profession or trade (19(1)(g)), do not apply it to a housing eviction.
If an article is about property rights (300A), describe it as property rights — not life and liberty.
Article 21 is the right to life and personal liberty.
Article 300A is the right not to be deprived of property without authority of law.
These are different — never mix them up.

RULE 6 — HONEST LIMITATIONS:
If the situation involves a private landlord and no state action, say clearly:
"Constitutional rights under Part III generally apply against the State, not private individuals.
Your remedies may lie primarily under tenancy law or civil law rather than constitutional law."

===== OUTPUT FORMAT =====

Respond in this EXACT JSON format:

{{
  "rights_violated": [
    {{
      "article": "Exact article number from the chunk header e.g. Article 21",
      "title": "Exact title from the chunk header",
      "explanation": "One careful sentence based on the actual chunk text — using cautious language"
    }}
  ],
  "plain_explanation": "2-3 sentences. Use 'may', 'could', 'if'. Mention missing facts. If this is a private landlord dispute mention that constitutional remedies may be limited and tenancy law may be more relevant.",
  "what_to_demand": [
    "Practical first step to understand the situation better",
    "Who to contact for free help",
    "What documents or evidence to gather"
  ],
  "legal_remedy": "Honest one sentence — mention civil/tenancy law remedies if appropriate. Only mention constitutional writs if clearly applicable.",
  "writ_type": "The most applicable writ OR write 'Civil/Tenancy Court' if no writ clearly applies"
}}

Return ONLY valid JSON. No text before or after."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise Indian constitutional law assistant. "
                        "You ONLY describe articles based on the text provided to you — never from memory. "
                        "You use cautious language always. "
                        "You never mix up Article 21 and Article 300A. "
                        "You never apply Article 19(1)(g) to housing disputes. "
                        "You always respond with valid JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0,   # zero temperature = most deterministic, least hallucination
            max_tokens=1200,
        )

        response_text = response.choices[0].message.content

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except json.JSONDecodeError:
                    result = _fallback_response(retrieved["situation"])
            else:
                result = _fallback_response(retrieved["situation"])

    except Exception as e:
        print(f"Groq API error: {e}")
        result = _fallback_response(retrieved["situation"])

    result["confidence"] = retrieved["confidence"]
    return result


def _fallback_response(situation: str) -> dict:
    return {
        "rights_violated": [
            {
                "article": "Article 32",
                "title": "Right to Constitutional Remedies",
                "explanation": (
                    "This article may be relevant if a fundamental right is found "
                    "to have been violated after a full review of all the facts."
                )
            }
        ],
        "plain_explanation": (
            "Based on what you have described, there may be legal protections available. "
            "However, for disputes with private individuals such as landlords, your remedies "
            "may lie primarily under tenancy law or civil law rather than constitutional law. "
            "More facts are needed before any conclusion can be drawn."
        ),
        "what_to_demand": [
            "Gather all documents — rental agreement, payment receipts, any written notices",
            "Contact your nearest District Legal Services Authority (DLSA) for free legal advice",
            "Approach a civil court or rent tribunal if the eviction was unlawful"
        ],
        "legal_remedy": (
            "Your primary remedy may be through a civil court or rent tribunal under "
            "applicable tenancy laws. A constitutional writ may apply only if a "
            "government body was involved in the eviction."
        ),
        "writ_type": "Civil/Tenancy Court",
        "confidence": 40.0
    }