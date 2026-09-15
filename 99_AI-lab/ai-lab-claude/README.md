# ai-lab-claude: Claude.ai Manual Testing

## 🎯 Purpose
These scripts are designed to be **manually tested in Claude.ai** or **run locally with Anthropic API key**.

## 🚀 Two Ways to Use

### Option 1: Claude.ai (Free, No Setup Required)
Perfect for learning without API costs:

1. Go to: https://claude.ai
2. Copy-paste the example code from any file
3. Ask Claude to explain or run it
4. Test interactively

**Example:**
```
Go to Claude.ai and paste:

"Here's a basic LLM example. Can you explain what this does and help me understand the concepts?

[paste code from 01_basic_llm.py]"
```

### Option 2: Local with API Key
Run the scripts locally (requires API key):

```bash
# 1. Get API key from: https://console.anthropic.com/account/keys

# 2. Install dependencies
pip install anthropic python-dotenv

# 3. Replace API_KEY in any file with your actual key
# Find: API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"
# Replace with: API_KEY = "sk-ant-v4-xxxxxxxxxxxx"

# 4. Run
python 01_basic_llm.py
```

## 📚 File Structure

```
ai-lab-claude/
├── 01_basic_llm.py              ← Start here
├── 02_llm_streaming_structured.py
├── 03_llm_production_wrapper.py
├── 04_rag_ingestion.py
├── 05_rag_retrieval.py
├── 06_advanced_rag.py
├── 07_rag_evaluation.py
├── 08_production_rag.py
├── 09_basic_agent.py
├── 10_agent_tools.py
├── 11_agent_state_memory.py
├── 12_reliable_agent.py
├── 13_secure_agent.py
├── 14_supervisor_agent.py
├── 15_parallel_multi_agent.py
├── 16_mas_state_communication.py
├── 17_mas_reliability.py
├── 18_complete_production_mas.py
├── 19_end_to_end_genai_platform.py
└── 20_architect_interview_exercises.py
```

## 💡 Learning Path

### Path 1: Quick Learning (Copy-Paste into Claude.ai)
1. Copy code from file
2. Go to Claude.ai
3. Paste and ask: "Can you explain this?"
4. Claude explains and helps you understand
5. No setup needed, no API costs

### Path 2: Deep Learning (Run Locally)
1. Get Anthropic API key ($)
2. Replace in scripts
3. Run locally
4. Modify and experiment
5. Small cost (~$1-2 for all 20 examples)

## 🎓 Best For

- ✅ Learning concepts without setup
- ✅ Understanding what each module does
- ✅ Getting help from Claude directly
- ✅ Small-scale testing
- ✅ Zero setup in Claude.ai mode

## ⚡ Quick Example

**In Claude.ai:**
```
"I'm learning about LLMs. Here's example code:

# [Paste code here]

1. What does this code do?
2. How would you modify it to handle errors better?
3. What are 3 key concepts I should understand?"
```

Claude will help you understand everything!

## 📖 Each File Contains

- Clear explanation at the top
- "MUST REMEMBER" section
- Example code
- Key concepts to learn
- How to extend it

## Next: Use ai-lab-ollama

Once you understand the concepts, move to **ai-lab-ollama** folder to run everything locally for free!
