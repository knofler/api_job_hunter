# AI Prompts Documentation

This directory contains all AI model prompts used throughout the Job Hunter application. Each prompt is carefully designed to ensure consistent, high-quality AI responses for specific workflow sections.

## Prompt Organization

### File Naming Convention
- `{feature}_{action}.md` - Descriptive names for each prompt file
- All prompts use Markdown format for readability and version control

### Current Prompts

#### Chat & Assistant
- `recruiter_chat_system.md` - Main system prompt for the recruiter chat assistant

#### Workflow Analysis Prompts
- `core_skills_analysis.md` - Identifies critical job skills and evaluates candidate alignment
- `ai_analysis.md` - Comprehensive candidate-job fit assessment with recommendations
- `candidate_ranking.md` - Multi-criteria candidate ranking methodology
- `engagement_plan.md` - Candidate communication and conversion strategies
- `fairness_guidance.md` - Bias detection and diversity assessment framework
- `interview_preparation.md` - Interview question design and evaluation rubrics

## Prompt Development Guidelines

### 1. Structure
Each prompt should include:
- **Task**: Clear description of what the AI should accomplish
- **Analysis Framework**: Step-by-step approach to the task
- **Output Structure**: Expected response format and organization
- **Guidelines**: Specific rules and constraints for responses

### 2. Best Practices
- Use clear, specific language
- Include examples where helpful
- Define evaluation criteria explicitly
- Consider edge cases and error handling
- Maintain ethical and unbiased approaches

### 3. Maintenance
- Review prompts regularly for effectiveness
- Update based on user feedback and performance data
- Document changes and rationale in commit messages
- Test prompt changes in staging environment before production

## Usage in Code

### Backend Integration
Prompts are loaded dynamically by the LLM orchestrator:
```python
def load_system_prompt() -> str:
    prompt_path = os.path.join(PROMPTS_DIR, "recruiter_chat_system.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()
```

### Version Control
- All prompts are tracked in git for change history
- Prompt updates require code review
- Breaking changes should be clearly documented

## Future Enhancements

### Planned Additions
- Resume parsing and analysis prompts
- Job description optimization prompts
- Candidate feedback automation prompts
- Performance prediction model prompts

### Prompt Testing
- Develop automated testing for prompt effectiveness
- A/B testing framework for prompt variations
- User feedback integration for continuous improvement