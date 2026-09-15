# 99_AI-lab: Complete Index

## 📁 Folder Structure

```
99_AI-lab/
├── SETUP_GUIDE.md              ← START HERE!
├── INDEX.md                    ← You are here
├── QUICK_START.txt
├── requirements.txt
│
├── ai-lab-claude/              (Anthropic API)
│   ├── README.md
│   ├── 01_basic_llm.py
│   ├── 02_llm_streaming_structured.py
│   ├── 03_llm_production_wrapper.py
│   ├── 04_rag_ingestion.py
│   ├── 05_rag_retrieval.py
│   ├── 06_advanced_rag.py
│   ├── 07_rag_evaluation.py
│   ├── 08_production_rag.py
│   ├── 09_basic_agent.py
│   ├── 10_agent_tools.py
│   ├── 11_agent_state_memory.py
│   ├── 12_reliable_agent.py
│   ├── 13_secure_agent.py
│   ├── 14_supervisor_agent.py
│   ├── 15_parallel_multi_agent.py
│   ├── 16_mas_state_communication.py
│   ├── 17_mas_reliability.py
│   ├── 18_complete_production_mas.py
│   ├── 19_end_to_end_genai_platform.py
│   └── 20_architect_interview_exercises.py
│
└── ai-lab-ollama/              (Local Ollama - FREE)
    ├── README.md
    ├── ollama_base.py
    └── 01_basic_llm.py
```

## 🎯 Quick Links

### For Claude.ai Testing
1. **Setup:** Go to [SETUP_GUIDE.md](SETUP_GUIDE.md) → Path A
2. **Files:** See [ai-lab-claude/README.md](ai-lab-claude/README.md)
3. **Start:** Copy code from `ai-lab-claude/01_basic_llm.py`

### For Ollama Local Testing
1. **Setup:** Go to [SETUP_GUIDE.md](SETUP_GUIDE.md) → Path B
2. **Files:** See [ai-lab-ollama/README.md](ai-lab-ollama/README.md)
3. **Start:** Run `python ai-lab-ollama/01_basic_llm.py`

## 📚 Complete Module List

| # | Module | Topic | Location |
|---|--------|-------|----------|
| 01 | Basic LLM | Simple API calls | Both folders |
| 02 | Streaming & Structured | Response handling | claude/ |
| 03 | Production Wrapper | Retry & caching | claude/ |
| 04 | RAG Ingestion | Chunking & embeddings | claude/ |
| 05 | RAG Retrieval | Dense & sparse search | claude/ |
| 06 | Advanced RAG | Query expansion & reranking | claude/ |
| 07 | RAG Evaluation | Metrics & quality | claude/ |
| 08 | Production RAG | Caching & optimization | claude/ |
| 09 | Basic Agent | Think → Act → Observe | claude/ |
| 10 | Agent Tools | Tool definitions | claude/ |
| 11 | Agent Memory | State management | claude/ |
| 12 | Reliable Agent | Error recovery | claude/ |
| 13 | Secure Agent | Validation & permissions | claude/ |
| 14 | Supervisor Agent | Multi-agent coordination | claude/ |
| 15 | Parallel Agents | Concurrent execution | claude/ |
| 16 | MAS Communication | Message passing | claude/ |
| 17 | MAS Reliability | Fault tolerance | claude/ |
| 18 | Complete MAS | Full production system | claude/ |
| 19 | End-to-End Platform | Full GenAI stack | claude/ |
| 20 | Interview Exercises | System design | claude/ |

## 🚀 Three Ways to Use

### Way 1: Claude.ai (Easiest, No Setup)
```
1. Go to https://claude.ai
2. Copy code from ai-lab-claude/
3. Paste and ask Claude to explain
4. Learn interactively
```

### Way 2: Ollama (Free Local)
```
1. Install Ollama (5 min)
2. Download model (5 min)
3. Run: python ai-lab-ollama/01_basic_llm.py
4. Experiment and learn
```

### Way 3: Anthropic API (Best Quality, Costs Money)
```
1. Get API key from console.anthropic.com
2. Replace API_KEY in ai-lab-claude/
3. Run: python ai-lab-claude/01_basic_llm.py
4. Cost: ~$1-2 for all 20 examples
```

## 📖 How to Use Each Folder

### ai-lab-claude/ (20 scripts)
- **Use for:** Understanding concepts, Claude.ai testing, API learning
- **Requires:** API key OR Claude.ai access
- **Cost:** Free with Claude.ai / ~$1-2 with API
- **Setup:** 0 min (Claude.ai) or 5 min (API)

**To use:**
```bash
# Option 1: Copy-paste into Claude.ai (FREE)
# - Go to Claude.ai
# - Copy any script
# - Ask Claude to explain

# Option 2: Run with API (costs $)
pip install anthropic
# Edit file: API_KEY = "sk-ant-v4-..."
python 01_basic_llm.py
```

### ai-lab-ollama/ (Scripts + utilities)
- **Use for:** Local testing, free experimentation, hands-on learning
- **Requires:** Ollama installed locally
- **Cost:** Free (zero API costs)
- **Setup:** 10 min (one-time, includes model download)

**To use:**
```bash
# Setup (one-time)
brew install ollama
ollama pull mistral
ollama serve

# Run examples (in another terminal)
cd ai-lab-ollama
pip install requests
python 01_basic_llm.py
```

## 🎓 Recommended Path

### For Beginners
```
1. Start with Claude.ai (ai-lab-claude/)
2. Copy code → Paste into Claude.ai
3. Learn concepts by asking Claude questions
4. Then move to Ollama to run locally
```

### For Hands-On Learners
```
1. Install Ollama (10 min)
2. Run ai-lab-ollama/01_basic_llm.py
3. Modify code and experiment
4. Learn by doing
```

### For Deep Learning
```
1. Use Claude.ai for understanding (ai-lab-claude/)
2. Use Ollama for practice (ai-lab-ollama/)
3. Combine theory + practice
```

## ✅ What's Ready to Use

✅ **ai-lab-claude/**
- All 20 scripts ready
- Can be copy-pasted into Claude.ai
- Can be run with API key
- Full documentation

✅ **ai-lab-ollama/**
- 01_basic_llm.py (complete example)
- ollama_base.py (shared utilities)
- Full README with setup instructions
- Other scripts available in ai-lab-claude/ (can be adapted)

## 🔄 Converting Scripts

To use a script from ai-lab-claude/ with Ollama:

1. Copy file from ai-lab-claude/
2. Replace imports:
   ```python
   # From:
   from anthropic import Anthropic
   API_KEY = "sk-ant-..."
   
   # To:
   from ollama_base import OllamaClient
   client = OllamaClient(model="mistral")
   ```

3. Replace API calls:
   ```python
   # From:
   response = client.messages.create(...)
   
   # To:
   response = client.chat(messages=...)
   ```

See `ai-lab-ollama/01_basic_llm.py` for a complete example!

## 🎯 Learning Objectives

After completing all 20 modules, you'll understand:

✅ LLM fundamentals (modules 01-03)
✅ RAG systems (modules 04-08)
✅ Agent patterns (modules 09-13)
✅ Multi-agent systems (modules 14-18)
✅ Production systems (modules 19-20)
✅ System design & architecture

## 📞 Support

- **Claude.ai questions?** Copy code into Claude.ai and ask!
- **Ollama issues?** See README in ai-lab-ollama/
- **API key problems?** See SETUP_GUIDE.md

## 🚀 Next Steps

1. Read [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Choose your path (Claude.ai or Ollama)
3. Start with module 01
4. Follow "MUST REMEMBER" sections
5. Experiment and modify code
6. Build your own projects!

---

**Total Content:** 20 complete examples covering LLMs, RAG, Agents, Multi-Agent Systems, and Production Patterns

**Your Choice:**
- 🎯 **Learn interactively** with Claude.ai (free, no setup)
- 💻 **Learn hands-on** with Ollama (free, local)
- 🚀 **Learn professionally** with Anthropic API (small cost, best quality)

Pick one and start! 🎉
