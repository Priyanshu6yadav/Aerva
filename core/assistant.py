import subprocess
import ollama
from datetime import datetime
import platform
# Import Aerva's web-search tool.
# This lets the AI agent call search_web() when web research is needed.
from core.web_search import search_web
# Import Aerva's web-research function.
# It searches the web and uses the local Qwen model
# to summarize the retrieved information.
from core.web_search import research_web

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
# _________________________________________________SYSTEM PART _______________________________#
# =========================================================
# SYSTEM INFORMATION
# =========================================================

def get_system_info():

    result = subprocess.run(
        [
            "system_profiler",
            "SPHardwareDataType"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return "I couldn't retrieve the system information."

    info = result.stdout

    model = "Unknown"
    chip = "Unknown"
    memory = "Unknown"
    cores = "Unknown"

    for line in info.splitlines():

        line = line.strip()

        if line.startswith("Model Name:"):
            model = line.split(":", 1)[1].strip()

        elif line.startswith("Chip:"):
            chip = line.split(":", 1)[1].strip()

        elif line.startswith("Memory:"):
            memory = line.split(":", 1)[1].strip()

        elif line.startswith("Total Number of Cores:"):
            cores = line.split(":", 1)[1].strip()

    return (
        f"You are using a {model} with an {chip} chip, "
        f"{memory} of memory, and {cores} CPU cores."
    )
# =========================================================
# CPU USAGE
# =========================================================

def get_cpu_usage():

    result = subprocess.run(
        [
            "top",
            "-l",
            "1",
            "-n",
            "0"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return "I couldn't retrieve CPU usage."

    for line in result.stdout.splitlines():

        if "CPU usage:" in line:

            cpu_info = line.strip()

            return f"Current {cpu_info}"

    return "I couldn't determine the current CPU usage."
# =========================================================
# MEMORY USAGE
# =========================================================

def get_memory_usage():
    result = subprocess.run(
        ["vm_stat"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return "I couldn't retrieve memory usage."
    page_size = 16384
    stats = {}
    for line in result.stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().rstrip(".")
        try:
            stats[key.strip()] = int(value)
        except ValueError:
            continue
    free_pages = stats.get(
        "Pages free",
        0
    )
    inactive_pages = stats.get(
        "Pages inactive",
        0
    )
    purgeable_pages = stats.get(
        "Pages purgeable",
        0
    )
    free_bytes = (
        free_pages +
        inactive_pages +
        purgeable_pages
    ) * page_size
    free_gb = free_bytes / (
        1024 ** 3
    )
    return (
        f"Approximately {free_gb:.2f} GB of memory "
        f"is currently available."
    )
# =========================================================
# DISK USAGE
# =========================================================

def get_disk_usage():

    result = subprocess.run(
        ["df", "-h", "/"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return "I couldn't retrieve disk usage."

    lines = result.stdout.strip().splitlines()

    if len(lines) < 2:
        return "I couldn't determine disk usage."

    parts = lines[1].split()

    if len(parts) < 5:
        return "I couldn't determine disk usage."

    total = parts[1]
    used = parts[2]
    available = parts[3]
    capacity = parts[4]

    return (
        f"Your Mac has {total} of total storage. "
        f"{used} is currently used and {available} is available. "
        f"Disk usage is {capacity}."
    )
# =========================================================
# NETWORK STATUS
# =========================================================

def get_network_status():

    result = subprocess.run(
        ["networksetup", "-getinfo", "Wi-Fi"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return "I couldn't retrieve network information."

    info = {}

    for line in result.stdout.splitlines():

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        info[key.strip()] = value.strip()

    ip_address = info.get(
        "IP address",
        "Unknown"
    )

    router = info.get(
        "Router",
        "Unknown"
    )

    if ip_address == "Unknown":

        return "Wi-Fi is not currently connected."

    return (
        f"Your Mac is connected to Wi-Fi. "
        f"Your local IP address is {ip_address} "
        f"and your router is {router}."
    )
def get_network_quality():

    result = subprocess.run(
        ["networkquality"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return "I couldn't check the network quality."

    output = result.stdout.strip()

    # Example:
    # Downlink: 6.550 Mbps, 60 RPM - Uplink: 50.337 Mbps, 60 RPM

    try:
        parts = output.split(" - ")

        downlink_part = parts[0]
        uplink_part = parts[1]

        download_speed = downlink_part.split(":")[1].split(",")[0].strip()
        download_rpm = downlink_part.split(",")[1].strip()

        upload_speed = uplink_part.split(":")[1].split(",")[0].strip()
        upload_rpm = uplink_part.split(",")[1].strip()

        return (
            f"Your download speed is {download_speed}, "
            f"and your upload speed is {upload_speed}. "
            f"Network responsiveness is {download_rpm}."
        )

    except (IndexError, ValueError):
        return "I checked the network, but I couldn't understand the results."
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
GET_SYSTEM_INFO
GET_CPU_USAGE
GET_MEMORY_USAGE
GET_DISK_USAGE
GET_NETWORK_STATUS
get_network_quality()
SEARCH_WEB: search_web(query)

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

4. GET_SYSTEM_INFO

Use GET_SYSTEM_INFO when the user asks about
their Mac hardware, processor, RAM, CPU cores,
or system hardware.

Examples:

User: What Mac am I using?
GET_SYSTEM_INFO

User: What processor do I have?
GET_SYSTEM_INFO

User: How much RAM does my Mac have?
GET_SYSTEM_INFO

User: Tell me about my Mac hardware.
GET_SYSTEM_INFO

5. GET_CPU_USAGE
Use GET_CPU_USAGE when the user asks about
current CPU usage or CPU load.
Examples:
User: How much CPU am I using?
GET_CPU_USAGE
User: Check CPU usage.
GET_CPU_USAGE
User: Is my CPU under heavy load?
GET_CPU_USAGE

6. GET_MEMORY_USAGE
Use GET_MEMORY_USAGE when the user asks about
RAM, memory usage, available memory, or whether
the Mac is running low on memory.
Examples:
User: How much RAM am I using?
GET_MEMORY_USAGE
User: How much memory is available?
GET_MEMORY_USAGE
User: Is my Mac running low on memory?
GET_MEMORY_USAGE

7. GET_DISK_USAGE
Use GET_DISK_USAGE when the user asks about
storage, disk space, available storage, or
whether the Mac is running out of space.
Examples:
User: How much storage do I have?
GET_DISK_USAGE
User: How much disk space is free?
GET_DISK_USAGE
User: Is my Mac storage full?
GET_DISK_USAGE

8. GET_NETWORK_STATUS

Use GET_NETWORK_STATUS when the user asks about
Wi-Fi, network connection, local IP address,
router, or whether the Mac is connected.
Examples:
User: Am I connected to Wi-Fi?
GET_NETWORK_STATUS
User: What's my IP address?
GET_NETWORK_STATUS
User: What's my network status?
GET_NETWORK_STATUS
User: How fast is my internet?
Tool: GET_NETWORK_QUALITY

User: Check my network quality.
Tool: GET_NETWORK_QUALITY
# -----------------------------------------------------------------------
SEARCH_WEB: Search the internet for current or unknown information.
Examples:
User: What are the latest Python 3.14 features?
Tool: SEARCH_WEB: latest Python 3.14 features

User: Search the web for the latest AI news.
Tool: SEARCH_WEB: latest AI news

User: What is the current price of Bitcoin?
Tool: SEARCH_WEB: current Bitcoin price
#---------------------------------------------------------------------------
SEARCH_WEB: Search the internet for information that is current,
unknown, or specifically requested by the user.

Format:
SEARCH_WEB: <search query>

Examples:

User: What are the latest Python 3.14 features?
Tool: SEARCH_WEB: latest Python 3.14 features

User: Search the web for the latest AI news.
Tool: SEARCH_WEB: latest AI news

User: What is the current price of Bitcoin?
Tool: SEARCH_WEB: current Bitcoin price
# -------------------------------------------------------------------------
9. NONE
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
    # GET SYSTEM INFO
    elif decision.startswith("GET_SYSTEM_INFO"):
        return {
            "tool": "get_system_info"
        }
    # CPU INFO
    elif decision.startswith("GET_CPU_USAGE"):
        return {
            "tool": "get_cpu_usage"
        }
    # MEMORY INFORMATION 
    elif decision.startswith("GET_MEMORY_USAGE"):
        return {
            "tool": "get_memory_usage"
        }
    # DISK USAGE
    elif decision.startswith("GET_DISK_USAGE"):
        return {
             "tool": "get_disk_usage"
        }
    elif decision.startswith("GET_NETWORK_STATUS"):
        return {
            "tool": "get_network_status"
        }
    # NETWORK STATUS
    elif decision.startswith("GET_NETWORK_STATUS"):
        return {
            "tool": "get_network_status"
    }
    elif decision.startswith("GET_NETWORK_QUALITY"):
        return {"tool": "get_network_quality"}
    # Detect a web-search request from the AI's tool decision.
    elif decision.startswith("SEARCH_WEB:"):
        query = decision.split(":", 1)[1].strip()
        return {
            "tool": "search_web",
            "query": query
        }
    # ---------------------------------------------------------
# SEARCH_WEB
#
# Extract the search query selected by Qwen.
# Example:
# SEARCH_WEB: latest Python 3.14 features
# ---------------------------------------------------------

    elif decision.startswith("SEARCH_WEB:"):
        query = decision.split(":", 1)[1].strip()
        return {
            "tool": "search_web",
            "query": query
        }
    return {
        "tool": None
    }


# =========================================================
# EXECUTE TOOL
# =========================================================

def execute_tool(tool_decision):

    tool = tool_decision.get("tool")

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

    elif tool == "get_system_info":
        return get_system_info()

    elif tool == "get_cpu_usage":
        return get_cpu_usage()
    elif tool == "get_memory_usage":
        return get_memory_usage()
    elif tool == "get_disk_usage":
        return get_disk_usage()
    elif tool == "get_network_status":
        return get_network_status()
    elif tool == "get_network_status":
        return get_network_status()
    elif tool == "get_network_quality":
        return get_network_quality()
    # Run the full web-research pipeline:
    # search -> retrieve results -> Qwen summarizes -> answer
    elif tool == "search_web":
        return research_web(tool_decision["query"])
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