import re

SPACE = re.compile(r"[ \t]+")
EXCESS_BLANKS = re.compile(r"\n{3,}")


def clean_content(content: str) -> str:
    lines = [SPACE.sub(" ", line).strip() for line in content.replace("\x00", "").splitlines()]
    cleaned = "\n".join(lines)
    return EXCESS_BLANKS.sub("\n\n", cleaned).strip()

