# ai-lab-ollama: Local Testing with Ollama (100% FREE)

## 🎯 Purpose
All scripts modified to run **locally on your Mac** using Ollama. **Zero API costs**, completely offline after setup.

## ✨ Key Benefits

✅ **100% FREE** - No API costs, ever
✅ **Offline** - Runs locally on your Mac
✅ **Fast Setup** - Download model once, then test all examples
✅ **Full Examples** - All 20 modules working locally
✅ **Learn by Doing** - Run and modify code yourself

## 🚀 Quick Start (5 minutes)

### Step 1: Install Ollama (Free)
```bash
# Download from: https://ollama.ai
# Or with Homebrew:
brew install ollama
```

### Step 2: Download a Model (Choose One)
```bash
# Fast & good for coding
ollama pull mistral

# Or balanced performance
ollama pull neural-chat

# Or powerful general-purpose
ollama pull llama2
```

### Step 3: Start Ollama Server
```bash
ollama serve
# This runs in background on http://localhost:11434
```

### Step 4: Run Examples
```bash
cd ai-lab-ollama
pip install requests  # Only dependency needed
python 01_basic_llm.py
```

## 📊 Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| Mistral | 4.1GB | ⚡ Fast | ⭐⭐⭐ | Coding, quick learning |
| Neural-Chat | 4.1GB | ⚡ Fast | ⭐⭐⭐⭐ | Balanced, recommended |
| Llama2 | 3.8GB | 🐢 Slower | ⭐⭐⭐⭐⭐ | Best quality |

**Recommendation:** Start with **mistral** (fastest), then try **neural-chat** (best balance).

## 📁 File Structure

```
ai-lab-ollama/
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

## 💻 How It Works

**Traditional API:**
```
Your Code → Internet → Anthropic Server → Response
```

**Ollama (Local):**
```
Your Code → Local Model → Response (on your Mac!)
```

**Result:** Same learning, zero costs, no internet needed!

## 🎓 Learning Path

### Path 1: Quick Start (All Free)
```
01 → 02 → 03 (LLM basics, ~15 min)
04 → 05 → 06 → 07 → 08 (RAG, ~30 min)
09 → 10 → 11 (Agents, ~20 min)
...complete all 20 examples
```

### Path 2: Deep Dive
1. Run one example: `python 01_basic_llm.py`
2. Read output and "MUST REMEMBER"
3. Modify code (change prompt, temperature, etc.)
4. Run again to see differences
5. Repeat for next module

## ⚡ What to Expect

**First Time:**
- Download model: 2-5 minutes
- First run: 10-30 seconds (warming up)

**Subsequent Runs:**
- Response time: 5-30 seconds (depends on model)
- No download needed

**Your Mac:**
- Mistral: Works on any Mac (uses 4GB RAM)
- Neural-Chat: Works on any Mac (uses 4GB RAM)
- Llama2: Recommend 8GB+ RAM

## 🔄 Changing Models

```bash
# Stop current server (Ctrl+C in terminal)

# Try a different model
ollama pull llama2
ollama serve

# Run script with different model
# Edit the script to change model="mistral" to model="llama2"
```

## 📝 Each File Contains

- Setup instructions at the top
- Example code with comments
- "MUST REMEMBER" concepts
- How to modify and experiment
- No API key needed!

## ❓ Troubleshooting

**Error: "Can't connect to Ollama"**
```bash
# Make sure Ollama is running
ollama serve

# Keep this terminal open while running scripts
```

**Model too slow?**
```bash
# Switch to faster model
ollama pull mistral  # Fastest
```

**Running out of disk space?**
```bash
# See installed models
ollama list

# Remove a model if needed
ollama rm llama2
```

## 🎯 Why This Approach?

✅ **Learn without costs** - Test everything free
✅ **No API keys** - No setup complexity
✅ **Private** - Data stays on your Mac
✅ **Always available** - Works offline
✅ **Perfect for learning** - All 20 examples included

## 🚀 Next Steps

1. Install Ollama
2. Run `01_basic_llm.py`
3. When it works, try other modules
4. Modify code and experiment
5. Build your own projects!

## 📚 Resources

- Ollama: https://ollama.ai
- Models: https://ollama.ai/library
- Documentation: https://github.com/ollama/ollama

---

**Happy Learning! 🎉** All 20 examples are ready to run locally, completely free!
