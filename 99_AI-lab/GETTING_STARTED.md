# GETTING STARTED: Quick Reference
## AI-Lab Setup & Testing

---

## 🎯 CHOOSE YOUR PATH

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Which method do you want to use?                          │
│                                                             │
│  1️⃣  CLAUDE.AI (Easiest - 0 min setup)                     │
│      → Go to Claude.ai, copy code, ask Claude             │
│      → No installation needed                              │
│      → FREE with Claude.ai account                         │
│                                                             │
│  2️⃣  OLLAMA (Best for coding - 15 min setup)               │
│      → Run locally on your Mac                             │
│      → 100% FREE, no API costs                             │
│      → Works offline after setup                           │
│                                                             │
│  3️⃣  ANTHROPIC API (Professional - 5 min setup)            │
│      → Use real Claude API                                 │
│      → Cost: ~$1-2 for all examples                        │
│      → Best quality responses                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 DETAILED GUIDES

**Choose your method above, then:**

### Path 1: Claude.ai
📖 **No detailed setup needed** - Just copy code!
- Go to: https://claude.ai
- Copy scripts from: `ai-lab-claude/`
- Paste into Claude and ask

### Path 2: Ollama (RECOMMENDED FOR THIS PROJECT)
📖 **Full setup guide:** `SETUP_OLLAMA_DETAILED.md`
```bash
# Quick summary:
1. brew install ollama
2. ollama pull mistral
3. ollama serve
4. python3 ai-lab-ollama/01_basic_llm.py
```

### Path 3: Anthropic API
📖 **Full setup guide:** `SETUP_CLAUDE_DETAILED.md`
```bash
# Quick summary:
1. Get API key: https://console.anthropic.com/account/keys
2. pip3 install anthropic python-dotenv
3. Update API_KEY in scripts
4. python3 ai-lab-claude/01_basic_llm.py
```

---

## 🚀 QUICK START (Choose ONE)

### Option 1: Ollama (5 commands)
```bash
# 1. Install Ollama
brew install ollama

# 2. Download model
ollama pull mistral

# 3. Start server
ollama serve

# 4. In new terminal:
cd ai-lab-ollama
pip3 install requests

# 5. Run test
python3 01_basic_llm.py
```

### Option 2: Claude API (4 commands)
```bash
# 1. Get API key from: https://console.anthropic.com/account/keys

# 2. Install dependencies
pip3 install anthropic python-dotenv

# 3. Navigate to folder
cd ai-lab-claude

# 4. Update API key in files, then run:
python3 01_basic_llm.py
```

### Option 3: Claude.ai (0 commands)
```
1. Go to: https://claude.ai
2. Copy code from: ai-lab-claude/01_basic_llm.py
3. Paste into Claude
4. Ask: "What does this code do?"
Done! ✅
```

---

## 🧪 TEST YOUR SETUP

### If using Ollama:
```bash
# Terminal 1 (keep running)
ollama serve

# Terminal 2 (run tests)
cd ai-lab-ollama
python3 01_basic_llm.py
python3 02_llm_streaming_structured.py
python3 03_llm_production_wrapper.py
```

### If using Claude API:
```bash
cd ai-lab-claude
python3 01_basic_llm.py
python3 02_llm_streaming_structured.py
python3 03_llm_production_wrapper.py
```

### If using Claude.ai:
Just copy each script and paste into Claude.ai

---

## ✅ VERIFICATION CHECKLIST

### For Ollama
- [ ] Ollama installed: `ollama --version`
- [ ] Model downloaded: `ollama list`
- [ ] Server running: `curl http://localhost:11434`
- [ ] Python requests: `pip3 list | grep requests`
- [ ] Module 01 test passes: `python3 01_basic_llm.py`
- [ ] Module 02 test passes: `python3 02_llm_streaming_structured.py`

### For Claude API
- [ ] Python installed: `python3 --version`
- [ ] Dependencies: `pip3 list | grep anthropic`
- [ ] API key in files
- [ ] Module 01 test passes: `python3 01_basic_llm.py`
- [ ] Module 02 test passes: `python3 02_llm_streaming_structured.py`

### For Claude.ai
- [ ] Claude.ai account created
- [ ] Can copy-paste code
- [ ] Can see responses from Claude
- [ ] Understand basic concepts

---

## 📊 WHAT HAPPENS AFTER SETUP

You can run any module:

```bash
# LLM Fundamentals
python3 01_basic_llm.py
python3 02_llm_streaming_structured.py
python3 03_llm_production_wrapper.py

# RAG Systems
python3 04_rag_ingestion.py
python3 05_rag_retrieval.py
# ... and so on

# All 20 modules available
```

Each module:
- ✅ Runs independently
- ✅ Has clear comments
- ✅ Shows "MUST REMEMBER" concepts
- ✅ Includes working examples
- ✅ Can be modified to experiment

---

## 🎯 LEARNING SEQUENCE

After setup is working:

1. **Run Module 01:**
   - Execute the script
   - Read all comments
   - Understand what it does

2. **Check "MUST REMEMBER":**
   - Key concepts to learn
   - What to remember
   - Common pitfalls

3. **Experiment:**
   - Modify the code
   - Change prompts
   - See what changes

4. **Move to Module 02:**
   - Same process
   - Build on knowledge
   - Progressive learning

5. **Continue through all 20:**
   - Follow the pattern
   - Each builds on previous
   - 5-7 hours total learning time

---

## 💡 COMMON QUESTIONS

**Q: Which method should I choose?**
A: For this project, **Ollama is best** because:
- 100% FREE (no API costs)
- Works OFFLINE
- Good for hands-on learning
- No authentication needed

**Q: Can I switch between methods?**
A: Yes! Each folder has same 20 scripts:
- `ai-lab-claude/` - For Claude API
- `ai-lab-ollama/` - For Ollama
- Same learning, different execution

**Q: How much will it cost?**
- Ollama: $0 (completely free)
- Claude API: ~$1-2 total
- Claude.ai: Free

**Q: How long does setup take?**
- Ollama: 15 minutes (including model download)
- Claude API: 5 minutes
- Claude.ai: 0 minutes

**Q: Can I run multiple modules?**
A: Yes! Once setup, you can:
- Run any module at any time
- Run them in any order
- Run same module multiple times
- All are independent

---

## 📖 FULL DOCUMENTATION

If you need more details:

```
SETUP_OLLAMA_DETAILED.md    ← Complete Ollama guide
SETUP_CLAUDE_DETAILED.md    ← Complete Claude API guide
INDEX.md                     ← All 20 modules explained
FOLDER_ORGANIZATION.txt      ← What's in each folder
```

---

## 🆘 QUICK TROUBLESHOOTING

**Ollama: "Can't connect"**
```bash
# Make sure Ollama is running
curl http://localhost:11434
# If not, start: ollama serve
```

**Claude API: "API key invalid"**
- Check key at: https://console.anthropic.com/account/keys
- Verify it starts with `sk-ant-v4-`
- Update script with correct key

**Claude.ai: "Not working"**
- Go to: https://claude.ai
- Create account if needed
- Try again

---

## 🎉 YOU'RE READY!

**Next step:**

1. Pick your method (Ollama recommended)
2. Read the detailed guide for that method
3. Follow setup instructions
4. Run Module 01
5. Start learning!

---

## 📞 SUPPORT

**Each method has detailed help:**

- **Ollama:** See `SETUP_OLLAMA_DETAILED.md`
- **Claude API:** See `SETUP_CLAUDE_DETAILED.md`
- **Claude.ai:** Go to https://claude.ai and ask Claude!
- **All modules:** Read comments in each script

---

**Choose your path and start learning! 🚀**

```
Recommended: OLLAMA
Time to setup: 15 minutes
Cost: $0
Quality: Good
Difficulty: Easy
```
