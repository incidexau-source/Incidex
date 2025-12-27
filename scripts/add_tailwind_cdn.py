import os
import glob
import re

def add_cdn_to_html(file_path):
    print(f"Processing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'cdn.tailwindcss.com' in content:
        print(f"  Skipping: Tailwind CDN already present in {file_path}")
        return

    # Look for meta viewport to insert after
    viewport_pattern = re.compile(r'(<meta\s+name=["\']viewport["\'][^>]*>)', re.IGNORECASE)
    match = viewport_pattern.search(content)

    if match:
        print("  Found viewport meta tag, inserting after.")
        insertion_point = match.end()
        new_content = content[:insertion_point] + '\n  <link href="https://cdn.tailwindcss.com" rel="stylesheet">' + content[insertion_point:]
    else:
        # Fallback to <head>
        print("  Viewport meta tag not found, looking for <head>.")
        head_pattern = re.compile(r'(<head>)', re.IGNORECASE)
        match_head = head_pattern.search(content)
        if match_head:
             print("  Found <head> tag, inserting after.")
             insertion_point = match_head.end()
             new_content = content[:insertion_point] + '\n  <link href="https://cdn.tailwindcss.com" rel="stylesheet">' + content[insertion_point:]
        else:
             print("  <head> tag not found, skipping.")
             return

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("  Updated.")

def main():
    base_dir = r"TEMP_PATH"
    html_files = glob.glob(os.path.join(base_dir, "**/*.html"), recursive=True)
    
    # Filter out node_modules or .git if any (though recursive glob relative to project root might be safe if controlled)
    # user workspace is c:\Users\Tom\Incidex
    # targeted dir is c:\Users\Tom\Incidex\visualizations mostly, but instruction said "ALL HTML files in the project"
    
    target_dir = r"c:\Users\Tom\Incidex"
    print(f"Scanning {target_dir} for HTML files...")
    html_files = glob.glob(os.path.join(target_dir, "**/*.html"), recursive=True)
    
    for file_path in html_files:
        # Skip files in common exclude folders just in case
        if '.git' in file_path or 'node_modules' in file_path or '__pycache__' in file_path:
            continue
        add_cdn_to_html(file_path)

if __name__ == "__main__":
    main()
