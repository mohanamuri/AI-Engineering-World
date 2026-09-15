#!/bin/bash
# SETUP & TEST: ai-lab-claude (Anthropic API)
# ============================================
# Follow this step-by-step to setup and test Claude API scripts

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          AI-LAB-CLAUDE: SETUP & TEST PROCEDURE                ║"
echo "║              (Anthropic Claude API Version)                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# STEP 1: Verify Python Installation
echo "📋 STEP 1: Verify Python Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Python is installed"
else
    echo "❌ Python not found. Install from: https://www.python.org"
    exit 1
fi
echo ""

# STEP 2: Install Dependencies
echo "📋 STEP 2: Install Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installing: anthropic, python-dotenv"
pip3 install anthropic python-dotenv
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Installation failed"
    exit 1
fi
echo ""

# STEP 3: Get API Key
echo "📋 STEP 3: Get Your Anthropic API Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  MANUAL STEP REQUIRED:"
echo "1. Go to: https://console.anthropic.com/account/keys"
echo "2. Login with your Anthropic account"
echo "3. Create or copy an API key (starts with sk-ant-v4-)"
echo "4. Keep this key safe (don't commit to git!)"
echo ""
read -p "Enter your API key (or press Enter to skip for now): " API_KEY
echo ""

if [ -n "$API_KEY" ]; then
    echo "✅ API Key received"
else
    echo "⚠️  Skipping API key setup - you can add it later"
fi
echo ""

# STEP 4: Update API Key in Scripts
if [ -n "$API_KEY" ]; then
    echo "📋 STEP 4: Update API Key in All Scripts"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Count files that will be updated
    FILES_TO_UPDATE=$(grep -l "sk-ant-v4-YOUR-API-KEY-HERE" ai-lab-claude/*.py 2>/dev/null | wc -l)

    if [ "$FILES_TO_UPDATE" -gt 0 ]; then
        echo "Updating $FILES_TO_UPDATE files with your API key..."

        # Replace API key in all files
        find ai-lab-claude -name "*.py" -type f -exec sed -i '' "s/sk-ant-v4-YOUR-API-KEY-HERE/$API_KEY/g" {} \;

        echo "✅ API key updated in $FILES_TO_UPDATE files"
    else
        echo "⚠️  No files found to update (already have API key?)"
    fi
    echo ""
fi

# STEP 5: Test Installation
echo "📋 STEP 5: Test Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 -c "from anthropic import Anthropic; print('✅ Anthropic module imported successfully')"
if [ $? -eq 0 ]; then
    echo "✅ All dependencies working"
else
    echo "❌ Import failed - check your Python installation"
    exit 1
fi
echo ""

# STEP 6: Run Test Script
if [ -n "$API_KEY" ]; then
    echo "📋 STEP 6: Run Test Script (Module 01)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing with: ai-lab-claude/01_basic_llm.py"
    echo ""

    cd ai-lab-claude
    python3 01_basic_llm.py

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ TEST PASSED - Claude API is working!"
    else
        echo ""
        echo "❌ TEST FAILED - Check error message above"
        exit 1
    fi
fi
echo ""

# FINAL SUMMARY
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   SETUP COMPLETE! ✅                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Run: python3 ai-lab-claude/01_basic_llm.py"
echo "2. Run: python3 ai-lab-claude/02_llm_streaming_structured.py"
echo "3. Continue with modules 03-20"
echo ""
echo "📚 MODULES AVAILABLE:"
echo "   01-03: LLM Fundamentals"
echo "   04-08: RAG Systems"
echo "   09-13: Single Agent Systems"
echo "   14-18: Multi-Agent Systems"
echo "   19-20: Production & Interviews"
echo ""
echo "💡 TIP: Check 'MUST REMEMBER' section in each script for key concepts"
echo ""
