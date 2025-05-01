# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.auth import default
import vertexai
from vertexai.preview import rag
import os
from dotenv import load_dotenv, set_key
import requests
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
FILE_URL = os.getenv("FILE_URL", None)
FILE_NAME = os.getenv("FILE_NAME", None)

ENV_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".env")
)


# --- Start of the script ---
def initialize_vertex_ai():
    credentials, project = default()
    print(f"Authenticated with project: {project}")
    # credentials = _oauth2client.oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name(
    #     os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    # )
    vertexai.init(project=PROJECT_ID, location=LOCATION
                  , credentials=credentials
                  )


def create_or_get_corpus():
    """Creates a new corpus or retrieves an existing one."""
    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"
    )
    existing_corpora = rag.list_corpora()
    corpus = None
    for existing_corpus in existing_corpora:
        if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
            corpus = existing_corpus
            print(f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'")
            break
    if corpus is None:
        corpus = rag.create_corpus(
            display_name=CORPUS_DISPLAY_NAME,
            description=CORPUS_DESCRIPTION,
            embedding_model_config=embedding_model_config,
        )
        print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
    return corpus


def download_pdf_from_url(url, output_path):
    """Downloads a PDF file from the specified URL."""
    print(f"Downloading PDF from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"PDF downloaded successfully to {output_path}")
    return output_path


def upload_pdf_to_corpus(corpus_name, file_path, display_name, description):
    """Uploads a PDF file to the specified corpus."""
    print(f"Uploading {display_name} to corpus...")
    try:
        # Verify file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Verify file is readable
        with open(file_path, 'rb') as f:
            pass
        
        rag_file = rag.upload_file(
            corpus_name=corpus_name,
            path=file_path,
            display_name=display_name,
            description=description,
        )
        print(f"Successfully uploaded {display_name} to corpus")
        return rag_file
    except Exception as e:
        print(f"Error uploading file {display_name}: {e}")
        return None


def update_env_file(corpus_name, env_file_path):
    """Updates the .env file with the corpus name."""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as e:
        print(f"Error updating .env file: {e}")


def list_corpus_files(corpus_name):
    """Lists files in the specified corpus."""
    files = list(rag.list_files(corpus_name=corpus_name))
    print(f"Total files in corpus: {len(files)}")
    for file in files:
        print(f"File: {file.display_name} - {file.name}")
    return files

def delete_corpus_file(corpus_name, file_name):
    """Deletes a file from the specified corpus."""
    try:
        rag.delete_file(corpus_name=corpus_name, name=file_name)
        print(f"Deleted file {file_name} from corpus {corpus_name}")
        # Try reset indexing after deletion
        # rag.reset_index(corpus_name=corpus_name)
    except Exception as e:
        print(f"Error deleting file {file_name}: {e}")


def main():
    initialize_vertex_ai()
    corpus = create_or_get_corpus()

    if corpus:
        # delete corpus if exists

        files = list_corpus_files(corpus.name)
        if files:
            for file in files:
                if file.display_name == FILE_NAME:
                    print(f"File {file.display_name} already exists in corpus. Deleting...")
                    delete_corpus_file(corpus.name, file.name)
                    # files.remove(file)
        # rag.delete_corpus(corpus.name)
        # corpus = create_or_get_corpus()
        # print(f"Deleted corpus {corpus.name}")

    # Update the .env file with the corpus name
    update_env_file(corpus.name, ENV_FILE_PATH)

    # Create a temporary directory to store the downloaded PDF
    # with tempfile.TemporaryDirectory() as temp_dir:
    #   pdf_path = os.path.join(temp_dir, FILENAME)

    # Download the PDF from the URL
    # download_pdf_from_url(FILE_URL, pdf_path)

    # Upload the PDF to the corpus
    upload_pdf_to_corpus(
        corpus_name=corpus.name,
        file_path=FILE_URL,
        display_name=FILE_NAME,
        description="Hugo's password hints document",
    )

    # List all files in the corpus
    list_corpus_files(corpus_name=corpus.name)


if __name__ == "__main__":
    main()
