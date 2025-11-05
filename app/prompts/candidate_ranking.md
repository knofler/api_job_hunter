# Candidate Ranking Prompt

## Task
Rank candidates based on their overall fit for the position, considering multiple evaluation criteria and providing clear justification for ranking decisions.

## Ranking Methodology

### 1. Multi-Criteria Evaluation
Evaluate candidates across key dimensions:
- **Skills Match**: Alignment with core required competencies
- **Experience Level**: Years and relevance of professional experience
- **Career Trajectory**: Growth pattern and achievement progression
- **Qualification Fit**: Education and certification alignment
- **Potential**: Capacity for growth and adaptation

### 2. Scoring Framework
Assign weighted scores (1-5) for each criterion:
- 5: Exceptional match, significantly exceeds requirements
- 4: Strong match, meets and exceeds in key areas
- 3: Good match, meets requirements adequately
- 2: Below average match, some gaps but potentially addressable
- 1: Poor match, significant gaps or misalignments

### 3. Overall Ranking Logic
- Calculate weighted composite scores
- Consider qualitative factors beyond pure metrics
- Account for role level and seniority requirements
- Balance perfect fits with high-potential candidates

## Output Structure
For each candidate provide:
- **Rank Position**: Numerical ranking (1, 2, 3, etc.)
- **Candidate Name**: Identifier for reference
- **Overall Score**: Composite score out of maximum possible
- **Key Factors**: Top 3 reasons for ranking placement
- **Recommendation**: Suggested next steps (immediate interview, backup, reject)

## Ranking Guidelines
- Prioritize candidates with strongest overall profile fit
- Consider diversity of experience and perspectives
- Balance technical excellence with cultural alignment
- Account for both current capabilities and future potential
- Provide clear, evidence-based ranking rationale