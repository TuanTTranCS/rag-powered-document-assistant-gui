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
CORPUS_DISPLAY_NAME = os.getenv("CORPUS_DISPLAY_NAME", "Hugo_private_docs")
CORPUS_DESCRIPTION = "Corpus containing Hugo's private documents."
FILE_URL = "C:\\Users\\tuant\\OneDrive\\Documents\\accounts-pwds-banks\\pwd.docx"
FILENAME = "pwd.docx"
ENV_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".env")
)


# --- Start of the script ---
def initialize_vertex_ai():
    credentials, _ = default()
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

def delete_all_corpora():
    """Deletes all corpora in the project."""
    existing_corpora = rag.list_corpora()
    print(existing_corpora)
    for existing_corpus in existing_corpora:
        print(f"Deleting corpus with display name '{existing_corpus.display_name}'")
        rag.delete_corpus(existing_corpus.name)
        print(f"Deleted corpus with display name '{existing_corpus.display_name}'")

    print("All corpora have been deleted.")

if __name__ == "__main__":
    initialize_vertex_ai()
    delete_all_corpora()