# src/ingest.py
# Article-level chunking for the Constitution of India PDF
# Fixes: no mid-article splits, no footnotes, no page headers

import re
import pdfplumber
from langchain.schema import Document

PDF_PATH = "data/constitution of india.pdf"

# These strings appear on every page as headers — strip them
NOISE_PATTERNS = [
    r"THE CONSTITUTION OF INDIA",
    r"\(Part [IVX]+\..*?\)",          # (Part III.—Fundamental Rights)
    r"Contents\s*\([ivxlcdm]+\)",     # Contents (ii)
    r"ARTICLES\s*",
    r"^\d+\s*$",                       # lone page numbers
    r"_{5,}",                          # long underlines
]

# Footnote pattern — lines starting with superscript numbers + "Ins./Subs./Rep."
FOOTNOTE_PATTERN = re.compile(
    r"^\s*\d+[\.\)]\s+(Ins\.|Subs\.|Rep\.|Omitted|Added|Renumbered).*",
    re.MULTILINE
)

# Article start pattern — matches "21." or "21A." or "243ZA." followed by text
ARTICLE_START = re.compile(
    r"(?m)^(\d+[A-Z\-]*[a-z]?\.)\s+([A-Z][^\n]{3,}?)\.?—"
)


def clean_text(text: str) -> str:
    """Remove page headers, footnotes, and noise from extracted text."""

    # Remove noise patterns
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, "", text)

    # Remove footnote lines (lines starting with digit + Ins./Subs. etc.)
    text = FOOTNOTE_PATTERN.sub("", text)

    # Remove lines that are only underscores or dashes (separator lines)
    text = re.sub(r"^[\-_\*]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Remove superscript numbers that appear inline (amendment markers like ¹ ² ³)
    text = re.sub(r"[¹²³⁴⁵⁶⁷⁸⁹¹⁰]+", "", text)
    text = re.sub(r"\[\s*\d+\s*\]", "", text)  # [1] [2] style markers

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def extract_full_text(pdf_path: str) -> str:
    """Extract all text from PDF, page by page, into one string."""
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"  PDF has {total} pages")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text += "\n" + text
    return full_text


def split_by_article(full_text: str) -> list[dict]:
    """
    Split the full Constitution text into individual Articles.

    Strategy:
    - Find every Article boundary using regex (e.g. "21. Protection of life")
    - Capture everything from that boundary to the next Article boundary
    - Keep article_number and article_title as metadata
    """
    # Find all article start positions
    matches = list(ARTICLE_START.finditer(full_text))

    articles = []

    for i, match in enumerate(matches):
        article_num = match.group(1).rstrip(".")   # "21" or "21A"
        article_title = match.group(2).strip()      # "Protection of life and personal liberty"

        start = match.start()
        # End is where the next article starts (or end of document)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)

        article_text = full_text[start:end]
        article_text = clean_text(article_text)

        # Skip very short fragments (likely false matches, under 80 chars)
        if len(article_text) < 80:
            continue

        # Determine which Part this Article belongs to
        part = get_part(article_num)

        articles.append({
            "article_number": article_num,
            "article_title": article_title,
            "text": article_text,
            "part": part,
            "char_length": len(article_text)
        })

    return articles


def get_part(article_num: str) -> str:
    """
    Map article number to the Constitutional Part it belongs to.
    This is used as metadata for filtered retrieval.
    """
    # Extract numeric part for comparison
    try:
        num = int(re.match(r"\d+", article_num).group())
    except:
        return "Unknown"

    if num <= 4:
        return "Part I — Union and Territory"
    elif num <= 11:
        return "Part II — Citizenship"
    elif num <= 35:
        return "Part III — Fundamental Rights"
    elif num <= 51:
        return "Part IV — Directive Principles"
    elif num == 51:
        return "Part IVA — Fundamental Duties"
    elif num <= 122:
        return "Part V — The Union"
    elif num <= 212:
        return "Part VI — The States"
    elif num <= 243:
        return "Part VIII-IX — UTs and Panchayats"
    elif num <= 263:
        return "Part XI — Union-State Relations"
    elif num <= 300:
        return "Part XII — Finance"
    elif num <= 307:
        return "Part XIII — Trade and Commerce"
    elif num <= 323:
        return "Part XIV — Services"
    elif num <= 329:
        return "Part XV — Elections"
    elif num <= 342:
        return "Part XVI — Special Provisions"
    elif num <= 351:
        return "Part XVII — Official Language"
    elif num <= 360:
        return "Part XVIII — Emergency"
    elif num <= 367:
        return "Part XIX — Miscellaneous"
    elif num <= 392:
        return "Part XX — Amendment"
    else:
        return "Part XXI — Temporary Provisions"


def load_constitution() -> list[Document]:
    """
    Main function called by build_kb.py.
    Returns list of LangChain Documents, one per Article.
    """
    print("Step 1: Extracting text from PDF...")
    full_text = extract_full_text(PDF_PATH)

    print("Step 2: Splitting into Articles...")
    articles = split_by_article(full_text)
    print(f"  Found {len(articles)} Articles")

    # Handle long Articles by splitting into sub-chunks
    # (Some Articles like Art 19, 32, 226 are very long)
    print("Step 3: Handling long Articles...")
    documents = []

    for article in articles:
        text = article["text"]

        # If Article text is short enough — keep as one chunk
        if len(text) <= 1200:
            documents.append(Document(
                page_content=text,
                metadata={
                    "article_number": article["article_number"],
                    "article_title": article["article_title"],
                    "part": article["part"],
                    "source": "Constitution of India",
                    "chunk_type": "full_article"
                }
            ))

        else:
            # Long Article — split by clause while keeping Article header
            header = f"Article {article['article_number']}. {article['article_title']}.\n"
            clauses = split_into_clauses(text)

            for j, clause in enumerate(clauses):
                chunk_text = header + clause if j > 0 else clause
                documents.append(Document(
                    page_content=chunk_text,
                    metadata={
                        "article_number": article["article_number"],
                        "article_title": article["article_title"],
                        "part": article["part"],
                        "source": "Constitution of India",
                        "chunk_type": f"article_clause_{j+1}"
                    }
                ))

    print(f"  Total chunks created: {len(documents)}")
    return documents


def split_into_clauses(text: str, max_chars: int = 1000) -> list[str]:
    """
    Split a long Article into clause-level chunks.
    Splits on clause markers like (1), (2), (a), (b) etc.
    Never cuts mid-sentence.
    """
    # Split on clause patterns like "(1)", "(2)", "(a)", "(b)"
    clause_pattern = re.compile(r"(?=\(\d+\)|\([a-z]\))")
    parts = clause_pattern.split(text)

    chunks = []
    current = ""

    for part in parts:
        if len(current) + len(part) < max_chars:
            current += part
        else:
            if current.strip():
                chunks.append(current.strip())
            current = part

    if current.strip():
        chunks.append(current.strip())

    return chunks if chunks else [text]