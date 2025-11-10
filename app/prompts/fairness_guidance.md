# Fairness Guidance Prompt

## Task
Review recruitment process and candidate evaluations to ensure fairness, diversity, and inclusion principles are maintained throughout the hiring decision.

## Fairness Assessment Framework

### 1. Bias Detection and Mitigation
Identify potential bias sources in evaluation:
- **Confirmation Bias**: Seeking information that confirms initial impressions
- **Affinity Bias**: Favoring candidates similar to evaluators
- **Halo Effect**: Allowing one positive trait to influence overall assessment
- **Stereotype Threat**: Unconscious assumptions about candidate groups

### 2. Diversity and Inclusion Review
Evaluate representation and inclusion factors:
- **Demographic Diversity**: Balance across gender, ethnicity, age, background
- **Cognitive Diversity**: Range of thinking styles, experiences, perspectives
- **Inclusive Language**: Review job descriptions and communications
- **Accessibility**: Ensure process accommodates diverse candidate needs

### 3. Process Fairness Evaluation
Assess hiring process equity:
- **Consistent Criteria**: Application of same standards to all candidates
- **Transparent Process**: Clear communication of evaluation methods
- **Feedback Quality**: Constructive, actionable candidate feedback
- **Appeal Mechanisms**: Processes for addressing candidate concerns

### 4. Outcome Analysis
Review hiring outcomes for patterns:
- **Success Metrics**: Beyond hire rates to include retention, performance
- **Adverse Impact**: Statistical analysis of selection rates by group
- **Quality Indicators**: Assessment of hire quality and team fit
- **Continuous Improvement**: Recommendations for process enhancement

## Output Structure
Provide comprehensive fairness assessment with:
- **Bias Risk Assessment**: Identified potential bias areas with mitigation strategies
- **Diversity Metrics**: Current representation analysis and improvement targets
- **Process Recommendations**: Specific changes to enhance fairness
- **Monitoring Framework**: Ongoing evaluation and adjustment mechanisms

## Implementation Guidelines
- Focus on systemic improvements rather than individual blame
- Use data-driven approaches to identify and address disparities
- Implement blind review processes where appropriate
- Provide training and awareness for hiring team members
- Establish accountability measures for fairness commitments

## REQUIRED JSON OUTPUT FORMAT
Return ONLY a JSON object with one of these exact structures:

**Option 1 - Standard format:**
```json
{
  "fairness_guidance": [
    {
      "label": "Bias Mitigation Strategy",
      "value": "Implement blind resume review process to reduce unconscious bias...",
      "helper": "Optional explanation or additional context"
    }
  ]
}
```

**Option 2 - Alternative format:**
```json
{
  "fairness": [
    {
      "label": "Diversity Monitoring",
      "value": "Track candidate demographics and selection rates by group...",
      "helper": "Optional explanation"
    }
  ]
}
```

Each item in the array MUST have:
- `label`: A descriptive title (string)
- `value`: The detailed guidance or strategy (string)
- `helper`: Optional additional explanation or context (string, can be null)

Do not include any markdown formatting, code blocks, or additional text. Return only the JSON object.