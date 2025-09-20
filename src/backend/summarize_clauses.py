import os
import json
import time
import re
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level enumeration for type safety."""
    LOW = "Low"
    MEDIUM = "Medium"  
    HIGH = "High"
    
    @classmethod
    def get_priority(cls, risk_level) -> int:
        """Get numeric priority for comparison (higher = more risk)."""
        priorities = {cls.LOW: 1, cls.MEDIUM: 2, cls.HIGH: 3}
        return priorities.get(risk_level, 1)


@dataclass
class ClauseSummary:
    """Standardized data structure for clause summaries."""
    original_text: str
    plain_english: str
    user_impact: str
    risk_level: RiskLevel
    risk_reason: str
    clause_heading: Optional[str] = None
    word_count: int = 0
    contains_numbers: bool = False
    contains_dates: bool = False
    contains_financial: bool = False
    clause_type: Optional[str] = None
    key_entities: List[str] = None
    confidence_score: float = 1.0
    completeness_score: float = 1.0
    numeric_obligations: List[str] = None
    conditional_language: List[str] = None
    
    def __post_init__(self):
        if self.key_entities is None:
            self.key_entities = []
        if self.numeric_obligations is None:
            self.numeric_obligations = []
        if self.conditional_language is None:
            self.conditional_language = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enum handling."""
        result = asdict(self)
        result['risk_level'] = self.risk_level.value
        return result


class TextCleaner:
    """Enhanced text cleaning and preprocessing."""
    
    # Refined boilerplate patterns - more precise to avoid removing important clauses
    BOILERPLATE_PATTERNS = [
        r'^page\s+\d+\s+of\s+\d+\s*$',
        r'^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\s*$',
        r'^[A-Z\s]+\s+\d{4}\s*$',
        r'^\s*[\-_=]{5,}\s*$',  # Increased threshold
        r'^\s*\[signature\]?\s*$',
        r'^\s*confidential\s*$',
        r'^\s*draft\s*$',
        r'^\s*exhibit\s+[a-zA-Z0-9]\s*:?\s*$',
        r'^\s*appendix\s+[a-zA-Z0-9]\s*:?\s*$',
    ]
    
    # Enhanced jargon replacements
    JARGON_REPLACEMENTS = {
        'liable': 'responsible',
        'liability': 'responsibility', 
        'breach': 'break',
        'terminate': 'end',
        'pursuant to': 'according to',
        'lessee': 'tenant',
        'lessor': 'landlord',
        'covenant': 'promise',
        'indemnify': 'protect from costs',
        'arbitration': 'private dispute resolution',
        'whereas': 'since',
        'thereof': 'of it',
        'herein': 'in this document',
        'notwithstanding': 'despite',
        'forthwith': 'immediately',
        'stipulate': 'agree',
        'constitute': 'make up',
        'deemed': 'considered',
        'execute': 'sign',
        'supersede': 'replace',
        'void': 'cancelled',
        'null and void': 'completely cancelled',
        'in lieu of': 'instead of',
        'pro rata': 'proportional',
        'force majeure': 'uncontrollable events',
    }
    
    # Legal clause type patterns
    CLAUSE_TYPE_PATTERNS = {
        'payment': r'(pay|payment|rent|fee|charge|cost|price|amount|due|owing)',
        'termination': r'(terminate|end|cancel|expire|dissolution|breach)',
        'liability': r'(liable|liability|responsible|damages|loss|harm|injury)',
        'property': r'(property|premises|real estate|land|building|unit)',
        'duration': r'(term|duration|period|month|year|day|time)',
        'obligations': r'(shall|must|required|obligation|duty|responsibility)',
        'rights': r'(right|entitle|may|permit|allow)',
        'restrictions': r'(not|cannot|shall not|prohibited|forbidden|restrict)',
        'default': r'(default|fail|breach|violation|non-compliance)',
        'remedies': r'(remedy|cure|notice|evict|sue|legal action)',
        'insurance': r'(insurance|insure|coverage|policy|claim)',
        'maintenance': r'(maintain|repair|upkeep|condition|care)',
        'confidentiality': r'(confidential|secret|proprietary|non-disclosure)',
    }
    
    # Numeric obligation patterns
    NUMERIC_PATTERNS = {
        'percentage': r'\b\d+(?:\.\d+)?%',
        'money': r'\$[\d,]+(?:\.\d{2})?',
        'days': r'\b\d+\s*days?\b',
        'months': r'\b\d+\s*months?\b',
        'years': r'\b\d+\s*years?\b',
        'hours': r'\b\d+\s*hours?\b',
        'late_fee': r'\b(?:late\s+fee|penalty)\s+of\s+[\$\d%]+',
        'interest_rate': r'\b\d+(?:\.\d+)?%\s*(?:interest|rate)',
    }
    
    # Conditional language patterns
    CONDITIONAL_PATTERNS = [
        r'\bunless\b', r'\bsubject to\b', r'\bif\b', r'\bthen\b', 
        r'\bprovided that\b', r'\bin the event\b', r'\bwhen\b',
        r'\bshould\b', r'\bmay\b', r'\bcondition\b'
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                for pattern in self.BOILERPLATE_PATTERNS]
        self.clause_type_compiled = {
            clause_type: re.compile(pattern, re.IGNORECASE)
            for clause_type, pattern in self.CLAUSE_TYPE_PATTERNS.items()
        }
        self.numeric_compiled = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.NUMERIC_PATTERNS.items()
        }
        self.conditional_compiled = [re.compile(pattern, re.IGNORECASE) 
                                   for pattern in self.CONDITIONAL_PATTERNS]
    
    def is_boilerplate(self, text: str) -> bool:
        """Enhanced boilerplate detection with protection for numeric clauses."""
        text_clean = text.strip().lower()
        
        # Never remove text with important legal or numeric content
        important_indicators = [
            r'\$\d', r'\d+%', r'\d+\s*days?', r'\d+\s*months?',
            r'shall', r'must', r'liable', r'penalty', r'fee',
            r'terminate', r'breach', r'default'
        ]
        
        for indicator in important_indicators:
            if re.search(indicator, text_clean):
                return False
        
        # Check against boilerplate patterns
        for pattern in self.compiled_patterns:
            if pattern.match(text_clean):
                return True
        
        # Filter very short lines without legal significance
        words = text_clean.split()
        if len(words) < 3:
            return True
            
        # Filter lines that are mostly symbols/numbers (but not financial)
        alpha_ratio = len(re.sub(r'[^a-zA-Z\s]', '', text_clean)) / max(len(text_clean), 1)
        if alpha_ratio < 0.2 and not re.search(r'\$|\d+%', text_clean):
            return True
        
        return False
    
    def clean_text(self, text: str) -> str:
        """Enhanced text cleaning with better preservation of important clauses."""
        lines = text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not self.is_boilerplate(line):
                line = re.sub(r'\s+', ' ', line)
                line = re.sub(r'\.{3,}', '...', line)
                cleaned_lines.append(line)
        
        # Improved merging with protection for numbered items and financial terms
        merged_lines = []
        i = 0
        while i < len(cleaned_lines):
            current = cleaned_lines[i]
            
            # Don't merge if current line has financial/numeric content or is numbered
            has_numbers = re.search(r'\$|\d+%|\d+\s*(?:days?|months?)', current)
            is_numbered = re.match(r'^\d+\.', current)
            ends_properly = current.endswith(('.', ':', ')', ';', '!', '?'))
            
            should_merge = (
                not has_numbers and
                not is_numbered and
                len(current.split()) < 10 and
                not ends_properly and
                not current.isupper() and
                i + 1 < len(cleaned_lines) and
                not cleaned_lines[i + 1].isupper()
            )
            
            if should_merge:
                merged = current + ' ' + cleaned_lines[i + 1]
                merged_lines.append(merged)
                i += 2
            else:
                merged_lines.append(current)
                i += 1
        
        return '\n'.join(merged_lines)
    
    def extract_clause_heading(self, text: str) -> Optional[str]:
        """Extract clause heading with better pattern matching."""
        lines = text.strip().split('\n')
        if not lines:
            return None
        
        first_line = lines[0].strip()
        
        heading_patterns = [
            r'^\d+\.?\s*[-:]?\s*[A-Z]',
            r'^Section\s+\d+',
            r'^Article\s+[IVX\d]+',
            r'^\([a-zA-Z0-9]+\)',
            r'^\w\.\s+[A-Z]',
            r'^\d+\.\d+\s+[A-Z]',
        ]
        
        for pattern in heading_patterns:
            if re.match(pattern, first_line, re.IGNORECASE):
                return first_line
        
        if (len(first_line) < 80 and first_line.isupper() and len(first_line.split()) <= 8):
            return first_line
            
        return None
    
    def identify_clause_type(self, text: str) -> Optional[str]:
        """Identify clause type with weighted scoring."""
        text_lower = text.lower()
        scores = {}
        
        for clause_type, pattern in self.clause_type_compiled.items():
            matches = len(pattern.findall(text_lower))
            if matches > 0:
                scores[clause_type] = matches
        
        return max(scores.items(), key=lambda x: x[1])[0] if scores else None
    
    def extract_numeric_obligations(self, text: str) -> List[str]:
        """Extract numeric obligations and requirements."""
        obligations = []
        
        for name, pattern in self.numeric_compiled.items():
            matches = pattern.findall(text)
            for match in matches:
                obligations.append(f"{name}: {match}")
        
        return obligations
    
    def extract_conditional_language(self, text: str) -> List[str]:
        """Extract conditional language that affects obligations."""
        conditionals = []
        
        for pattern in self.conditional_compiled:
            matches = pattern.findall(text)
            conditionals.extend(matches)
        
        return list(set(conditionals))
    
    def extract_key_entities(self, text: str) -> List[str]:
        """Extract key entities with improved patterns."""
        entities = []
        
        # Enhanced patterns
        patterns = {
            'money': r'\$[\d,]+(?:\.\d{2})?',
            'percentage': r'\d+(?:\.\d+)?%',
            'timeframe': r'\b\d+\s*(?:days?|weeks?|months?|years?|hours?)\b',
            'dates': r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
            'late_fees': r'late\s+fee\s+of\s+[\$\d%]+',
            'penalties': r'penalty\s+of\s+[\$\d%]+',
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(f"{entity_type}: {match}")
        
        return entities
    
    def simplify_language(self, text: str) -> str:
        """Enhanced jargon replacement with context preservation."""
        result = text
        for jargon, simple in self.JARGON_REPLACEMENTS.items():
            pattern = re.compile(r'\b' + re.escape(jargon) + r'\b', re.IGNORECASE)
            def replace_func(match):
                original = match.group(0)
                if original.isupper():
                    return simple.upper()
                elif original.istitle():
                    return simple.title()
                else:
                    return simple
            result = pattern.sub(replace_func, result)
        
        return result


class SmartRiskAssessment:
    """Enhanced risk assessment with numeric obligation awareness."""
    
    # Weighted risk keywords with severity scores
    RISK_KEYWORDS = {
        RiskLevel.HIGH: {
            'penalty': 10, 'termination': 9, 'liability': 8, 'damages': 8,
            'indemnify': 8, 'default': 7, 'breach': 7, 'forfeit': 9,
            'sue': 9, 'lawsuit': 10, 'eviction': 10, 'foreclosure': 10,
            'non-refundable': 7, 'liquidated damages': 9, 'attorney fees': 8,
            'personal guarantee': 8, 'immediate termination': 10,
            'without notice': 8, 'collection agency': 8, 'credit report': 7,
        },
        RiskLevel.MEDIUM: {
            'notice': 4, 'maintenance': 3, 'interest': 5, 'dispute': 5,
            'arbitration': 5, 'modify': 4, 'amendment': 4, 'inspection': 4,
            'compliance': 5, 'audit': 5, 'confidential': 4, 'assignment': 5,
            'renewal': 4, 'late fee': 6, 'deposit': 3, 'insurance required': 5,
            'background check': 4, 'security deposit': 4, 'approval required': 5,
        },
        RiskLevel.LOW: {
            'signature': 1, 'effective date': 1, 'definitions': 1, 'contact': 1,
            'address': 1, 'business hours': 1, 'acknowledgment': 1,
            'governing law': 2, 'entire agreement': 2, 'severability': 2,
        }
    }
    
    # Numeric risk thresholds
    NUMERIC_RISK_THRESHOLDS = {
        'percentage': [(10, RiskLevel.HIGH), (5, RiskLevel.MEDIUM)],
        'days': [(30, RiskLevel.HIGH), (7, RiskLevel.MEDIUM)],
        'money': [(1000, RiskLevel.HIGH), (100, RiskLevel.MEDIUM)],
    }
    
    def assess_risk(self, text: str, numeric_obligations: List[str], 
                   conditional_language: List[str], ai_risk: Optional[RiskLevel] = None) -> Tuple[RiskLevel, str, float]:
        """Enhanced risk assessment with numeric and conditional analysis."""
        text_lower = text.lower()
        risk_score = 0
        risk_factors = []
        
        # Keyword-based risk scoring
        for risk_level, keywords in self.RISK_KEYWORDS.items():
            for keyword, weight in keywords.items():
                if keyword in text_lower:
                    risk_score += weight
                    risk_factors.append(f"{keyword}({weight})")
        
        # Numeric obligation risk assessment
        numeric_risk = self._assess_numeric_risk(numeric_obligations)
        if numeric_risk:
            level, reason = numeric_risk
            additional_score = RiskLevel.get_priority(level) * 3
            risk_score += additional_score
            risk_factors.append(f"numeric:{reason}({additional_score})")
        
        # Conditional language risk
        if conditional_language:
            conditional_score = len(conditional_language) * 2
            risk_score += conditional_score
            risk_factors.append(f"conditionals:{len(conditional_language)}({conditional_score})")
        
        # Determine base risk level
        if risk_score >= 20:
            base_risk = RiskLevel.HIGH
        elif risk_score >= 10:
            base_risk = RiskLevel.MEDIUM
        else:
            base_risk = RiskLevel.LOW
        
        # Consider AI assessment
        final_risk = base_risk
        if ai_risk and RiskLevel.get_priority(ai_risk) > RiskLevel.get_priority(base_risk):
            final_risk = ai_risk
            risk_factors.append(f"ai_override:{ai_risk.value}")
        
        # Generate comprehensive reason
        reason = f"Score: {risk_score}. Factors: {', '.join(risk_factors[:5])}"
        confidence = min(risk_score / 25.0, 1.0)
        
        return final_risk, reason, confidence
    
    def _assess_numeric_risk(self, numeric_obligations: List[str]) -> Optional[Tuple[RiskLevel, str]]:
        """Assess risk based on numeric obligations."""
        highest_risk = None
        reasons = []
        
        for obligation in numeric_obligations:
            if ':' not in obligation:
                continue
                
            obligation_type, value = obligation.split(':', 1)
            obligation_type = obligation_type.strip()
            value = value.strip()
            
            # Extract numeric value
            numeric_match = re.search(r'(\d+(?:\.\d+)?)', value)
            if not numeric_match:
                continue
                
            numeric_value = float(numeric_match.group(1))
            
            # Check against thresholds
            if obligation_type in self.NUMERIC_RISK_THRESHOLDS:
                for threshold, risk_level in self.NUMERIC_RISK_THRESHOLDS[obligation_type]:
                    if numeric_value >= threshold:
                        if not highest_risk or RiskLevel.get_priority(risk_level) > RiskLevel.get_priority(highest_risk[0]):
                            highest_risk = (risk_level, f"{obligation_type}:{numeric_value}")
                        reasons.append(f"{obligation_type}:{numeric_value}")
                        break
        
        return highest_risk


class GeminiSummarizer:
    """Enhanced Gemini API integration with improved prompts."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=400,
            temperature=0.1,
        )
    
    def create_prompt(self, clause_text: str, clause_type: Optional[str] = None, 
                     key_entities: List[str] = None, numeric_obligations: List[str] = None) -> str:
        """Enhanced prompt with focus on actionable guidance and numbers."""
        
        context = f"Clause type: {clause_type}" if clause_type else "General legal clause"
        entities = f"Key numbers/dates: {', '.join(key_entities[:3])}" if key_entities else ""
        obligations = f"Numeric requirements: {', '.join(numeric_obligations[:3])}" if numeric_obligations else ""
        
        return f"""You are a legal expert explaining a contract clause to help someone understand their obligations and risks.

CONTEXT: {context}
NUMBERS FOUND: {entities}
REQUIREMENTS: {obligations}

INSTRUCTIONS:
1. PLAIN ENGLISH: Write exactly 1-2 clear sentences using simple words
2. HIGHLIGHT NUMBERS: Include ALL specific amounts, percentages, deadlines, and timeframes
3. USER IMPACT: Explain what the person must do or what could happen to them
4. ACTIONABLE GUIDANCE: Tell them what to watch out for or what action to take
5. RISK LEVEL: High (serious consequences), Medium (moderate impact), or Low (minor impact)

EXAMPLES:
- "You must pay rent by the 5th of each month or face a $50 late fee and possible eviction after 10 days."
- "If you break this agreement, you'll pay 15% interest on any money owed plus attorney fees."
- "You have 30 days to report any problems, or you lose the right to complain later."

Legal Clause: "{clause_text}"

Respond ONLY with this JSON format:
{{
  "plain_english": "[1-2 sentences with ALL numbers/dates included]",
  "user_impact": "[What this means for the person - action required or consequence]", 
  "risk": "High/Medium/Low",
  "reasoning": "[Why this risk level - be specific]",
  "confidence": 0.9
}}

CRITICAL: Include every important number, date, percentage, or deadline from the original clause."""
    
    def call_api(self, prompt: str, max_retries: int = 3) -> Optional[Dict]:
        """API call with exponential backoff and better error handling."""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                
                if response.candidates and response.candidates[0].content:
                    text = response.candidates[0].content.parts[0].text.strip()
                    parsed = self._parse_json_response(text)
                    if parsed:
                        return parsed
                    else:
                        logger.warning(f"Failed to parse response on attempt {attempt + 1}")
                        
            except Exception as e:
                logger.error(f"API error (attempt {attempt + 1}): {e}")
                if "quota" in str(e).lower() or "limit" in str(e).lower():
                    logger.error("API quota exceeded. Consider using --mock mode.")
                    return None
                
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Enhanced JSON parsing with better error handling."""
        try:
            cleaned = response.strip()
            
            # Remove markdown formatting
            for marker in ['```json', '```', '`']:
                cleaned = cleaned.replace(marker, '')
            
            # Extract JSON object
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            
            if start == -1 or end <= start:
                return None
            
            json_str = cleaned[start:end]
            parsed = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['plain_english', 'user_impact', 'risk']
            if not all(field in parsed for field in required_fields):
                return None
            
            # Validate and normalize risk level
            risk_mapping = {
                'high': 'High', 'medium': 'Medium', 'low': 'Low',
                'High': 'High', 'Medium': 'Medium', 'Low': 'Low'
            }
            
            parsed['risk'] = risk_mapping.get(parsed['risk'], 'Medium')
            
            return parsed
                    
        except json.JSONDecodeError:
            return None


class AccuracyMetrics:
    """Enhanced accuracy metrics with confidence scoring."""
    
    @staticmethod
    def calculate_completeness_score(original: str, summary: str, key_entities: List[str]) -> float:
        """Calculate completeness based on entity preservation and length."""
        if not key_entities:
            # Base completeness on summary comprehensiveness
            words_original = len(original.split())
            words_summary = len(summary.split())
            return min(1.0, words_summary / max(words_original * 0.1, 5))
        
        entities_preserved = sum(1 for entity in key_entities 
                               if any(part in summary.lower() for part in entity.lower().split(':')[-1].split()))
        return min(1.0, entities_preserved / len(key_entities))
    
    @staticmethod
    def calculate_chunk_confidence(summaries: List[Dict]) -> float:
        """Calculate average confidence across chunks."""
        if not summaries:
            return 0.5
        
        confidences = [s.get('confidence', 0.8) for s in summaries]
        return sum(confidences) / len(confidences)


class LegalClauseSummarizer:
    """Enhanced main class with improved multi-chunk handling."""
    
    def __init__(self, api_key: Optional[str] = None, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.text_cleaner = TextCleaner()
        self.risk_assessor = SmartRiskAssessment()
        self.accuracy_metrics = AccuracyMetrics()
        
        if not mock_mode:
            if not api_key:
                raise ValueError("API key required when not in mock mode")
            self.gemini = GeminiSummarizer(api_key)
        else:
            self.gemini = None
            logger.info("Running in mock mode - no API calls will be made")
    
    def _chunk_text(self, text: str, max_words: int = 200) -> List[str]:
        """Improved chunking with better context preservation."""
        words = text.split()
        
        if len(words) <= max_words:
            return [text]
        
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        current_words = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            if current_words + sentence_words <= max_words:
                current_chunk += sentence + " "
                current_words += sentence_words
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If single sentence is too long, split it
                if sentence_words > max_words:
                    sentence_parts = sentence.split(',')
                    temp_chunk = ""
                    for part in sentence_parts:
                        if len((temp_chunk + part).split()) <= max_words:
                            temp_chunk += part + ","
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.rstrip(',').strip())
                            temp_chunk = part + ","
                    current_chunk = temp_chunk.rstrip(',').strip() + " "
                else:
                    current_chunk = sentence + " "
                
                current_words = len(current_chunk.split())
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _create_mock_summary(self, text: str, filename: str = "") -> ClauseSummary:
        """Enhanced mock summary with all new features."""
        numeric_obligations = self.text_cleaner.extract_numeric_obligations(text)
        conditional_language = self.text_cleaner.extract_conditional_language(text)
        
        risk_level, risk_reason, risk_score = self.risk_assessor.assess_risk(
            text, numeric_obligations, conditional_language
        )
        
        heading = self.text_cleaner.extract_clause_heading(text)
        clause_type = self.text_cleaner.identify_clause_type(text)
        key_entities = self.text_cleaner.extract_key_entities(text)
        
        word_count = len(text.split())
        contains_numbers = bool(re.search(r'\d', text))
        contains_dates = bool(re.search(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b', text))
        contains_financial = bool(re.search(r'\$|dollars?|cents?|payment|fee|cost', text, re.IGNORECASE))
        
        # Create more realistic mock summaries
        entity_text = ", ".join([e.split(':')[-1] for e in key_entities[:2]]) if key_entities else "specific requirements"
        plain_english = f"This {clause_type or 'clause'} requires compliance with {entity_text}."
        user_impact = f"You must follow these {risk_level.value.lower()}-risk requirements or face consequences."
        
        completeness_score = self.accuracy_metrics.calculate_completeness_score(text, plain_english, key_entities)
        
        return ClauseSummary(
            original_text=text,
            plain_english=plain_english,
            user_impact=user_impact,
            risk_level=risk_level,
            risk_reason=risk_reason,
            clause_heading=heading,
            word_count=word_count,
            contains_numbers=contains_numbers,
            contains_dates=contains_dates,
            contains_financial=contains_financial,
            clause_type=clause_type,
            key_entities=key_entities,
            confidence_score=0.8,
            completeness_score=completeness_score,
            numeric_obligations=numeric_obligations,
            conditional_language=conditional_language
        )
    
    def summarize_clause(self, text: str, filename: str = "") -> Optional[ClauseSummary]:
        """Enhanced clause summarization with improved handling."""
        # Clean and validate text
        cleaned_text = self.text_cleaner.clean_text(text)
        
        if len(cleaned_text.strip()) < 10:
            logger.warning(f"Clause too short after cleaning: {filename}")
            return None
        
        # Extract enhanced metadata
        heading = self.text_cleaner.extract_clause_heading(cleaned_text)
        clause_type = self.text_cleaner.identify_clause_type(cleaned_text)
        key_entities = self.text_cleaner.extract_key_entities(cleaned_text)
        numeric_obligations = self.text_cleaner.extract_numeric_obligations(cleaned_text)
        conditional_language = self.text_cleaner.extract_conditional_language(cleaned_text)
        
        word_count = len(cleaned_text.split())
        contains_numbers = bool(re.search(r'\d', cleaned_text))
        contains_dates = bool(re.search(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b', cleaned_text))
        contains_financial = bool(re.search(r'\$|dollars?|cents?|payment|fee|cost', cleaned_text, re.IGNORECASE))
        
        # Mock mode
        if self.mock_mode:
            return self._create_mock_summary(cleaned_text, filename)
        
        # Real API processing
        if word_count <= 200:
            # Process directly
            summary_data = self._process_chunk(cleaned_text, clause_type, key_entities, numeric_obligations)
        else:
            # Multi-chunk processing with improved combination
            chunks = self._chunk_text(cleaned_text)
            logger.info(f"Processing {len(chunks)} chunks for {filename}")
            
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                chunk_entities = self.text_cleaner.extract_key_entities(chunk)
                chunk_obligations = self.text_cleaner.extract_numeric_obligations(chunk)
                
                result = self._process_chunk(chunk, clause_type, chunk_entities, chunk_obligations)
                if result:
                    chunk_summaries.append(result)
                time.sleep(0.5)
            
            summary_data = self._combine_chunks(chunk_summaries, cleaned_text, key_entities, numeric_obligations)
        
        if not summary_data:
            logger.error(f"Failed to generate summary for {filename}")
            return None
        
        # Enhanced risk assessment with all factors
        ai_risk = RiskLevel(summary_data.get('risk', 'Medium'))
        final_risk, risk_reason, risk_confidence = self.risk_assessor.assess_risk(
            cleaned_text, numeric_obligations, conditional_language, ai_risk
        )
        
        # Calculate accuracy metrics
        completeness_score = self.accuracy_metrics.calculate_completeness_score(
            cleaned_text, summary_data['plain_english'], key_entities
        )
        
        return ClauseSummary(
            original_text=cleaned_text,
            plain_english=self.text_cleaner.simplify_language(summary_data['plain_english']),
            user_impact=summary_data['user_impact'],
            risk_level=final_risk,
            risk_reason=risk_reason,
            clause_heading=heading,
            word_count=word_count,
            contains_numbers=contains_numbers,
            contains_dates=contains_dates,
            contains_financial=contains_financial,
            clause_type=clause_type,
            key_entities=key_entities,
            confidence_score=summary_data.get('confidence', 0.8),
            completeness_score=completeness_score,
            numeric_obligations=numeric_obligations,
            conditional_language=conditional_language
        )
    
    def _process_chunk(self, text: str, clause_type: Optional[str] = None, 
                      key_entities: List[str] = None, numeric_obligations: List[str] = None) -> Optional[Dict]:
        """Process a single chunk with enhanced context."""
        prompt = self.gemini.create_prompt(text, clause_type, key_entities, numeric_obligations)
        return self.gemini.call_api(prompt)
    
    def _combine_chunks(self, chunk_summaries: List[Dict], original_text: str, 
                       key_entities: List[str], numeric_obligations: List[str]) -> Optional[Dict]:
        """Intelligently combine chunks with improved logic."""
        if not chunk_summaries:
            return None
        
        if len(chunk_summaries) == 1:
            return chunk_summaries[0]
        
        # Smart combination of plain English summaries
        combined_sentences = []
        seen_concepts = set()
        
        for summary in chunk_summaries:
            text = summary['plain_english'].strip()
            
            # Remove redundant introductory phrases
            redundant_starts = ['This means', 'This clause', 'This section', 'The clause']
            for start in redundant_starts:
                if text.startswith(start) and combined_sentences:
                    # Keep the substantive part
                    remaining = text[len(start):].strip()
                    if remaining.startswith('that'):
                        remaining = remaining[4:].strip()
                    text = remaining
                    break
            
            # Avoid repeating similar concepts
            text_lower = text.lower()
            is_duplicate = any(concept in text_lower for concept in seen_concepts)
            
            if not is_duplicate and text:
                combined_sentences.append(text)
                # Track key concepts to avoid duplication
                important_words = re.findall(r'\b(?:\d+%?|\$\d+|payment|fee|penalty|days?|months?)\b', text_lower)
                seen_concepts.update(important_words)
        
        # Combine with proper sentence flow
        if len(combined_sentences) == 1:
            combined_plain = combined_sentences[0]
        elif len(combined_sentences) == 2:
            combined_plain = f"{combined_sentences[0]} Additionally, {combined_sentences[1].lower()}"
        else:
            first_sentence = combined_sentences[0]
            other_sentences = [s.lower() for s in combined_sentences[1:]]
            combined_plain = f"{first_sentence} Also, {' and '.join(other_sentences)}"
        
        # Combine user impacts - prioritize most specific/detailed
        impacts = [s['user_impact'] for s in chunk_summaries]
        
        # Find impact with most specific details (numbers, actions)
        def impact_specificity(impact):
            numbers = len(re.findall(r'\d+', impact))
            actions = len(re.findall(r'\b(?:must|will|pay|face|lose|required|charged)\b', impact.lower()))
            return numbers * 2 + actions
        
        combined_impact = max(impacts, key=impact_specificity)
        
        # Take highest risk level using priority system
        risks = [s['risk'] for s in chunk_summaries]
        risk_levels = [RiskLevel(risk) for risk in risks]
        final_risk = max(risk_levels, key=RiskLevel.get_priority)
        
        # Calculate weighted confidence
        chunk_confidence = self.accuracy_metrics.calculate_chunk_confidence(chunk_summaries)
        
        # Ensure all important numeric obligations are preserved
        all_numbers = []
        for summary in chunk_summaries:
            numbers_in_text = re.findall(r'\b(?:\d+%?|\$[\d,]+(?:\.\d{2})?|\d+\s*(?:days?|months?|years?))\b', 
                                       summary['plain_english'])
            all_numbers.extend(numbers_in_text)
        
        # Verify important numbers are in final summary
        missing_numbers = [num for num in all_numbers if num not in combined_plain]
        if missing_numbers:
            # Add missing important numbers
            number_text = ", ".join(missing_numbers[:2])
            combined_plain += f" Key amounts: {number_text}."
        
        return {
            'plain_english': combined_plain,
            'user_impact': combined_impact,
            'risk': final_risk.value,
            'confidence': chunk_confidence,
            'reasoning': f'Combined from {len(chunk_summaries)} sections'
        }
    
    def process_directory(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """Enhanced directory processing with improved metrics."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        clause_files = list(input_path.glob("**/*.txt"))
        
        if not clause_files:
            logger.error(f"No .txt files found in {input_dir}")
            return {"error": "No files found"}
        
        logger.info(f"Processing {len(clause_files)} clause files")
        
        results = []
        stats = {
            'total': len(clause_files),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'risk_distribution': {'High': 0, 'Medium': 0, 'Low': 0},
            'clause_types': {},
            'numeric_obligations_found': 0,
            'conditional_clauses': 0,
            'accuracy_metrics': {}
        }
        
        all_summaries = []
        
        for clause_file in clause_files:
            try:
                logger.info(f"Processing: {clause_file.name}")
                
                with open(clause_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Enhanced boilerplate detection
                if self.text_cleaner.is_boilerplate(content) and len(content.split()) < 15:
                    logger.info(f"Skipping boilerplate: {clause_file.name}")
                    stats['skipped'] += 1
                    continue
                
                # Generate summary
                summary = self.summarize_clause(content, clause_file.name)
                
                if summary:
                    stats['successful'] += 1
                    stats['risk_distribution'][summary.risk_level.value] += 1
                    
                    if summary.clause_type:
                        stats['clause_types'][summary.clause_type] = stats['clause_types'].get(summary.clause_type, 0) + 1
                    
                    if summary.numeric_obligations:
                        stats['numeric_obligations_found'] += len(summary.numeric_obligations)
                    
                    if summary.conditional_language:
                        stats['conditional_clauses'] += 1
                    
                    all_summaries.append(summary)
                    
                    # Save enhanced output
                    output_file = output_path / f"{clause_file.stem}_summary.json"
                    summary_dict = summary.to_dict()
                    
                    # Add processing metadata
                    summary_dict['processing_metadata'] = {
                        'original_file': clause_file.name,
                        'processed_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'word_count_original': len(content.split()),
                        'word_count_cleaned': summary.word_count,
                        'cleaning_ratio': summary.word_count / max(len(content.split()), 1),
                        'has_numeric_obligations': len(summary.numeric_obligations) > 0,
                        'has_conditional_language': len(summary.conditional_language) > 0
                    }
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(summary_dict, f, indent=2, ensure_ascii=False)
                    
                    results.append({
                        'file': clause_file.name,
                        'summary': summary_dict
                    })
                    
                    logger.info(f"✅ {clause_file.name} -> Risk: {summary.risk_level.value}, "
                              f"Type: {summary.clause_type or 'Unknown'}, "
                              f"Numeric: {len(summary.numeric_obligations)}")
                else:
                    stats['failed'] += 1
                    logger.error(f"❌ Failed: {clause_file.name}")
                
                # Rate limiting for API calls
                if not self.mock_mode:
                    time.sleep(0.7)
                    
            except Exception as e:
                stats['failed'] += 1
                logger.error(f"Error processing {clause_file.name}: {e}")
        
        # Enhanced accuracy metrics
        if all_summaries:
            # Calculate consistency metrics
            consistency_metrics = self._calculate_enhanced_consistency(all_summaries)
            stats['accuracy_metrics'].update(consistency_metrics)
            
            # Calculate average scores
            completeness_scores = [s.completeness_score for s in all_summaries]
            confidence_scores = [s.confidence_score for s in all_summaries]
            
            stats['accuracy_metrics'].update({
                'average_completeness': sum(completeness_scores) / len(completeness_scores),
                'average_confidence': sum(confidence_scores) / len(confidence_scores),
                'min_confidence': min(confidence_scores),
                'max_confidence': max(confidence_scores),
                'total_entities_found': sum(len(s.key_entities) for s in all_summaries),
                'avg_entities_per_clause': sum(len(s.key_entities) for s in all_summaries) / len(all_summaries)
            })
        
        # Create comprehensive output
        success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
        output_data = {
            'statistics': stats,
            'success_rate': f"{success_rate:.1f}%",
            'processing_info': {
                'mock_mode': self.mock_mode,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'enhanced_features': {
                    'numeric_obligations_detected': stats['numeric_obligations_found'],
                    'conditional_clauses_found': stats['conditional_clauses'],
                    'smart_risk_assessment': True,
                    'multi_chunk_combination': True
                }
            },
            'quality_assessment': {
                'estimated_accuracy': self._estimate_enhanced_accuracy(stats),
                'coverage_completeness': f"{(stats['successful'] / stats['total'] * 100):.1f}%",
                'risk_distribution_analysis': self._analyze_risk_distribution(stats['risk_distribution']),
                'feature_utilization': {
                    'numeric_analysis': f"{stats['numeric_obligations_found']} obligations found",
                    'conditional_detection': f"{stats['conditional_clauses']} conditional clauses"
                }
            },
            'summaries': results
        }
        
        # Save results
        combined_file = output_path / "all_summaries_enhanced.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Print enhanced summary
        self._print_comprehensive_summary(stats, output_data, output_path)
        
        return output_data
    
    def _calculate_enhanced_consistency(self, summaries: List[ClauseSummary]) -> Dict[str, float]:
        """Calculate enhanced consistency metrics."""
        if len(summaries) < 2:
            return {"consistency": 1.0}
        
        # Risk consistency within clause types
        type_risks = {}
        for summary in summaries:
            if summary.clause_type:
                if summary.clause_type not in type_risks:
                    type_risks[summary.clause_type] = []
                type_risks[summary.clause_type].append(summary.risk_level)
        
        consistent_types = 0
        total_types = 0
        
        for clause_type, risks in type_risks.items():
            if len(risks) > 1:
                total_types += 1
                risk_counts = {risk: risks.count(risk) for risk in set(risks)}
                max_count = max(risk_counts.values())
                if max_count / len(risks) >= 0.7:
                    consistent_types += 1
        
        consistency = consistent_types / max(total_types, 1)
        
        # Numeric obligation consistency
        numeric_clauses = [s for s in summaries if s.numeric_obligations]
        numeric_consistency = 1.0
        
        if len(numeric_clauses) > 1:
            # Check if similar numeric patterns get similar risk levels
            high_risk_numeric = sum(1 for s in numeric_clauses if s.risk_level == RiskLevel.HIGH)
            numeric_consistency = min(1.0, (high_risk_numeric / len(numeric_clauses)) * 2)
        
        return {
            "risk_consistency": consistency,
            "clause_types_analyzed": total_types,
            "consistent_types": consistent_types,
            "numeric_consistency": numeric_consistency,
            "numeric_clauses_analyzed": len(numeric_clauses)
        }
    
    def _estimate_enhanced_accuracy(self, stats: Dict) -> str:
        """Enhanced accuracy estimation with new features."""
        accuracy_score = 0
        factors = []
        
        # Base success rate
        success_rate = stats['successful'] / max(stats['total'], 1)
        accuracy_score += success_rate * 0.25
        factors.append(f"Success: {success_rate:.2f}")
        
        # Risk distribution quality
        risk_dist = stats['risk_distribution']
        total_risks = sum(risk_dist.values())
        if total_risks > 0:
            high_ratio = risk_dist['High'] / total_risks
            medium_ratio = risk_dist['Medium'] / total_risks
            
            # Ideal distribution: some high risk, good medium distribution
            if 0.15 <= high_ratio <= 0.35 and medium_ratio >= 0.25:
                accuracy_score += 0.25
                factors.append("Balanced risk dist")
            else:
                accuracy_score += 0.15
                factors.append("Skewed risk dist")
        
        # Feature utilization
        if stats['numeric_obligations_found'] > 0:
            numeric_ratio = stats['numeric_obligations_found'] / max(stats['successful'], 1)
            if numeric_ratio >= 0.3:
                accuracy_score += 0.15
                factors.append("Good numeric detection")
            else:
                accuracy_score += 0.1
                factors.append("Some numeric detection")
        
        # Conditional language detection
        if stats['conditional_clauses'] > 0:
            conditional_ratio = stats['conditional_clauses'] / max(stats['successful'], 1)
            if conditional_ratio >= 0.2:
                accuracy_score += 0.1
                factors.append("Good conditional detection")
        
        # Accuracy metrics
        if 'accuracy_metrics' in stats:
            metrics = stats['accuracy_metrics']
            
            if 'average_completeness' in metrics:
                completeness = metrics['average_completeness']
                accuracy_score += completeness * 0.15
                factors.append(f"Completeness: {completeness:.2f}")
            
            if 'average_confidence' in metrics:
                confidence = metrics['average_confidence']
                accuracy_score += confidence * 0.1
                factors.append(f"Confidence: {confidence:.2f}")
        
        # Convert to percentage
        accuracy_percentage = min(accuracy_score * 100, 95)
        
        if accuracy_percentage >= 85:
            category = "Excellent"
        elif accuracy_percentage >= 75:
            category = "Good"
        elif accuracy_percentage >= 60:
            category = "Moderate"
        else:
            category = "Needs Improvement"
        
        return f"{accuracy_percentage:.1f}% ({category})"
    
    def _analyze_risk_distribution(self, risk_dist: Dict[str, int]) -> str:
        """Analyze risk distribution quality."""
        total = sum(risk_dist.values())
        if total == 0:
            return "No data"
        
        high_pct = risk_dist['High'] / total * 100
        medium_pct = risk_dist['Medium'] / total * 100
        low_pct = risk_dist['Low'] / total * 100
        
        analysis = f"H:{high_pct:.1f}%, M:{medium_pct:.1f}%, L:{low_pct:.1f}%"
        
        if high_pct > 50:
            assessment = "Risk-heavy (may be over-sensitive)"
        elif low_pct > 70:
            assessment = "Risk-light (may be under-sensitive)"
        elif 15 <= high_pct <= 35 and medium_pct >= 25:
            assessment = "Well-balanced distribution"
        else:
            assessment = "Moderate distribution"
        
        return f"{analysis} - {assessment}"
    
    def _print_comprehensive_summary(self, stats: Dict, output_data: Dict, output_path: Path):
        """Print comprehensive processing summary."""
        logger.info(f"\n🎉 Enhanced Processing Complete!")
        logger.info(f"✅ Successful: {stats['successful']}")
        logger.info(f"⭐ Skipped: {stats['skipped']}")
        logger.info(f"❌ Failed: {stats['failed']}")
        logger.info(f"📊 Success Rate: {output_data['success_rate']}")
        logger.info(f"⚠️ Risk Distribution: {stats['risk_distribution']}")
        
        if stats['clause_types']:
            logger.info(f"📋 Clause Types: {dict(list(stats['clause_types'].items())[:5])}")
        
        # Enhanced feature summary
        logger.info(f"🔢 Numeric Obligations Found: {stats['numeric_obligations_found']}")
        logger.info(f"🔀 Conditional Clauses: {stats['conditional_clauses']}")
        
        if 'quality_assessment' in output_data:
            qa = output_data['quality_assessment']
            logger.info(f"🎯 Estimated Accuracy: {qa['estimated_accuracy']}")
            logger.info(f"📈 Coverage: {qa['coverage_completeness']}")
            logger.info(f"⚖️ Risk Analysis: {qa['risk_distribution_analysis']}")
        
        if 'accuracy_metrics' in stats:
            metrics = stats['accuracy_metrics']
            if 'average_completeness' in metrics:
                logger.info(f"📝 Avg Completeness: {metrics['average_completeness']:.2f}")
            if 'average_confidence' in metrics:
                logger.info(f"🎯 Avg Confidence: {metrics['average_confidence']:.2f}")
        
        logger.info(f"📁 Results saved to: {output_path}")


def main():
    """Enhanced main function with additional options."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Legal Clause Summarizer v2.0")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    parser.add_argument(
        "--input", 
        default=project_root / "docs" / "clauses",
        help="Input directory with clause files"
    )
    parser.add_argument(
        "--output",
        default=project_root / "docs" / "summaries_enhanced", 
        help="Output directory for summaries"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock mode (no API calls)"
    )
    parser.add_argument(
        "--fast",
        action="store_true", 
        help="Reduce delays for faster processing"
    )
    parser.add_argument(
        "--single-file",
        help="Process only a specific file"
    )
    parser.add_argument(
        "--detailed-report",
        action="store_true",
        help="Generate detailed accuracy and feature utilization report"
    )
    
    args = parser.parse_args()
    
    # API key handling
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key and not args.mock:
        logger.error("GEMINI_API_KEY not found. Use --mock flag or set the API key.")
        return 1
    
    # Fast mode implementation
    if args.fast:
        logger.info("🚀 Fast mode enabled")
        import time as time_module
        original_sleep = time_module.sleep
        time_module.sleep = lambda seconds: original_sleep(min(seconds, 0.2))
    
    # Initialize enhanced summarizer
    summarizer = LegalClauseSummarizer(api_key=api_key, mock_mode=args.mock)
    
    # Process single file or directory
    if args.single_file:
        input_file = Path(args.single_file)
        if not input_file.exists():
            logger.error(f"File not found: {input_file}")
            return 1
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            summary = summarizer.summarize_clause(content, input_file.name)
            if summary:
                print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))
                logger.info(f"✅ Successfully processed: {input_file.name}")
                return 0
            else:
                logger.error(f"❌ Failed to process: {input_file.name}")
                return 1
                
        except Exception as e:
            logger.error(f"Error processing {input_file}: {e}")
            return 1
    else:
        # Enhanced directory processing
        results = summarizer.process_directory(str(args.input), str(args.output))
        
        # Generate detailed report
        if args.detailed_report and 'statistics' in results:
            report_file = Path(args.output) / "enhanced_analysis_report.json"
            report_data = {
                'feature_analysis': {
                    'numeric_obligations': results['statistics'].get('numeric_obligations_found', 0),
                    'conditional_clauses': results['statistics'].get('conditional_clauses', 0),
                    'clause_type_distribution': results['statistics'].get('clause_types', {}),
                    'risk_assessment_quality': results.get('quality_assessment', {}).get('risk_distribution_analysis', '')
                },
                'accuracy_assessment': results['statistics'].get('accuracy_metrics', {}),
                'recommendations': _generate_enhanced_recommendations(results['statistics'])
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Detailed report saved to: {report_file}")
        
        return 0 if results.get('statistics', {}).get('successful', 0) > 0 else 1


def _generate_enhanced_recommendations(stats: Dict) -> List[str]:
    """Generate enhanced recommendations."""
    recommendations = []
    
    success_rate = stats['successful'] / max(stats['total'], 1)
    if success_rate < 0.8:
        recommendations.append("Consider reviewing text preprocessing - low success rate may indicate filtering issues")
    
    # Risk distribution analysis
    risk_dist = stats['risk_distribution']
    total_risks = sum(risk_dist.values())
    if total_risks > 0:
        high_ratio = risk_dist['High'] / total_risks
        if high_ratio > 0.5:
            recommendations.append("High-risk detection may be too aggressive - consider adjusting thresholds")
        elif high_ratio < 0.1:
            recommendations.append("Risk detection may be too conservative - review numeric obligation patterns")
    
    # Feature utilization
    if stats['numeric_obligations_found'] == 0:
        recommendations.append("No numeric obligations detected - verify numeric pattern recognition")
    elif stats['numeric_obligations_found'] / max(stats['successful'], 1) < 0.2:
        recommendations.append("Low numeric obligation detection - consider expanding pattern coverage")
    
    if stats['conditional_clauses'] == 0:
        recommendations.append("No conditional language detected - verify conditional pattern matching")
    
    # Accuracy metrics
    if 'accuracy_metrics' in stats:
        metrics = stats['accuracy_metrics']
        if metrics.get('average_completeness', 1) < 0.7:
            recommendations.append("Low completeness scores - verify entity preservation in summaries")
        
        if metrics.get('average_confidence', 1) < 0.7:
            recommendations.append("Low confidence scores - consider improving AI prompts or chunk combination")
    
    if not recommendations:
        recommendations.append("Processing quality is good - system is performing well with enhanced features")
    
    return recommendations


if __name__ == "__main__":
    exit(main())