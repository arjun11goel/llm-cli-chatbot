"""Small API test required by PromptForge Week 1: send 'Hello' to Groq."""

import os

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

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
API_KEY = os.getenv("GROQ_API_KEY", "").strip()


def main() -> None:
    if not API_KEY or API_KEY == "your_groq_api_key_here":
        print("GROQ_API_KEY is missing. Add your key to the .env file first.")
        raise SystemExit(1)

    try:
        client = Groq(api_key=API_KEY)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.2,
            max_completion_tokens=100,
        )
        print(f"Model: {MODEL}")
        print("Prompt: Hello")
        print("Reply:")
        print(response.choices[0].message.content)
    except AuthenticationError:
        print("Authentication failed. Verify your Groq API key in .env.")
        raise SystemExit(1)
    except RateLimitError:
        print("Rate limit reached. Wait and run the test again.")
        raise SystemExit(1)
    except APITimeoutError:
        print("The request timed out. Try again.")
        raise SystemExit(1)
    except APIConnectionError:
        print("Could not connect to Groq. Check your internet connection.")
        raise SystemExit(1)
    except APIStatusError as error:
        print(f"Groq returned HTTP {error.status_code}. Check the model name and API status.")
        raise SystemExit(1)
    except APIError as error:
        print(f"Groq API error: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
