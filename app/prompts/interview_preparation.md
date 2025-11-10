# Interview Preparation Prompt

## Task
Design comprehensive interview questions and evaluation framework for assessing candidate fit across multiple dimensions of the role requirements.

## Interview Structure Design

### 1. Question Categories
Develop balanced question sets covering:
- **Technical Proficiency**: Role-specific skills and competencies
- **Problem-Solving Ability**: Analytical thinking and solution development
- **Experience Validation**: Past performance and achievement verification
- **Cultural Alignment**: Values, work style, and team fit assessment
- **Growth Potential**: Learning agility and career development orientation

### 2. Question Development Framework
For each question category, create:
- **Behavioral Questions**: "Tell me about a time when..." scenarios
- **Situational Questions**: "How would you handle..." hypothetical situations
- **Technical Questions**: Skill-specific assessment items
- **Follow-up Questions**: Probing deeper into initial responses

### 3. Evaluation Rubrics
Establish clear scoring criteria:
- **Response Quality**: Depth, relevance, and insight level
- **Evidence Strength**: Concrete examples and specific achievements
- **Problem-Solving Approach**: Methodology and reasoning process
- **Communication Clarity**: Articulation and professional presentation

### 4. Interview Flow Optimization
Structure efficient interview process:
- **Question Sequencing**: Logical flow from broad to specific
- **Time Allocation**: Appropriate duration for each question type
- **Candidate Comfort**: Balance assessment with positive experience
- **Decision Readiness**: Ensure sufficient information for hiring choice

## Output Structure
Provide complete interview package with:
- **Question Set**: 8-12 carefully crafted questions with context
- **Evaluation Guide**: Scoring criteria and interpretation framework
- **Interview Script**: Suggested flow and timing guidelines
- **Follow-up Protocol**: Additional questions based on initial responses

## Implementation Guidelines
- Balance structured assessment with conversational flow
- Include questions that reveal both competencies and character
- Ensure questions are legally compliant and non-discriminatory
- Test questions for clarity and effectiveness before use
- Provide interviewer training notes for consistent application

## REQUIRED JSON OUTPUT FORMAT
Return ONLY a JSON object with this exact structure:
```json
{
  "interview_preparation": [
    {
      "question": "Tell me about a time when you had to solve a complex technical problem under tight deadline.",
      "rationale": "Assesses problem-solving skills, technical expertise, and ability to work under pressure."
    },
    {
      "question": "How do you approach learning new technologies or frameworks?",
      "rationale": "Evaluates learning agility and continuous improvement mindset."
    }
  ]
}
```

Each item in the interview_preparation array MUST have:
- `question`: The interview question text (string)
- `rationale`: The reason for asking this question and what it assesses (string)

Do not include any markdown formatting, code blocks, or additional text. Return only the JSON object.