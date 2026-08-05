import re
import math
from collections.abc import Iterable
from collections import Counter


REDACTION_PATTERNS = (
    re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[0-9A-Za-z]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"\bglpat-[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{20,}\b"),
    re.compile(r"\b(?:sk|rk)_(?:live|test)_[0-9A-Za-z]{16,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}=*"),
    re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
    re.compile(
        r"""(?ix)
        \b(api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|secret|password|private[_-]?key|database[_-]?url|connection[_-]?string)
        \s*[:=]\s*
        (["']?)([^\s"',;}{]{8,})\2
        """
    ),
)

HIGH_ENTROPY_ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    \b(key|token|secret|credential|password|dsn|database[_-]?url|connection[_-]?string)
    \s*[:=]\s*(["']?)([A-Za-z0-9_./+=:-]{20,})\2
    """
)


def _entropy(value: str) -> float:
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


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
    redacted = HIGH_ENTROPY_ASSIGNMENT_PATTERN.sub(
        lambda match: (
            f"{match.group(1)}=[REDACTED]"
            if _entropy(match.group(3)) >= 3.5
            else match.group(0)
        ),
        redacted,
    )
    return redacted
