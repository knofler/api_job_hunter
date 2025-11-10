# Engagement Plan Prompt

## Task
Develop a comprehensive engagement strategy for top candidates, focusing on communication, relationship building, and conversion optimization.

## Strategy Components

### 1. Communication Cadence
Design multi-touch outreach sequence:
- **Initial Contact**: Personalized introduction and value proposition
- **Follow-up Schedule**: Strategic timing for subsequent interactions
- **Content Strategy**: Mix of information, questions, and relationship building
- **Channel Selection**: Email, phone, LinkedIn, and other appropriate platforms

### 2. Value Proposition Development
Craft compelling candidate-specific messaging:
- **Role Benefits**: Highlight unique aspects of the position
- **Company Advantages**: Emphasize organizational strengths
- **Growth Opportunities**: Showcase career development potential
- **Cultural Alignment**: Connect candidate values with company culture

### 3. Objection Handling Framework
Prepare responses for common candidate concerns:
- **Compensation Questions**: Address salary, benefits, equity
- **Role Clarity**: Provide detailed job scope and expectations
- **Timeline Concerns**: Explain process duration and decision dates
- **Competition Response**: Differentiate from other opportunities

### 4. Relationship Building Tactics
Develop long-term candidate engagement:
- **Personalization**: Reference specific candidate background and interests
- **Stakeholder Introduction**: Plan connections with team members
- **Process Transparency**: Keep candidates informed of progress
- **Feedback Integration**: Incorporate candidate input into process

## Output Structure
Provide actionable engagement plan with:
- **Communication Timeline**: Day-by-day outreach schedule
- **Key Messages**: Core talking points for each interaction
- **Contingency Responses**: Handling for common objections
- **Success Metrics**: How to measure engagement effectiveness

## Implementation Guidelines
- Balance persistence with respect for candidate time
- Maintain authentic, genuine communication style
- Adapt strategy based on candidate responses and feedback
- Coordinate with hiring team for consistent messaging
- Track engagement metrics and adjust approach accordingly

## REQUIRED JSON OUTPUT FORMAT
Return ONLY a JSON object with one of these exact structures:

**Option 1 - Standard format:**
```json
{
  "engagement_plan": [
    {
      "label": "Communication Timeline",
      "value": "Day 1: Initial contact via email, Day 3: Follow-up call...",
      "helper": "Optional explanation or additional context"
    }
  ]
}
```

**Option 2 - Alternative format:**
```json
{
  "follow_up_actions": [
    {
      "step": "Initial Screening",
      "action": "Assess security skills alignment...",
      "owner": "Recruiter"
    }
  ]
}
```

Each item in the array MUST have:
- For Option 1: `label`, `value`, and optional `helper` fields
- For Option 2: `step`, `action`, and optional `owner` fields

Do not include any markdown formatting, code blocks, or additional text. Return only the JSON object.