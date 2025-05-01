from google.auth import default
import vertexai
from vertexai.preview import rag
import os
from dotenv import load_dotenv
# import requests
# import tempfile

# Load environment variables from .env file
load_dotenv()

# --- Please fill in your configurations ---
# Retrieve the PROJECT_ID from the environmental variables.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )

def check_corpus_status(corpus_display_name):
    """Checks the status of a corpus by corpus display name."""
    try:
        # Find corpus by display name
        existing_corpora = rag.list_corpora()
        corpus = None
        for existing_corpus in existing_corpora:
            if existing_corpus.display_name == corpus_display_name:
                corpus = existing_corpus
                print(f"Found existing corpus with display name '{corpus_display_name}'")
                break
        files = rag.list_files(corpus_name=corpus.name) if corpus else None
        if files:
            print(f"Files in corpus '{corpus.display_name}':")
            for file in files:
                print(f" - File: {file.display_name} - {file.create_time} - {file.name}")
        else:
            print(f"No files found in corpus '{corpus.display_name}'")
        return corpus
    except Exception as e:
        print(f"Error retrieving corpus status: {e}")
        return None
    
def main():
    # Initialize Vertex AI
    credentials, project = default()
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

    # Check the status of the corpus
    corpus_display_name = os.getenv("CORPUS_DISPLAY_NAME")
    corpus_status = check_corpus_status(corpus_display_name)
    if corpus_status:
        print(f"Corpus '{corpus_display_name}' status: {corpus_status}")
    else:
        print(f"Corpus '{corpus_display_name}' not found or error occurred.")


if __name__ == "__main__":
    main()