# AI-LAB-OLLAMA: SETUP & TEST GUIDE
## Complete Step-by-Step Instructions (100% FREE & LOCAL)

---

## 📋 PREREQUISITES

- ✅ Mac with 8GB+ RAM (4GB minimum)
- ✅ 10GB+ free disk space (for models)
- ✅ Python 3.8 or higher
- ✅ Internet connection (for model download, then offline after)

---

## 🚀 SETUP (15 minutes)

### Step 1: Install Ollama

**Method 1: Download (Recommended)**
1. Go to: https://ollama.ai
2. Click "Download"
3. Choose macOS version
4. Open .dmg file and drag Ollama to Applications
5. Launch Ollama from Applications
6. You should see Ollama icon in menu bar

**Method 2: Homebrew**
```bash
brew install ollama
```

---

### Step 2: Verify Ollama Installation

```bash
ollama --version
# Should show: ollama version X.X.X
```

If command not found:
- Restart your terminal/Mac
- Try again

---

### Step 3: Download a Model (Choose One)

Models available:
- **mistral** (4.1GB) - Fast, good quality ⭐ RECOMMENDED
- **neural-chat** (4.1GB) - Balanced performance
- **llama2** (3.8GB) - Slower but higher quality

```bash
# Download mistral (fastest, recommended)
ollama pull mistral

# Or download neural-chat
ollama pull neural-chat

# Or download llama2
ollama pull llama2
```

**⏳ This will take 5-10 minutes depending on internet speed**

**Expected output:**
```
pulling manifest
pulling 8934d3bdab53
downloading ef07efb9c58b 36% [============>       ]

pulling 8c91da2d7c0b
downloading 335aed735dbe

pulling 7c23fb36d801
downloading [finish]

Verifying sha256 digest
Writing manifest
Success
```

---

### Step 4: Verify Model is Installed

```bash
ollama list
```

**Expected output:**
```
NAME            ID              SIZE
mistral         8932...          4.1GB
```

---

### Step 5: Start Ollama Server

```bash
ollama serve
```

**Expected output:**
```
time=2024-09-15T12:00:00.000Z level=INFO msg="server listening on 127.0.0.1:11434"
```

**⚠️ IMPORTANT: Keep this terminal/process running!**
- Don't close this window
- Leave it running while using scripts
- You can minimize it

---

### Step 6: Open New Terminal Window

Open a **new** terminal window (keep Ollama running in first one)

```bash
# Navigate to ai-lab-ollama
cd ai-lab-ollama

# Verify you can see the scripts
ls *.py
```

---

### Step 7: Install Python Dependencies

```bash
pip3 install requests
```

---

## ✅ TEST (5 minutes)

### Test 1: Verify Ollama is Running

```bash
curl http://localhost:11434
```

**Expected:** HTML response (shows Ollama is running)

---

### Test 2: Verify Python Dependencies

```bash
python3 -c "import requests; print('✅ Success')"
```

**Expected:** ✅ Success

---

### Test 3: Run Module 01 (Basic LLM)

```bash
# Make sure you're in ai-lab-ollama directory
cd ai-lab-ollama

# Run the test
python3 01_basic_llm.py
```

**Expected output:**
```
============================================================
01: BASIC LLM APPLICATION (Ollama - Local & FREE)
============================================================

📝 Example 1: Simple Question
----------------------------------------
💭 Agent: Python is a high-level, interpreted programming language...
[continues]

✅ MUST REMEMBER:
...
```

**⏳ First run takes 10-30 seconds (model warming up)**

---

### Test 4: Run Module 02 (Streaming)

```bash
python3 02_llm_streaming_structured.py
```

**Expected:** See tokens streaming in real-time

---

### Test 5: Run Module 03 (Production Wrapper)

```bash
python3 03_llm_production_wrapper.py
```

**Expected:** All examples run successfully

---

### Test 6: Quick Module Check

```bash
# Test a few more modules
python3 04_rag_ingestion.py
python3 05_rag_retrieval.py
python3 09_basic_agent.py
```

---

## 🐛 TROUBLESHOOTING

### ❌ Error: "Can't connect to Ollama"

**Solution:**
1. Check if Ollama is running: `curl http://localhost:11434`
2. If not running, start it: `ollama serve`
3. Make sure you didn't close the Ollama window
4. Restart Ollama if needed

---

### ❌ Error: "Model not found"

**Solution:**
1. Check installed models: `ollama list`
2. If empty, download one: `ollama pull mistral`
3. Wait for download to complete
4. Try script again

---

### ❌ Error: "Connection refused"

**Solution:**
```bash
# Kill any existing ollama processes
killall ollama

# Start fresh
ollama serve
```

---

### ❌ Error: "Python requests module not found"

**Solution:**
```bash
pip3 install --upgrade requests
```

---

### ❌ Script is very slow

**Solution:**
1. Normal for first run (model warming up)
2. Subsequent runs are faster
3. Try faster model: `ollama pull mistral`
4. Check available RAM: `vm_stat`

---

### ❌ Out of disk space

**Solution:**
```bash
# Check disk usage
df -h

# Remove unused models
ollama rm llama2  # Only if you won't use it

# Keep most frequently used model
```

---

## 🔧 CHANGE MODELS

Want to try a different model?

1. Download new model:
   ```bash
   ollama pull neural-chat
   ```

2. Edit the Python script:
   ```python
   # In 01_basic_llm.py, find:
   client = OllamaClient(model="mistral")
   
   # Change to:
   client = OllamaClient(model="neural-chat")
   ```

3. Run again:
   ```bash
   python3 01_basic_llm.py
   ```

---

## 📊 MODEL COMPARISON

| Model | Speed | Quality | Size | Best For |
|-------|-------|---------|------|----------|
| Mistral | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | 4.1GB | Learning (RECOMMENDED) |
| Neural-Chat | ⚡⚡ Medium | ⭐⭐⭐⭐ Better | 4.1GB | Balanced use |
| Llama2 | ⚡ Slow | ⭐⭐⭐⭐⭐ Best | 3.8GB | Production |

---

## 📚 NEXT STEPS

Once all tests pass:

1. **Keep Ollama Running:**
   - Leave `ollama serve` terminal open
   - Keep it running while learning

2. **Understand Module 01:**
   - Read all comments in `01_basic_llm.py`
   - Read "MUST REMEMBER" section
   - Understand what each function does

3. **Experiment:**
   - Modify the prompt in main()
   - Change temperature values (0.0 to 1.0)
   - Try with different models

4. **Continue Learning:**
   - Move to Module 02: `python3 02_llm_streaming_structured.py`
   - Follow same pattern for all 20 modules

5. **Track Progress:**
   ```
   ✅ Module 01: Basic LLM
   ✅ Module 02: Streaming + Structured
   ⬜ Module 03: Production Wrapper
   ...
   ```

---

## 💡 USEFUL COMMANDS

```bash
# List all models
ollama list

# Download a model
ollama pull mistral

# Remove a model
ollama rm llama2

# Start server
ollama serve

# Test Ollama is running
curl http://localhost:11434

# Run specific module
python3 01_basic_llm.py

# Run all modules (in ai-lab-ollama directory)
for file in *.py; do
  echo "Running $file..."
  python3 "$file"
done

# Check Python packages
pip3 list | grep requests
```

---

## 🚨 IMPORTANT NOTES

1. **Keep Ollama Running:**
   - Don't close the `ollama serve` terminal
   - All scripts need it running
   - You can minimize it (don't close)

2. **First Run Takes Longer:**
   - Model warming up: 10-30 seconds
   - Subsequent runs: 2-5 seconds
   - Normal behavior

3. **Offline After Setup:**
   - Once model is downloaded, no internet needed
   - Only `ollama serve` needs to run locally
   - Perfect for offline learning

4. **No API Costs:**
   - 100% free
   - Run unlimited times
   - No token counting

---

## ✨ YOU'RE READY!

Once tests pass:
```bash
✅ Ollama installed
✅ Model downloaded (mistral/neural-chat/llama2)
✅ Ollama server running
✅ Python dependencies installed
✅ Module 01 tested
```

**Start learning with Module 01!** 🎉

---

## 📞 QUICK REFERENCE

| Task | Command |
|------|---------|
| Install Ollama | Download from https://ollama.ai |
| Download model | `ollama pull mistral` |
| Start server | `ollama serve` |
| List models | `ollama list` |
| Install Python deps | `pip3 install requests` |
| Run Module 01 | `python3 01_basic_llm.py` |
| Check Ollama | `curl http://localhost:11434` |
| Verify model | `ollama list` |

---

## 🆘 QUICK HELP

**Setup stuck?**
- Restart Mac
- Reinstall Ollama
- Clear terminal cache: `clear`

**Model download slow?**
- Check internet: `ping 8.8.8.8`
- Normal download: 5-10 min
- Be patient!

**Script not working?**
- Check Ollama running: `curl http://localhost:11434`
- Check model downloaded: `ollama list`
- Check Python: `python3 --version`

---

**Happy Learning! 🚀 (And it's FREE!)**
