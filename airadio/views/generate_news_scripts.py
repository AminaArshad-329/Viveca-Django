import json
import random
import requests
import logging
from django.conf import settings
from openai import OpenAI
from gnews import GNews

logger = logging.getLogger(__name__)


OPENAI_KEY = getattr(settings, "OPENAI_KEY")
OPEN_WEATHER_API_KEY = getattr(settings, "OPEN_WEATHER_API_KEY")
SERPER_API_KEY = getattr(settings, "SERPER_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)


def generate_voicetrack_from_prompts(system_prompt: str, prompt: str):

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0]


def get_openweather(location, units="metric"):
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&units={units}&appid={OPEN_WEATHER_API_KEY}"
    data = requests.get(api_url).json()

    weather_info = {
        "location": location,
        "temperature": data.get("main").get("temp"),
        "unit": units,
    }
    return json.dumps(weather_info)


def get_current_weather(location, unit="celsius"):
    data = (
        requests.get(
            f"https://api.weatherapi.com/v1/current.json?key=8206f9f86975490098a174007231907&q={location}"
        )
        .json()
        .get("current")
    )
    weather_info = {
        "location": location,
        "temperature": data.get("temp_c") if unit == "celsius" else data.get("temp_f"),
        "unit": unit,
    }
    return json.dumps(weather_info)


def get_news(topic: str, period="2d", maxResults=10):
    google_news = GNews(period=period, max_results=maxResults)
    try:
        news = google_news.get_news_by_topic(topic=topic)
        random.shuffle(news)
        news = news[0]

    except IndexError:
        news = {
            "title": "NFL fines former Commanders owner Dan Snyder $60M for workplace misconduct - The Athletic",
            "description": "NFL fines former Commanders owner Dan Snyder $60M for workplace misconduct  The AthleticCommanders' Dan Snyder fined $60M over findings in investigation  ESPNDaniel Snyder selling doesn't make things right. That's up to Josh Harris.  The Washington PostWashington Commanders sold to Josh Harris group  WUSA9NFL owners approve $6.05B sale of Commanders to Harris group - ESPN  ESPNView Full Coverage on Google News",
        }
    news_data = {"title": news.get("title"), "description": news.get("description")}

    return json.dumps(news_data)


def get_news_script(prompt: str):
    messages = [{"role": "user", "content": prompt}]

    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location of same day",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location", "unit"],
            },
        },
        {
            "name": "get_news",
            "description": "Get news about a topic user specifies",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["SPORTS", "WORLD", "ENTERTAINMENT"],
                    }
                },
            },
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    response_message = response["choices"][0]["message"]

    if response_message.get("function_call"):
        available_functions = {
            "get_current_weather": get_current_weather,
            "get_news": get_news,
        }

        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(**function_args)

        messages.append(response_message)  # extend conversation with assistant's reply
        messages.extend(
            [
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
                {
                    "role": "system",
                    "content": "You are a news reporter that creates a 5 second script from a title and a brief description of an article. The scripts you write dont have breaking news or stay tuned or good eventing or anything like that, they are just about the article itself. You also dont talk about how to follow up the article. You dont talk about your name.",
                },
            ]
        )

        if function_name == "get_current_weather":
            messages.append(
                {
                    "role": "user",
                    "content": "Create a 5 second script for a news reporter to read live about this weather situation",
                }
            )
        else:
            messages.append(
                {
                    "role": "user",
                    "content": "Create a 5 second script for a news reporter to read live about this news given the title and description. No hashtags",
                }
            )

        second_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
        )

        return second_response["choices"][0]["message"].content


def generate_bulletin(bulletin):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a news reporter that creates a news bulletin from a comma separated set of news. The scripts you write dont have breaking news or stay tuned or good evening or anything like that, they are just about the news. You also dont talk about how to follow up the articles. There is no intro and no outros",
            },
            {
                "role": "user",
                "content": "Create a script for a news reporter to read live about these news."
                + bulletin,
            },
        ],
    )

    return response.choices[0].message.content
