from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

model = LiteLlm(model="groq/llama-3.1-8b-instant")


# --- Tools ---

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: status and result or error msg.
    """
    city_normalized = city.lower().replace(" ", "")
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25 degrees C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15 degrees C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18 degrees C."},
    }
    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


def say_hello(name: Optional[str] = None) -> str:
    """Provides a simple greeting. If a name is provided, it will be used.

    Args:
        name (str, optional): The name of the person to greet.

    Returns:
        str: A friendly greeting message.
    """
    if name:
        return f"Hello, {name}!"
    return "Hello there!"


def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    return "Goodbye! Have a great day."


# --- Sub-agents (specialists) ---

greeting_agent = Agent(
    model=model,
    name="greeting_agent",
    instruction=(
        "You are the Greeting Agent. Your ONLY task is to provide a friendly "
        "greeting using the 'say_hello' tool. Do nothing else."
    ),
    description="Handles simple greetings and hellos using the 'say_hello' tool.",
    tools=[say_hello],
)

farewell_agent = Agent(
    model=model,
    name="farewell_agent",
    instruction=(
        "You are the Farewell Agent. Your ONLY task is to provide a polite "
        "goodbye message using the 'say_goodbye' tool. Do not perform any other actions."
    ),
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
    tools=[say_goodbye],
)


# --- Root agent (orchestrator) ---

root_agent = Agent(
    name="weather_agent_team",
    model=model,
    description=(
        "The main coordinator agent. Handles weather requests and delegates "
        "greetings/farewells to specialists."
    ),
    instruction=(
        "You are the main Weather Agent coordinating a team. "
        "IMPORTANT: For weather questions, NEVER transfer or delegate — call your own "
        "'get_weather' tool directly and answer immediately. You already have this tool; "
        "you do not need any other agent's help for weather. "
        "Only use transfer_to_agent in these two exact cases: "
        "1. If the message is ONLY a greeting (e.g., 'Hi', 'Hello') with no other request, "
        "transfer to 'greeting_agent'. "
        "2. If the message is ONLY a farewell (e.g., 'Bye', 'Thanks, bye') with no other request, "
        "transfer to 'farewell_agent'. "
        "Never transfer to yourself. Never transfer for weather questions."
    ),

    tools=[get_weather],
    sub_agents=[greeting_agent, farewell_agent],
)