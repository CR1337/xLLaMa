import os
import sys
from typing import List, Generator, Tuple


DEFAULT_THEME = 'default'
DEFAULT_FORMAT = 'svg'


def read_file() -> List[str]:
    with open("diagrams.md", 'r') as file:
        return file.readlines()


def parse(lines: List[str]) -> Generator[Tuple[str, str], None, None]:
    headline_counter = 0
    current_headline = ""
    inside_mermaid = False
    current_maermaid_code = ""

    for line in lines:
        if inside_mermaid:
            if line.startswith('```'):
                inside_mermaid = False
                yield (
                    f"{current_headline}_{headline_counter}",
                    current_maermaid_code
                )
                current_maermaid_code = ""
                headline_counter += 1
            else:
                current_maermaid_code += f"\n{line}"
        elif line.startswith('#'):
            current_headline = line.strip("#").strip()
            current_headline = current_headline.replace(" ", "_").lower()
            headline_counter = 0
        elif line.startswith('```mermaid'):
            inside_mermaid = True


def main():
    out_format = DEFAULT_FORMAT
    theme = DEFAULT_THEME

    for i, arg in enumerate(sys.argv):
        if arg == '-f':
            out_format = sys.argv[i + 1]
        elif arg == '-t':
            theme = sys.argv[i + 1]

    lines = read_file()
    for headline, code in parse(lines):
        print(f"Rendering {headline}")
        command = (
            f"echo '{code}' | mmdc -t {theme} -i - -e {out_format}"
            f" -o diagrams/{headline}.{out_format}"
        )
        if os.system(command) != 0:
            print(f"Rendering {headline} failed")
            print("Did you install mermaid-cli?")
            print("Install it using: npm install -g @mermaid-js/mermaid-cli")

    print("Done")


if __name__ == "__main__":
    main()
