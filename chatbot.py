"""PromptForge Week 1: a command-line chatbot powered by the Groq API."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from colorama import Fore, Style, init
from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    Groq,
    RateLimitError,
)

load_dotenv()
init(autoreset=True)

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
LOG_DIRECTORY = Path("chat_logs")

PERSONAS = {
    "1": {
        "name": "Patient Coding Tutor",
        "prompt": (
            "You are a patient coding tutor. Explain concepts in simple language, "
            "use small steps and practical examples, and encourage the learner. "
            "Do not assume the user already knows advanced terminology."
        ),
    },
    "2": {
        "name": "Concise Study Assistant",
        "prompt": (
            "You are a concise study assistant. Answer directly, organize information "
            "with short bullets when useful, avoid unnecessary detail, and define "
            "technical terms briefly."
        ),
    },
    "3": {
        "name": "Creative Storyteller",
        "prompt": (
            "You are a creative storyteller. Explain ideas with vivid analogies, "
            "imaginative examples, and engaging language while keeping factual claims "
            "clear and useful."
        ),
    },
}


def utc_now() -> str:
    """Return a timezone-aware ISO 8601 timestamp."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def print_help() -> None:
    print(
        "\nCommands:\n"
        "  /help         Show this help message\n"
        "  /persona      Choose one of the three system prompts\n"
        "  /temperature  Set temperature from 0.0 to 2.0\n"
        "  /clear        Clear conversation history but keep the current persona\n"
        "  quit / exit   End the chat and save the conversation\n"
    )


def choose_persona(current_key: str) -> str:
    """Display available personas and return the selected key."""
    print("\nChoose a persona:")
    for key, persona in PERSONAS.items():
        marker = " (current)" if key == current_key else ""
        print(f"  {key}. {persona['name']}{marker}")

    choice = input("Enter 1, 2, or 3 (or press Enter to cancel): ").strip()
    if choice in PERSONAS:
        print(Fore.GREEN + f"Persona set to: {PERSONAS[choice]['name']}\n")
        return choice
    if choice == "":
        print("Persona unchanged.\n")
    else:
        print(Fore.YELLOW + "Invalid choice. Persona unchanged.\n")
    return current_key


def choose_temperature(current_temperature: float) -> float:
    """Ask for a valid temperature between 0 and 2."""
    raw_value = input(
        f"Enter temperature from 0.0 to 2.0 (current {current_temperature:.1f}): "
    ).strip()
    if not raw_value:
        print("Temperature unchanged.\n")
        return current_temperature

    try:
        value = float(raw_value)
    except ValueError:
        print(Fore.YELLOW + "Please enter a number, such as 0.2 or 1.0.\n")
        return current_temperature

    if not 0.0 <= value <= 2.0:
        print(Fore.YELLOW + "Temperature must be between 0.0 and 2.0.\n")
        return current_temperature

    print(Fore.GREEN + f"Temperature set to {value:.1f}.\n")
    return value


def save_session(
    messages: list[dict[str, str]],
    started_at: str,
    model: str,
    persona_key: str,
    starting_temperature: float,
    ending_temperature: float,
) -> Path | None:
    """Save the current chat to a timestamped JSON file."""
    # Save only if the session contains at least one user/assistant turn.
    if not any(message.get("role") == "user" for message in messages):
        print("No conversation turns to save.")
        return None

    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("session_%Y%m%d_%H%M%S.json")
    output_path = LOG_DIRECTORY / filename
    session_data = {
        "session_started_at": started_at,
        "session_ended_at": utc_now(),
        "model": model,
        "persona": PERSONAS[persona_key]["name"],
        "system_prompt": messages[0]["content"],
        "starting_temperature": starting_temperature,
        "ending_temperature": ending_temperature,
        "messages": messages,
    }

    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(session_data, json_file, indent=2, ensure_ascii=False)

    print(Fore.GREEN + f"Conversation saved to: {output_path}")
    return output_path


def get_assistant_reply(
    client: Groq,
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
) -> str:
    """Call Groq and return the assistant's text response."""
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=1024,
    )
    reply = completion.choices[0].message.content
    return reply.strip() if reply else "I did not receive a text response. Please try again."


def main() -> None:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_groq_api_key_here":
        print(
            Fore.RED
            + "GROQ_API_KEY is missing. Create a .env file and add your Groq API key."
        )
        return

    client = Groq(api_key=api_key)
    persona_key = "1"
    starting_temperature = 0.2
    temperature = starting_temperature
    started_at = utc_now()
    messages: list[dict[str, str]] = [
        {"role": "system", "content": PERSONAS[persona_key]["prompt"]}
    ]

    print(Fore.CYAN + "=" * 62)
    print(Fore.CYAN + " PromptForge Week 1 | Groq CLI Chatbot")
    print(Fore.CYAN + "=" * 62)
    print(f"Model: {MODEL}")
    print(f"Persona: {PERSONAS[persona_key]['name']}")
    print(f"Temperature: {temperature:.1f}")
    print("Type /help to view commands. Type 'quit' or 'exit' to finish.\n")

    while True:
        try:
            user_text = input(Fore.GREEN + "You: " + Style.RESET_ALL).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat...")
            break

        if not user_text:
            print(Fore.YELLOW + "Please enter a message; empty input was ignored.\n")
            continue

        if user_text.lower() in {"quit", "exit", "0"}:
            break
        if user_text.lower() == "/help":
            print_help()
            continue
        if user_text.lower() == "/persona":
            persona_key = choose_persona(persona_key)
            messages[0]["content"] = PERSONAS[persona_key]["prompt"]
            continue
        if user_text.lower() == "/temperature":
            temperature = choose_temperature(temperature)
            continue
        if user_text.lower() == "/clear":
            messages[:] = [messages[0]]
            print(Fore.GREEN + "Conversation history cleared. The current persona is unchanged.\n")
            continue

        messages.append({"role": "user", "content": user_text})
        try:
            reply = get_assistant_reply(client, messages, MODEL, temperature)
        except AuthenticationError:
            messages.pop()  # Don't keep a user turn that did not receive a reply.
            print(Fore.RED + "Authentication failed. Check that your Groq API key is correct.\n")
            continue
        except RateLimitError:
            messages.pop()
            print(Fore.RED + "Groq rate limit reached. Wait a little and try again.\n")
            continue
        except APITimeoutError:
            messages.pop()
            print(Fore.RED + "The request timed out. Please try again.\n")
            continue
        except APIConnectionError:
            messages.pop()
            print(Fore.RED + "Could not connect to Groq. Check your internet connection.\n")
            continue
        except APIStatusError as error:
            messages.pop()
            print(Fore.RED + f"Groq returned an API error (HTTP {error.status_code}).")
            print("Check the model name and Groq Console for service details.\n")
            continue
        except APIError as error:
            messages.pop()
            print(Fore.RED + f"Groq API error: {error}\n")
            continue
        except Exception as error:  # Defensive fallback for unexpected SDK errors.
            messages.pop()
            print(Fore.RED + f"Unexpected error: {error}\n")
            continue

        messages.append({"role": "assistant", "content": reply})
        print(Fore.CYAN + f"Bot: {reply}\n")

    save_session(
        messages=messages,
        started_at=started_at,
        model=MODEL,
        persona_key=persona_key,
        starting_temperature=starting_temperature,
        ending_temperature=temperature,
    )
    print(Fore.CYAN + "Goodbye! Thanks for trying PromptForge Week 1.\n")


if __name__ == "__main__":
    main()
