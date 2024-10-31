import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from google.cloud import translate_v2 as translate

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize translation client
translate_client = translate.Client()

prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video, providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

# Function to extract transcript details
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1].split("&")[0]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except NoTranscriptFound:
        st.error("No transcripts found for the video.")
        return None
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
        return None
    except VideoUnavailable:
        st.error("The requested video is unavailable.")
        return None
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None

# Function to translate text to English
def translate_to_english(text):
    translation = translate_client.translate(text, target_language='en')
    return translation['translatedText']

# Function to generate summary based on prompt
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit app
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        video_id = youtube_link.split("v=")[1].split("&")[0]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.error("Invalid YouTube link. Please make sure it is formatted correctly.")

if st.button("Get Detailed Notes"):
    if youtube_link:
        # Step 1: Extract transcript
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            # Step 2: Translate transcript to English
            translated_text = translate_to_english(transcript_text)

            # Step 3: Generate summary
            summary = generate_gemini_content(translated_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.error("Could not generate summary. Please check the transcript.")
    else:
        st.error("Please enter a valid YouTube link.")
