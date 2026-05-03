import os
import re
import sys

IGNORE_DIRS = {"node_modules", "dist", "build", "__pycache__"}

heading_pattern = re.compile(r"^(#{1,6})\s*(.+)")
todo_heading_pattern = re.compile(r"^TODO\b", re.IGNORECASE)


def find_todo_lines(root_dir):
    results = {}

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in IGNORE_DIRS]

        for file in files:
            if not file.endswith(".md"):
                continue

            path = os.path.join(root, file)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    in_todo_section = False
                    todo_level = None
                    collected = []

                    for line in f:
                        # keep original line (only remove newline)
                        raw = line.rstrip("\n")
                        stripped = raw.strip()

                        heading_match = heading_pattern.match(stripped)
                        if heading_match:
                            level = len(heading_match.group(1))
                            title = heading_match.group(2)

                            if todo_heading_pattern.match(title):
                                in_todo_section = True
                                todo_level = level
                                collected.append(raw)  # keep the TODO heading itself
                            elif in_todo_section and level <= todo_level:
                                in_todo_section = False
                                todo_level = None
                            elif in_todo_section:
                                # deeper subsection --> keep it
                                collected.append(raw)

                            continue

                        if in_todo_section:
                            collected.append(raw)

                    if collected:
                        results[path] = collected

            except Exception:
                pass

    return results


def main(projectsFolderPath):
    todos_by_file = find_todo_lines(projectsFolderPath)

    for path in sorted(todos_by_file):
        print(f"=== {os.path.relpath(path, projectsFolderPath)} ===")
        for line in todos_by_file[path]:
            print(line)
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please give the patch to the folder as run parameter:")
        print(f'e.g.: python {os.path.basename(__file__)} "C:/path/to/projects"')
        sys.exit()
    folderPath = sys.argv[1]
    main(folderPath)
