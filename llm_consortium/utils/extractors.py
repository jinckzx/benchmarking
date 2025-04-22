# import re
# from typing import Optional

# class ResponseExtractor:
#     @staticmethod
#     def extract_confidence(text: str) -> float:
#         try:
#             if match := re.search(r"### Confidence Score:\s*([0-9]\.[0-9]{2})", text, re.I):
#                 return float(match.group(1))
#             if match := re.search(r"\b(0?\.\d{1,2}|1\.00)\b", text):
#                 return float(match.group())
#             if match := re.search(r"(\d{1,3})%", text):
#                 return float(match.group(1)) / 100
#             return 0.0
#         except (ValueError, TypeError):
#             return 0.0

#     @staticmethod
#     def extract_answer(text: str) -> str:
#         if match := re.search(r"### Answer:\s*(.*?)(?=\n###|$)", text, re.DOTALL):
#             return match.group(1).strip()
#         return text.strip()

#     @staticmethod
#     def extract_section(text: str, start_marker: str, end_marker: Optional[str] = None) -> str:
#         try:
#             start_idx = text.index(start_marker) + len(start_marker)
#             end_idx = text.index(end_marker) if end_marker else len(text)
#             return text[start_idx:end_idx].strip()
#         except ValueError:
#             return ""
    
#     @staticmethod
#     def extract_intent(text: str) -> str:
#         """Extracts the intent from model output."""
#         if match := re.search(r"### NLQ Intent:\s*(.*?)(?=\n###|$)", text, re.DOTALL):
#             return match.group(1).strip()
#         return "Unknown"









import re
from typing import Optional

class ResponseExtractor:
    @staticmethod
    def extract_confidence(text: str) -> float:
        """Extracts confidence score from model response"""
        try:
            patterns = [
                r"### Confidence Score:\s*([0-9]\.[0-9]{2})",
                r"\b(0?\.\d{1,2}|1\.00)\b",
                r"(\d{1,3})%"
            ]
            
            for pattern in patterns:
                if match := re.search(pattern, text, re.I):
                    value = match.group(1)
                    if '%' in pattern:
                        return float(value) / 100
                    return float(value)
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    @staticmethod
    def extract_answer(text: str) -> str:
        if match := re.search(r"### Answer:\s*(.*?)(?=\n###|$)", text, re.DOTALL):
            return match.group(1).strip()
        return text.strip()

    @staticmethod
    def extract_sql(text: str) -> str:
        """Extracts SQL query from model response with multiple fallback strategies"""
        # Try structured extraction first
        if (structured := ResponseExtractor._extract_structured_sql(text)):
            return structured
            
        # Fallback to raw SQL extraction
        return ResponseExtractor._extract_raw_sql(text) or "No SQL detected"

    @staticmethod
    def _extract_structured_sql(text: str) -> Optional[str]:
        """Extracts SQL from structured response sections"""
        section_patterns = [
            r"### Answer:\s*(.*?)(?=\n###|$)",
            r"```sql(.*?)```",
            r"SQL QUERY:\s*(.*?);"
        ]
        
        for pattern in section_patterns:
            if match := re.search(pattern, text, re.DOTALL | re.IGNORECASE):
                content = match.group(1).strip()
                if sql := ResponseExtractor._extract_raw_sql(content):
                    return sql
        return None

    @staticmethod
    def _extract_raw_sql(text: str) -> Optional[str]:
        """Extracts raw SQL from unstructured text"""
        if (match := re.search(
            r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP).*?;",
            text,
            re.DOTALL | re.IGNORECASE
        )):
            return match.group().strip()
        return None

    @staticmethod
    def extract_intent(text: str) -> str:
        """Extracts the intent from model output"""
        if match := re.search(r"### NLQ Intent:\s*(.*?)(?=\n###|$)", text, re.DOTALL):
            return match.group(1).strip()
        return "Unknown"

    @staticmethod
    def extract_section(text: str, start_marker: str, end_marker: Optional[str] = None) -> str:
        """Extract text section between markers"""
        if start_marker not in text:
            return ""
            
        parts = text.split(start_marker, 1)
        if len(parts) < 2:
            return ""
            
        section = parts[1].strip()
        
        if end_marker and end_marker in section:
            section = section.split(end_marker, 1)[0].strip()
            
        return section
    @staticmethod
    def extract_class( text: str) -> str:
        """Extract the final class label from the response"""
        # Try to find with specific formatting
        pattern = r"Final\s+Class\s*[:|=]?\s*([A-Za-z0-9_\-\s]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # Try to find class with alternate format
        pattern = r"Class\s*[:|=]?\s*([A-Za-z0-9_\-\s]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # Try to find classification with alternate format
        pattern = r"Classification\s*[:|=]?\s*([A-Za-z0-9_\-\s]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # If no specific format found, look for any class-like pattern
        pattern = r"(?:predicted|final|chosen|selected|best)\s+class\s*[:|=]?\s*([A-Za-z0-9_\-\s]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # Fallback: return "UNKNOWN"
        return "UNKNOWN"
    

    @staticmethod
    def extract_reasoning(text: str) -> str:
        """Extract reasoning section from classification response"""
        # Try multiple possible section headers for reasoning
        for header in ["Reasoning:", "### Reasoning:", "Rationale:", "Explanation:", "Analysis:"]:
            reasoning = ResponseExtractor.extract_section(text, header)
            if reasoning:
                return reasoning
        
        # If no specific section found, look for any reasoning-like paragraph
        pattern = r"(?:reasoning|rationale|explanation)[:\s]+([^\n]+(?:\n[^\n]+)*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""