import os
import subprocess
import argparse

# Define constants
LAYOUT = "webnovel"
SUPABASE_PAGE_FORMAT = True
REPO_URL = "liraymond04/re0-translations"

cur_dir = os.getcwd()

def generate_yaml_frontmatter(md_file_path):
    title = os.path.splitext(os.path.basename(md_file_path))[0]
    
    file_path = os.path.relpath(md_file_path, start=cur_dir)

    frontmatter = f"""---
layout: {LAYOUT}
title: {title}
repo_url: {REPO_URL}
file_path: {file_path}
supabase_page_format: {str(SUPABASE_PAGE_FORMAT).lower()}
---
"""
    return frontmatter

def prepend_frontmatter_to_md(md_file_path):
    frontmatter = generate_yaml_frontmatter(md_file_path)
    
    print(md_file_path)
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)

def convert_docx_to_md(input_file, output_file, output_dir, lua_filter=None):
    inf = os.path.abspath(input_file)
    dir = os.path.abspath(output_file)
    command = ['pandoc', '--extract-media', './', '-f', 'docx', '-t', 'gfm', inf, '-o', dir]

    if lua_filter:
        command.extend(['--lua-filter', os.path.abspath(lua_filter)])

    try:
        os.chdir(output_dir)
        subprocess.run(command, check=True)
        print(f"Converted {input_file} to {output_file}")
        prepend_frontmatter_to_md(dir)
    except subprocess.CalledProcessError:
        print(f"Error converting {input_file} to {output_file}")
    finally:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

def process_directories(root_dir, output_dir, lua_filter=None):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'omegat.project' in filenames:
            print(f"Found omegat.project in {dirpath}")
            
            target_dir = os.path.join(dirpath, 'target')
            if os.path.isdir(target_dir):
                print(f"Found target/ directory in {dirpath}")
                
                for target_file in os.listdir(target_dir):
                    if target_file.endswith('.docx'):
                        input_file = os.path.join(target_dir, target_file)
                        
                        rel_path = os.path.relpath(dirpath, root_dir)
                        output_file_dir = os.path.join(output_dir, rel_path)
                        
                        os.makedirs(output_file_dir, exist_ok=True)
                        
                        output_file = os.path.join(output_file_dir, target_file.replace('.docx', '.md'))
                        
                        convert_docx_to_md(input_file, output_file, output_file_dir, lua_filter)
            else:
                # print(f"No target/ directory in {dirpath}")
                pass
        else:
            # print(f"No omegat.project file in {dirpath}")
            pass

def main():
    parser = argparse.ArgumentParser(description="Convert DOCX files from OmegaT target directories to Markdown.")
    parser.add_argument("root_directory", help="Root directory to start searching from.")
    parser.add_argument("output_directory", help="Directory to save converted .md files.")
    parser.add_argument("--lua-filter", help="Path to the Lua filter to apply during conversion.", default=None)
    
    args = parser.parse_args()

    process_directories(args.root_directory, args.output_directory, args.lua_filter)

if __name__ == "__main__":
    main()
