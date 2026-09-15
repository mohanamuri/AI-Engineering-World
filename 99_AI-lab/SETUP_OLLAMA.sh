#!/bin/bash
# SETUP & TEST: ai-lab-ollama (Local Ollama - FREE)
# ==================================================
# Follow this step-by-step to setup and test Ollama locally

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           AI-LAB-OLLAMA: SETUP & TEST PROCEDURE               ║"
echo "║              (Local Ollama - 100% FREE)                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# STEP 1: Check if Ollama is installed
echo "📋 STEP 1: Check Ollama Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    ollama --version
else
    echo "❌ Ollama not found"
    echo ""
    echo "Install Ollama:"
    echo "1. Download from: https://ollama.ai"
    echo "2. Or use Homebrew: brew install ollama"
    echo "3. After install, restart your terminal"
    echo ""
    read -p "Press Enter after installing Ollama..."
fi
echo ""

# STEP 2: List available models
echo "📋 STEP 2: Check Available Models"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Models available locally:"
ollama list 2>/dev/null || echo "ℹ️  No models installed yet"
echo ""

# STEP 3: Download a model
echo "📋 STEP 3: Download Model (If Not Already Downloaded)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Available models:"
echo "  1) mistral      - Fast (4.1GB) - RECOMMENDED"
echo "  2) neural-chat  - Balanced (4.1GB)"
echo "  3) llama2       - Powerful (3.8GB)"
echo ""
read -p "Choose model (1-3, default: 1 mistral): " MODEL_CHOICE

case $MODEL_CHOICE in
    2) MODEL="neural-chat" ;;
    3) MODEL="llama2" ;;
    *) MODEL="mistral" ;;
esac

echo "Downloading $MODEL model (this may take 5-10 minutes)..."
ollama pull $MODEL

if [ $? -eq 0 ]; then
    echo "✅ Model $MODEL downloaded successfully"
else
    echo "❌ Failed to download model"
    exit 1
fi
echo ""

# STEP 4: Start Ollama Server (in background)
echo "📋 STEP 4: Start Ollama Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting Ollama server..."
echo "⚠️  This will run in background"
echo ""

# Check if ollama is already running
if curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "✅ Ollama server is already running"
else
    echo "Starting ollama serve in background..."
    ollama serve > /dev/null 2>&1 &

    # Wait for server to start
    sleep 3

    # Check if it started
    if curl -s http://localhost:11434 > /dev/null 2>&1; then
        echo "✅ Ollama server started successfully"
    else
        echo "❌ Failed to start Ollama server"
        echo "Try manually: ollama serve"
        exit 1
    fi
fi
echo ""

# STEP 5: Install Python Dependencies
echo "📋 STEP 5: Install Python Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installing: requests"
pip3 install requests

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Installation failed"
    exit 1
fi
echo ""

# STEP 6: Test Connection to Ollama
echo "📋 STEP 6: Test Connection to Ollama"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing Ollama server on http://localhost:11434..."

if curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "✅ Ollama server is responding"
else
    echo "❌ Cannot connect to Ollama"
    echo "Make sure to run: ollama serve"
    exit 1
fi
echo ""

# STEP 7: Run Test Script
echo "📋 STEP 7: Run Test Script (Module 01)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing with: ai-lab-ollama/01_basic_llm.py"
echo "Model: $MODEL"
echo ""
echo "⏳ First run may take 10-30 seconds (model warming up)..."
echo ""

cd ai-lab-ollama
python3 01_basic_llm.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ TEST PASSED - Ollama is working locally!"
else
    echo ""
    echo "❌ TEST FAILED - Check error message above"
    echo ""
    echo "Troubleshooting:"
    echo "1. Is 'ollama serve' running? (check with: ps aux | grep ollama)"
    echo "2. Is model downloaded? (check with: ollama list)"
    echo "3. Is port 11434 available?"
    exit 1
fi
echo ""

# FINAL SUMMARY
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   SETUP COMPLETE! ✅                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 IMPORTANT - Keep Ollama Running:"
echo "   Don't close the 'ollama serve' terminal/process!"
echo "   Leave it running while you use the scripts"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Run: python3 ai-lab-ollama/01_basic_llm.py"
echo "2. Run: python3 ai-lab-ollama/02_llm_streaming_structured.py"
echo "3. Continue with modules 03-20"
echo ""
echo "📚 MODULES AVAILABLE:"
echo "   01-03: LLM Fundamentals"
echo "   04-08: RAG Systems"
echo "   09-13: Single Agent Systems"
echo "   14-18: Multi-Agent Systems"
echo "   19-20: Production & Interviews"
echo ""
echo "💡 TIP: Check 'MUST REMEMBER' section in each script"
echo ""
echo "🔧 CHANGING MODELS:"
echo "   Edit line in script: client = OllamaClient(model='mistral')"
echo "   Change 'mistral' to 'neural-chat' or 'llama2'"
echo ""
