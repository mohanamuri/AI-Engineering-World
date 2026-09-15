# 99_AI-lab: Two Folders for Two Learning Styles

## 🎯 Overview

```
99_AI-lab/
│
├── ai-lab-claude/                  (For Claude.ai & API testing)
│   ├── 01-20 Python scripts
│   └── Requires: Anthropic API key OR Claude.ai access
│
└── ai-lab-ollama/                  (For LOCAL free testing)
    ├── 01-20 Python scripts (Ollama versions)
    ├── ollama_base.py (shared utilities)
    └── Requires: Ollama installed locally (FREE)
```

## 🚀 Choose Your Path

### Path A: Claude.ai Testing (Minimal Setup)
**Best for:** Quick learning, no installation

```bash
cd ai-lab-claude
# Copy code → Paste into Claude.ai (https://claude.ai)
# Ask Claude to explain and help you understand
# ZERO SETUP, NO API KEY NEEDED
```

**OR run locally:**
```bash
cd ai-lab-claude
pip install anthropic
# Replace API_KEY in scripts
python 01_basic_llm.py
```

### Path B: Ollama Testing (100% FREE, Local)
**Best for:** Learning by doing, zero costs, offline

```bash
# 1. Install Ollama (free)
brew install ollama

# 2. Download a model (free, one-time)
ollama pull mistral

# 3. Start server
ollama serve

# 4. In another terminal, run examples
cd ai-lab-ollama
pip install requests
python 01_basic_llm.py
```

---

## 📊 Comparison

| Aspect | ai-lab-claude | ai-lab-ollama |
|--------|---------------|---------------|
| **Cost** | Free in Claude.ai / $1-2 with API key | Free (zero costs) |
| **Setup Time** | 0 min (Claude.ai) / 5 min (API) | 5 min (first time) |
| **Internet** | Required | Not required (after setup) |
| **Speed** | Fast (cloud) | Medium (local) |
| **Best For** | Understanding concepts | Running code yourself |
| **Quality** | Best (Claude 3.5) | Good (Mistral/Llama2) |

---

## 🎓 Recommended Learning Sequence

### Option 1: Start with Claude.ai (Recommended for Beginners)
```
1. Go to Claude.ai
2. Copy code from ai-lab-claude/01_basic_llm.py
3. Paste and ask Claude to explain
4. Learn the concepts
5. Move to ai-lab-ollama to run locally
```

### Option 2: Start with Ollama (Recommended for Hands-On Learning)
```
1. Install Ollama (5 min)
2. Download model (5 min)
3. Run ai-lab-ollama/01_basic_llm.py
4. Modify code and experiment
5. Learn by doing
```

### Option 3: Use Both (Best Learning)
```
1. Go to Claude.ai with ai-lab-claude code (understand concepts)
2. Run ai-lab-ollama code (practice and experiment)
3. Combine learning: theory + practice
```

---

## 📁 File Organization

### ai-lab-claude/
All 20 scripts use **Anthropic API**. Can be:
- Copied to Claude.ai for manual testing
- Run locally with API key (costs money, but small amounts)

**When to use:**
- ✅ Learning without running code
- ✅ Getting help from Claude
- ✅ Understanding concepts first
- ✅ Testing with best quality model

### ai-lab-ollama/
All 20 scripts modified for **Ollama** (local, free):
- `ollama_base.py` - Shared utilities
- `01-20_*.py` - Example scripts for Ollama

**When to use:**
- ✅ Running code on your machine
- ✅ Zero API costs
- ✅ Learning by experimenting
- ✅ Offline testing

---

## ⚡ Quick Start (Choose One)

### Quick Start A: Claude.ai (No Setup)
```bash
1. Go to: https://claude.ai
2. Copy code from: ai-lab-claude/01_basic_llm.py
3. Paste into Claude and ask to explain
4. Done! Start learning
```

### Quick Start B: Ollama (Free, Local)
```bash
# Install Ollama
brew install ollama

# Download model (one-time)
ollama pull mistral

# Start server (keep running)
ollama serve

# In another terminal:
cd ai-lab-ollama
pip install requests
python 01_basic_llm.py
```

---

## 🎯 Which Scripts Are Available

### ai-lab-claude/ (All 20)
- ✅ 01-03: LLM Fundamentals
- ✅ 04-08: RAG Systems
- ✅ 09-13: Single Agent
- ✅ 14-18: Multi-Agent
- ✅ 19-20: Integration & Interviews

### ai-lab-ollama/ (All 20)
- ✅ 01-10: Core examples (fully adapted)
- ✅ 11-20: Available with basic Ollama support

---

## 💡 Tips

**For Claude.ai Testing:**
```
Effective prompt:
"Here's code I'm learning about. Can you:
1. Explain what it does
2. Tell me the key concepts
3. How would you modify it?"
```

**For Ollama Local Testing:**
```
# Try different models
ollama pull neural-chat  # Better quality
ollama pull llama2       # Most powerful

# Edit script to change model:
client = OllamaClient(model="neural-chat")
```

---

## 🚨 Troubleshooting

### "Can't connect to Ollama"
```bash
# Make sure Ollama is running
ollama serve

# Keep this terminal open while running scripts
# Run scripts in a NEW terminal
```

### "No API Key Error" (ai-lab-claude)
```
Option 1: Use Claude.ai instead
Option 2: Get key from: https://console.anthropic.com/account/keys
Option 3: Use ai-lab-ollama (free, no key needed)
```

### "Model not found"
```bash
ollama pull mistral  # Download before running scripts
```

---

## 🎓 Learning Goals

- Module 01-03: Understand LLM APIs and basic concepts
- Module 04-08: Master RAG systems and retrieval
- Module 09-13: Learn agent patterns and tool use
- Module 14-18: Understand multi-agent coordination
- Module 19-20: Full system design and interviews

---

## 🚀 Next Steps

1. **Choose a path** (Claude.ai or Ollama)
2. **Start with module 01**
3. **Read the comments** in each file
4. **Check "MUST REMEMBER"** sections
5. **Modify and experiment**
6. **Build your own projects**

---

## 📞 Need Help?

**For ai-lab-claude:**
- Use Claude.ai directly
- Copy code and ask for help
- Claude will explain everything

**For ai-lab-ollama:**
- Read README.md in that folder
- Check error messages
- Check setup instructions at top of scripts

---

**Happy Learning! Choose your path and start with module 01.** 🎉
