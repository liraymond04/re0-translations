import datetime
import os
import logging
import sys

import yaml
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
from supabase import create_client, Client

API_KEY: str = os.getenv("SUPABASE_SERVICE_KEY") or ""
SUPABASE_URL: str = os.getenv("SUPABASE_URL") or ""

supabase: Client = create_client(SUPABASE_URL, API_KEY)

def extract_yaml_frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        return yaml.safe_load(yaml_content)
    else:
        raise ValueError("No YAML frontmatter found")

def remove_yaml_frontmatter(text):
    pattern = r"^---\n.*?\n---\n"
    content_without_frontmatter = re.sub(pattern, "", text, flags=re.DOTALL)
    return content_without_frontmatter

excluded_files = ["LICENSE.md", "README.md"]

def get_added_files_from_env():
    try:
        added_files_env = os.getenv("ADDED_MARKDOWN_FILES")
        if not added_files_env:
            logger.error("No added markdown files found in the environment variable.")
            return []

        added_files = [
            file.strip() for file in added_files_env.split(",")
            if file.strip() and file.strip() not in excluded_files
        ]
        return added_files
    except Exception as e:
        logger.error(f"Error parsing added markdown files: {e}")
        sys.exit(1)

def get_deleted_files_from_env():
    try:
        deleted_files_env = os.getenv("DELETED_MARKDOWN_FILES")
        if not deleted_files_env:
            logger.error("No deleted markdown files found in the environment variable.")
            return []

        deleted_files = [
            file.strip() for file in deleted_files_env.split(",")
            if file.strip() and file.strip() not in excluded_files
        ] 
        return deleted_files
    except Exception as e:
        logger.error(f"Error parsing deleted markdown files: {e}")
        sys.exit(1)

def get_changed_files_from_env():
    try:
        changed_files_env = os.getenv("CHANGED_MARKDOWN_FILES")
        if not changed_files_env:
            logger.error("No changed markdown files found in the environment variable.")
            return []

        changed_files = [
            file.strip() for file in changed_files_env.split(",")
            if file.strip() and file.strip() not in excluded_files
        ]
        return changed_files
    except Exception as e:
        logger.error(f"Error parsing changed markdown files: {e}")
        sys.exit(1)

def check(response, metadata, field):
    return response[field] == metadata[field]

def update_post_field_in_db(metadata, field):
    file = metadata["file_path"] or ""
    try:
        _ = (
            supabase.table("posts")
            .update({field: metadata[field]})
            .eq("repo_url", metadata["repo_url"])
            .eq("file_path", metadata["file_path"])
            .execute()
        )
        logger.info(f"Successfully updated {field} in post for {file}")
    except Exception as e:
        logger.error(f"Error updating {field} in post for {file}: {e}")
        sys.exit(1)

def create_new_post(file, metadata):
    try:
        post_data = {
            "title": metadata["title"],
            "content": metadata["content"],
            "repo_url": metadata["repo_url"],
            "file_path": metadata["file_path"],
            "updated_at": str(datetime.datetime.now())
        }

        if "tags" in metadata:
            post_data["tags"] = metadata["tags"]

        if "keywords" in metadata:
            post_data["keywords"] = metadata["keywords"]

        _ = (
            supabase
            .table("posts")
            .insert(post_data)
            .execute()
        )
    except Exception as e:
        logger.error(f"Error creating new post for {file}: {e}")
        sys.exit(1)

def delete_post(file, metadata):
    try:
        _ = (
            supabase
            .table("posts")
            .delete()
            .eq("repo_url", metadata["repo_url"])
            .eq("file_path", metadata["file_path"])
            .execute()
        )
    except Exception as e:
        logger.error(f"Error deleting post for {file}: {e}")
        sys.exit(1)

def check_if_differences_exist(file, metadata):
    try:
        response = (
            supabase
            .table("posts")
            .select("*")
            .eq("repo_url", metadata["repo_url"])
            .eq("file_path", metadata["file_path"])
            .single()
            .execute()
        )

        updated = False
        fields = ["title", "content", "tags", "keywords", "media_files", "layout", "updated_at", "created_at"]

        for field in fields:
            if field in metadata:
                if not check(response.data, metadata, field):
                    update_post_field_in_db(metadata, field)
                    updated = True

        if updated:
            _ = (
                supabase.table("posts")
                .update({"updated_at": str(datetime.datetime.now())})
                .eq("repo_url", metadata["repo_url"])
                .eq("file_path", metadata["file_path"])
                .execute()
            )
            logger.info(f"Successfully updated updated_at in post for {file}")
    except Exception as e:
        logger.error(f"Error checking differences for {file}: {e}")
        sys.exit(1)

def read_markdown_metadata(file_path, deleted=False):
    try:
        if deleted:
            file_path = os.path.join("actions/recovered", file_path)

        with open(file_path, 'r') as f:
            content = f.read()

        ret = extract_yaml_frontmatter(content)
        ret["content"] = remove_yaml_frontmatter(content)
        return ret
    except FileNotFoundError:
        logger.error(f"Markdown file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading metadata from {file_path}: {e}")
        sys.exit(1)

def main():
    try:
        repo_url = os.getenv("GITHUB_REPOSITORY_URL")
        if not repo_url:
            logger.error("GITHUB_REPOSITORY_URL environment variable not set.")
            sys.exit(1)

        # added
        added_files = get_added_files_from_env()
        if not added_files:
            logger.info("No markdown files were added.")

        for file in added_files:
            if file.endswith('.md'):
                logger.info(f"Processing {file}")
                metadata = read_markdown_metadata(file)
                # print("Markdown files were added.")
                # print(metadata)
                create_new_post(file, metadata)

        # changed
        changed_files = get_changed_files_from_env()
        if not changed_files:
            logger.info("No markdown files were changed.")

        for file in changed_files:
            if file.endswith('.md'):
                logger.info(f"Processing {file}")
                metadata = read_markdown_metadata(file)
                # print("Markdown files were modified.")
                # print(metadata)
                check_if_differences_exist(file, metadata)

        # deleted
        deleted_files = get_deleted_files_from_env()
        if not deleted_files:
            logger.info("No markdown files were deleted.")

        for file in deleted_files:
            if file.endswith('.md'):
                logger.info(f"Processing {file}")
                metadata = read_markdown_metadata(file, deleted=True)
                # print("Markdown files were deleted.")
                # print(metadata)
                delete_post(file, metadata)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
