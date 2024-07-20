import json
import os

import azure.cognitiveservices.speech as speechsdk
import openai
import requests
from gnews import GNews


def getTopNews(period="1d", maxResults=5):
    openai.api_key = os.getenv("OPENAI_KEY")

    google_news = GNews(period=period, max_results=maxResults)
    return google_news.get_top_news()


def alphaGenerateScript(title, description):
    openai.api_key = os.getenv("OPENAI_KEY")

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system",
             "content": "You are a news reporter that creates a 5 second script from a title and a brief description of an article. The scripts you write dont have breaking news or stay tuned or good eventing or anything like that, they are just about the article itself. You also dont talk about how to follow up the artcile. No stay tuned words should be added"},
            {"role": "user",
             "content": "Crate a script for a newsreporter to read live about this article: Title: " + title + "\nDescription: " + description}
        ]
    )

    # Retrieve the generated response
    message = response.choices[0].message.content
    return message


def speak(text, filename):
    key = os.getenv("AZURE_COGNITIVE_KEY")
    region = "westus"

    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)

    # The language of the voice that speaks.
    # speech_config.speech_synthesis_voice_name='en-GB, ThomasNeural'
    speech_config.speech_synthesis_voice_name = 'en-GB-LibbyNeural'
    # speech_config.speech_synthesis_voice_name='en-US-SaraNeural'

    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm)

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Success")


def speak_elevenlabs(text, filename, voice='Patrick'):
    voices = {'Patrick': '6ojqEwe8C35npMRgRZxr', 'Paul': 'EXFJSSZT3nA081bVg99i', 'Peter': 'MGPAlYFBTf6viQcpoCVf',
              'Philip': 'OJjYoSIpSUXCRMMxj5Je', 'Pippa': 'VqhODWFVNPDD7zn9N0p0', 'Howard': 'eiFEEKWFowmp1lZBzF5v',
              'Polly': 'pTQ1CLytjIBKIIszzqV9', 'Piers': 'slOtqOiygfkR71FQ8H9s', 'Pamela': 'v5LtDujiFgAmwVYuEHrF'}

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voices[voice]}?optimize_streaming_latency=0"

    payload = json.dumps({
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0,
            "style": 0.5,
            "use_speaker_boost": True
        }
    })

    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': os.environ.get('ELEVENLABS_API_KEY'),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
