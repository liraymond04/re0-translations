import os
import logging
import sys
import mimetypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
from supabase import create_client, Client

API_KEY: str = os.getenv("SUPABASE_SERVICE_KEY") or ""
SUPABASE_URL: str = os.getenv("SUPABASE_URL") or ""
repo_url: str = os.getenv("GITHUB_REPOSITORY_URL") or ""

supabase: Client = create_client(SUPABASE_URL, API_KEY)

def get_content_type(file_path):
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type

def get_added_files_from_env():
    try:
        added_files_env = os.getenv("ADDED_IMAGE_FILES")
        if not added_files_env:
            logger.error("No added image files found in the environment variable.")
            return []

        added_files = [
            file.strip() for file in added_files_env.split(",")
            if file.strip()
        ]
        return added_files
    except Exception as e:
        logger.error(f"Error parsing added image files: {e}")
        sys.exit(1)

def get_deleted_files_from_env():
    try:
        deleted_files_env = os.getenv("DELETED_IMAGE_FILES")
        if not deleted_files_env:
            logger.error("No deleted image files found in the environment variable.")
            return []

        deleted_files = [
            file.strip() for file in deleted_files_env.split(",")
            if file.strip()
        ] 
        return deleted_files
    except Exception as e:
        logger.error(f"Error parsing deleted image files: {e}")
        sys.exit(1)

def get_changed_files_from_env():
    try:
        changed_files_env = os.getenv("CHANGED_IMAGE_FILES")
        if not changed_files_env:
            logger.error("No changed image files found in the environment variable.")
            return []

        changed_files = [
            file.strip() for file in changed_files_env.split(",")
            if file.strip()
        ]
        return changed_files
    except Exception as e:
        logger.error(f"Error parsing changed image files: {e}")
        sys.exit(1)

def check(response, metadata, field):
    return response[field] == metadata[field]

def update_image(file):
    try:
        with open(file, "rb") as f:
            _ = supabase.storage.from_("images").upload(
                file=f,
                path=os.path.join(repo_url, file),
                file_options={
                    "content-type": get_content_type(file) or "text/plain;charset=UTF-8",
                    "cache-control": "3600",
                    "upsert": "true"
                },
            )
        logger.info(f"Successfully updated {file}")
    except Exception as e:
        logger.error(f"Error updating {file}: {e}")
        sys.exit(1)

def create_image(file):
    try:
        with open(file, "rb") as f:
            _ = supabase.storage.from_("images").upload(
                file=f,
                path=os.path.join(repo_url, file),
                file_options={
                    "content-type": get_content_type(file) or "text/plain;charset=UTF-8",
                    "cache-control": "3600",
                    "upsert": "false"
                },
            )
        logger.info(f"Successfully created {file}")
    except Exception as e:
        logger.error(f"Error creating new post for {file}: {e}")
        sys.exit(1)

def delete_image(file):
    try:
        supabase.storage.from_("images").remove([os.path.join(repo_url, file)])
        logger.info(f"Successfully deleted {file}")
    except Exception as e:
        logger.error(f"Error deleting post for {file}: {e}")
        sys.exit(1)

def is_image(file: str):
    return file.endswith('.png') or file.endswith('.jpg')

def main():
    try:
        repo_url = os.getenv("GITHUB_REPOSITORY_URL")
        if not repo_url:
            logger.error("GITHUB_REPOSITORY_URL environment variable not set.")
            sys.exit(1)

        # added
        added_files = get_added_files_from_env()
        if not added_files:
            logger.info("No image files were added.")

        for file in added_files:
            if is_image(file):
                logger.info(f"Processing {file}")
                create_image(file)

        # changed
        changed_files = get_changed_files_from_env()
        if not changed_files:
            logger.info("No image files were changed.")

        for file in changed_files:
            if is_image(file):
                logger.info(f"Processing {file}")
                update_image(file)

        # deleted
        deleted_files = get_deleted_files_from_env()
        if not deleted_files:
            logger.info("No image files were deleted.")

        for file in deleted_files:
            if is_image(file):
                logger.info(f"Processing {file}")
                delete_image(file)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
