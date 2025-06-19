# Lesson 1 Exercises: Command Line and Development Environment

## Exercise 1: Command Line Navigation (Beginner)

**Objective**: Practice basic command line navigation and file operations.

### Tasks:
1. Open your terminal/command prompt
2. Find out what directory you're currently in
3. List all files and folders in your current directory
4. Create a new folder called `my_coding_journey`
5. Navigate into this folder
6. Create three files: `notes.txt`, `ideas.txt`, and `questions.txt`
7. List the contents of your folder to verify the files were created
8. Navigate back to the parent directory
9. List the contents to see your new folder

### Commands to Use:
```bash
pwd             # Print working directory
ls              # List directory contents  
mkdir           # Make directory
cd              # Change directory
touch           # Create empty file (Linux/Mac)
echo > filename # Create file with content (Windows compatible)
```

### Expected Output:
```
my_coding_journey/
├── notes.txt
├── ideas.txt
└── questions.txt
```

---

## Exercise 2: File Content Manipulation (Intermediate)

**Objective**: Learn to create and view file contents from the command line.

### Tasks:
1. Navigate to your `my_coding_journey` folder
2. Add content to `notes.txt`: "Today I learned about the command line!"
3. Add content to `ideas.txt`: "I want to build a web app someday."
4. Add content to `questions.txt`: "What programming language should I learn first?"
5. Display the contents of each file
6. Create a summary file called `day1_summary.txt` that contains all the information from the other three files

### Commands to Use:
```bash
echo "text" > filename     # Write text to file (overwrites)
echo "text" >> filename    # Append text to file
cat filename               # Display file contents
cat file1 file2 > newfile  # Combine files
```

### Sample Solution:
```bash
cd my_coding_journey
echo "Today I learned about the command line!" > notes.txt
echo "I want to build a web app someday." > ideas.txt
echo "What programming language should I learn first?" > questions.txt
cat notes.txt ideas.txt questions.txt > day1_summary.txt
cat day1_summary.txt
```

---

## Exercise 3: Directory Structure Creation (Advanced)

**Objective**: Create a complex directory structure for a coding project.

### Tasks:
Create the following directory structure:
```
my_first_project/
├── src/
│   ├── main/
│   └── tests/
├── docs/
│   ├── user_guide/
│   └── developer_guide/
├── data/
│   ├── input/
│   └── output/
└── config/
```

And create these files:
- `my_first_project/README.md`
- `my_first_project/src/main/app.py`
- `my_first_project/src/tests/test_app.py`
- `my_first_project/docs/project_overview.md`
- `my_first_project/config/settings.txt`

### Commands Needed:
```bash
mkdir -p path/to/nested/directory  # Create nested directories
tree directory_name                # Display directory structure (if available)
find . -type d                     # List all directories
find . -type f                     # List all files
```

### Verification:
Use `tree my_first_project` or `find my_first_project` to verify your structure.

---

## Exercise 4: Development Environment Setup (Practical)

**Objective**: Set up a basic development environment.

### Tasks:
1. Create a new project folder called `hello_world_project`
2. Navigate into the project folder
3. Create a `.gitignore` file with common entries
4. Create a `README.md` file with project description
5. Create a simple project structure
6. Initialize a git repository (if git is available)

### Steps:
```bash
# Create project
mkdir hello_world_project
cd hello_world_project

# Create .gitignore
echo "__pycache__/" > .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo ".vscode/" >> .gitignore

# Create README
echo "# Hello World Project" > README.md
echo "" >> README.md
echo "This is my first coding project!" >> README.md
echo "" >> README.md
echo "## Getting Started" >> README.md
echo "1. Clone this repository" >> README.md
echo "2. Run the main script" >> README.md

# Create project structure
mkdir src
mkdir tests
mkdir docs
touch src/main.py
touch tests/test_main.py
touch docs/project_plan.md

# Initialize git (optional)
git init
git add .
git commit -m "Initial project setup"
```

---

## Challenge Exercises

### Challenge 1: Command Line File Manager
Create a series of commands that:
1. Creates 5 folders with sequential names (folder1, folder2, etc.)
2. Creates 2 files in each folder
3. Copies one file from folder1 to all other folders
4. Lists all files in all folders
5. Removes all files that contain a specific word in their name

### Challenge 2: Project Template Creator
Write a series of commands that creates a template for any new coding project:
1. Takes a project name as input
2. Creates the standard directory structure
3. Creates template files (README, .gitignore, main script)
4. Initializes version control
5. Creates a "project created successfully" message

### Challenge 3: File Organization
Create commands that:
1. Finds all `.txt` files in your current directory and subdirectories
2. Creates a `text_files` folder
3. Copies all `.txt` files to this folder
4. Creates an index file listing all the copied files with their original paths

---

## Solutions and Tips

### General Tips:
- Use `Tab` key for auto-completion
- Use `↑` arrow to repeat previous commands
- Use `Ctrl+C` to cancel a command
- Use `clear` to clean your terminal screen
- Use `--help` flag with commands to see options

### Common Mistakes to Avoid:
1. **Case sensitivity**: File names are case-sensitive on Linux/Mac
2. **Spaces in names**: Use quotes around names with spaces
3. **Path confusion**: Always check where you are with `pwd`
4. **Overwriting files**: Be careful with `>` vs `>>`

### Safety Commands:
```bash
ls -la           # Always check before making changes
cp original backup  # Create backups before modifying
rm -i filename   # Interactive delete (asks for confirmation)
```

---

## Homework Assignment

**Task**: Create your personal coding workspace

1. Create a main folder called `coding_workspace`
2. Inside, create folders for:
   - `lessons` (for lesson notes)
   - `exercises` (for practice code)
   - `projects` (for personal projects)
   - `resources` (for useful files and links)
3. In each folder, create an appropriate README file explaining its purpose
4. Practice navigating between folders using only command line
5. Document 5 new command line commands you discover on your own

**Deliverable**: A screenshot or text output showing your directory structure and file contents.

**Time**: 30 minutes

---

## Additional Resources

- [Command Line Cheat Sheet](https://www.git-tower.com/blog/command-line-cheat-sheet/)
- [Terminal Commands for Beginners](https://ubuntu.com/tutorials/command-line-for-beginners)
- [Bash Scripting Tutorial](https://ryanstutorials.net/bash-scripting-tutorial/)
- [VS Code Terminal Guide](https://code.visualstudio.com/docs/terminal/basics)
