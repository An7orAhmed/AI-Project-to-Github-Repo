import os
import re
import subprocess
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
GITHUB_USERNAME = "An7orAhmed"
AI_MODEL = "deepseek/deepseek-r1:free"
#AI_MODEL = "google/gemini-2.0-flash-thinking-exp:free"
# Change to your project directory
BASE_PATH = "/Users/an7or/Library/CloudStorage/GoogleDrive-kitswarebd@gmail.com/My Drive/Projects/Student/"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY,
)

completed_count = 0

def contains_source_files(project_dir):
    """Checks if any subfolder contains C/C++/Python/Arduino/Basic files."""
    for root, _, files in os.walk(project_dir):
        if any(file.endswith(('.c', '.cpp', '.ino', '.bas', '.py')) for file in files):
            return True
    return False

def process_project(project_dir):
    """Handles README generation and GitHub push for a project"""
    print(f"\n🔍 Processing: {project_dir}")
    original_name = os.path.basename(project_dir)

    # Get project files
    code_files, pdf_files = get_project_files(project_dir)

    # Generate README with AI title
    readme_content, ai_project_name = generate_readme(original_name, code_files, pdf_files)

    # Path to README.md
    readme_path = os.path.join(project_dir, "README.md")

    # If the directory exists, we should be able to write the file
    if not os.path.exists(os.path.dirname(readme_path)):
        print("❌ Directory does not exist!")

    # Delete the existing README.md if it exists
    if os.path.exists(readme_path):
        os.remove(readme_path)
        print(f"❌ Existing README.md deleted for {original_name}")

    # Save README.md
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"✅ README.md created for {original_name} (AI Name: {ai_project_name})")

    # Push to GitHub using AI-generated name
    push_to_github(project_dir, ai_project_name)
    print(f"🚀 {ai_project_name} pushed to GitHub!\n")


def find_project_and_push(base_path):
    """Searches for project directories matching '<number>. <text>' and processes them all"""
    global completed_count
    pattern = re.compile(r"^\d+\.\s+.*")  # Matches "<number>. <text>"
    project_dirs = []  # Collects all valid project directories

    # Get the current directory where the script is running
    pushed_folders_file = os.path.join(os.getcwd(), "pushed_folder.txt")

    if os.path.exists(pushed_folders_file):
        with open(pushed_folders_file, "r", encoding="utf-8") as f:
            pushed_folders = set(f.read().splitlines())  # Read already processed dirs into a set
            completed_count = len(pushed_folders)
    else:
        pushed_folders = set()  # If the file doesn't exist, assume no project has been processed

    for root, dirs, _ in os.walk(base_path):
        folder_name = os.path.basename(root)

        if "AIPoster" in root:
            continue  
        if not pattern.match(folder_name):
            continue  
        if not contains_source_files(root):
            continue  
        if root in pushed_folders:
            continue 

        project_dirs.append(root)  # Collect valid project paths

    # Process all collected projects
    for project in project_dirs:
        process_project(project)
        
        # After processing, mark the project as pushed by appending it to the file
        with open(pushed_folders_file, "a", encoding="utf-8") as f:
            f.write(project + "\n")
        print(f"✅ {project} marked as pushed.")
        completed_count += 1


def get_project_files(project_dir):
    """Returns code and PDF files, but keeps only .ino files if any exist"""
    code_files = []
    pdf_files = []
    ino_files = []
    
    for root, _, files in os.walk(project_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.ino'):
                ino_files.append(file_path)
                print(f"📄 Found .ino file: {file_path}")
            elif file.endswith(('.c', '.cpp', '.bas', '.py')):
                code_files.append(file_path)
                print(f"📄 Found code file: {file_path}")
            elif file.endswith('.pdf'):
                pdf_files.append(file_path)
                print(f"📘 Found PDF file: {file_path}")
    
    return (ino_files if ino_files else code_files), pdf_files


def generate_readme(project_name, code_files, pdf_files):
    """Generates README using OpenAI and extracts the AI-generated project title"""
    global completed_count
    print(f"🧠 [{completed_count + 1}] Generating README for {project_name}...")
    
    try:
        code_snippets = []
        for file in code_files:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            code_snippets.append(f"### {os.path.basename(file)}\n\n{content}...\n\n") 
        
        prompt = f"""
        Generate a project documentation README file for a project named '{project_name}'.
        This project may contains one or multiple C/C++/Arduino/Proton Basic source code.
        Provide a meaningful project title(within 50char) and detailed description about the project.
        Do not include contribution, license information in the README.
        if possible include pinmap in the README.
        add a note that diagram may not be accurate (adjust as needed).
        (Just reply with actual content without unnecessary query explaination)
        list of pdf files: {','.join(pdf_files)}
        Here are some code snippets:
        {''.join(code_snippets)}
        """

        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        if completion is None or completion.choices is None or len(completion.choices) == 0:
            print("❌ README generation failed. Retrying...")
            return generate_readme(project_name, code_files, pdf_files)
        readme_content = completion.choices[0].message.content

        ai_project_name = ""
        startI = readme_content.find("# ")
        if startI != -1:
            readme_content = readme_content[startI:]
            readme_content = readme_content.replace("```markdown\n", "")

            # Extract AI-generated project title (first line of README)
            first_line = readme_content.split("\n", 1)[0]
            ai_project_name = first_line.strip("# ").strip()  # Remove Markdown heading
            if ai_project_name == "" or ai_project_name.startswith("Okay"):
                ai_project_name = re.sub(r'^\d+\.\s*', '', project_name) 
        else:
            readme_content = ""
        
        return readme_content, ai_project_name
    except:
        print(f"❌ Restarting...")
        generate_readme(project_name, code_files, pdf_files)


def sanitize_repo_name(repo_name):
    """Sanitizes the AI-generated project name for GitHub"""
    repo_name = repo_name.replace(" ", "-")  # Replace spaces with dashes
    repo_name = re.sub(r"[^\w\-]", "", repo_name)  # Remove special characters
    return repo_name[:50]  # Limit to 50 chars (GitHub repo limit)


def create_github_repo(repo_name):
    """Creates a new GitHub repository if it does not exist."""
    url = f"https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"name": repo_name, "private": False}  # Set to True if you want a private repo

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"✅ GitHub repository '{repo_name}' created successfully!")
    elif response.status_code == 422:
        print(f"⚠️ Repository '{repo_name}' already exists.")
        repo_name += "-2"
        create_github_repo(repo_name)
    else:
        print(f"❌ Failed to create repository: {response.json()}")

def push_to_github(project_dir, ai_project_name):
    """Initializes Git repo, commits, and pushes to GitHub using AI-generated name via HTTPS."""
    os.chdir(project_dir)

    # Initialize new Git repository
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

    # Sanitize AI-generated project name
    repo_name = sanitize_repo_name(ai_project_name)
    repo_url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}.git"

    # Create GitHub repo if not found
    create_github_repo(repo_name)

    # Check if remote origin already exists
    try:
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
    except subprocess.CalledProcessError:
        print("❌ Remote origin already exists. Skipping remote addition.")

    # Ensure the branch is main
    subprocess.run(["git", "branch", "-M", "main"], check=True)

    # Push to GitHub
    try:
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        print(f"🚀 Successfully pushed {repo_name} to GitHub via HTTPS!")
    except:
        print(f"❌ Failed to push {repo_name} to GitHub. Check authentication or repo status.")
        subprocess.run(["rm", "-rf", ".git"], check=True)
        print("🔄 Retrying...")
        push_to_github(project_dir, ai_project_name)

def main():  
    find_project_and_push(BASE_PATH) 

if __name__ == "__main__":
    main()
