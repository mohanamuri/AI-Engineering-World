# AI-LAB-CLAUDE: SETUP & TEST GUIDE
## Complete Step-by-Step Instructions

---

## 📋 PREREQUISITES

- ✅ Python 3.8 or higher
- ✅ Internet connection (for API calls)
- ✅ Anthropic API account
- ✅ Your API key from https://console.anthropic.com

---

## 🚀 SETUP (5 minutes)

### Step 1: Verify Python Installation

```bash
python3 --version
# Should show Python 3.8 or higher
# Example: Python 3.12.7
```

If Python is not installed, download from: https://www.python.org

---

### Step 2: Install Dependencies

```bash
pip3 install anthropic python-dotenv
```

**Expected output:**
```
Successfully installed anthropic
Successfully installed python-dotenv
```

---

### Step 3: Get Your API Key

1. Go to: https://console.anthropic.com/account/keys
2. Login with your Anthropic account
3. Create new key or copy existing key
4. Key starts with `sk-ant-v4-`
5. **Keep it private! Don't commit to git!**

---

### Step 4: Add API Key to Scripts

Navigate to the claude folder:
```bash
cd ai-lab-claude
```

**Option A: Automatic (using sed)**
```bash
sed -i '' 's/sk-ant-v4-YOUR-API-KEY-HERE/sk-ant-v4-YOUR-ACTUAL-KEY/g' *.py
```

**Option B: Manual (edit one file)**
1. Open: `01_basic_llm.py`
2. Find line: `API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"`
3. Replace with your actual key: `API_KEY = "sk-ant-v4-abc123xyz..."`
4. Save file

**Option C: Using environment variable**
```bash
export ANTHROPIC_API_KEY="sk-ant-v4-YOUR-KEY"
```

---

## ✅ TEST (2 minutes)

### Test 1: Verify Installation

```bash
python3 -c "from anthropic import Anthropic; print('✅ Success')"
```

**Expected:** ✅ Success

---

### Test 2: Run Module 01 (Basic LLM)

```bash
cd ai-lab-claude
python3 01_basic_llm.py
```

**Expected output:**
```
============================================================
01: BASIC LLM APPLICATION
============================================================

📝 Example 1: Simple Question
----------------------------------------
Response: Python is a high-level programming language...

📝 Example 2: Multi-turn (uses history)
----------------------------------------
Response: For example, you could use Python to...

[continues with more examples]

✅ MUST REMEMBER:
...
```

---

### Test 3: Run Module 02 (Streaming)

```bash
python3 02_llm_streaming_structured.py
```

**Expected:** See streaming tokens in real-time

---

### Test 4: Run Multiple Modules

```bash
# Test LLM fundamentals
python3 01_basic_llm.py
python3 02_llm_streaming_structured.py
python3 03_llm_production_wrapper.py

# If all pass, continue with others
```

---

## 🐛 TROUBLESHOOTING

### ❌ Error: "API key is invalid"

**Solution:**
1. Check your API key is correct: https://console.anthropic.com/account/keys
2. Verify it starts with `sk-ant-v4-`
3. Make sure no extra spaces or quotes
4. Update the script with correct key

```python
# ✅ Correct
API_KEY = "sk-ant-v4-abc123..."

# ❌ Wrong
API_KEY = "sk-ant-v4-abc123..."  # (with quotes in the value)
API_KEY = " sk-ant-v4-abc123..."  # (with space)
```

---

### ❌ Error: "anthropic module not found"

**Solution:**
```bash
pip3 install --upgrade anthropic
```

---

### ❌ Error: "Rate limit exceeded"

**Solution:**
- Wait 60 seconds
- You're making requests too fast
- The script has retry logic (wait and try again)

---

### ❌ Error: "Connection timeout"

**Solution:**
1. Check internet connection
2. Anthropic API might be down (check: https://status.anthropic.com)
3. Try again in a few minutes

---

## 📚 NEXT STEPS

Once all tests pass:

1. **Understand Module 01:**
   - Read all comments in `01_basic_llm.py`
   - Read "MUST REMEMBER" section
   - Understand what each function does

2. **Experiment:**
   - Modify the prompt in main()
   - Change temperature values (0.0 to 1.0)
   - Add your own examples

3. **Continue Learning:**
   - Move to Module 02: `python3 02_llm_streaming_structured.py`
   - Follow same pattern for all 20 modules

4. **Track Progress:**
   ```
   ✅ Module 01: Basic LLM
   ✅ Module 02: Streaming + Structured
   ⬜ Module 03: Production Wrapper
   ...
   ```

---

## 💡 USEFUL COMMANDS

```bash
# Run specific module
python3 01_basic_llm.py

# Run all modules in sequence
for i in {01..20}; do
  echo "Running Module $i..."
  python3 0${i}_*.py 2>/dev/null || python3 1${i}_*.py 2>/dev/null
done

# Check Python packages
pip3 list | grep anthropic

# Check API key in use
python3 -c "from anthropic import Anthropic; print('API ready')"
```

---

## 📊 COST ESTIMATE

- **Module 01-03:** ~$0.10
- **Module 04-08:** ~$0.15
- **Module 09-13:** ~$0.25
- **Module 14-18:** ~$0.30
- **Module 19-20:** ~$0.10
- **Total:** ~$0.90 for all 20 examples

---

## ✨ YOU'RE READY!

Once tests pass:
```bash
✅ Python installed
✅ Dependencies installed
✅ API key configured
✅ Module 01 tested
```

**Start learning with Module 01!** 🎉

---

## 📞 QUICK REFERENCE

| Task | Command |
|------|---------|
| Install dependencies | `pip3 install anthropic python-dotenv` |
| Update API keys | `sed -i '' 's/OLD_KEY/NEW_KEY/g' *.py` |
| Run Module 01 | `python3 01_basic_llm.py` |
| Run Module 02 | `python3 02_llm_streaming_structured.py` |
| Check Python | `python3 --version` |
| Get help | Read comments in each script |

---

**Happy Learning! 🚀**
