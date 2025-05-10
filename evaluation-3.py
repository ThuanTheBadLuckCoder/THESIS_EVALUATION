"""
Enhanced evaluation script for comparing model responses using ROUGE metrics
with detailed analysis and visualization capabilities.

This script is designed to be versatile across different question types and answer formats,
not limited to HTML/web development evaluation.

Installation:
    pip install rouge_score matplotlib pandas seaborn pyyaml
    
Usage Instructions:
    python evaluation-3.py --file 3-responses.txt --output-dir evaluation_results --config config.json
"""

import re
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from rouge_score import rouge_scorer
from datetime import datetime
import os
import argparse
import yaml
from collections import defaultdict

def preprocess_text(text):
    """Clean and preprocess text for evaluation"""
    # Remove HTML tags
    text = re.sub(r'<.*?>', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_content_from_file(file_path, format_config=None):
    """Extract the different sections from the file with flexible pattern matching
    
    Args:
        file_path: Path to the file with responses
        format_config: Dictionary with regex patterns for extraction
        
    Returns:
        Dictionary with extracted content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use provided format config or default
        if format_config is None:
            format_config = {
                "question_pattern": r'Question:\s*"(.*?)"\s*-+',
                "standard_answer_pattern": r'Standard Answer(?:\s*Code)?:\s*"(.*?)"\s*-+',
                "model_patterns": {
                    "gpt": r'GPT:\s*"(.*?)"\s*----',
                    "gemini": r'GEMINI:\s*"(.*?)"\s*RAG',
                    "rag": r'RAG SYSTEM:\s*"(.*?)"$'
                }
            }
            
        # Extract question and standard answer
        question_match = re.search(format_config["question_pattern"], content, re.DOTALL)
        standard_answer_match = re.search(format_config["standard_answer_pattern"], content, re.DOTALL)
        
        # Initialize result dict
        result = {
            "question": "",
            "standard_answer": "",
            "responses": {}
        }
        
        # Extract question and standard answer
        if question_match:
            result["question"] = question_match.group(1).strip()
        if standard_answer_match:
            result["standard_answer"] = standard_answer_match.group(1).strip()
        
        # Extract model responses
        missing = []
        for model_name, pattern in format_config["model_patterns"].items():
            model_match = re.search(pattern, content, re.DOTALL)
            if model_match:
                result["responses"][model_name] = model_match.group(1).strip()
            else:
                missing.append(model_name)
                result["responses"][model_name] = ""
        
        # Check if we have all sections
        if not question_match:
            missing.append("Question")
        if not standard_answer_match:
            missing.append("Standard Answer")
        
        if missing:
            print(f"Warning: Could not extract all sections. Missing: {', '.join(missing)}")
        
        return result
    except Exception as e:
        print(f"Error extracting content from file: {e}")
        return None

def calculate_rouge_scores(reference, candidate):
    """Calculate ROUGE-1, ROUGE-2, and ROUGE-L scores"""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, candidate)
    
    return {
        'rouge1_precision': scores['rouge1'].precision,
        'rouge1_recall': scores['rouge1'].recall,
        'rouge1_f1': scores['rouge1'].fmeasure,
        'rouge2_precision': scores['rouge2'].precision,
        'rouge2_recall': scores['rouge2'].recall,
        'rouge2_f1': scores['rouge2'].fmeasure,
        'rougeL_precision': scores['rougeL'].precision,
        'rougeL_recall': scores['rougeL'].recall,
        'rougeL_f1': scores['rougeL'].fmeasure
    }

def extract_html_content(text):
    """Extract HTML content from the text with improved pattern matching"""
    # Try to find complete HTML document
    html_match = re.search(r'<!DOCTYPE html>[\s\S]*?</html>', text, re.IGNORECASE)
    if html_match:
        return html_match.group(0)
    
    # Try to find body content
    body_match = re.search(r'<body[\s\S]*?</body>', text, re.IGNORECASE)
    if body_match:
        return body_match.group(0)
    
    # Try to find any HTML tags
    html_match = re.search(r'<([^>]*)>[\s\S]*?</\1>', text, re.DOTALL)
    if html_match:
        return html_match.group(0)
    
    # Look for code blocks
    code_match = re.search(r'```(?:html)?\s*([\s\S]*?)\s*```', text, re.DOTALL)
    if code_match:
        return code_match.group(1)
    
    return text

def extract_code_content(text, language=None):
    """Extract code content from text based on specified language
    
    Args:
        text: The text containing code
        language: Programming language to extract (e.g., 'python', 'javascript')
        
    Returns:
        Extracted code as string
    """
    # Look for code blocks with language marker
    lang_pattern = language if language else r'[a-zA-Z0-9]+'
    code_match = re.search(rf'```(?:{lang_pattern})?\s*([\s\S]*?)\s*```', text, re.DOTALL)
    if code_match:
        return code_match.group(1)
    
    # Look for code blocks without language marker
    code_match = re.search(r'```\s*([\s\S]*?)\s*```', text, re.DOTALL)
    if code_match:
        return code_match.group(1)
    
    # Look for indented code blocks
    indented_code = re.findall(r'(?:^|\n)( {4,}|\t+).*(?:\n(?:\1.*|\s*)){2,}', text)
    if indented_code:
        return '\n'.join(indented_code)
    
    return text

def html_structure_similarity(html1, html2):
    """Measure similarity between HTML structures with advanced metrics"""
    # Extract and count HTML tags
    tags1 = re.findall(r'<([a-zA-Z0-9]+)[^>]*>', html1.lower())
    tags2 = re.findall(r'<([a-zA-Z0-9]+)[^>]*>', html2.lower())
    
    # Count occurrences of each tag
    tag_counts1 = {tag: tags1.count(tag) for tag in set(tags1)}
    tag_counts2 = {tag: tags2.count(tag) for tag in set(tags2)}
    
    # Calculate Jaccard similarity between tag sets
    all_tags = set(tags1 + tags2)
    intersection = sum(min(tag_counts1.get(tag, 0), tag_counts2.get(tag, 0)) for tag in all_tags)
    union = sum(max(tag_counts1.get(tag, 0), tag_counts2.get(tag, 0)) for tag in all_tags)
    jaccard = intersection / union if union > 0 else 0
    
    # Calculate tag presence percentage
    standard_tags = set(tags1)
    response_tags = set(tags2)
    if standard_tags:
        tag_presence = len(standard_tags.intersection(response_tags)) / len(standard_tags)
    else:
        tag_presence = 0
    
    # Calculate tag sequence similarity
    # Convert to lowercase for case-insensitive comparison
    seq1 = [tag.lower() for tag in tags1]
    seq2 = [tag.lower() for tag in tags2]
    
    # Find longest common subsequence length
    m, n = len(seq1), len(seq2)
    if m == 0 or n == 0:
        lcs_length = 0
    else:
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        lcs_length = dp[m][n]
    
    sequence_similarity = lcs_length / max(len(seq1), len(seq2)) if max(len(seq1), len(seq2)) > 0 else 0
    
    # Extract and compare attributes
    attr_pattern = r'<[^>]+\s+([a-zA-Z0-9-]+)\s*=\s*["\'][^"\']*["\']'
    attrs1 = set(re.findall(attr_pattern, html1.lower()))
    attrs2 = set(re.findall(attr_pattern, html2.lower()))
    
    attr_similarity = len(attrs1.intersection(attrs2)) / len(attrs1.union(attrs2)) if attrs1.union(attrs2) else 0
    
    return {
        'jaccard': jaccard,
        'tag_presence': tag_presence,
        'sequence_similarity': sequence_similarity,
        'attribute_similarity': attr_similarity,
        'overall': (jaccard + tag_presence + sequence_similarity + attr_similarity) / 4
    }

def code_structure_similarity(code1, code2, language=None):
    """Measure similarity between code structures based on language
    
    Args:
        code1: Reference code
        code2: Candidate code
        language: Programming language for specialized analysis
        
    Returns:
        Dictionary with similarity metrics
    """
    # Basic lexical similarity
    tokens1 = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|[^\w\s]+', code1.lower())
    tokens2 = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|[^\w\s]+', code2.lower())
    
    # Remove common keywords based on language
    if language:
        if language.lower() == 'python':
            keywords = {'def', 'class', 'import', 'from', 'if', 'else', 'elif', 'while', 'for', 'in', 'return', 'None', 'True', 'False'}
        elif language.lower() in ('javascript', 'js'):
            keywords = {'function', 'const', 'let', 'var', 'if', 'else', 'return', 'for', 'while', 'null', 'undefined', 'true', 'false'}
        else:
            keywords = set()
            
        tokens1 = [t for t in tokens1 if t not in keywords]
        tokens2 = [t for t in tokens2 if t not in keywords]
    
    # Calculate token-based similarity
    token_set1 = set(tokens1)
    token_set2 = set(tokens2)
    
    # Jaccard similarity for tokens
    token_intersection = len(token_set1.intersection(token_set2))
    token_union = len(token_set1.union(token_set2))
    token_jaccard = token_intersection / token_union if token_union > 0 else 0
    
    # Calculate frequency-based similarity
    token_freq1 = {token: tokens1.count(token) for token in token_set1}
    token_freq2 = {token: tokens2.count(token) for token in token_set2}
    
    all_tokens = set(tokens1 + tokens2)
    freq_intersection = sum(min(token_freq1.get(token, 0), token_freq2.get(token, 0)) for token in all_tokens)
    freq_union = sum(max(token_freq1.get(token, 0), token_freq2.get(token, 0)) for token in all_tokens)
    freq_similarity = freq_intersection / freq_union if freq_union > 0 else 0
    
    # Structure analysis based on patterns
    structure_patterns = {
        'function_def': r'(?:function\s+\w+|def\s+\w+|const\s+\w+\s*=\s*(?:function|async function|\([^)]*\)\s*=>))',
        'class_def': r'class\s+\w+',
        'import_stmt': r'(?:import|from\s+\w+\s+import)',
        'condition': r'if\s*\(',
        'loop': r'(?:for|while)\s*\(',
        'variable_assign': r'(?:let|var|const)\s+\w+\s*=',
    }
    
    pattern_counts1 = {name: len(re.findall(pattern, code1)) for name, pattern in structure_patterns.items()}
    pattern_counts2 = {name: len(re.findall(pattern, code2)) for name, pattern in structure_patterns.items()}
    
    # Calculate structure similarity
    structure_similarity = 0
    pattern_count = 0
    
    for name in structure_patterns:
        count1 = pattern_counts1.get(name, 0)
        count2 = pattern_counts2.get(name, 0)
        if count1 > 0 or count2 > 0:
            pattern_count += 1
            max_count = max(count1, count2)
            min_count = min(count1, count2)
            structure_similarity += min_count / max_count if max_count > 0 else 0
    
    structure_similarity = structure_similarity / pattern_count if pattern_count > 0 else 0
    
    # Line count similarity
    lines1 = [line.strip() for line in code1.split('\n') if line.strip()]
    lines2 = [line.strip() for line in code2.split('\n') if line.strip()]
    
    line_count_similarity = min(len(lines1), len(lines2)) / max(len(lines1), len(lines2)) if max(len(lines1), len(lines2)) > 0 else 0
    
    # Calculate overall code similarity
    overall = (token_jaccard + freq_similarity + structure_similarity + line_count_similarity) / 4
    
    return {
        'token_jaccard': token_jaccard,
        'frequency_similarity': freq_similarity,
        'structure_similarity': structure_similarity,
        'line_count_similarity': line_count_similarity,
        'overall': overall
    }

def implementation_score(content, requirements=None, content_type=None):
    """Score how well the content implements specific requirements
    
    Args:
        content: The text content to evaluate
        requirements: Dictionary of requirements to check
        content_type: Type of content ('html', 'python', 'javascript', etc.)
        
    Returns:
        Tuple of (score, details, explanations)
    """
    if requirements is None:
        # Default to empty requirements
        requirements = {}
        
    scores = {}
    explanations = {}
    content_lower = content.lower()
    
    for req_name, req_info in requirements.items():
        # Check for patterns
        found_patterns = []
        for pattern in req_info['patterns']:
            if re.search(pattern, content_lower):
                found_patterns.append(pattern)
        
        # Calculate score based on pattern matches
        if found_patterns:
            score = min(1.0, len(found_patterns) / (len(req_info['patterns']) / 2))
        else:
            score = 0.0
            
        scores[req_name] = score * req_info['weight']
        
        # Prepare explanation
        if score > 0:
            explanations[req_name] = f"Found {len(found_patterns)} relevant patterns: {', '.join(found_patterns[:3])}" + \
                                     (f" and {len(found_patterns) - 3} more" if len(found_patterns) > 3 else "")
        else:
            explanations[req_name] = "No relevant patterns found"
    
    # Calculate overall implementation score (weighted)
    total_weight = sum(req_info['weight'] for req_info in requirements.values())
    weighted_score = sum(scores.values()) / total_weight if total_weight > 0 else 0
    
    return weighted_score, scores, explanations

def extract_content_characteristics(content, content_type=None):
    """Extract key characteristics from content based on its type
    
    Args:
        content: The text content to analyze
        content_type: Type of content ('html', 'python', 'javascript', etc.)
        
    Returns:
        Dictionary of characteristics
    """
    characteristics = {}
    
    # Common characteristics for all content types
    lines = content.count('\n') + 1
    characteristics['total_lines'] = lines
    characteristics['avg_line_length'] = len(content) / lines if lines > 0 else 0
    
    # Extract type-specific characteristics
    if content_type == 'html':
        # HTML-specific characteristics
        characteristics.update(extract_html_characteristics(content))
    elif content_type in ('python', 'py'):
        # Python-specific characteristics
        characteristics.update(extract_python_characteristics(content))
    elif content_type in ('javascript', 'js'):
        # JavaScript-specific characteristics
        characteristics.update(extract_js_characteristics(content))
    else:
        # Generic code characteristics
        characteristics.update(extract_generic_code_characteristics(content))
    
    return characteristics

def extract_html_characteristics(html):
    """Extract key characteristics from HTML code"""
    characteristics = {}
    
    # Count HTML elements
    elements = len(re.findall(r'<[a-zA-Z][^>]*>', html))
    characteristics['total_elements'] = elements
    
    # Check if it has basic HTML structure
    has_doctype = bool(re.search(r'<!DOCTYPE', html, re.IGNORECASE))
    has_html_tag = bool(re.search(r'<html', html, re.IGNORECASE))
    has_head = bool(re.search(r'<head', html, re.IGNORECASE))
    has_body = bool(re.search(r'<body', html, re.IGNORECASE))
    
    characteristics['has_doctype'] = has_doctype
    characteristics['has_html_tag'] = has_html_tag
    characteristics['has_head'] = has_head
    characteristics['has_body'] = has_body
    characteristics['has_basic_structure'] = has_doctype and has_html_tag and has_head and has_body
    
    # Check for CSS usage
    inline_css = len(re.findall(r'style=', html, re.IGNORECASE))
    internal_css = bool(re.search(r'<style[^>]*>[\s\S]*?</style>', html, re.IGNORECASE))
    external_css = bool(re.search(r'<link[^>]*stylesheet[^>]*>', html, re.IGNORECASE))
    
    characteristics['inline_css_count'] = inline_css
    characteristics['has_internal_css'] = internal_css
    characteristics['has_external_css'] = external_css
    
    # Check for JavaScript usage
    inline_js = len(re.findall(r'on[a-z]+=', html, re.IGNORECASE))
    internal_js = bool(re.search(r'<script[^>]*>[\s\S]*?</script>', html, re.IGNORECASE))
    external_js = bool(re.search(r'<script[^>]*src=', html, re.IGNORECASE))
    
    characteristics['inline_js_count'] = inline_js
    characteristics['has_internal_js'] = internal_js
    characteristics['has_external_js'] = external_js
    
    # Look for specific elements
    characteristics['has_form'] = bool(re.search(r'<form', html, re.IGNORECASE))
    characteristics['has_images'] = bool(re.search(r'<img', html, re.IGNORECASE))
    characteristics['has_buttons'] = bool(re.search(r'<button', html, re.IGNORECASE))
    characteristics['has_links'] = bool(re.search(r'<a\s', html, re.IGNORECASE))
    
    # Check for tailwind classes
    tailwind_classes = re.findall(r'class=["\'](.*?)["\']', html, re.IGNORECASE)
    tailwind_count = sum(1 for cls in tailwind_classes if re.search(r'(bg-|text-|p-|m-|flex|grid|w-|h-)', cls))
    characteristics['tailwind_class_count'] = tailwind_count
    
    # Check for semantic elements
    semantic_elements = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
    semantic_count = sum(1 for tag in semantic_elements if re.search(f'<{tag}[^>]*>', html, re.IGNORECASE))
    characteristics['semantic_element_count'] = semantic_count
    
    return characteristics

def extract_python_characteristics(code):
    """Extract key characteristics from Python code"""
    characteristics = {}
    
    # Count functions and classes
    function_defs = re.findall(r'def\s+\w+\s*\(', code)
    class_defs = re.findall(r'class\s+\w+', code)
    
    characteristics['function_count'] = len(function_defs)
    characteristics['class_count'] = len(class_defs)
    
    # Check for imports
    import_statements = re.findall(r'(?:import|from)\s+\w+', code)
    characteristics['import_count'] = len(import_statements)
    
    # Check for list/dict comprehensions (Pythonic feature)
    list_comprehensions = re.findall(r'\[\s*\w+\s+for\s+\w+\s+in', code)
    dict_comprehensions = re.findall(r'\{\s*\w+\s*:\s*\w+\s+for\s+\w+\s+in', code)
    
    characteristics['list_comprehension_count'] = len(list_comprehensions)
    characteristics['dict_comprehension_count'] = len(dict_comprehensions)
    
    # Check for docstrings
    docstrings = re.findall(r'"""[\s\S]*?"""', code)
    characteristics['has_docstrings'] = len(docstrings) > 0
    characteristics['docstring_count'] = len(docstrings)
    
    # Check for error handling
    try_blocks = re.findall(r'try\s*:', code)
    except_blocks = re.findall(r'except\s*(\w+)?:', code)
    
    characteristics['has_error_handling'] = len(try_blocks) > 0
    characteristics['try_except_count'] = len(try_blocks)
    
    # Check for comments
    comments = re.findall(r'#.*$', code, re.MULTILINE)
    characteristics['comment_count'] = len(comments)
    
    return characteristics

def extract_js_characteristics(code):
    """Extract key characteristics from JavaScript code"""
    characteristics = {}
    
    # Count functions (all types)
    function_defs = re.findall(r'function\s+\w+\s*\(', code)
    arrow_functions = re.findall(r'=>', code)
    method_defs = re.findall(r'\w+\s*\([^)]*\)\s*\{', code)
    
    characteristics['named_function_count'] = len(function_defs)
    characteristics['arrow_function_count'] = len(arrow_functions)
    characteristics['method_count'] = len(method_defs)
    characteristics['total_function_count'] = len(function_defs) + len(arrow_functions) + len(method_defs)
    
    # Variable declarations
    const_vars = re.findall(r'const\s+\w+', code)
    let_vars = re.findall(r'let\s+\w+', code)
    var_vars = re.findall(r'var\s+\w+', code)
    
    characteristics['const_var_count'] = len(const_vars)
    characteristics['let_var_count'] = len(let_vars)
    characteristics['var_var_count'] = len(var_vars)
    characteristics['total_var_count'] = len(const_vars) + len(let_vars) + len(var_vars)
    
    # Modern JS features
    destructuring = re.findall(r'(?:const|let|var)\s*\{[^}]*\}', code)
    template_literals = re.findall(r'`[^`]*`', code)
    spread_operators = re.findall(r'\.\.\.', code)
    
    characteristics['destructuring_count'] = len(destructuring)
    characteristics['template_literal_count'] = len(template_literals)
    characteristics['spread_operator_count'] = len(spread_operators)
    
    # Async features
    async_functions = re.findall(r'async\s+\w+|\w+\s*=\s*async', code)
    promises = re.findall(r'Promise|\.then\(|\.catch\(', code)
    
    characteristics['async_function_count'] = len(async_functions)
    characteristics['promise_usage_count'] = len(promises)
    
    # Error handling
    try_blocks = re.findall(r'try\s*\{', code)
    catch_blocks = re.findall(r'catch\s*\(', code)
    
    characteristics['has_error_handling'] = len(try_blocks) > 0
    characteristics['try_catch_count'] = len(try_blocks)
    
    # Comments
    single_line_comments = re.findall(r'//.*$', code, re.MULTILINE)
    multi_line_comments = re.findall(r'/\*[\s\S]*?\*/', code)
    
    characteristics['single_line_comment_count'] = len(single_line_comments)
    characteristics['multi_line_comment_count'] = len(multi_line_comments)
    characteristics['total_comment_count'] = len(single_line_comments) + len(multi_line_comments)
    
    return characteristics

def extract_generic_code_characteristics(code):
    """Extract general characteristics from any code"""
    characteristics = {}
    
    # Basic code metrics
    non_empty_lines = [line for line in code.split('\n') if line.strip()]
    characteristics['non_empty_line_count'] = len(non_empty_lines)
    
    # Indentation analysis
    indentation_levels = []
    for line in non_empty_lines:
        leading_spaces = len(line) - len(line.lstrip())
        if leading_spaces > 0:
            indentation_levels.append(leading_spaces)
    
    if indentation_levels:
        characteristics['avg_indentation'] = sum(indentation_levels) / len(indentation_levels)
        characteristics['max_indentation'] = max(indentation_levels)
    else:
        characteristics['avg_indentation'] = 0
        characteristics['max_indentation'] = 0
    
    # Complexity indicators
    conditionals = re.findall(r'if\s*\(|if\s+', code)
    loops = re.findall(r'for\s*\(|for\s+|while\s*\(|while\s+', code)
    
    characteristics['conditional_count'] = len(conditionals)
    characteristics['loop_count'] = len(loops)
    
    # Estimate cyclomatic complexity (very rough)
    complexity = 1 + len(conditionals) + len(loops)
    characteristics['estimated_complexity'] = complexity
    
    # Comments (generic pattern)
    comments = re.findall(r'(?://|#).*$|/\*[\s\S]*?\*/', code, re.MULTILINE)
    characteristics['comment_count'] = len(comments)
    
    return characteristics

def detect_content_type(text):
    """Detect the type of content based on patterns
    
    Args:
        text: The text to analyze
        
    Returns:
        Detected content type as string ('html', 'python', 'javascript', 'generic')
    """
    # Check for HTML patterns
    html_indicators = [
        r'<!DOCTYPE html>',
        r'<html',
        r'<body',
        r'<div',
        r'<p>',
        r'class=["\'](.*?)["\']'
    ]
    
    html_score = sum(1 for pattern in html_indicators if re.search(pattern, text, re.IGNORECASE))
    
    # Check for Python patterns
    python_indicators = [
        r'def\s+\w+\s*\(',
        r'import\s+\w+',
        r'from\s+\w+\s+import',
        r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
        r'class\s+\w+\s*:',
        r'print\s*\(',
        r'#.*$'
    ]
    
    python_score = sum(1 for pattern in python_indicators if re.search(pattern, text, re.MULTILINE))
    
    # Check for JavaScript patterns
    js_indicators = [
        r'function\s+\w+\s*\(',
        r'const\s+\w+\s*=',
        r'let\s+\w+\s*=',
        r'var\s+\w+\s*=',
        r'=>',
        r'document\.getElementById',
        r'console\.log'
    ]
    
    js_score = sum(1 for pattern in js_indicators if re.search(pattern, text))
    
    # Determine the type based on the highest score
    scores = {
        'html': html_score,
        'python': python_score,
        'javascript': js_score
    }
    
    max_type = max(scores.items(), key=lambda x: x[1])
    
    # If the score is too low, default to generic
    if max_type[1] < 2:
        return 'generic'
    
    return max_type[0]

def load_requirements(config_path=None, content_type=None):
    """Load requirements from config file or use defaults based on content type
    
    Args:
        config_path: Path to config file
        content_type: Type of content ('html', 'python', 'javascript', etc.)
        
    Returns:
        Dictionary of requirements
    """
    if config_path:
        try:
            # Load from config file
            if config_path.endswith('.json'):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            elif config_path.endswith(('.yaml', '.yml')):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            else:
                print(f"Unsupported config file format: {config_path}")
                config = {}
            
            # Return requirements section
            return config.get('requirements', {})
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    # Default requirements based on content type
    if content_type == 'html':
        return {
            'responsive_design': {
                'description': 'Responsive design implementation',
                'patterns': ['sm:', 'md:', 'lg:', 'xl:', '@media', 'flex', 'grid'],
                'weight': 1
            },
            'semantic_html': {
                'description': 'Use of semantic HTML elements',
                'patterns': ['<header', '<nav', '<main', '<section', '<article', '<aside', '<footer'],
                'weight': 1
            },
            'accessibility': {
                'description': 'Accessibility features',
                'patterns': ['aria-', 'role=', 'alt=', 'tabindex', '<label'],
                'weight': 1
            }
        }
    elif content_type in ('python', 'py'):
        return {
            'code_organization': {
                'description': 'Well-organized code structure',
                'patterns': ['def\\s+', 'class\\s+', 'if\\s+__name__\\s*=='],
                'weight': 1
            },
            'error_handling': {
                'description': 'Proper error handling',
                'patterns': ['try:', 'except', 'finally:', 'raise\\s+'],
                'weight': 1
            },
            'documentation': {
                'description': 'Code documentation',
                'patterns': ['"""', '#\\s+\\w+', "'''"],
                'weight': 1
            }
        }
    elif content_type in ('javascript', 'js'):
        return {
            'modern_js': {
                'description': 'Modern JavaScript features',
                'patterns': ['const\\s+', 'let\\s+', '=>', '...', 'async', 'await'],
                'weight': 1
            },
            'error_handling': {
                'description': 'Proper error handling',
                'patterns': ['try\\s*{', 'catch', 'finally', '.catch('],
                'weight': 1
            },
            'code_organization': {
                'description': 'Well-organized code',
                'patterns': ['function\\s+', 'class\\s+', 'import\\s+', 'export\\s+'],
                'weight': 1
            }
        }
    
    # Generic requirements
    return {
        'completeness': {
            'description': 'Solution completeness',
            'patterns': [],  # Will need to be filled based on the specific task
            'weight': 1
        },
        'clarity': {
            'description': 'Code clarity and readability',
            'patterns': [],  # Will need to be filled based on the specific task
            'weight': 1
        }
    }

def plot_evaluation_results(results, metric_config=None, save_path=None):
    """Create visualizations of evaluation results with configurable metrics
    
    Args:
        results: List of result tuples from evaluation
        metric_config: Configuration for which metrics to display
        save_path: Path to save the plot
    """
    try:
        # Set up the style
        sns.set(style="whitegrid")
        plt.figure(figsize=(14, 10))
        
        # Default metrics if not specified
        if metric_config is None:
            metric_config = {
                'main_metrics': ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'Structure', 'Implementation'],
                'implementation_features': None  # Will use all available features
            }
        
        # Extract model names
        model_names = [result[0] for result in results]
        
        # Create a dataframe with scores
        main_metrics_data = []
        for result in results:
            model, rouge, structure_sim, impl_score, impl_details, overall = result
            
            # Add main metrics
            main_metrics_data.append({
                'Model': model,
                'ROUGE-1': rouge['rouge1_f1'],
                'ROUGE-2': rouge['rouge2_f1'],
                'ROUGE-L': rouge['rougeL_f1'],
                'Structure': structure_sim['overall'] if 'overall' in structure_sim else 0,
                'Implementation': impl_score,
                'Overall': overall
            })
        
        df = pd.DataFrame(main_metrics_data)
        
        # Filter metrics based on config
        metric_cols = [m for m in metric_config['main_metrics'] if m in df.columns]
        metric_cols.append('Overall')
        
        # Melt the dataframe for seaborn
        df_melted = pd.melt(df, id_vars=['Model'], 
                           value_vars=metric_cols,
                           var_name='Metric', value_name='Score')
        
        # Plot the metrics
        plt.subplot(2, 1, 1)
        chart = sns.barplot(x='Model', y='Score', hue='Metric', data=df_melted)
        chart.set_title('Evaluation Metrics by Model', fontsize=16)
        chart.set_ylim(0, 1)
        
        # Adjust legend position
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Plot implementation details
        plt.subplot(2, 1, 2)
        
        # Gather implementation details
        implementation_data = []
        for result in results:
            model, _, _, _, impl_details, _ = result
            
            # Filter features if specified
            if metric_config['implementation_features']:
                impl_details = {k: v for k, v in impl_details.items() 
                               if k in metric_config['implementation_features']}
            
            # Use up to 8 features to avoid overcrowding
            if len(impl_details) > 8:
                # Sort by score and keep top 8
                sorted_details = sorted(impl_details.items(), key=lambda x: x[1], reverse=True)[:8]
                impl_details = dict(sorted_details)
            
            for feature, score in impl_details.items():
                implementation_data.append({
                    'Model': model,
                    'Feature': feature.replace('_', ' ').title(),
                    'Score': score
                })
        
        if implementation_data:
            impl_df = pd.DataFrame(implementation_data)
            
            sns.barplot(x='Feature', y='Score', hue='Model', data=impl_df)
            plt.title('Implementation Details by Model', fontsize=16)
            plt.xticks(rotation=45, ha='right')
            plt.ylim(0, 1)
        else:
            plt.text(0.5, 0.5, 'No implementation details available', 
                     horizontalalignment='center', verticalalignment='center')
        
        plt.tight_layout()
        
        # Save the plot if a path is provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        
        # Close the figure to free memory
        plt.close()
        
    except Exception as e:
        print(f"Error creating visualization: {e}")

def generate_evaluation_report(results, model_details, file_path, config=None, output_dir=None):
    """Generate a comprehensive evaluation report with configurable metrics
    
    Args:
        results: List of result tuples from evaluation
        model_details: Dictionary with additional model details
        file_path: Path to the input file
        config: Configuration dictionary
        output_dir: Directory to save the report
    
    Returns:
        Report text
    """
    # Initialize output directory
    if output_dir is None:
        output_dir = '.'
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get content type from config
    content_type = config.get('content_type', 'generic') if config else 'generic'
    
    # Generate report in markdown format
    report = f"""# Model Response Evaluation Report
    
## Overview
- **Evaluation Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Input File:** {file_path}
- **Content Type:** {content_type}

## Evaluation Summary

| Model | ROUGE-1 | ROUGE-2 | ROUGE-L | Structure Similarity | Implementation | Overall |
|-------|---------|---------|---------|---------------------|----------------|---------|
"""
    
    # Add model results
    for model, rouge, structure_sim, impl_score, _, overall in results:
        structure_score = structure_sim['overall'] if isinstance(structure_sim, dict) and 'overall' in structure_sim else 0
        report += f"| {model} | {rouge['rouge1_f1']:.4f} | {rouge['rouge2_f1']:.4f} | {rouge['rouge1_f1']:.4f} | "
        report += f"{structure_score:.4f} | {impl_score:.4f} | {overall:.4f} |\n"
    
    # Determine best model
    best_model = max(results, key=lambda x: x[5])
    report += f"\n**Best Model:** {best_model[0]} (Score: {best_model[5]:.4f})\n\n"
    
    # Add detailed metrics
    report += "## Detailed Metrics\n\n"
    
    for model, rouge, structure_sim, impl_score, impl_details, _ in results:
        report += f"### {model}\n\n"
        
        # ROUGE metrics
        report += "#### ROUGE Metrics\n\n"
        report += "| Metric | Precision | Recall | F1 |\n"
        report += "|--------|-----------|--------|----|\n"
        report += f"| ROUGE-1 | {rouge['rouge1_precision']:.4f} | {rouge['rouge1_recall']:.4f} | {rouge['rouge1_f1']:.4f} |\n"
        report += f"| ROUGE-2 | {rouge['rouge2_precision']:.4f} | {rouge['rouge2_recall']:.4f} | {rouge['rouge2_f1']:.4f} |\n"
        report += f"| ROUGE-L | {rouge['rougeL_precision']:.4f} | {rouge['rougeL_recall']:.4f} | {rouge['rougeL_f1']:.4f} |\n\n"
        
        # Structure similarity based on content type
        if isinstance(structure_sim, dict) and 'overall' in structure_sim:
            report += f"#### {content_type.title()} Structure Similarity\n\n"
            report += "| Metric | Score |\n"
            report += "|--------|-------|\n"
            
            for key, value in structure_sim.items():
                if key != 'overall':  # We'll add overall at the end
                    report += f"| {key.replace('_', ' ').title()} | {value:.4f} |\n"
            
            report += f"| Overall | {structure_sim['overall']:.4f} |\n\n"
        
        # Implementation details
        if impl_details:
            report += "#### Implementation Details\n\n"
            report += "| Feature | Score | Explanation |\n"
            report += "|---------|-------|-------------|\n"
            
            for feature, score in impl_details.items():
                explanation = model_details[model].get(feature, "No explanation available")
                report += f"| {feature.replace('_', ' ').title()} | {score:.2f} | {explanation} |\n"
            
            report += "\n"
        
        # Content characteristics
        if 'characteristics' in model_details[model]:
            report += "#### Content Characteristics\n\n"
            report += "| Characteristic | Value |\n"
            report += "|---------------|-------|\n"
            
            for key, value in model_details[model]['characteristics'].items():
                if isinstance(value, bool):
                    report += f"| {key.replace('_', ' ').title()} | {'Yes' if value else 'No'} |\n"
                else:
                    report += f"| {key.replace('_', ' ').title()} | {value} |\n"
            
            report += "\n"
    
    # Strengths and weaknesses
    report += "## Strengths and Weaknesses\n\n"
    
    for model, rouge, structure_sim, impl_score, impl_details, _ in results:
        report += f"### {model}\n\n"
        
        # Strengths
        report += "#### Strengths\n\n"
        strengths = []
        if rouge['rouge1_f1'] > 0.5:
            strengths.append(f"High ROUGE-1 score ({rouge['rouge1_f1']:.4f}), indicating good content overlap with reference")
        if rouge['rouge2_f1'] > 0.4:
            strengths.append(f"High ROUGE-2 score ({rouge['rouge2_f1']:.4f}), showing good phrase matching with reference")
        
        structure_score = structure_sim.get('overall', 0) if isinstance(structure_sim, dict) else 0
        if structure_score > 0.5:
            strengths.append(f"Good {content_type} structure similarity ({structure_score:.4f})")
        
        # Find top implementation features
        if impl_details:
            top_features = sorted(impl_details.items(), key=lambda x: x[1], reverse=True)[:3]
            for feature, score in top_features:
                if score > 0.5:
                    strengths.append(f"Strong {feature.replace('_', ' ')} implementation (Score: {score:.2f})")
        
        # Add characteristics-based strengths
        if 'characteristics' in model_details[model]:
            chars = model_details[model]['characteristics']
            
            # Content-type specific strengths
            if content_type == 'html':
                if chars.get('has_basic_structure', False):
                    strengths.append("Uses proper HTML document structure")
                if chars.get('semantic_element_count', 0) >= 3:
                    strengths.append(f"Good use of semantic HTML ({chars['semantic_element_count']} elements)")
                if chars.get('tailwind_class_count', 0) >= 10:
                    strengths.append(f"Extensive use of Tailwind CSS ({chars['tailwind_class_count']} classes)")
            elif content_type in ('python', 'py'):
                if chars.get('has_docstrings', False):
                    strengths.append("Includes docstrings for better code documentation")
                if chars.get('has_error_handling', False):
                    strengths.append("Implements proper error handling with try/except")
                if chars.get('list_comprehension_count', 0) > 0:
                    strengths.append(f"Uses Pythonic list comprehensions ({chars['list_comprehension_count']} instances)")
            elif content_type in ('javascript', 'js'):
                if chars.get('const_var_count', 0) > chars.get('var_var_count', 0):
                    strengths.append("Uses modern variable declarations (const/let) over var")
                if chars.get('template_literal_count', 0) > 0:
                    strengths.append("Uses template literals for string formatting")
                if chars.get('async_function_count', 0) > 0:
                    strengths.append("Implements async/await pattern for asynchronous code")
        
        if strengths:
            for s in strengths:
                report += f"- {s}\n"
        else:
            report += "- No significant strengths identified\n"
        
        # Weaknesses
        report += "\n#### Weaknesses\n\n"
        weaknesses = []
        if rouge['rouge1_f1'] < 0.3:
            weaknesses.append(f"Low ROUGE-1 score ({rouge['rouge1_f1']:.4f}), indicating poor content overlap with reference")
        
        if structure_score < 0.3:
            weaknesses.append(f"Poor {content_type} structure similarity ({structure_score:.4f})")
        
        # Find bottom implementation features
        if impl_details:
            bottom_features = sorted(impl_details.items(), key=lambda x: x[1])[:3]
            for feature, score in bottom_features:
                if score < 0.3:
                    weaknesses.append(f"Weak {feature.replace('_', ' ')} implementation (Score: {score:.2f})")
        
        # Add characteristics-based weaknesses
        if 'characteristics' in model_details[model]:
            chars = model_details[model]['characteristics']
            
            # Content-type specific weaknesses
            if content_type == 'html':
                if not chars.get('has_basic_structure', False):
                    weaknesses.append("Missing proper HTML document structure")
                if chars.get('semantic_element_count', 0) < 2:
                    weaknesses.append("Limited use of semantic HTML elements")
                if chars.get('inline_css_count', 0) > 5 and not chars.get('has_internal_css', False):
                    weaknesses.append("Relies heavily on inline styles rather than structured CSS")
            elif content_type in ('python', 'py'):
                if not chars.get('has_docstrings', False):
                    weaknesses.append("Missing docstrings for code documentation")
                if not chars.get('has_error_handling', False) and chars.get('estimated_complexity', 0) > 5:
                    weaknesses.append("Complex code without error handling")
                if chars.get('comment_count', 0) < chars.get('non_empty_line_count', 0) / 10:
                    weaknesses.append("Low comment-to-code ratio")
            elif content_type in ('javascript', 'js'):
                if chars.get('var_var_count', 0) > chars.get('const_var_count', 0) + chars.get('let_var_count', 0):
                    weaknesses.append("Uses outdated var declarations over modern const/let")
                if not chars.get('has_error_handling', False) and chars.get('promise_usage_count', 0) > 0:
                    weaknesses.append("Uses promises without proper error handling")
        
        if weaknesses:
            for w in weaknesses:
                report += f"- {w}\n"
        else:
            report += "- No significant weaknesses identified\n"
        
        report += "\n"
    
    # Write report to file
    report_path = f"{output_dir}/evaluation_report_{timestamp}.md"
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Evaluation report saved to {report_path}")
    except Exception as e:
        print(f"Error saving report: {e}")
        
    # Return report as a string too
    return report

def evaluate_responses(file_path, config_path=None, output_dir=None, save_plots=True):
    """Evaluate responses from different models with enhanced metrics and reporting
    
    Args:
        file_path: Path to the file with responses
        config_path: Path to configuration file (optional)
        output_dir: Directory to save outputs
        save_plots: Whether to save visualization plots
        
    Returns:
        List of evaluation results
    """
    # Set up output directory
    if output_dir is None:
        output_dir = '.'
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Load configuration
    config = None
    if config_path:
        try:
            if config_path.endswith('.json'):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            elif config_path.endswith(('.yaml', '.yml')):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            else:
                print(f"Unsupported config file format: {config_path}")
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Extract content from file
    print("\nReading file and extracting content...")
    format_config = config.get('file_format', None) if config else None
    content = extract_content_from_file(file_path, format_config)
    
    if not content:
        print("Failed to extract content from file. Please check the file format.")
        return
    
    # Print question for reference
    print("\n--- Question ---")
    print(content['question'][:200] + "..." if len(content['question']) > 200 else content['question'])
    print("----------------\n")
    
    # Detect content type if not specified in config
    content_type = config.get('content_type', None) if config else None
    if not content_type:
        content_type = detect_content_type(content['standard_answer'])
        print(f"Detected content type: {content_type}")
    
    # Extract content based on type
    print(f"Extracting and analyzing {content_type} content...")
    if content_type == 'html':
        standard_content = extract_html_content(content['standard_answer'])
        extracted_contents = {model: extract_html_content(resp) for model, resp in content['responses'].items()}
    else:
        standard_content = extract_code_content(content['standard_answer'], content_type)
        extracted_contents = {model: extract_code_content(resp, content_type) for model, resp in content['responses'].items()}
    
    # Extract content characteristics
    print("Analyzing content characteristics...")
    standard_chars = extract_content_characteristics(standard_content, content_type)
    content_chars = {model: extract_content_characteristics(cont, content_type) for model, cont in extracted_contents.items()}
    
    # Preprocess texts for evaluation
    print("Preprocessing text for ROUGE evaluation...")
    standard_text = preprocess_text(content['standard_answer'])
    preprocessed_texts = {model: preprocess_text(resp) for model, resp in content['responses'].items()}
    
    # Calculate ROUGE scores
    print("Calculating ROUGE scores...")
    rouge_scores = {model: calculate_rouge_scores(standard_text, text) for model, text in preprocessed_texts.items()}
    
    # Calculate structure similarity based on content type
    print(f"Calculating {content_type} structure similarity...")
    if content_type == 'html':
        structure_sims = {model: html_structure_similarity(standard_content, cont) for model, cont in extracted_contents.items()}
    else:
        structure_sims = {model: code_structure_similarity(standard_content, cont, content_type) for model, cont in extracted_contents.items()}
    
    # Load requirements based on content type and config
    requirements = load_requirements(config_path, content_type)
    
    # Score implementation
    print("Scoring implementation...")
    impl_scores = {}
    impl_details = {}
    impl_explanations = {}
    
    for model, cont in extracted_contents.items():
        score, details, explanations = implementation_score(cont, requirements, content_type)
        impl_scores[model] = score
        impl_details[model] = details
        impl_explanations[model] = explanations
    
    # Store model details
    model_details = {}
    for model in content['responses'].keys():
        model_details[model] = {
            "characteristics": content_chars.get(model, {}),
            **impl_explanations.get(model, {})
        }
    
    # Calculate overall score (weighted average)
    # Get weights from config or use defaults
    weights = config.get('weights', {}) if config else {}
    if not weights:
        weights = {
            'rouge1': 0.15,
            'rouge2': 0.15,
            'rougeL': 0.10,
            'structure': 0.30,
            'impl': 0.30
        }
    
    # Compile results
    print("Compiling and analyzing results...")
    results = []
    
    for model in content['responses'].keys():
        rouge = rouge_scores.get(model, {})
        structure_sim = structure_sims.get(model, {'overall': 0})
        impl_score = impl_scores.get(model, 0)
        details = impl_details.get(model, {})
        
        overall = (
            rouge.get('rouge1_f1', 0) * weights.get('rouge1', 0.15) +
            rouge.get('rouge2_f1', 0) * weights.get('rouge2', 0.15) +
            rouge.get('rougeL_f1', 0) * weights.get('rougeL', 0.10) +
            structure_sim.get('overall', 0) * weights.get('structure', 0.30) +
            impl_score * weights.get('impl', 0.30)
        )
        
        results.append((model, rouge, structure_sim, impl_score, details, overall))
    
    # Sort results by overall score (descending)
    results.sort(key=lambda x: x[5], reverse=True)
    
    # Print summary results
    print("\n" + "="*60)
    print("EVALUATION RESULTS SUMMARY")
    print("="*60)
    
    print(f"{'Model':<12} {'ROUGE-1':<10} {'ROUGE-2':<10} {'ROUGE-L':<10} {'Structure':<10} {'Impl Score':<10} {'Overall':<10}")
    print("-" * 75)
    
    for model, rouge, structure_sim, impl_score, _, overall in results:
        structure_score = structure_sim.get('overall', 0)
        print(f"{model:<12} {rouge.get('rouge1_f1', 0):<10.4f} {rouge.get('rouge2_f1', 0):<10.4f} {rouge.get('rougeL_f1', 0):<10.4f} "
              f"{structure_score:<10.4f} {impl_score:<10.4f} {overall:<10.4f}")
    
    best_model = results[0][0]
    best_score = results[0][5]
    print(f"\nBest model: {best_model} (Score: {best_score:.4f})")
    
    # Print detailed analysis for each model
    print("\n" + "="*60)
    print("DETAILED ANALYSIS")
    print("="*60)
    
    for model, rouge, structure_sim, impl_score, impl_details, overall in results:
        print(f"\n--- {model} Analysis ---")
        
        # ROUGE scores analysis
        print("\nROUGE Metrics:")
        rouge1_f1 = rouge.get('rouge1_f1', 0)
        rouge2_f1 = rouge.get('rouge2_f1', 0)
        rougeL_f1 = rouge.get('rougeL_f1', 0)
        
        print(f"  ROUGE-1: {rouge1_f1:.4f} (Precision: {rouge.get('rouge1_precision', 0):.4f}, Recall: {rouge.get('rouge1_recall', 0):.4f})")
        print(f"  ROUGE-2: {rouge2_f1:.4f} (Precision: {rouge.get('rouge2_precision', 0):.4f}, Recall: {rouge.get('rouge2_recall', 0):.4f})")
        print(f"  ROUGE-L: {rougeL_f1:.4f} (Precision: {rouge.get('rougeL_precision', 0):.4f}, Recall: {rouge.get('rougeL_recall', 0):.4f})")
        
        if rouge1_f1 > 0.7:
            print("  ✓ Excellent content overlap with reference answer")
        elif rouge1_f1 > 0.5:
            print("  ✓ Good content overlap with reference answer")
        elif rouge1_f1 < 0.3:
            print("  ✗ Poor content overlap with reference answer")
            
        if rouge2_f1 > 0.6:
            print("  ✓ Excellent phrase matching with reference")
        elif rouge2_f1 < 0.2:
            print("  ✗ Poor phrase matching with reference")
        
        # Structure analysis
        print(f"\n{content_type.title()} Structure Analysis:")
        structure_score = structure_sim.get('overall', 0)
        for key, value in structure_sim.items():
            if key != 'overall':
                print(f"  {key.replace('_', ' ').title()}: {value:.4f}")
        print(f"  Overall Structure Similarity: {structure_score:.4f}")
        
        if structure_score > 0.7:
            print(f"  ✓ Excellent {content_type} structure similarity")
        elif structure_score > 0.5:
            print(f"  ✓ Good {content_type} structure similarity")
        elif structure_score < 0.3:
            print(f"  ✗ Poor {content_type} structure similarity")
        
        # Content characteristics
        chars = model_details[model]['characteristics']
        print(f"\n{content_type.title()} Characteristics:")
        
        # Print common characteristics
        print(f"  Total Lines: {chars.get('total_lines', 0)}")
        print(f"  Avg Line Length: {chars.get('avg_line_length', 0):.2f} chars")
        
        # Print content-type specific characteristics
        if content_type == 'html':
            print(f"  Total Elements: {chars.get('total_elements', 0)}")
            print(f"  Basic HTML Structure: {'Yes' if chars.get('has_basic_structure', False) else 'No'}")
            print(f"  Semantic Elements: {chars.get('semantic_element_count', 0)}")
            print(f"  Has Form: {'Yes' if chars.get('has_form', False) else 'No'}")
            print(f"  Has Images: {'Yes' if chars.get('has_images', False) else 'No'}")
        elif content_type in ('python', 'py'):
            print(f"  Functions: {chars.get('function_count', 0)}")
            print(f"  Classes: {chars.get('class_count', 0)}")
            print(f"  Has Docstrings: {'Yes' if chars.get('has_docstrings', False) else 'No'}")
            print(f"  Error Handling: {'Yes' if chars.get('has_error_handling', False) else 'No'}")
            print(f"  Comments: {chars.get('comment_count', 0)}")
        elif content_type in ('javascript', 'js'):
            print(f"  Functions: {chars.get('total_function_count', 0)}")
            print(f"  Modern JS (const/let): {chars.get('const_var_count', 0) + chars.get('let_var_count', 0)}")
            print(f"  Legacy JS (var): {chars.get('var_var_count', 0)}")
            print(f"  Error Handling: {'Yes' if chars.get('has_error_handling', False) else 'No'}")
            print(f"  Comments: {chars.get('total_comment_count', 0)}")
        
        # Implementation details
        if impl_details:
            print("\nImplementation Details:")
            for feature, score in impl_details.items():
                explanation = model_details[model].get(feature, "N/A")
                symbol = "✓" if score >= 0.5 else "✗"
                print(f"  {symbol} {feature.replace('_', ' ').title()}: {score:.2f} - {explanation}")
        
        # Overall verdict
        print("\nOverall Assessment:")
        if overall > 0.7:
            print(f"  EXCELLENT: {model} delivers an exceptional implementation (Score: {overall:.4f})")
        elif overall > 0.5:
            print(f"  GOOD: {model} provides a solid implementation (Score: {overall:.4f})")
        elif overall > 0.3:
            print(f"  FAIR: {model} delivers an adequate implementation (Score: {overall:.4f})")
        else:
            print(f"  POOR: {model} implementation needs significant improvement (Score: {overall:.4f})")
    
    # Create visualizations
    if save_plots:
        print("\nGenerating visualizations...")
        plot_path = f"{output_dir}/evaluation_plot_{timestamp}.png"
        
        # Prepare plot configuration
        plot_config = config.get('plot_config', None) if config else None
        plot_evaluation_results(results, plot_config, plot_path)
    
    # Generate full report
    print("\nGenerating comprehensive evaluation report...")
    report = generate_evaluation_report(results, model_details, file_path, config, output_dir)
    
    return results

def create_default_config(output_path='config.json'):
    """Create a default configuration file for the evaluation script
    
    Args:
        output_path: Path to save the configuration file
    """
    default_config = {
        # File format configuration
        "file_format": {
            "question_pattern": r'Question:\s*"(.*?)"\s*-+',
            "standard_answer_pattern": r'Standard Answer(?:\s*Code)?:\s*"(.*?)"\s*-+',
            "model_patterns": {
                "gpt": r'GPT:\s*"(.*?)"\s*----',
                "gemini": r'GEMINI:\s*"(.*?)"\s*----',
                "rag": r'RAG SYSTEM:\s*"(.*?)"$'
            }
        },
        
        # Content type (auto-detected if not specified)
        "content_type": None,  # Can be "html", "python", "javascript", etc.
        
        # Evaluation weights
        "weights": {
            "rouge1": 0.15,
            "rouge2": 0.15,
            "rougeL": 0.10,
            "structure": 0.30,
            "impl": 0.30
        },
        
        # Visualization configuration
        "plot_config": {
            "main_metrics": ["ROUGE-1", "ROUGE-2", "ROUGE-L", "Structure", "Implementation"],
            "implementation_features": None  # Will use all available features
        },
        
        # Requirements for various content types
        "requirements": {
            "html": {
                "responsive_design": {
                    "description": "Responsive design implementation",
                    "patterns": ["sm:", "md:", "lg:", "xl:", "@media", "flex", "grid"],
                    "weight": 1
                },
                "semantic_html": {
                    "description": "Use of semantic HTML elements",
                    "patterns": ["<header", "<nav", "<main", "<section", "<article", "<aside", "<footer"],
                    "weight": 1
                },
                "accessibility": {
                    "description": "Accessibility features",
                    "patterns": ["aria-", "role=", "alt=", "tabindex", "<label"],
                    "weight": 1
                }
            },
            "python": {
                "code_organization": {
                    "description": "Well-organized code structure",
                    "patterns": ["def\\s+", "class\\s+", "if\\s+__name__\\s*=="],
                    "weight": 1
                },
                "error_handling": {
                    "description": "Proper error handling",
                    "patterns": ["try:", "except", "finally:", "raise\\s+"],
                    "weight": 1
                },
                "documentation": {
                    "description": "Code documentation",
                    "patterns": ["\"\"\"", "#\\s+\\w+", "'''"],
                    "weight": 1
                }
            },
            "javascript": {
                "modern_js": {
                    "description": "Modern JavaScript features",
                    "patterns": ["const\\s+", "let\\s+", "=>", "...", "async", "await"],
                    "weight": 1
                },
                "error_handling": {
                    "description": "Proper error handling",
                    "patterns": ["try\\s*{", "catch", "finally", ".catch("],
                    "weight": 1
                },
                "code_organization": {
                    "description": "Well-organized code",
                    "patterns": ["function\\s+", "class\\s+", "import\\s+", "export\\s+"],
                    "weight": 1
                }
            }
            # You can add more content types and custom requirements
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2)
    
    print(f"Default configuration saved to {output_path}")
    print("You can modify this file to customize the evaluation process.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Versatile evaluation script for comparing model responses.")
    parser.add_argument("--file", help="Input file containing the question and responses.")
    parser.add_argument("--config", help="Configuration file (JSON or YAML).")
    parser.add_argument("--output-dir", default="evaluation_results", help="Directory to store evaluation results.")
    parser.add_argument("--create-config", action="store_true", help="Create a default configuration file.")
    parser.add_argument("--no-plots", action="store_true", help="Skip generating plots.")
    
    args = parser.parse_args()
    
    if args.create_config:
        create_default_config('evaluation_config.json')
    elif args.file:
        evaluate_responses(
            file_path=args.file, 
            config_path=args.config, 
            output_dir=args.output_dir,
            save_plots=not args.no_plots
        )
    else:
        parser.print_help()