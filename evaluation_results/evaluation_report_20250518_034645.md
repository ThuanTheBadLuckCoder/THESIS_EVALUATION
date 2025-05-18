# Model Response Evaluation Report
    
## Overview
- **Evaluation Date:** 2025-05-18 03:46:45
- **Input File:** more-complex-prompt.txt
- **Content Type:** html

## Evaluation Summary

| Model | ROUGE-1 | ROUGE-2 | ROUGE-L | Structure Similarity | Implementation | Overall |
|-------|---------|---------|---------|---------------------|----------------|---------|
| rag | 0.2514 | 0.1878 | 0.2514 | 0.6697 | 0.5549 | 0.4584 |
| gpt | 0.1860 | 0.0845 | 0.1860 | 0.6245 | 0.5363 | 0.4046 |
| gemini | 0.1407 | 0.0448 | 0.1407 | 0.6035 | 0.5252 | 0.3768 |

**Best Model:** rag (Score: 0.4584)

## Detailed Metrics

### rag

#### ROUGE Metrics

| Metric | Precision | Recall | F1 |
|--------|-----------|--------|----|
| ROUGE-1 | 0.4600 | 0.1729 | 0.2514 |
| ROUGE-2 | 0.3469 | 0.1288 | 0.1878 |
| ROUGE-L | 0.4600 | 0.1729 | 0.2514 |

#### Html Structure Similarity

| Metric | Score |
|--------|-------|
| Jaccard | 0.6512 |
| Tag Presence | 0.7778 |
| Sequence Similarity | 0.7500 |
| Attribute Similarity | 0.5000 |
| Overall | 0.6697 |

#### Implementation Details

| Feature | Score | Explanation |
|---------|-------|-------------|
| Semantic Structure | 0.00 | No relevant patterns found |
| Responsive Design | 1.00 | Found 7 relevant patterns: sm:, lg:, flex-col and 4 more |
| Accessibility | 0.00 | No relevant patterns found |
| Tailwind Layout | 1.00 | Found 6 relevant patterns: flex, grid, cols- and 3 more |
| Tailwind Spacing | 0.73 | Found 5 relevant patterns: p-, px-, py- and 2 more |
| Tailwind Typography | 0.62 | Found 4 relevant patterns: text-, font-, tracking- and 1 more |
| Tailwind Colors | 0.73 | Found 5 relevant patterns: bg-, text-, border- and 2 more |
| Tailwind Effects | 0.16 | Found 1 relevant patterns: transform |
| Tailwind Borders | 0.60 | Found 3 relevant patterns: border, rounded-, shadow- |
| Tailwind Interactivity | 0.00 | No relevant patterns found |
| Form Elements | 0.00 | No relevant patterns found |
| Dark Theme | 0.00 | No relevant patterns found |
| Image Handling | 0.70 | Found 5 relevant patterns: <img, object-, w- and 2 more |
| Interactive Cta | 0.62 | Found 4 relevant patterns: shadow, bg-, text- and 1 more |

#### Content Characteristics

| Characteristic | Value |
|---------------|-------|
| Total Lines | 67 |
| Avg Line Length | 44.0 |
| Total Elements | 35 |
| Has Doctype | Yes |
| Has Html Tag | Yes |
| Has Head | Yes |
| Has Body | Yes |
| Has Basic Structure | Yes |
| Inline Css Count | 0 |
| Has Internal Css | Yes |
| Has External Css | No |
| Inline Js Count | 1 |
| Has Internal Js | Yes |
| Has External Js | Yes |
| Has Form | No |
| Has Images | Yes |
| Has Buttons | No |
| Has Links | No |
| Tailwind Class Count | 19 |
| Semantic Element Count | 0 |

### gpt

#### ROUGE Metrics

| Metric | Precision | Recall | F1 |
|--------|-----------|--------|----|
| ROUGE-1 | 0.2439 | 0.1504 | 0.1860 |
| ROUGE-2 | 0.1111 | 0.0682 | 0.0845 |
| ROUGE-L | 0.2073 | 0.1278 | 0.1581 |

#### Html Structure Similarity

| Metric | Score |
|--------|-------|
| Jaccard | 0.5814 |
| Tag Presence | 0.7778 |
| Sequence Similarity | 0.6389 |
| Attribute Similarity | 0.5000 |
| Overall | 0.6245 |

#### Implementation Details

| Feature | Score | Explanation |
|---------|-------|-------------|
| Semantic Structure | 0.20 | Found 1 relevant patterns: <section |
| Responsive Design | 1.00 | Found 7 relevant patterns: sm:, md:, lg: and 4 more |
| Accessibility | 0.16 | Found 1 relevant patterns: alt= |
| Tailwind Layout | 1.00 | Found 5 relevant patterns: grid, cols-, gap- and 2 more |
| Tailwind Spacing | 0.80 | Found 7 relevant patterns: p-, px-, py- and 4 more |
| Tailwind Typography | 0.31 | Found 2 relevant patterns: text-, font- |
| Tailwind Colors | 0.58 | Found 4 relevant patterns: bg-, text-, border- and 1 more |
| Tailwind Effects | 0.00 | No relevant patterns found |
| Tailwind Borders | 0.40 | Found 2 relevant patterns: border, rounded- |
| Tailwind Interactivity | 0.00 | No relevant patterns found |
| Form Elements | 0.18 | Found 1 relevant patterns: placeholder |
| Dark Theme | 0.00 | No relevant patterns found |
| Image Handling | 0.70 | Found 5 relevant patterns: <img, object-, w- and 2 more |
| Interactive Cta | 0.62 | Found 4 relevant patterns: shadow, bg-, text- and 1 more |

#### Content Characteristics

| Characteristic | Value |
|---------------|-------|
| Total Lines | 78 |
| Avg Line Length | 38.705128205128204 |
| Total Elements | 32 |
| Has Doctype | Yes |
| Has Html Tag | Yes |
| Has Head | Yes |
| Has Body | Yes |
| Has Basic Structure | Yes |
| Inline Css Count | 0 |
| Has Internal Css | Yes |
| Has External Css | No |
| Inline Js Count | 1 |
| Has Internal Js | Yes |
| Has External Js | Yes |
| Has Form | No |
| Has Images | Yes |
| Has Buttons | No |
| Has Links | No |
| Tailwind Class Count | 14 |
| Semantic Element Count | 1 |

### gemini

#### ROUGE Metrics

| Metric | Precision | Recall | F1 |
|--------|-----------|--------|----|
| ROUGE-1 | 0.1387 | 0.1429 | 0.1407 |
| ROUGE-2 | 0.0441 | 0.0455 | 0.0448 |
| ROUGE-L | 0.1022 | 0.1053 | 0.1037 |

#### Html Structure Similarity

| Metric | Score |
|--------|-------|
| Jaccard | 0.6364 |
| Tag Presence | 0.7222 |
| Sequence Similarity | 0.7222 |
| Attribute Similarity | 0.3333 |
| Overall | 0.6035 |

#### Implementation Details

| Feature | Score | Explanation |
|---------|-------|-------------|
| Semantic Structure | 0.00 | No relevant patterns found |
| Responsive Design | 1.00 | Found 7 relevant patterns: sm:, lg:, hidden and 4 more |
| Accessibility | 0.16 | Found 1 relevant patterns: alt= |
| Tailwind Layout | 0.80 | Found 4 relevant patterns: grid, cols-, gap- and 1 more |
| Tailwind Spacing | 0.80 | Found 6 relevant patterns: p-, px-, py- and 3 more |
| Tailwind Typography | 0.31 | Found 2 relevant patterns: text-, font- |
| Tailwind Colors | 0.58 | Found 4 relevant patterns: bg-, text-, border- and 1 more |
| Tailwind Effects | 0.16 | Found 1 relevant patterns: transform |
| Tailwind Borders | 0.60 | Found 3 relevant patterns: border, rounded-, shadow- |
| Tailwind Interactivity | 0.15 | Found 1 relevant patterns: pointer-events- |
| Form Elements | 0.18 | Found 1 relevant patterns: placeholder |
| Dark Theme | 0.00 | No relevant patterns found |
| Image Handling | 0.47 | Found 3 relevant patterns: <img, w-, h- |
| Interactive Cta | 0.62 | Found 4 relevant patterns: shadow, bg-, text- and 1 more |

#### Content Characteristics

| Characteristic | Value |
|---------------|-------|
| Total Lines | 75 |
| Avg Line Length | 53.093333333333334 |
| Total Elements | 36 |
| Has Doctype | Yes |
| Has Html Tag | Yes |
| Has Head | Yes |
| Has Body | Yes |
| Has Basic Structure | Yes |
| Inline Css Count | 0 |
| Has Internal Css | Yes |
| Has External Css | Yes |
| Inline Js Count | 1 |
| Has Internal Js | No |
| Has External Js | No |
| Has Form | No |
| Has Images | Yes |
| Has Buttons | No |
| Has Links | No |
| Tailwind Class Count | 18 |
| Semantic Element Count | 0 |

## Strengths and Weaknesses

### rag

#### Strengths

- Good html structure similarity (0.6697)
- Strong responsive design implementation (Score: 1.00)
- Strong tailwind layout implementation (Score: 1.00)
- Strong tailwind spacing implementation (Score: 0.73)
- Uses proper HTML document structure
- Extensive use of Tailwind CSS (19 classes)

#### Weaknesses

- Low ROUGE-1 score (0.2514), indicating poor content overlap with reference
- Weak semantic structure implementation (Score: 0.00)
- Weak accessibility implementation (Score: 0.00)
- Weak tailwind interactivity implementation (Score: 0.00)
- Limited use of semantic HTML elements

### gpt

#### Strengths

- Good html structure similarity (0.6245)
- Strong responsive design implementation (Score: 1.00)
- Strong tailwind layout implementation (Score: 1.00)
- Strong tailwind spacing implementation (Score: 0.80)
- Uses proper HTML document structure
- Extensive use of Tailwind CSS (14 classes)

#### Weaknesses

- Low ROUGE-1 score (0.1860), indicating poor content overlap with reference
- Weak tailwind effects implementation (Score: 0.00)
- Weak tailwind interactivity implementation (Score: 0.00)
- Weak dark theme implementation (Score: 0.00)
- Limited use of semantic HTML elements

### gemini

#### Strengths

- Good html structure similarity (0.6035)
- Strong responsive design implementation (Score: 1.00)
- Strong tailwind layout implementation (Score: 0.80)
- Strong tailwind spacing implementation (Score: 0.80)
- Uses proper HTML document structure
- Extensive use of Tailwind CSS (18 classes)

#### Weaknesses

- Low ROUGE-1 score (0.1407), indicating poor content overlap with reference
- Weak semantic structure implementation (Score: 0.00)
- Weak dark theme implementation (Score: 0.00)
- Weak tailwind interactivity implementation (Score: 0.15)
- Limited use of semantic HTML elements

