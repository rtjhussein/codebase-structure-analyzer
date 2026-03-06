import os

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def list_directory(path):
    """
    Lists all files and folders in the given directory path.
    Returns a list of tuples (name, full_path, is_dir).
    """
    items = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.name == 'codebase_contents.txt':
                continue  # Skip the output file itself
            items.append((entry.name, entry.path, entry.is_dir()))
    return items

def display_options(items):
    """
    Displays the list of items with numbering.
    """
    for idx, (name, path, is_dir) in enumerate(items, 1):
        print(f"{idx}. [{'D' if is_dir else 'F'}] {name}")

def get_user_selection(items):
    """
    Prompts the user to select items by entering numbers separated by commas.
    Returns the list of selected items.
    """
    while True:
        selection = input("Enter the numbers of the files/folders you want to include (e.g., 1,3,5), or 'all' to include all: ")
        if selection.strip().lower() == 'all':
            return items
        selected_indices = selection.split(',')
        try:
            selected = [items[int(idx.strip())-1] for idx in selected_indices]
            return selected
        except (ValueError, IndexError):
            print("Invalid input. Please enter valid numbers separated by commas or 'all'.")

def collect_selected_paths(selected_items):
    """
    Given a list of selected items, collect all file paths.
    If a folder is selected, prompt to include entire folder or select contents.
    """
    paths = []
    for name, path, is_dir in selected_items:
        if is_dir:
            include_entire = prompt_include_entire_folder(path)
            if include_entire:
                paths.extend(collect_all_files(path))
            else:
                sub_items = list_directory(path)
                if not sub_items:
                    print(f"No selectable items in folder: {path}")
                    continue
                print(f"\nSelecting contents of folder: {os.path.relpath(path)}")
                display_options(sub_items)
                selected_sub = get_user_selection(sub_items)
                paths.extend(collect_selected_paths(selected_sub))
        else:
            if is_code_file(path):
                paths.append(path)
    return paths

def prompt_include_entire_folder(folder_path):
    """
    Asks the user whether to include the entire folder or select specific items.
    Returns True if entire folder is to be included, False otherwise.
    """
    while True:
        choice = input(f"Do you want to include the entire folder '{os.path.basename(folder_path)}'? (y/n): ").strip().lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def collect_all_files(folder_path):
    """
    Recursively collects all code file paths within the given folder.
    """
    collected = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_code_file(file_path):
                collected.append(file_path)
    return collected

def is_code_file(file_path):
    """
    Determines if a file is a code file based on its extension.
    Modify this function to include/exclude specific file types as needed.
    """
    code_extensions = {'.py', '.java', '.c', '.cpp', '.js', '.json', '.html', '.css', '.txt', '.md', '.rb', '.go', '.php', '.ts', '.swift', '.kt'}
    _, ext = os.path.splitext(file_path)
    return ext.lower() in code_extensions

def write_code_to_file(file_paths, output_path):
    """
    Writes the contents of each file to the output file with headers.
    """
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for file_path in file_paths:
            relative_path = os.path.relpath(file_path)
            outfile.write(f"\n\n===== {relative_path} =====\n\n")
            outfile.write("```\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
            except Exception as e:
                outfile.write(f"Error reading file: {e}\n")
            outfile.write("```\n")

def get_project_structure(selected_paths, root_path):
    """
    Generates a tree-like string representation of the selected project structure.
    """
    tree = {}
    for path in selected_paths:
        parts = os.path.relpath(path, root_path).split(os.sep)
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    return build_tree_string(tree)

def build_tree_string(tree, prefix=''):
    """
    Recursively builds a tree-like string from a nested dictionary.
    """
    tree_str = ""
    for idx, (name, subtree) in enumerate(sorted(tree.items()), 1):
        connector = "└── " if idx == len(tree) else "├── "
        tree_str += f"{prefix}{connector}{name}\n"
        if subtree:
            extension = "    " if idx == len(tree) else "│   "
            tree_str += build_tree_string(subtree, prefix + extension)
    return tree_str

def main():
    root_dir = os.getcwd()
    print(f"Root directory: {root_dir}\n")

    items = list_directory(root_dir)
    if not items:
        print("No files or folders found in the root directory.")
        return

    print("Select the files and folders you want to include:")
    display_options(items)

    selected_items = get_user_selection(items)
    selected_paths = collect_selected_paths(selected_items)

    if not selected_paths:
        print("No valid files selected.")
        return

    output_file = os.path.join(root_dir, 'codebase_contents.txt')
    write_code_to_file(selected_paths, output_file)
    print(f"\nCode has been written to {output_file}")

    # Append project structure
    project_structure = "\n\n===== Project Structure =====\n\n"
    project_structure += get_project_structure(selected_paths, root_dir)
    with open(output_file, 'a', encoding='utf-8') as outfile:
        outfile.write(project_structure)
    print("Project structure has been appended to the output file.")

if __name__ == "__main__":
    main()
