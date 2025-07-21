# Lead Scoring Agent

This project provides an interactive marketing assistant and lead scoring system for customer conversations. It consists of two main Python files:

---

## 1. LeadScoring.py

**Purpose:**  
Scores the quality of a sales lead based on a chat conversation between a seller and a customer.

**How it works:**
- Uses OpenAI's GPT model to analyze chat text.
- Evaluates the conversation on five criteria:
  1. Purchase intent
  2. Interest in price
  3. Urgency
  4. Engagement
  5. Request for follow-up
- Returns a JSON object with scores (0, 1, or 2) and explanations for each criterion.
- Calculates a total score and classifies the lead as `"interested"`, `"natural"`, or `"non-interested"` based on a threshold.

**Usage:**  
Call the `leadScoring(chat: str, threshold=8)` function with a chat transcript to get a detailed lead score.

---

## 2. LeadScoringAgent.py

**Purpose:**  
Implements an interactive agent that simulates a sales conversation and uses the lead scoring function to evaluate customer interest.

**How it works:**
- Loads a FAQ and a bulk marketing message to provide context for the assistant.
- Uses LangChain and LangGraph to manage conversation flow.
- Starts by sending a bulk message to the user.
- Accepts user input in a loop:
  - If the user types `"lead"`, the conversation is scored using `leadScoring.py` and results are saved to a JSON file.
  - Otherwise, the agent responds to the user's message using the FAQ and marketing context.
- The conversation continues until the user types `"exit"`.

**Usage:**  
Run the script and interact with the assistant. Type `"lead"` to score the current conversation, or `"exit"` to quit.

---

## Example Workflow

1. Start the agent (`LeadScoringAgent.py`).
2. The agent sends a bulk marketing message.
3. You reply as a customer.
4. The agent answers using the FAQ and context.
5. At any time, type `"lead"` to score the conversation and save the results.
6. Type `"exit"` to end the session.

---

## Requirements

- Python 3.10+
- [LangChain](https://python.langchain.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [OpenAI API Key](https://platform.openai.com/)
- `python-dotenv`

---

## Files

- `LeadScoring.py`: Lead scoring logic and criteria.
- `LeadScoringAgent.py`: Interactive agent and conversation manager.

---

## License

This project is for educational and