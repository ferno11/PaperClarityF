import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Clause:
    """Container for a single clause with metadata."""
    id: str
    text: str
    clause_type: str
    number: Optional[str]
    title: Optional[str]
    word_count: int
    is_complete: bool
    risk_level: str = "standard"

class DynamicClauseSplitter:
    """Dynamic clause splitter that extracts COMPLETE clauses from any document type."""
    
    def __init__(self, processed_folder: str = "docs/processed", output_folder: str = "docs/clauses"):
        self.processed_folder = Path(processed_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration for different document types."""
        return {
            "patterns": {
                # Primary pattern for numbered clauses with full content
                "numbered_full": r'(?:^|\n)\s*(\d{1,2})\.\s*([A-Z][A-Z\s&\-,()]+?)[:.]?\s*([\s\S]*?)(?=\n\s*\d{1,2}\.\s*[A-Z]|\n\s*SCHEDULE|\Z)',
                
                # Alternative for special formatting
                "numbered_multiline": r'(\d{1,2})\.\s*([A-Z][^:.\n]+)[:.]?\s*((?:[^\n]|\n(?!\d{1,2}\.))*)',
                
                # For section-based documents
                "section_based": r'(?:Section|SECTION)\s*(\d+[.]?\d*)\s*[-:]?\s*([A-Z][^.\n]+)\s*\n([\s\S]*?)(?=(?:Section|SECTION)\s*\d+|$)',
                
                # Article-based (Terms of Service)
                "article_based": r'(?:Article|ARTICLE)\s*(\d+)\s*[-:]?\s*([A-Z][^.\n]+)\s*\n([\s\S]*?)(?=(?:Article|ARTICLE)\s*\d+|$)',
            },
            
            "clause_keywords": {
                # Rental/Lease specific
                "duration": ["duration", "period", "term", "months", "lease", "commencing", "renewal"],
                "rent": ["rent", "monthly", "payment", "payable", "consideration"],
                "deposit": ["deposit", "security", "refund", "interest"],
                "maintenance": ["maintenance", "repair", "condition", "damage"],
                "termination": ["termination", "terminate", "notice", "vacate"],
                "utilities": ["electrical", "water", "bills", "charges"],
                
                # Employment specific
                "compensation": ["salary", "compensation", "wage", "payment", "remuneration"],
                "duties": ["duties", "responsibilities", "perform", "services"],
                "benefits": ["benefits", "insurance", "vacation", "sick", "leave"],
                
                # Loan specific
                "principal": ["principal", "amount", "loan", "sum"],
                "interest": ["interest", "rate", "per annum", "percentage"],
                "repayment": ["repayment", "installment", "payment", "monthly"],
                
                # General
                "liability": ["liability", "liable", "damages", "responsible"],
                "confidentiality": ["confidential", "proprietary", "disclosure"],
                "governing_law": ["governing", "law", "jurisdiction", "disputes"],
            },
            
            "risk_indicators": {
                "high": [
                    "without notice", "immediate termination", "forfeit", "penalty",
                    "non-refundable", "waive", "indemnify", "unlimited liability"
                ],
                "medium": [
                    "breach", "default", "damages", "responsible for", "at tenant's cost",
                    "deducted from deposit", "three months notice"
                ],
                "low": [
                    "lessor shall", "owner responsible", "refundable", "with notice"
                ]
            }
        }

    def extract_clauses(self, text: str, doc_name: str) -> List[Dict]:
        """Extract complete clauses from document text."""
        # Clean text
        text = self._clean_text(text)
        
        # Try different extraction patterns
        clauses = []
        
        # Method 1: Try numbered pattern first (most common)
        clauses = self._extract_numbered_clauses(text)
        
        # Method 2: If not enough clauses, try section-based
        if len(clauses) < 3:
            clauses = self._extract_section_clauses(text)
        
        # Method 3: If still not enough, try article-based
        if len(clauses) < 3:
            clauses = self._extract_article_clauses(text)
        
        # Method 4: Last resort - paragraph-based splitting
        if len(clauses) < 3:
            clauses = self._extract_paragraph_clauses(text)
        
        # Process and enrich clauses
        processed_clauses = []
        for i, clause_data in enumerate(clauses):
            clause_num, title, content = clause_data
            
            # Create full clause object
            clause_obj = self._create_clause_object(
                clause_num, title, content, doc_name, i
            )
            processed_clauses.append(clause_obj)
        
        return processed_clauses

    def _extract_numbered_clauses(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract numbered clauses with COMPLETE content."""
        clauses = []
        
        # Split by numbered patterns
        # Pattern to match: "1. TITLE: content until next number or end"
        pattern = r'(?:^|\n)\s*(\d{1,2})\.\s*([A-Z][^:.\n]*?)[:.]?\s*([^\n].*?)(?=\n\s*\d{1,2}\.\s*[A-Z]|\n\s*SCHEDULE|\Z)'
        
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            clause_num = match.group(1).strip()
            title = match.group(2).strip()
            
            # Get the full content - from this clause to the start of next clause
            start_pos = match.start(3)
            
            # Find the next clause number or end of document
            next_pattern = rf'\n\s*{int(clause_num)+1}\.\s*[A-Z]'
            next_match = re.search(next_pattern, text[start_pos:])
            
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                # Check for SCHEDULE or end of document
                schedule_match = re.search(r'\n\s*SCHEDULE', text[start_pos:])
                if schedule_match:
                    end_pos = start_pos + schedule_match.start()
                else:
                    end_pos = len(text)
            
            content = text[start_pos:end_pos].strip()
            
            if len(content) > 10:  # Ensure meaningful content
                clauses.append((clause_num, title, content))
        
        # If the pattern didn't work well, try alternative approach
        if not clauses or all(len(c[2]) < 50 for c in clauses):
            clauses = self._extract_numbered_alternative(text)
        
        return clauses

    def _extract_numbered_alternative(self, text: str) -> List[Tuple[str, str, str]]:
        """Alternative method for numbered clauses - looks for complete content."""
        clauses = []
        lines = text.split('\n')
        
        current_clause = None
        current_content = []
        
        for i, line in enumerate(lines):
            # Check if this line starts a new clause
            clause_match = re.match(r'^\s*(\d{1,2})\.\s*([A-Z][^:.\n]*?)[:.]?\s*(.*)', line)
            
            if clause_match:
                # Save previous clause if exists
                if current_clause and current_content:
                    content = ' '.join(current_content).strip()
                    if len(content) > 20:
                        clauses.append((current_clause[0], current_clause[1], content))
                
                # Start new clause
                current_clause = (clause_match.group(1), clause_match.group(2).strip())
                current_content = [clause_match.group(3).strip()] if clause_match.group(3) else []
            elif current_clause:
                # Add to current clause content
                stripped_line = line.strip()
                if stripped_line and not re.match(r'^SCHEDULE|^WITNESS|^IN WITNESS', stripped_line):
                    current_content.append(stripped_line)
        
        # Don't forget the last clause
        if current_clause and current_content:
            content = ' '.join(current_content).strip()
            if len(content) > 20:
                clauses.append((current_clause[0], current_clause[1], content))
        
        return clauses

    def _extract_section_clauses(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract section-based clauses."""
        pattern = self.config["patterns"]["section_based"]
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        
        clauses = []
        for match in matches:
            clause_num = match.group(1)
            title = match.group(2).strip()
            content = match.group(3).strip()
            
            if len(content) > 20:
                clauses.append((clause_num, title, content))
        
        return clauses

    def _extract_article_clauses(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract article-based clauses (common in ToS)."""
        pattern = self.config["patterns"]["article_based"]
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        
        clauses = []
        for match in matches:
            clause_num = match.group(1)
            title = match.group(2).strip()
            content = match.group(3).strip()
            
            if len(content) > 20:
                clauses.append((clause_num, title, content))
        
        return clauses

    def _extract_paragraph_clauses(self, text: str) -> List[Tuple[str, str, str]]:
        """Fallback: Extract clauses based on paragraphs."""
        # Split by double newlines or clear paragraph breaks
        paragraphs = re.split(r'\n\s*\n', text)
        
        clauses = []
        clause_num = 1
        
        for para in paragraphs:
            para = para.strip()
            if len(para) > 50:  # Meaningful paragraph
                # Try to extract a title from first sentence
                first_sentence = para.split('.')[0]
                if len(first_sentence) < 50:
                    title = first_sentence
                    content = para
                else:
                    title = f"Clause {clause_num}"
                    content = para
                
                clauses.append((str(clause_num), title, content))
                clause_num += 1
        
        return clauses

    def _clean_text(self, text: str) -> str:
        """Clean text for better extraction."""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Fix common OCR issues
        text = text.replace('â€œ', '"').replace('â€', '"')
        text = text.replace('â€™', "'")
        
        # Normalize numbering
        text = re.sub(r'(\d+)\s*\.\s*([A-Z])', r'\1. \2', text)
        
        return text.strip()

    def _create_clause_object(self, clause_num: str, title: str, content: str, 
                             doc_name: str, index: int) -> Dict:
        """Create a complete clause object with all metadata."""
        # Classify clause type
        clause_type = self._classify_clause(title, content)
        
        # Assess risk level
        risk_level = self._assess_risk(content)
        
        # Clean up title
        if not title or title == f"Clause {clause_num}":
            # Try to extract title from content
            first_words = content.split()[:5]
            title = ' '.join(first_words) if first_words else f"Clause {clause_num}"
        
        return {
            "clause_id": f"{doc_name}_clause_{clause_num}",
            "clause_number": clause_num,
            "clause_title": title.upper() if len(title) < 50 else title,
            "clause_type": clause_type,
            "original_text": content,
            "word_count": len(content.split()),
            "risk_level": risk_level,
            "is_complete": len(content.split()) > 20,
            "tags": self._extract_tags(content)
        }

    def _classify_clause(self, title: str, content: str) -> str:
        """Classify the clause type based on keywords."""
        text = (title + " " + content).lower()
        
        best_match = "general"
        best_score = 0
        
        for clause_type, keywords in self.config["clause_keywords"].items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_score = score
                best_match = clause_type
        
        return best_match

    def _assess_risk(self, content: str) -> str:
        """Assess risk level of clause."""
        content_lower = content.lower()
        
        # Check for high risk indicators
        high_risk_count = sum(1 for indicator in self.config["risk_indicators"]["high"] 
                            if indicator in content_lower)
        if high_risk_count >= 2:
            return "high"
        
        # Check for medium risk
        medium_risk_count = sum(1 for indicator in self.config["risk_indicators"]["medium"] 
                              if indicator in content_lower)
        if medium_risk_count >= 2 or high_risk_count >= 1:
            return "medium"
        
        # Check for low risk
        low_risk_count = sum(1 for indicator in self.config["risk_indicators"]["low"] 
                           if indicator in content_lower)
        if low_risk_count >= 1:
            return "low"
        
        return "standard"

    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from clause content."""
        tags = []
        content_lower = content.lower()
        
        # Common legal terms to tag
        tag_keywords = {
            "payment": ["payment", "pay", "amount"],
            "deadline": ["days", "months", "deadline", "within"],
            "penalty": ["penalty", "fine", "forfeit"],
            "notice": ["notice", "notify", "inform"],
            "permission": ["consent", "permission", "approval"],
            "restriction": ["shall not", "prohibited", "restricted"],
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(tag)
        
        return tags

    def save_clauses(self, clauses: List[Dict], doc_name: str, doc_type: str = "unknown"):
        """Save extracted clauses to files."""
        doc_folder = self.output_folder / doc_name
        doc_folder.mkdir(parents=True, exist_ok=True)
        
        # Create summary metadata
        metadata = {
            "document_name": doc_name,
            "document_type": doc_type,
            "total_clauses": len(clauses),
            "extraction_timestamp": str(Path().absolute()),
            "risk_summary": {
                "high": sum(1 for c in clauses if c["risk_level"] == "high"),
                "medium": sum(1 for c in clauses if c["risk_level"] == "medium"),
                "low": sum(1 for c in clauses if c["risk_level"] == "low"),
                "standard": sum(1 for c in clauses if c["risk_level"] == "standard"),
            },
            "clauses": clauses
        }
        
        # Save individual clause files
        for clause in clauses:
            clause_file = doc_folder / f"clause_{clause['clause_number']}_{clause['clause_type']}.txt"
            with open(clause_file, 'w', encoding='utf-8') as f:
                f.write(f"CLAUSE {clause['clause_number']}: {clause['clause_title']}\n")
                f.write("=" * 60 + "\n")
                f.write(f"Type: {clause['clause_type']}\n")
                f.write(f"Risk Level: {clause['risk_level']}\n")
                f.write(f"Word Count: {clause['word_count']}\n")
                f.write("-" * 60 + "\n\n")
                f.write(clause['original_text'])
        
        # Save metadata JSON
        metadata_file = doc_folder / f"{doc_name}_clauses.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✓ Saved {len(clauses)} complete clauses for {doc_name}")
        
        # Print summary
        print(f"\n📄 Document: {doc_name}")
        print(f"   Total Clauses: {len(clauses)}")
        print(f"   Risk Distribution:")
        print(f"     • High Risk: {metadata['risk_summary']['high']}")
        print(f"     • Medium Risk: {metadata['risk_summary']['medium']}")
        print(f"     • Low Risk: {metadata['risk_summary']['low']}")
        print(f"     • Standard: {metadata['risk_summary']['standard']}")
        
        return metadata

    def process_document(self, text_file: Path):
        """Process a single document."""
        doc_name = text_file.stem
        
        # Read text
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Detect document type from metadata if available
        doc_type = "unknown"
        metadata_file = text_file.parent / f"{doc_name}_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                doc_type = metadata.get("doc_type", "unknown")
        
        logger.info(f"Processing {doc_name} (type: {doc_type})")
        
        # Extract clauses
        clauses = self.extract_clauses(text, doc_name)
        
        if not clauses:
            logger.warning(f"No clauses found in {doc_name}")
            return None
        
        # Save clauses
        return self.save_clauses(clauses, doc_name, doc_type)

def main():
    """Main execution."""
    splitter = DynamicClauseSplitter()
    
    # Process all documents in processed folder
    processed_folder = Path("docs/processed")
    text_files = list(processed_folder.glob("*.txt"))
    
    if not text_files:
        print("No text files found in docs/processed")
        return
    
    print(f"Found {len(text_files)} documents to process\n")
    
    for text_file in text_files:
        if "_metadata" not in text_file.name:
            splitter.process_document(text_file)

if __name__ == "__main__":
    main()