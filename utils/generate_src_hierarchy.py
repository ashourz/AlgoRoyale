import os

def print_directory_structure(root_dir, exclude_dirs=None, indent=""):
    if exclude_dirs is None:
        exclude_dirs = {".git", "__pycache__", "node_modules", ".venv", ".idea"}

    for item in os.listdir(root_dir):
        path = os.path.join(root_dir, item)
        if os.path.isdir(path) and item not in exclude_dirs:
            print(f"{indent}📂 {item}")
            print_directory_structure(path, exclude_dirs, indent + "  ")
        elif os.path.isfile(path):
            print(f"{indent}📄 {item}")

if __name__ == "__main__":
    # Set the root directory to the `src` folder in your project
    project_root = os.path.join(os.getcwd(), "src")
    
    # Ensure the src folder exists
    if os.path.exists(project_root):
        print(f"Project hierarchy starting from: {project_root}")
        print_directory_structure(project_root)
    else:
        print("The 'src' folder does not exist in the current directory.")