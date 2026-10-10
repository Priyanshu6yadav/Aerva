# ---------------------------------------------------------
# AERVA WEB PAGE READER
# Version: v0.8
#
# Purpose:
# Download a webpage and extract readable text from it.
#
# This is separate from web_search.py because searching and
# reading a webpage are two different agent capabilities.
# ---------------------------------------------------------

import requests
from bs4 import BeautifulSoup


def read_webpage(url, max_characters=12000):
    """
    Download a webpage and extract its readable text.

    Args:
        url (str):
            URL of the webpage to read.

        max_characters (int):
            Maximum amount of page text returned.

    Returns:
        str:
            Extracted webpage text.
    """

    try:

        # Identify Aerva as the client making the request.
        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X) "
                "AppleWebKit/537.36 "
                "Chrome/131 Safari/537.36"
            )
        }

        # Download the webpage.
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        # Raise an error for HTTP failures such as 404/500.
        response.raise_for_status()

        # Parse the HTML document.
        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove elements that normally don't contain
        # useful article information.
        for element in soup(
            ["script", "style", "noscript"]
        ):
            element.decompose()

        # Extract visible text.
        text = soup.get_text(
            separator=" ",
            strip=True
        )

        # Limit the amount of text sent to the LLM.
        return text[:max_characters]

    except Exception as error:

        print(
            f"❌ Web page reading error: {error}"
        )

        return ""


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    url = input("URL: ").strip()

    content = read_webpage(url)

    if content:

        print("\n✅ Page content:\n")
        print(content)

    else:

        print("\n❌ Could not read webpage.")