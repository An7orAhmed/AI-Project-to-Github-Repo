# 🚀 AI-Powered Project Scanner & GitHub Uploader  

This Python script automates the process of **identifying, documenting, and uploading projects** to GitHub using AI. It scans a specified directory, detects project folders based on naming conventions, generates a meaningful **title and README** using **DeepSeek AI**, and automatically pushes them to GitHub.  

## 🔥 Features  

✅ **Project Detection** – Scans directories for folders following the pattern `<number>. <Project Name>`  
✅ **Source Code Extraction** – Identifies C, C++, Python, Arduino, and Basic files  
✅ **AI-Powered README Generation** – Uses DeepSeek AI to generate project titles and descriptions  
✅ **GitHub Automation** – Creates repositories and pushes projects automatically  
✅ **Prevents Duplicate Uploads** – Tracks already processed projects  

## 📂 Folder Naming Convention  

- The script considers a folder as a project if its name follows:  
  ```plaintext
  1. Project Name
  2. Another Project
  ```  
- It scans for **source code files** (`.c`, `.cpp`, `.ino`, `.bas`, `.py`) inside each project folder.  

## 🔧 Setup & Usage  

### 1️⃣ Install Dependencies  

Ensure you have Python 3 installed. Install required packages using:  
```bash
pip install openai requests python-dotenv
```  

### 2️⃣ Set Up API Keys  

Create a `.env` file in the same directory and add:  
```plaintext
GITHUB_TOKEN=your_github_personal_access_token
OPENAI_API_KEY=your_openai_api_key
```  

### 3️⃣ Modify Base Path  

Edit the `BASE_PATH` in the script to match your project directory:  
```python
BASE_PATH = "/path/to/your/projects/"
```  

### 4️⃣ Run the Script  

Execute the script with:  
```bash
python script.py
```  

## 🚀 How It Works  

1️⃣ **Scans** the given directory for folders matching the naming pattern  
2️⃣ **Extracts** source code and relevant project files  
3️⃣ **Generates** a meaningful **README.md** using **DeepSeek AI**  
4️⃣ **Creates** a repository on GitHub (if not already present)  
5️⃣ **Pushes** the project files along with the AI-generated README  

## 🤖 AI-Powered README Generation  

The script uses **DeepSeek AI** to generate a README based on:  
- Source code snippets  
- Project name  
- Available PDF files (if any)  

## 🛠 Technologies Used  

- **Python** – Core scripting language  
- **GitHub API** – Automates repo creation & pushing  
- **OpenAI API (DeepSeek)** – Generates project titles & README  
- **Regex & File Handling** – For scanning and processing project files  

## ⚡ Future Improvements  

- Support for additional programming languages  
- Enhanced AI prompts for better documentation  
- Integration with **Gemini AI** for alternative README generation  
