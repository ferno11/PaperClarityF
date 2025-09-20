import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pathlib import Path
import re
import os
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """Container for extraction results with metadata."""
    text: str
    doc_type: str
    method_used: str
    quality_score: int
    encoding_issues: int
    word_count: int
    has_structure: bool

class DynamicPDFExtractor:
    """Dynamic PDF text extraction with adaptive methods and cleaning."""
    
    def __init__(self, input_folder: str = "docs", output_folder: str = "docs/processed"):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Dynamic configuration
        self.config = self._load_config()
        self._setup_tesseract()
        
        # Statistics tracking
        self.stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'methods_used': {},
            'doc_types': {},
            'quality_distribution': []
        }

    def _load_config(self) -> Dict:
        """Load or create dynamic configuration."""
        config_file = Path("extraction_config.json")
        default_config = {
            "quality_threshold": 100,
            "min_text_length": 50,
            "tesseract_path": r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            "encoding_fixes": {
                'â€œ': '"', 'â€': '"', 'â€˜': "'", 'â€™': "'",
                'â€"': '—', 'â€"': '–', 'â€¢': '•', 'â€¦': '...',
                'â€"': '-', 'â€': '™', 'â€': '®', 'â€': '©',
                'â€': '€', 'â€': '£', 'â€': '¥',
                'BEngaluru': 'Bengaluru', 'Kamataka': 'Karnataka',
                'â€œLESSOR/OWNERâ€': '"LESSOR/OWNER"',
                'â€œLESSEES/TENANTSâ€': '"LESSEES/TENANTS"'
            },
            "document_patterns": {
                "rental": {
                    "filename_keywords": ["rental", "lease"],
                    "content_patterns": ["RENTAL AGREEMENT", "LEASE AGREEMENT", "LESSOR", "LESSEE"],
                    "structure_indicators": ["LESSOR", "LESSEE", "RENT", "DEPOSIT", "TENANT", "LANDLORD"],
                    "cleaning_patterns": [
                        r'WOODARD PROPERTIES.*?Phone:.*?Fax:.*?(?=WOODARD|SAMPLE)',
                        r'Group Initials Page \d+',
                        r'THIS RENTAL AGREEMENT IS NOT VALID UNLESS EXECUTED BY.*'
                    ]
                },
                "loan": {
                    "filename_keywords": ["loan", "credit"],
                    "content_patterns": ["LOAN AGREEMENT", "BORROWER", "LENDER"],
                    "structure_indicators": ["BORROWER", "LENDER", "INTEREST", "REPAYMENT", "PRINCIPAL"],
                    "cleaning_patterns": [r'IN WITNESS WHEREOF.*?SIGNATURES.*?$']
                },
                "tos": {
                    "filename_keywords": ["tos", "terms"],
                    "content_patterns": ["TERMS OF SERVICE", "TERMS AND CONDITIONS"],
                    "structure_indicators": ["USER", "SERVICE", "PRIVACY", "TERMS", "CONDITIONS"],
                    "cleaning_patterns": [
                        r'\[.*?\]',
                        r'This document was generated with.*?template\.'
                    ]
                },
                "nda": {
                    "filename_keywords": ["nda", "confidential"],
                    "content_patterns": ["NON-DISCLOSURE", "CONFIDENTIAL"],
                    "structure_indicators": ["CONFIDENTIAL", "DISCLOSURE", "RECEIVING PARTY", "DISCLOSING PARTY"],
                    "cleaning_patterns": []
                },
                "employment": {
                    "filename_keywords": ["employment", "job"],
                    "content_patterns": ["EMPLOYMENT AGREEMENT", "EMPLOYEE", "EMPLOYER"],
                    "structure_indicators": ["EMPLOYEE", "EMPLOYER", "COMPENSATION", "TERMINATION"],
                    "cleaning_patterns": []
                },
                "vendor": {
                    "filename_keywords": ["vendor", "supplier"],
                    "content_patterns": ["VENDOR AGREEMENT", "SUPPLIER"],
                    "structure_indicators": ["VENDOR", "SUPPLIER", "SERVICES", "PAYMENT"],
                    "cleaning_patterns": []
                },
                "insurance": {
                    "filename_keywords": ["insurance", "policy"],
                    "content_patterns": ["INSURANCE POLICY", "COVERAGE"],
                    "structure_indicators": ["POLICY", "COVERAGE", "PREMIUM", "CLAIM"],
                    "cleaning_patterns": []
                },
                "consent": {
                    "filename_keywords": ["consent", "medical"],
                    "content_patterns": ["CONSENT TO TREAT", "MEDICAL CARE"],
                    "structure_indicators": ["CONSENT", "GUARDIAN", "MEDICAL", "TREATMENT"],
                    "cleaning_patterns": []
                }
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
        
        # Save default config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config

    def _setup_tesseract(self):
        """Dynamically setup Tesseract path."""
        tesseract_paths = [
            self.config.get('tesseract_path'),
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract'
        ]
        
        for path in tesseract_paths:
            if path and Path(path).exists():
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Using Tesseract at: {path}")
                return
        
        logger.warning("Tesseract not found. OCR extraction will be disabled.")

    def detect_document_type(self, text: str, filename: str) -> str:
        """Dynamically detect document type using configuration."""
        text_upper = text.upper()
        filename_lower = filename.lower()
        
        # Score-based detection for better accuracy
        type_scores = {}
        
        for doc_type, patterns in self.config['document_patterns'].items():
            score = 0
            
            # Check filename keywords
            for keyword in patterns['filename_keywords']:
                if keyword in filename_lower:
                    score += 10
            
            # Check content patterns
            for pattern in patterns['content_patterns']:
                if pattern.upper() in text_upper:
                    score += 15
            
            # Check structure indicators
            for indicator in patterns['structure_indicators']:
                score += text_upper.count(indicator.upper()) * 2
            
            type_scores[doc_type] = score
        
        # Return type with highest score, or 'unknown' if all scores are 0
        best_type = max(type_scores, key=type_scores.get)
        return best_type if type_scores[best_type] > 0 else 'unknown'

    def clean_text_dynamic(self, text: str, doc_type: str) -> str:
        """Dynamic text cleaning based on document type and configuration."""
        if not text:
            return ""
        
        # Apply encoding fixes
        for bad, good in self.config['encoding_fixes'].items():
            text = text.replace(bad, good)
        
        # Apply document-specific cleaning patterns
        if doc_type in self.config['document_patterns']:
            patterns = self.config['document_patterns'][doc_type]['cleaning_patterns']
            for pattern in patterns:
                text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Universal cleaning patterns
        universal_patterns = [
            # Remove stamp/certificate information
            r'INDIA NON JUDICIAL.*?(?=RENTAL AGREEMENT|LOAN AGREEMENT|THIS AGREEMENT)',
            r'Government of Karnataka.*?(?=RENTAL AGREEMENT|LOAN AGREEMENT|THIS AGREEMENT)',
            r'e-stamp.*?(?=RENTAL AGREEMENT|LOAN AGREEMENT|THIS AGREEMENT)',
            r'Certificate No\..*?(?=RENTAL AGREEMENT|LOAN AGREEMENT|THIS AGREEMENT)',
            # Remove witness blocks
            r'IN WITNESS WHEREOF.*?(?:Page\s*\d+\s*of\s*\d+|$)',
            r'WITNESSES?:.*?(?:Signature|$)',
            # Remove page references
            r'Page\s*\d+\s*of\s*\d+',
            # Remove signature lines
            r'^\s*[-_]{3,}\s*$'
        ]
        
        for pattern in universal_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE | re.MULTILINE)
        
        # Clean up whitespace and random characters
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove random single characters that appear at start of lines
        text = re.sub(r'^[;:i]\s+', '', text, flags=re.MULTILINE)
        
        # Process lines intelligently
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Remove lines that are just random characters
            if re.match(r'^[;:i!\.]+$', line):
                continue
            
            # Keep important content
            if (len(line) > 2 or 
                re.match(r'^\d+[\.)]\s*$', line) or
                line.upper() in ['AND', 'OR', 'WHEREAS', 'NOW', 'THEREFORE', 'HEREBY'] or
                re.match(r'^(ARTICLE|SCHEDULE|ANNEXURE|CLAUSE|SECTION)', line.upper()) or
                re.match(r'^\d+[\.)]\s+', line)):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()

    def calculate_quality_score(self, text: str, doc_type: str) -> int:
        """Calculate text extraction quality score dynamically."""
        if not text:
            return 0
        
        base_score = len(text)
        
        # Deduct points for encoding issues
        encoding_issues = sum(text.count(bad) for bad in self.config['encoding_fixes'].keys())
        base_score -= encoding_issues * 20
        base_score -= text.count('?') * 5
        
        # Add points for document structure
        if doc_type in self.config['document_patterns']:
            indicators = self.config['document_patterns'][doc_type]['structure_indicators']
            for indicator in indicators:
                base_score += text.upper().count(indicator.upper()) * 10
        
        # Add points for proper clause numbering
        base_score += len(re.findall(r'\n\d+\.\s+[A-Z]', text)) * 15
        
        return max(0, base_score)

    def extract_text_pdfplumber(self, path: Path) -> ExtractionResult:
        """Extract text using pdfplumber with improved settings."""
        try:
            text = ""
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(
                        x_tolerance=1,
                        y_tolerance=1,
                        layout=True
                    )
                    if page_text:
                        text += page_text + "\n"
            
            doc_type = self.detect_document_type(text, path.name)
            cleaned_text = self.clean_text_dynamic(text, doc_type)
            quality_score = self.calculate_quality_score(cleaned_text, doc_type)
            
            return ExtractionResult(
                text=cleaned_text,
                doc_type=doc_type,
                method_used="PDFPlumber",
                quality_score=quality_score,
                encoding_issues=sum(cleaned_text.count(bad) for bad in self.config['encoding_fixes'].keys()),
                word_count=len(cleaned_text.split()),
                has_structure=bool(re.search(r'\n\d+\.\s+', cleaned_text))
            )
            
        except Exception as e:
            logger.error(f"PDFPlumber failed for {path.name}: {e}")
            return ExtractionResult("", "unknown", "PDFPlumber", 0, 0, 0, False)

    def extract_text_pymupdf(self, path: Path) -> ExtractionResult:
        """Extract text using PyMuPDF."""
        try:
            text = ""
            doc = fitz.open(path)
            for page in doc:
                page_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                if page_text:
                    text += page_text + "\n"
            doc.close()
            
            doc_type = self.detect_document_type(text, path.name)
            cleaned_text = self.clean_text_dynamic(text, doc_type)
            quality_score = self.calculate_quality_score(cleaned_text, doc_type)
            
            return ExtractionResult(
                text=cleaned_text,
                doc_type=doc_type,
                method_used="PyMuPDF",
                quality_score=quality_score,
                encoding_issues=sum(cleaned_text.count(bad) for bad in self.config['encoding_fixes'].keys()),
                word_count=len(cleaned_text.split()),
                has_structure=bool(re.search(r'\n\d+\.\s+', cleaned_text))
            )
            
        except Exception as e:
            logger.error(f"PyMuPDF failed for {path.name}: {e}")
            return ExtractionResult("", "unknown", "PyMuPDF", 0, 0, 0, False)

    def extract_text_ocr(self, path: Path) -> ExtractionResult:
        """Extract text using OCR for scanned documents."""
        try:
            text = ""
            doc = fitz.open(path)
            for page_num, page in enumerate(doc):
                try:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    page_text = pytesseract.image_to_string(img, config='--psm 6')
                    text += page_text + "\n"
                except Exception as page_error:
                    logger.warning(f"OCR failed for page {page_num} in {path.name}: {page_error}")
            doc.close()
            
            doc_type = self.detect_document_type(text, path.name)
            cleaned_text = self.clean_text_dynamic(text, doc_type)
            quality_score = self.calculate_quality_score(cleaned_text, doc_type)
            
            return ExtractionResult(
                text=cleaned_text,
                doc_type=doc_type,
                method_used="OCR",
                quality_score=quality_score,
                encoding_issues=sum(cleaned_text.count(bad) for bad in self.config['encoding_fixes'].keys()),
                word_count=len(cleaned_text.split()),
                has_structure=bool(re.search(r'\n\d+\.\s+', cleaned_text))
            )
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {path.name}: {e}")
            return ExtractionResult("", "unknown", "OCR", 0, 0, 0, False)

    def process_single_pdf(self, pdf_path: Path) -> Optional[ExtractionResult]:
        """Process a single PDF with dynamic method selection."""
        logger.info(f"Processing: {pdf_path.name}")
        
        # Try extraction methods in order of preference
        methods = [
            self.extract_text_pdfplumber,
            self.extract_text_pymupdf,
            self.extract_text_ocr
        ]
        
        best_result = None
        
        for method in methods:
            try:
                result = method(pdf_path)
                
                if result.quality_score >= self.config['quality_threshold']:
                    logger.info(f"  ✓ Success with {result.method_used} "
                              f"(Type: {result.doc_type}, Quality: {result.quality_score})")
                    best_result = result
                    break
                else:
                    logger.info(f"  ⚠ {result.method_used} quality too low "
                              f"({result.quality_score}), trying next method")
                    if best_result is None or result.quality_score > best_result.quality_score:
                        best_result = result
                        
            except Exception as e:
                logger.error(f"  ✗ {method.__name__} failed: {str(e)[:50]}...")
                continue
        
        return best_result

    def save_extraction_result(self, pdf_path: Path, result: ExtractionResult) -> bool:
        """Save extraction result with metadata."""
        if not result.text or len(result.text.strip()) < self.config['min_text_length']:
            logger.warning(f"Text too short for {pdf_path.name}")
            return False
        
        # Save text file
        text_file = self.output_folder / (pdf_path.stem + ".txt")
        metadata_file = self.output_folder / (pdf_path.stem + "_metadata.json")
        
        try:
            # Save text
            with open(text_file, 'w', encoding='utf-8', errors='replace') as f:
                f.write(result.text)
            
            # Save metadata
            metadata = {
                'original_file': pdf_path.name,
                'doc_type': result.doc_type,
                'method_used': result.method_used,
                'quality_score': result.quality_score,
                'word_count': result.word_count,
                'encoding_issues': result.encoding_issues,
                'has_structure': result.has_structure,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"  ✅ Saved: {text_file.name} "
                       f"({len(result.text)} chars, {result.doc_type}, Q:{result.quality_score})")
            
            # Quality warnings
            if result.encoding_issues > 0:
                logger.warning(f"     ⚠️ Contains {result.encoding_issues} encoding issues")
            if result.doc_type == 'unknown':
                logger.warning(f"     ⚠️ Could not detect document type")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save results for {pdf_path.name}: {e}")
            return False

    def update_stats(self, result: ExtractionResult, success: bool):
        """Update processing statistics."""
        if success:
            self.stats['successful'] += 1
            self.stats['methods_used'][result.method_used] = \
                self.stats['methods_used'].get(result.method_used, 0) + 1
            self.stats['doc_types'][result.doc_type] = \
                self.stats['doc_types'].get(result.doc_type, 0) + 1
            self.stats['quality_distribution'].append(result.quality_score)
        else:
            self.stats['failed'] += 1

    def process_all_pdfs(self) -> Dict:
        """Process all PDFs with comprehensive reporting."""
        pdf_files = list(self.input_folder.glob("*.pdf"))
        self.stats['total_files'] = len(pdf_files)
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        logger.info("-" * 60)
        
        for pdf_file in pdf_files:
            result = self.process_single_pdf(pdf_file)
            success = False
            
            if result:
                success = self.save_extraction_result(pdf_file, result)
            
            if not success:
                logger.error(f"  ❌ Failed to process {pdf_file.name}")
            
            self.update_stats(result if result else ExtractionResult("", "unknown", "None", 0, 0, 0, False), success)
            logger.info("")  # Empty line for readability
        
        # Generate final report
        self.generate_report()
        return self.stats

    def generate_report(self):
        """Generate processing report."""
        logger.info("=" * 60)
        logger.info("PROCESSING REPORT")
        logger.info("=" * 60)
        logger.info(f"Total files: {self.stats['total_files']}")
        logger.info(f"Successfully processed: {self.stats['successful']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Success rate: {(self.stats['successful']/self.stats['total_files']*100):.1f}%")
        
        if self.stats['methods_used']:
            logger.info("\nMethods used:")
            for method, count in self.stats['methods_used'].items():
                logger.info(f"  {method}: {count}")
        
        if self.stats['doc_types']:
            logger.info("\nDocument types detected:")
            for doc_type, count in self.stats['doc_types'].items():
                logger.info(f"  {doc_type}: {count}")
        
        if self.stats['quality_distribution']:
            avg_quality = sum(self.stats['quality_distribution']) / len(self.stats['quality_distribution'])
            logger.info(f"\nAverage quality score: {avg_quality:.0f}")
        
        # Save report to file
        report_file = self.output_folder / "extraction_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)

def main():
    """Main function to run the dynamic PDF extractor."""
    extractor = DynamicPDFExtractor()
    stats = extractor.process_all_pdfs()
    
    return stats

if __name__ == "__main__":
    main()
