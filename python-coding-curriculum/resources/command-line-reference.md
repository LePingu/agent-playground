# Command Line Quick Reference

This is a handy reference guide for command line operations covered in Lesson 1.

## Navigation Commands

| Command | Description | Example |
|---------|-------------|---------|
| `pwd` | Print working directory (where am I?) | `pwd` |
| `ls` | List directory contents | `ls -la` |
| `cd` | Change directory | `cd /path/to/directory` |
| `cd ..` | Go up one directory level | `cd ..` |
| `cd ~` | Go to home directory | `cd ~` |
| `cd` | Go to home directory (shortcut) | `cd` |

## File and Directory Operations

| Command | Description | Example |
|---------|-------------|---------|
| `mkdir` | Create directory | `mkdir new_folder` |
| `mkdir -p` | Create nested directories | `mkdir -p path/to/nested/folder` |
| `touch` | Create empty file (Linux/Mac) | `touch newfile.txt` |
| `echo >` | Create file with content | `echo "Hello" > file.txt` |
| `cp` | Copy files | `cp source.txt dest.txt` |
| `cp -r` | Copy directories recursively | `cp -r folder1/ folder2/` |
| `mv` | Move/rename files | `mv old.txt new.txt` |
| `rm` | Remove files | `rm file.txt` |
| `rm -r` | Remove directories | `rm -r folder/` |
| `rm -i` | Interactive removal (asks confirmation) | `rm -i file.txt` |

## File Content Operations

| Command | Description | Example |
|---------|-------------|---------|
| `cat` | Display file contents | `cat file.txt` |
| `head` | Show first 10 lines | `head file.txt` |
| `tail` | Show last 10 lines | `tail file.txt` |
| `less` | View file page by page | `less file.txt` |
| `echo "text" >` | Write to file (overwrite) | `echo "Hello" > file.txt` |
| `echo "text" >>` | Append to file | `echo "World" >> file.txt` |

## System Information

| Command | Description | Example |
|---------|-------------|---------|
| `whoami` | Current username | `whoami` |
| `date` | Current date and time | `date` |
| `which` | Location of command | `which python` |
| `history` | Command history | `history` |
| `clear` | Clear terminal screen | `clear` |

## File Permissions (Linux/Mac)

| Command | Description | Example |
|---------|-------------|---------|
| `chmod` | Change file permissions | `chmod 755 script.py` |
| `ls -l` | List with permissions | `ls -l` |

## Search and Find

| Command | Description | Example |
|---------|-------------|---------|
| `find` | Find files and directories | `find . -name "*.txt"` |
| `grep` | Search text in files | `grep "hello" file.txt` |
| `locate` | Find files by name | `locate filename` |

## Process Management

| Command | Description | Example |
|---------|-------------|---------|
| `ps` | List running processes | `ps aux` |
| `top` | System activity monitor | `top` |
| `kill` | Terminate process | `kill PID` |
| `Ctrl+C` | Stop current command | Press Ctrl+C |
| `Ctrl+Z` | Suspend current command | Press Ctrl+Z |

## Shortcuts and Tips

### Keyboard Shortcuts
- **Tab**: Auto-complete file/directory names
- **↑/↓**: Navigate command history
- **Ctrl+C**: Cancel current command
- **Ctrl+L**: Clear screen (alternative to `clear`)
- **Ctrl+A**: Move to beginning of line
- **Ctrl+E**: Move to end of line
- **Ctrl+U**: Clear line before cursor
- **Ctrl+K**: Clear line after cursor

### Wildcards
- `*`: Matches any characters
- `?`: Matches single character
- `[abc]`: Matches any character in brackets
- `{txt,pdf}`: Matches either txt or pdf

### Examples:
```bash
ls *.txt        # List all .txt files
rm test?.log    # Remove test1.log, test2.log, etc.
cp *.{py,txt} backup/  # Copy all .py and .txt files
```

## Command Combinations

### Pipes (|)
Send output of one command to another:
```bash
ls -la | grep ".txt"    # List files and filter for .txt
cat file.txt | head -5  # Show first 5 lines of file
```

### Redirection
```bash
command > file.txt      # Send output to file (overwrite)
command >> file.txt     # Send output to file (append)
command < file.txt      # Use file as input
```

### Command Chaining
```bash
cd projects && ls       # Change directory AND list contents
mkdir test; cd test     # Create directory; then change to it
```

## Development Environment Commands

### Git (if installed)
```bash
git init                # Initialize repository
git status              # Check repository status
git add .               # Add all files to staging
git commit -m "message" # Commit changes
git log                 # View commit history
```

### Python (if installed)
```bash
python --version        # Check Python version
python script.py        # Run Python script
pip install package     # Install Python package
pip list                # List installed packages
```

### Virtual Environments
```bash
python -m venv myenv    # Create virtual environment
source myenv/bin/activate  # Activate (Linux/Mac)
myenv\Scripts\activate     # Activate (Windows)
deactivate              # Deactivate virtual environment
```

## Common Error Solutions

### "Command not found"
- Check spelling of command
- Verify the program is installed
- Check if command is in PATH

### "Permission denied"
- Use `sudo` for system commands (Linux/Mac)
- Check file permissions with `ls -l`
- Ensure you have write access to directory

### "No such file or directory"
- Check current directory with `pwd`
- Verify file path is correct
- Use `ls` to see available files

### "Directory not empty"
- Use `rm -r` to remove directories with contents
- Or remove contents first, then directory

## Best Practices

1. **Always know where you are**: Use `pwd` frequently
2. **List before you leap**: Use `ls` before operations
3. **Use tab completion**: Saves time and prevents typos
4. **Be careful with rm**: It's permanent! Use `rm -i` when unsure
5. **Use descriptive names**: Avoid spaces and special characters
6. **Practice daily**: Command line skills improve with regular use
7. **Read error messages**: They usually tell you what's wrong
8. **Use --help**: Most commands have built-in help

## Platform Differences

### Windows Command Prompt vs PowerShell vs WSL
- **Command Prompt**: `dir` instead of `ls`, `copy` instead of `cp`
- **PowerShell**: Similar to Unix commands but some differences
- **WSL**: Linux environment on Windows, uses standard Unix commands

### Recommended Setup
- **Windows**: Use WSL (Windows Subsystem for Linux) or Git Bash
- **Mac**: Terminal.app or iTerm2
- **Linux**: Default terminal emulator

---

*Remember: The command line is powerful but unforgiving. Always double-check commands that modify or delete files!*
