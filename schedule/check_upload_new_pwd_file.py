import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from rag.shared_libraries.prepare_corpus_and_data import (
    initialize_vertex_ai,
    create_or_get_corpus,
    list_corpus_files,
    delete_corpus_file,
    upload_pdf_to_corpus
)

# Load environment variables
load_dotenv(override=True)

# Configure logging to print to both file and console
log_file = './schedule/upload_history.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def get_last_updated_time(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get("last_updated")
    return None

def write_last_updated_time(file_path, last_updated):
    if isinstance(last_updated, datetime):
        last_updated = last_updated.isoformat()
    with open(file_path, 'w') as f:
        json.dump({"last_updated": last_updated}, f, indent=4)

def get_file_last_modified_time(file_path):
    return datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()

def main():
    logging.info("\n" + "="*50 + "\nExecution started at: " + datetime.now().isoformat() + "\n" + "="*50)

    initialize_vertex_ai()

    last_updated_file = './schedule/last_updated.json'
    file_url = os.getenv("FILE_URL")
    file_name = os.getenv("FILE_NAME")

    if not file_url or not file_name:
        logging.error("FILE_URL or FILE_NAME is not set in the environment variables.")
        return

    last_updated = get_last_updated_time(last_updated_file)
    if last_updated:
        logging.info(f"Last updated time from file: {last_updated}")
    else:
        logging.info("'last_updated.json' not found or does not have a valid value. Checking corpus for existing file.")

    if not last_updated:
        corpus = create_or_get_corpus()
        files = list_corpus_files(corpus.name)

        for file in files:
            if file.display_name == file_name:
                last_updated = file.update_time
                logging.info(f"Found existing file in corpus. Last updated time: {last_updated}")
                write_last_updated_time(last_updated_file, last_updated)
                break

    file_last_modified = get_file_last_modified_time(file_url)
    logging.info(f"File last modified time: {file_last_modified}")

    if not last_updated or file_last_modified > last_updated:
        logging.info("File has been modified since last update. Updating corpus.")
        corpus = create_or_get_corpus()
        files = list_corpus_files(corpus.name)

        for file in files:
            if file.display_name == file_name:
                delete_corpus_file(corpus.name, file.name)
                logging.info(f"Deleted existing file: {file_name} from corpus.")

        upload_pdf_to_corpus(
            corpus_name=corpus.name,
            file_path=file_url,
            display_name=file_name,
            description="Updated file uploaded to corpus."
        )
        completed_upload_time = datetime.now().isoformat()
        write_last_updated_time(last_updated_file, completed_upload_time)
        logging.info(f"Uploaded new file: {file_name} to corpus. Completed upload time: {completed_upload_time}")
    else:
        logging.info("File has not been modified since last update. No action taken.")

if __name__ == "__main__":
    main()