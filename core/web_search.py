# ---------------------------------------------------------
# AERVA WEB SEARCH TOOL
# Version: v0.8
#
# Purpose:
# Search the internet and return useful search results.
# ---------------------------------------------------------

from ddgs import DDGS
import ollama
from web_reader import read_webpage


def search_web(query, max_results=5):
    """
    Search the web using DuckDuckGo.

    Args:
        query (str):
            The user's search query.

        max_results (int):
            Maximum number of search results.

    Returns:
        list:
            Search-result dictionaries.
    """

    # Prevent empty queries from being sent to the search engine.
    if not query or not query.strip():
        return []

    try:

        # Create the DuckDuckGo search client.
        with DDGS() as ddgs:

            # Perform the web search.
            results = ddgs.text(
                query=query,
                max_results=max_results
            )

            # Convert the returned results into a normal list.
            return list(results)

    except Exception as error:

        # Print the error so we can diagnose search failures.
        print(f"❌ Web search error: {error}")

        return []


def research_web(query, max_results=5):
    """
    Perform a deeper web-research workflow.

    Workflow:
        Search web
        → Select search results
        → Read webpages
        → Give page content to Qwen
        → Generate final answer
    """

    # -----------------------------------------------------
    # STEP 1: Search the web
    # -----------------------------------------------------

    results = search_web(
        query,
        max_results=max_results
    )

    if not results:

        return (
            "I couldn't find any web results "
            "for that question."
        )

    # -----------------------------------------------------
    # STEP 2: Read the most useful webpages
    #
    # We don't want to download too many pages because
    # that would waste time and consume unnecessary context.
    # -----------------------------------------------------

    sources = []

    for index, result in enumerate(results[:3], start=1):

        title = result.get(
            "title",
            "Unknown title"
        )

        url = result.get(
            "href",
            ""
        )

        # Skip results without a valid URL.
        if not url:
            continue

        print(
            f"🌐 Reading source {index}: {title}"
        )

        page_text = read_webpage(
            url,
            max_characters=8000
        )

        # Only keep pages that were successfully read.
        if page_text:

            sources.append({
                "title": title,
                "url": url,
                "content": page_text
            })

    # -----------------------------------------------------
    # STEP 3: Make sure we actually obtained page content.
    # -----------------------------------------------------

    if not sources:

        return (
            "I found search results, but I "
            "couldn't read the webpages."
        )

    # -----------------------------------------------------
    # STEP 4: Build research context for Qwen
    # -----------------------------------------------------

    context_parts = []

    for index, source in enumerate(
        sources,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {index}

Title:
{source["title"]}

URL:
{source["url"]}

Content:
{source["content"]}
"""
        )

    context = "\n".join(context_parts)

    # -----------------------------------------------------
    # STEP 5: Ask Qwen to analyze the actual webpages.
    # -----------------------------------------------------

    prompt = f"""
You are Aerva, a local AI research assistant.

Answer the user's question using the webpage
content provided below.

USER QUESTION:
{query}

WEB RESEARCH:
{context}

RULES:

1. Use only information supported by the sources.
2. Do not invent facts.
3. Combine information from multiple sources when useful.
4. If sources disagree, mention the disagreement.
5. Give a concise but useful answer.
6. Mention the source names when appropriate.
7. If the available information is insufficient,
   clearly say so.
"""

    try:

        # Generate the final research answer locally.
        response = ollama.chat(
            model="qwen3:1.7b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Aerva, a local AI "
                        "research assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            think=False
        )

        # Extract Qwen's final research answer.
        answer = response["message"]["content"].strip()

        # Build a source list from the webpages that were
        # actually read and provided to Qwen.
        source_text = "\n\nSources:\n"

        for index, source in enumerate(sources, start=1):
            source_text += (
                f"{index}. {source['title']}\n"
                f"   {source['url']}\n"
            )

        # Return the answer together with the sources used.
        return answer + source_text

    except Exception as error:

        print(
            f"❌ Research generation error: {error}"
        )

        return (
            "I collected web information, "
            "but I couldn't generate the final answer."
        )

# ---------------------------------------------------------
# TESTING
#
# This section runs only when web_search.py is executed
# directly. It does not run when imported by assistant.py.
# ---------------------------------------------------------

if __name__ == "__main__":

    print("🌐 Aerva Web Research Test")
    print("--------------------------")

    query = input("Research: ").strip()

    answer = research_web(query)

    print("\n🤖 Aerva:")
    print(answer)