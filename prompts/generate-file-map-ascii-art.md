## Instruction

Generate a complete ASCII art directory tree of this repository with the following requirements:

1. ALWAYS use the built-in AI tools like `list_dir`, `read_file`, and `file_search` to explore the repository structure - DO NOT use command line tools like `ls`, `find`, or any terminal commands
2. Start by using `list_dir` on the root directory, then recursively explore subdirectories using the same tool
3. RECURSIVELY explore ALL directories and subdirectories to their full depth using only the built-in tools
4. First use `read_file` on `.cursorignore` and strictly apply its exclusions
5. EXCLUDE any file or directory listed in `.cursorignore` - do not attempt to read, list, or access these files in any way
6. EXCLUDE `node_modules/` and `.git/` directories entirely
7. For each file and directory included, provide a brief but useful description as an inline comment
8. Use proper tree formatting with connecting lines (│, ├, └, etc.)
9. Verify your exclusions match `.cursorignore` contents before finalizing - don't mention the verification in the file output, just do the verification checks
10. IMPORTANT: Do NOT attempt to read or access any files or directories that are listed in `.cursorignore`. These files are intentionally excluded and should not be processed.

Save the output to `file-map.txt` in the project root.
