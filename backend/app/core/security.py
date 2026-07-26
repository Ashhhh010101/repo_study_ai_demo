import re
from collections.abc import Iterable


REDACTION_PATTERNS = (
    re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[0-9A-Za-z]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[0-9A-Za-z_-]{20,}\b"),
    re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
    re.compile(
        r"""(?ix)
        \b(api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password)
        \s*[:=]\s*
        (["']?)([^\s"',;}{]{8,})\2
        """
    ),
)


def redact_sensitive_text(text: str, extra_values: Iterable[str] = ()) -> str:
    """Remove common credential shapes before repository content leaves the app."""
    redacted = text
    for value in extra_values:
        if value:
            redacted = redacted.replace(value, "[REDACTED]")
    for pattern in REDACTION_PATTERNS:
        if pattern.groups >= 3:
            redacted = pattern.sub(lambda match: f"{match.group(1)}=[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED]", redacted)
    return redacted
