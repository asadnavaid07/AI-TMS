import re
from config import INAPPROPRIATE_PATTERNS

class ContentValidator:
    def __init__(self):
        self.inappropriate_patterns = INAPPROPRIATE_PATTERNS

    def is_inappropriate_content(self, description: str) -> bool:
        """Checks for inappropriate content in the description."""
        description_lower = description.lower()
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, description_lower, re.IGNORECASE):
                return True
        return False

    def is_ambiguous_description(self, description: str) -> bool:
        """Checks if the description is too vague or ambiguous."""
        description = description.strip()
        if len(description) < 10 or len(set(description.lower().replace(' ', ''))) < 3 or re.match(r'^[0-9\s\W]+$', description):
            return True
        return False