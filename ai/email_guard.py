# ai/email_guard.py
import os
import sys
from typing import List, Dict, Any, Optional
import re
from datetime import datetime

# Try to import phishing_detection_py
try:
    from phishing_detection_py import PhishingDetector
    PHISHING_DETECTOR_AVAILABLE = True
except ImportError:
    PHISHING_DETECTOR_AVAILABLE = False
    print("Warning: phishing_detection_py not available.")

class ModelAnalyzer:
    """Base class for all model analyzers"""
    
    def __init__(self, model_name: str, model_source: str):
        self.model_name = model_name
        self.model_source = model_source
    
    def analyze(self, email_text: str) -> Dict[str, Any]:
        """Analyze email text and return results"""
        raise NotImplementedError("Subclasses must implement analyze method")

class PhishingDetectorAnalyzer(ModelAnalyzer):
    """Primary analyzer using phishing-detection-py package"""
    
    def __init__(self):
        super().__init__("phishing-detection-py", "PyPI")
        self.detector = None
        self.load_model()
    
    def load_model(self):
        """Load the phishing detector model"""
        if not PHISHING_DETECTOR_AVAILABLE:
            print("Warning: phishing-detection-py not available, using rule-based analysis only")
            return
        
        try:
            # Initialize the phishing detector for URL analysis
            self.detector = PhishingDetector(model_type="url")
            print(f"✓ Loaded primary model: {self.model_name}")
        except Exception as e:
            print(f"✗ Failed to load primary model {self.model_name}: {e}")
            print("   Using rule-based analysis as fallback")
            # Don't set detector to None, so we can still use text analysis
    
    def analyze(self, email_text: str) -> Dict[str, Any]:
        """Analyze email using phishing-detection-py"""
        try:
            # Extract URLs from email text for analysis
            urls = self._extract_urls(email_text)
            
            # If we have a working detector and URLs, try URL analysis
            if self.detector and urls:
                try:
                    # Analyze the first URL using the detector
                    url_result = self.detector.predict(urls[0])
                    
                    # Process the result - phishing-detection-py returns a dict with prediction and description
                    if url_result is not None:
                        if isinstance(url_result, dict):
                            # Extract prediction and description from the result
                            prediction = url_result.get('prediction', 0)
                            description = url_result.get('description', 'No description available')
                            confidence = url_result.get('confidence', 0.85)
                        else:
                            # Fallback if result is just a prediction value
                            prediction = url_result
                            description = f'URL analysis result for {urls[0]}'
                            confidence = 0.85
                        
                        # Map prediction to standard format
                        if prediction == 1:
                            decision = 'phishing'
                        elif prediction == 0:
                            decision = 'safe'
                        else:
                            decision = 'unknown'
                        
                        return {
                            'model_source': self.model_source,
                            'model_name': self.model_name,
                            'decision': decision,
                            'confidence': confidence,
                            'description': description
                        }
                except Exception as e:
                    # If URL analysis fails, fall back to text analysis
                    print(f"URL analysis failed, falling back to text analysis: {e}")
            
            # Fall back to text content analysis
            return self._analyze_text_content(email_text)
            
        except Exception as e:
            return self._error_result(f"Analysis failed: {str(e)}")
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from email text"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def _analyze_text_content(self, email_text: str) -> Dict[str, Any]:
        """Analyze email text content when no URLs are present or ML model fails"""
        # Use rule-based analysis as fallback
        
        # Check for suspicious patterns
        suspicious_words = ['urgent', 'account suspended', 'verify identity', 'click here', 'bank', 'password']
        text_lower = email_text.lower()
        
        suspicious_count = sum(1 for word in suspicious_words if word in text_lower)
        
        # Create detailed description
        if suspicious_count >= 3:
            decision = 'phishing'
            confidence = min(0.8 + (suspicious_count - 3) * 0.1, 0.95)
            description = f'High risk phishing indicators detected: {suspicious_count} suspicious patterns found in email content. Multiple red flags suggest this is likely a phishing attempt.'
        elif suspicious_count >= 1:
            decision = 'spam'
            confidence = 0.6 + suspicious_count * 0.1
            description = f'Spam indicators detected: {suspicious_count} suspicious patterns found. This email shows characteristics of spam or low-quality content.'
        else:
            decision = 'safe'
            confidence = 0.7
            description = f'No suspicious patterns detected: Email content appears safe with {suspicious_count} suspicious indicators found.'
        
        return {
            'model_source': self.model_source,
            'model_name': self.model_name,
            'decision': decision,
            'confidence': confidence,
            'description': description
        }
    
    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """Return error result"""
        return {
            'model_source': self.model_source,
            'model_name': self.model_name,
            'decision': 'error',
            'confidence': 0.0,
            'description': error_msg
        }

class RuleBasedAnalyzer(ModelAnalyzer):
    """Rule-based analyzer as fallback"""
    
    def __init__(self):
        super().__init__("rule-based", "built-in")
    
    def analyze(self, email_text: str) -> Dict[str, Any]:
        """Analyze email using rule-based approach"""
        try:
            # Extract metadata
            metadata = self._extract_metadata(email_text.lower())
            suspicious_patterns = self._detect_suspicious_patterns(email_text)
            
            # Calculate risk score
            risk_score = 0
            risk_factors = []
            
            # Check for suspicious patterns
            if 'urgency' in suspicious_patterns:
                risk_score += 30
                risk_factors.append('Urgency indicators detected')
            
            if 'financial_request' in suspicious_patterns:
                risk_score += 40
                risk_factors.append('Financial request detected')
            
            if 'personal_info_request' in suspicious_patterns:
                risk_score += 50
                risk_factors.append('Personal information request detected')
            
            if 'suspicious_domain' in suspicious_patterns:
                risk_score += 60
                risk_factors.append('Suspicious domain detected')
            
            # Check metadata
            if metadata['urgency_indicators'] > 0:
                risk_score += metadata['urgency_indicators'] * 10
                risk_factors.append(f'{metadata["urgency_indicators"]} urgency indicators')
            
            if metadata['money_indicators'] > 0:
                risk_score += metadata['money_indicators'] * 15
                risk_factors.append(f'{metadata["money_indicators"]} financial indicators')
            
            # Determine decision based on risk score
            if risk_score >= 70:
                decision = 'phishing'
                confidence = min(risk_score / 100.0, 0.95)
            elif risk_score >= 40:
                decision = 'spam'
                confidence = min(risk_score / 70.0, 0.85)
            else:
                decision = 'safe'
                confidence = max(1.0 - (risk_score / 40.0), 0.6)
            
            # Create detailed description
            if risk_factors:
                description = f'Risk score: {risk_score}/100. Detected factors: {", ".join(risk_factors)}. This analysis is based on pattern matching and content analysis.'
            else:
                description = f'Risk score: {risk_score}/100. No suspicious patterns detected. Email appears to be safe based on rule-based analysis.'
            
            return {
                'model_source': self.model_source,
                'model_name': self.model_name,
                'decision': decision,
                'confidence': confidence,
                'description': description
            }
            
        except Exception as e:
            return self._error_result(f"Analysis failed: {str(e)}")
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from email text"""
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        # Count urgency indicators
        urgency_words = ['urgent', 'immediate', 'asap', 'quickly', 'hurry', 'limited time', 'expires', 'deadline']
        urgency_indicators = sum(1 for word in urgency_words if word in text)
        
        # Count money indicators
        money_words = ['money', 'bank', 'account', 'credit card', 'payment', 'transfer', 'refund', 'lottery', 'inheritance']
        money_indicators = sum(1 for word in money_words if word in text)
        
        # Check for URLs and email addresses
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        has_urls = bool(re.search(url_pattern, text))
        has_email_addresses = bool(re.search(email_pattern, text))
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'urgency_indicators': urgency_indicators,
            'money_indicators': money_indicators,
            'has_urls': has_urls,
            'has_email_addresses': has_email_addresses
        }
    
    def _detect_suspicious_patterns(self, text: str) -> List[str]:
        """Detect suspicious patterns in email text"""
        patterns = []
        
        # Urgency patterns
        urgency_patterns = [
            r'urgent.*action',
            r'limited.*time',
            r'expires.*soon',
            r'act.*now',
            r'immediate.*attention'
        ]
        
        for pattern in urgency_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                patterns.append('urgency')
                break
        
        # Financial request patterns
        financial_patterns = [
            r'bank.*account',
            r'credit.*card',
            r'payment.*required',
            r'money.*transfer',
            r'account.*verification'
        ]
        
        for pattern in financial_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                patterns.append('financial_request')
                break
        
        # Personal info request patterns
        personal_patterns = [
            r'social.*security',
            r'password.*reset',
            r'personal.*information',
            r'verify.*identity',
            r'account.*details'
        ]
        
        for pattern in personal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                patterns.append('personal_info_request')
                break
        
        # Suspicious domain patterns
        suspicious_domains = [
            r'paypal.*verify',
            r'bank.*secure',
            r'account.*update',
            r'security.*alert'
        ]
        
        for pattern in suspicious_domains:
            if re.search(pattern, text, re.IGNORECASE):
                patterns.append('suspicious_domain')
                break
        
        return patterns
    
    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """Return error result"""
        return {
            'model_source': self.model_source,
            'model_name': self.model_name,
            'decision': 'error',
            'confidence': 0.0,
            'description': error_msg
        }

class EmailAnalyzer:
    """Main email analyzer that coordinates multiple models"""
    
    def __init__(self):
        self.analyzers = []
        self.load_analyzers()
    
    def load_analyzers(self):
        """Load available analyzers"""
        # Always try to load phishing-detection-py as primary analyzer
        if PHISHING_DETECTOR_AVAILABLE:
            try:
                phishing_analyzer = PhishingDetectorAnalyzer()
                self.add_analyzer(phishing_analyzer)
                print("✓ Primary ML analyzer loaded")
            except Exception as e:
                print(f"Failed to load primary ML analyzer: {e}")
        
        # Always add rule-based analyzer as fallback
        self.add_analyzer(RuleBasedAnalyzer())
        print("✓ Rule-based fallback analyzer loaded")
    
    def add_analyzer(self, analyzer: ModelAnalyzer):
        """Add an analyzer to the list"""
        self.analyzers.append(analyzer)
    
    def analyze_email(self, email_text: str) -> List[Dict[str, Any]]:
        """Analyze email using all available models"""
        results = []
        
        for analyzer in self.analyzers:
            try:
                result = analyzer.analyze(email_text)
                results.append(result)
            except Exception as e:
                # Add error result for this analyzer
                results.append({
                    'model_source': analyzer.model_source,
                    'model_name': analyzer.model_name,
                    'decision': 'error',
                    'confidence': 0.0,
                    'description': f'Analysis failed: {str(e)}'
                })
        
        return results

# Global analyzer instance
_analyzer = None

def get_analyzer() -> EmailAnalyzer:
    """Get or create the global analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = EmailAnalyzer()
    return _analyzer

def analyze_email_with_models(email_text: str) -> List[Dict[str, Any]]:
    """
    Main function to analyze email with all available models
    
    Args:
        email_text: Email text to analyze
        
    Returns:
        List of model results with required fields
    """
    analyzer = get_analyzer()
    return analyzer.analyze_email(email_text)

def get_model_info() -> Dict[str, Any]:
    """Get information about available models"""
    analyzer = get_analyzer()
    models = []
    
    for analyzer_instance in analyzer.analyzers:
        models.append({
            'name': analyzer_instance.model_name,
            'source': analyzer_instance.model_source,
            'status': 'loaded' if hasattr(analyzer_instance, 'detector') and analyzer_instance.detector else 'available'
        })
    
    return {
        'total_models': len(models),
        'models': models,
        'primary_ml_available': PHISHING_DETECTOR_AVAILABLE,
        'primary_model': 'phishing-detection-py' if PHISHING_DETECTOR_AVAILABLE else 'rule-based'
    }

def add_custom_analyzer(analyzer: ModelAnalyzer):
    """Add a custom analyzer to the global analyzer"""
    global_analyzer = get_analyzer()
    global_analyzer.add_analyzer(analyzer)