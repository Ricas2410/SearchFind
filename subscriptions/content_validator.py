import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class ContentValidator:
    """
    Class for validating document content and determining document types.

    This class implements confidence scoring for different document types
    (resume, cover letter, job description) and validates document structure
    to ensure it contains expected content.
    """

    # Confidence score thresholds
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.3  # Lowered from 0.5 to be more lenient
    LOW_CONFIDENCE = 0.1     # Lowered from 0.2 to be more lenient

    # Minimum word count for a valid document
    MIN_WORD_COUNT = 20      # Lowered from 50 to be more lenient

    def __init__(self, text_processor=None):
        """
        Initialize the ContentValidator.

        Args:
            text_processor (TextProcessor, optional): Instance of TextProcessor for text processing
        """
        self.text_processor = text_processor

    def validate_document(self, text, file_extension=None):
        """
        Validate a document and determine its type.

        Args:
            text (str): Document text content
            file_extension (str, optional): File extension for additional context

        Returns:
            dict: Validation results with document type and confidence scores
        """
        # Check for empty or very short documents
        if not text or len(text.split()) < self.MIN_WORD_COUNT:
            return {
                'is_valid': False,
                'document_type': 'unknown',
                'confidence': 0.0,
                'error': 'Document is too short or empty',
                'word_count': len(text.split()) if text else 0,
                'type_scores': {'resume': 0.0, 'cover_letter': 0.0, 'job_description': 0.0, 'other': 0.0}
            }

        # Calculate scores for different document types
        scores = {
            'resume': self._calculate_resume_score(text),
            'cover_letter': self._calculate_cover_letter_score(text),
            'job_description': self._calculate_job_description_score(text),
            'other': 0.2  # Default score for other document types
        }

        # Determine the most likely document type
        doc_type = max(scores, key=scores.get)
        confidence = scores[doc_type]

        # Validate if the document has sufficient confidence
        is_valid = confidence >= self.MEDIUM_CONFIDENCE

        # Provide error message if invalid
        error = None if is_valid else f"Document doesn't appear to be a valid {doc_type}"

        return {
            'is_valid': is_valid,
            'document_type': doc_type,
            'confidence': confidence,
            'error': error,
            'word_count': len(text.split()),
            'type_scores': scores
        }

    def _calculate_resume_score(self, text):
        """
        Calculate a confidence score for the document being a resume.

        Args:
            text (str): Document text content

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        score = 0.0
        text_lower = text.lower()

        # Check for common resume section headers
        resume_sections = [
            'experience', 'education', 'skills', 'summary', 'profile',
            'work history', 'employment', 'qualifications', 'projects',
            'certifications', 'references', 'publications', 'awards',
            'professional experience', 'career objective', 'technical skills'
        ]

        section_count = 0
        for section in resume_sections:
            # Look for patterns like "EXPERIENCE", "Experience:", "- Experience -"
            pattern = r'\b' + re.escape(section) + r'\b'
            if re.search(pattern, text_lower):
                section_count += 1

        # Score based on section count
        if section_count >= 4:
            score += 0.4
        elif section_count >= 2:
            score += 0.2
        elif section_count >= 1:
            score += 0.1

        # Check for contact information patterns
        contact_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # email
            r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',  # phone
            r'\b(?:linkedin\.com|github\.com|twitter\.com)/[\w-]+\b'  # social media
        ]

        contact_score = 0
        for pattern in contact_patterns:
            if re.search(pattern, text):
                contact_score += 1

        if contact_score >= 2:
            score += 0.2
        elif contact_score >= 1:
            score += 0.1

        # Check for dates (commonly found in work experience and education)
        date_patterns = [
            r'\b(19|20)\d{2}\s*-\s*(19|20)\d{2}\b',  # YYYY-YYYY
            r'\b(19|20)\d{2}\s*-\s*(present|current|now)\b',  # YYYY-Present
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (19|20)\d{2}\b'  # Month YYYY
        ]

        date_count = 0
        for pattern in date_patterns:
            date_count += len(re.findall(pattern, text, re.IGNORECASE))

        if date_count >= 3:
            score += 0.2
        elif date_count >= 1:
            score += 0.1

        # Check for skill keywords
        skill_indicators = [
            r'\bproficient in\b', r'\bexperienced with\b', r'\bskilled in\b',
            r'\bknowledge of\b', r'\bfamiliar with\b', r'\bexpertise in\b',
            r'\bcompetent with\b', r'\btechnical skills\b', r'\bsoft skills\b'
        ]

        skill_count = 0
        for indicator in skill_indicators:
            skill_count += len(re.findall(indicator, text_lower))

        if skill_count >= 3:
            score += 0.2
        elif skill_count >= 1:
            score += 0.1

        return min(1.0, score)

    def _calculate_cover_letter_score(self, text):
        """
        Calculate a confidence score for the document being a cover letter.

        Args:
            text (str): Document text content

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        score = 0.0
        text_lower = text.lower()

        # Check for common cover letter phrases
        cover_letter_phrases = [
            r'\b(?:dear|to) (?:hiring manager|recruiter|sir|madam)\b',
            r'\bI am (?:writing|applying) (?:to|for)\b',
            r'\bI am interested in\b',
            r'\bthank you for (?:your|the) consideration\b',
            r'\blook forward to\b',
            r'\bsincerely\b',
            r'\bregards\b',
            r'\benclosed\b',
            r'\battached\b'
        ]

        phrase_count = 0
        for phrase in cover_letter_phrases:
            if re.search(phrase, text_lower):
                phrase_count += 1

        # Score based on phrase count
        if phrase_count >= 4:
            score += 0.4
        elif phrase_count >= 2:
            score += 0.2
        elif phrase_count >= 1:
            score += 0.1

        # Check for personal pronouns (common in cover letters)
        pronouns = ['I', 'me', 'my', 'mine', 'myself']
        pronoun_freq = 0
        words = text_lower.split()

        for pronoun in pronouns:
            pronoun_freq += words.count(pronoun.lower())

        # Normalize by text length
        if words:
            pronoun_ratio = pronoun_freq / len(words)

            if pronoun_ratio >= 0.05:  # At least 5% of words are personal pronouns
                score += 0.3
            elif pronoun_ratio >= 0.02:  # At least 2% of words are personal pronouns
                score += 0.15

        # Check for company name mentions (common in cover letters)
        company_patterns = [
            r'at \w+',
            r'(?:join|with) \w+',
            r'(?:position|role|opportunity) at \w+'
        ]

        company_count = 0
        for pattern in company_patterns:
            company_count += len(re.findall(pattern, text_lower))

        if company_count >= 2:
            score += 0.2
        elif company_count >= 1:
            score += 0.1

        # Check if the document is relatively short (cover letters are typically shorter than resumes)
        word_count = len(text.split())
        if word_count < 500 and word_count > 100:
            score += 0.1

        return min(1.0, score)

    def _calculate_job_description_score(self, text):
        """
        Calculate a confidence score for the document being a job description.

        Args:
            text (str): Document text content

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        score = 0.0
        text_lower = text.lower()

        # Check for common job description section headers
        job_sections = [
            'job description', 'responsibilities', 'requirements', 'qualifications',
            'about the role', 'about the company', 'skills', 'experience required',
            'education required', 'who you are', 'what you\'ll do', 'benefits',
            'compensation', 'how to apply', 'about us', 'our company', 'the team'
        ]

        section_count = 0
        for section in job_sections:
            pattern = r'\b' + re.escape(section) + r'\b'
            if re.search(pattern, text_lower):
                section_count += 1

        # Score based on section count
        if section_count >= 4:
            score += 0.4
        elif section_count >= 2:
            score += 0.2
        elif section_count >= 1:
            score += 0.1

        # Check for phrases commonly found in job descriptions
        jd_phrases = [
            r'\b(?:we are|our company is) (?:seeking|looking for|hiring)\b',
            r'\bmust have\b',
            r'\brequired skills\b',
            r'\bpreferred qualifications\b',
            r'\bresponsibilities include\b',
            r'\breport to\b',
            r'\bwork with\b',
            r'\bfull[ -]time\b',
            r'\bpart[ -]time\b',
            r'\bremote\b',
            r'\bhybrid\b',
            r'\bon[ -]site\b',
            r'\bsalary\b',
            r'\bemployment type\b',
            r'\bapply now\b'
        ]

        phrase_count = 0
        for phrase in jd_phrases:
            if re.search(phrase, text_lower):
                phrase_count += 1

        if phrase_count >= 4:
            score += 0.3
        elif phrase_count >= 2:
            score += 0.15

        # Check for bullet points (common in job listings)
        bullet_patterns = [r'•', r'·', r'-', r'\*', r'\d+\.']
        bullet_count = 0

        for pattern in bullet_patterns:
            bullets = re.findall(f'^\\s*{pattern}\\s', text, re.MULTILINE)
            bullet_count += len(bullets)

        if bullet_count >= 10:
            score += 0.2
        elif bullet_count >= 5:
            score += 0.1

        # Check for "years of experience" mentions
        experience_patterns = [
            r'\b\d+\+?\s*(?:years|yrs)(?:\s*of\s*|\s+)experience\b',
            r'\bexperience: \d+\+?\s*(?:years|yrs)\b',
            r'\bminimum \d+\s*(?:years|yrs)\b'
        ]

        exp_count = 0
        for pattern in experience_patterns:
            exp_count += len(re.findall(pattern, text_lower))

        if exp_count >= 2:
            score += 0.1
        elif exp_count >= 1:
            score += 0.05

        return min(1.0, score)

    def validate_resume(self, text):
        """
        Validate if document is a resume and evaluate its quality.

        Args:
            text (str): Document text content

        Returns:
            dict: Resume validation results with section completeness and overall assessment
        """
        # First check if it's a resume
        validation = self.validate_document(text)

        if not validation['is_valid'] or validation['document_type'] != 'resume':
            return {
                'is_valid_resume': False,
                'error': validation.get('error', 'Document is not a valid resume'),
                'document_type': validation['document_type'],
                'confidence': validation['confidence']
            }

        # Essential sections for a good resume
        essential_sections = {
            'contact_info': {
                'present': False,
                'score': 0
            },
            'summary': {
                'present': False,
                'score': 0
            },
            'experience': {
                'present': False,
                'score': 0
            },
            'education': {
                'present': False,
                'score': 0
            },
            'skills': {
                'present': False,
                'score': 0
            }
        }

        # Process document with text processor if available
        sections = {}
        if self.text_processor:
            processed = self.text_processor.process_document(text, 'resume')
            sections = processed.get('sections', {})

        # Evaluate contact information
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'

        if re.search(email_pattern, text) and re.search(phone_pattern, text):
            essential_sections['contact_info']['present'] = True
            essential_sections['contact_info']['score'] = 1.0
        elif re.search(email_pattern, text) or re.search(phone_pattern, text):
            essential_sections['contact_info']['present'] = True
            essential_sections['contact_info']['score'] = 0.5

        # Evaluate summary/profile section
        summary_patterns = [
            r'\bprofessional summary\b', r'\bprofile\b', r'\bcareer objective\b',
            r'\bsummary\b', r'\babout me\b', r'\bcareer summary\b'
        ]

        for pattern in summary_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                essential_sections['summary']['present'] = True
                essential_sections['summary']['score'] = 0.8
                break

        # Check for summary section in processed sections
        if 'summary' in sections:
            summary_content = sections['summary']
            essential_sections['summary']['present'] = True

            # Rate the quality based on length
            words = summary_content.split()
            if len(words) >= 30:
                essential_sections['summary']['score'] = 1.0
            elif len(words) >= 15:
                essential_sections['summary']['score'] = 0.7
            else:
                essential_sections['summary']['score'] = 0.4

        # Evaluate experience section
        exp_patterns = [
            r'\bexperience\b', r'\bemployment\b', r'\bwork history\b',
            r'\bprofessional experience\b', r'\bcareer history\b'
        ]

        for pattern in exp_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                essential_sections['experience']['present'] = True
                break

        # Check for experience section in processed sections
        if 'experience' in sections:
            exp_content = sections['experience']
            essential_sections['experience']['present'] = True

            # Rate the quality based on content
            date_pattern = r'\b(19|20)\d{2}\s*-\s*((19|20)\d{2}|present|current)\b'
            dates = re.findall(date_pattern, exp_content, re.IGNORECASE)

            achievement_indicators = [
                r'\bmanaged\b', r'\bimproved\b', r'\bdeveloped\b', r'\bincreased\b',
                r'\breduced\b', r'\bcreated\b', r'\bimplemented\b', r'\bachieved\b',
                r'\bdelivered\b', r'\bout?performed\b'
            ]

            achievements = 0
            for indicator in achievement_indicators:
                achievements += len(re.findall(indicator, exp_content, re.IGNORECASE))

            if len(dates) >= 2 and achievements >= 3:
                essential_sections['experience']['score'] = 1.0
            elif len(dates) >= 1 and achievements >= 1:
                essential_sections['experience']['score'] = 0.7
            else:
                essential_sections['experience']['score'] = 0.4

        # Evaluate education section
        edu_patterns = [
            r'\beducation\b', r'\bacademic background\b', r'\bdegrees?\b', r'\bqualifications\b'
        ]

        for pattern in edu_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                essential_sections['education']['present'] = True
                break

        # Check for education section in processed sections
        if 'education' in sections:
            edu_content = sections['education']
            essential_sections['education']['present'] = True

            # Rate the quality based on content
            degree_patterns = [
                r'\b(bachelor|master|doctorate|phd|bs|ba|ms|ma|mba|b\.s\.|b\.a\.|m\.s\.|m\.a\.|ph\.d\.)\b',
                r'\bdegree\b'
            ]

            has_degree = False
            for pattern in degree_patterns:
                if re.search(pattern, edu_content, re.IGNORECASE):
                    has_degree = True
                    break

            # Check for graduation years
            year_pattern = r'\b(19|20)\d{2}\b'
            years = re.findall(year_pattern, edu_content)

            if has_degree and years:
                essential_sections['education']['score'] = 1.0
            elif has_degree or years:
                essential_sections['education']['score'] = 0.7
            else:
                essential_sections['education']['score'] = 0.4

        # Evaluate skills section
        skill_patterns = [
            r'\bskills\b', r'\btechnical skills\b', r'\bcompetencies\b', r'\bcapabilities\b'
        ]

        for pattern in skill_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                essential_sections['skills']['present'] = True
                break

        # Check for skills section in processed sections
        if 'skills' in sections:
            skills_content = sections['skills']
            essential_sections['skills']['present'] = True

            # Rate the quality based on content
            # Look for skill lists (comma or bullet separated)
            skill_count = 0

            if ',' in skills_content:
                skill_count = len([s.strip() for s in skills_content.split(',') if s.strip()])
            elif any(bullet in skills_content for bullet in ['•', '·', '-', '*']):
                for bullet in ['•', '·', '-', '*']:
                    if bullet in skills_content:
                        skill_count = len([s.strip() for s in skills_content.split(bullet) if s.strip()])
                        break
            else:
                # Count words as potential individual skills
                skill_count = len(skills_content.split())

            if skill_count >= 10:
                essential_sections['skills']['score'] = 1.0
            elif skill_count >= 5:
                essential_sections['skills']['score'] = 0.7
            else:
                essential_sections['skills']['score'] = 0.4

        # Calculate overall resume score
        present_sections = sum(1 for section in essential_sections.values() if section['present'])
        section_scores = sum(section['score'] for section in essential_sections.values())

        max_possible_score = len(essential_sections)
        overall_score = section_scores / max_possible_score

        # Create section recommendations
        recommendations = []
        for section_name, section_data in essential_sections.items():
            if not section_data['present']:
                recommendations.append(f"Add a {section_name.replace('_', ' ')} section")
            elif section_data['score'] < 0.7:
                recommendations.append(f"Improve your {section_name.replace('_', ' ')} section")

        return {
            'is_valid_resume': True,
            'sections': {
                name: {
                    'present': data['present'],
                    'score': data['score'],
                    'rating': 'Excellent' if data['score'] >= 0.9 else
                             'Good' if data['score'] >= 0.7 else
                             'Adequate' if data['score'] >= 0.4 else
                             'Needs Improvement'
                } for name, data in essential_sections.items()
            },
            'overall_score': round(overall_score * 100),
            'missing_sections': [name.replace('_', ' ') for name, data in essential_sections.items() if not data['present']],
            'recommendations': recommendations,
            'completeness': round((present_sections / len(essential_sections)) * 100)
        }