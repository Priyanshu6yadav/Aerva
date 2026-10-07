import subprocess
import ollama
from datetime import datetime


# =========================================================
# BASIC AERVA RESPONSES
# =========================================================

def say_hello():
    return "Hello! How can I help you?"


def get_name():
    return "I am Aerva."


def get_creator():
    return "I was created by Priyanshu as an AI assistant."


def get_status():
    return "All systems are running normally."


def get_who():
    return "I am your personal AI assistant."


def get_version():
    return "I am running Aerva v0.6."


def get_help():
    return (
        "Available commands: hello, name, who are you, "
        "creator, status, version, help, exit."
    )


# =========================================================
# OPEN macOS APPLICATION
# =========================================================

def open_app(app_name):

    app_aliases = {
        "google_chrome": "Google Chrome",
        "chrome": "Google Chrome",
        "safari": "Safari",
        "calculator": "Calculator",
        "visual_studio_code": "Visual Studio Code",
        "vscode": "Visual Studio Code"
    }

    app_name = app_aliases.get(
        app_name.lower().strip(),
        app_name.strip()
    )

    result = subprocess.run(
        ["open", "-a", app_name],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return f"Opening {app_name}."

    error = result.stderr.strip()

    if error:
        return f"I couldn't open {app_name}: {error}"

    return f"I couldn't open {app_name}."


# =========================================================
# OPEN WEBSITE / URL
# =========================================================

def open_url(url):

    website_names = {
        "https://www.instagram.com": "Instagram",
        "https://www.youtube.com": "YouTube",
        "https://www.google.com": "Google",
        "https://mail.google.com": "Gmail",
        "https://github.com": "GitHub",
        "https://chatgpt.com": "ChatGPT"
    }

    result = subprocess.run(
        ["open", url],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:

        name = website_names.get(
            url.rstrip("/"),
            url
        )

        return f"Opening {name}."

    error = result.stderr.strip()

    if error:
        return f"I couldn't open {url}: {error}"

    return f"I couldn't open {url}."


# =========================================================
# GET CURRENT TIME
# =========================================================

def get_time():

    current_time = datetime.now().strftime("%I:%M %p")

    return f"The current time is {current_time}."


# =========================================================
# ASK LOCAL AI
# =========================================================

def ask_ai(prompt):

    response = ollama.chat(
        model="qwen3:1.7b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Aerva, a local AI assistant "
                    "running on macOS."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        think=False
    )

    return response["message"]["content"]


# =========================================================
# AI TOOL DECISION
# =========================================================

def get_tool_decision(command):

    response = ollama.chat(
        model="qwen3:1.7b",
        messages=[
            {
                "role": "system",
                "content": """
You are Aerva's tool-selection assistant.

Available tools:

open_app(app_name)
open_url(url)
get_time()


1. OPEN_APP

Use OPEN_APP when the user wants to launch
an installed macOS application.

Examples:

User: open Safari
OPEN_APP:Safari

User: open Google Chrome
OPEN_APP:Google Chrome

User: launch VS Code
OPEN_APP:Visual Studio Code

User: open Calculator
OPEN_APP:Calculator


2. OPEN_URL

Use OPEN_URL when the user wants to open
a website or web address.

Examples:

User: open YouTube
OPEN_URL:https://www.youtube.com

User: open Google
OPEN_URL:https://www.google.com

User: open Instagram
OPEN_URL:https://www.instagram.com

User: open youtube.com
OPEN_URL:https://youtube.com


3. GET_TIME

Use GET_TIME when the user asks for
the current time.

Example:

User: what time is it?
GET_TIME


4. NONE

If no available tool is required:

NONE


Return exactly ONE command.

Valid formats:

OPEN_APP:application_name
OPEN_URL:url
GET_TIME
NONE

Do not provide explanations.
"""
            },
            {
                "role": "user",
                "content": command
            }
        ],
        think=False
    )

    return response["message"]["content"].strip()


# =========================================================
# PARSE AI TOOL DECISION
# =========================================================

def parse_tool_decision(decision):

    decision = decision.strip()

    # OPEN APP
    if decision.startswith("OPEN_APP:"):

        app_name = decision.split(
            ":",
            1
        )[1].strip()

        return {
            "tool": "open_app",
            "app_name": app_name
        }

    # OPEN APP - accidental space format
    elif decision.startswith("OPEN_APP "):

        app_name = decision.split(
            " ",
            1
        )[1].strip()

        return {
            "tool": "open_app",
            "app_name": app_name
        }

    # OPEN URL
    elif decision.startswith("OPEN_URL:"):

        url = decision.split(
            ":",
            1
        )[1].strip()

        # Remove accidental quotes
        url = url.strip('"').strip("'")

        return {
            "tool": "open_url",
            "url": url
        }

    # OPEN URL - accidental space format
    elif decision.startswith("OPEN_URL "):

        url = decision.split(
            " ",
            1
        )[1].strip()

        # Remove accidental quotes
        url = url.strip('"').strip("'")

        return {
            "tool": "open_url",
            "url": url
        }

    # GET TIME
    elif decision.startswith("GET_TIME"):

        return {
            "tool": "get_time"
        }

    return {
        "tool": None
    }


# =========================================================
# EXECUTE TOOL
# =========================================================

def execute_tool(tool_decision):

    tool = tool_decision["tool"]

    if tool == "open_app":

        return open_app(
            tool_decision["app_name"]
        )

    elif tool == "open_url":

        return open_url(
            tool_decision["url"]
        )

    elif tool == "get_time":

        return get_time()

    return "I don't have permission to execute that tool."


# =========================================================
# AERVA AGENT
# =========================================================

def run_agent(command):

    command_lower = command.lower().strip()

    # =====================================================
    # KNOWN WEBSITES
    # =====================================================

    website_aliases = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "chatgpt": "https://chatgpt.com",
        "instagram": "https://www.instagram.com"
    }

    # =====================================================
    # OPEN COMMAND
    # =====================================================

    if command_lower.startswith("open "):

        target = command_lower[5:].strip()

        # -------------------------------------------------
        # Known website
        # -------------------------------------------------

        if target in website_aliases:

            url = website_aliases[target]

            print(
                "Tool decision:",
                f"OPEN_URL:{url}"
            )

            return open_url(url)

        # -------------------------------------------------
        # Direct URL
        # -------------------------------------------------

        if "." in target:

            if not target.startswith(
                ("http://", "https://")
            ):
                target = "https://" + target

            print(
                "Tool decision:",
                f"OPEN_URL:{target}"
            )

            return open_url(target)

    # =====================================================
    # LET QWEN DECIDE
    # =====================================================

    decision = get_tool_decision(command)

    print(
        "Tool decision:",
        decision
    )

    parsed = parse_tool_decision(
        decision
    )

    # =====================================================
    # EXECUTE TOOL
    # =====================================================

    if parsed["tool"] is not None:

        return execute_tool(
            parsed
        )

    # =====================================================
    # NORMAL AI QUESTION
    # =====================================================

    return ask_ai(command)


# =========================================================
# COMMAND ROUTER
# =========================================================

def route_command(command):

    command = command.strip()
    if not command:
        return "Please enter a command."
    command_lower = command.lower()
    if command_lower == "hello":
        return say_hello()

    elif command_lower == "name":
        return get_name()

    elif command_lower == "who are you":
        return get_who()

    elif command_lower == "creator":
        return get_creator()

    elif command_lower == "status":
        return get_status()

    elif command_lower == "version":
        return get_version()

    elif command_lower == "help":
        return get_help()

    elif command_lower == "exit":
        return None

    else:
        return run_agent(command)