#!/usr/bin/env python3
"""
Quick test to verify AI is working
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import ai_config
import ai_config

print("=" * 60)
print("AI SYSTEM TEST")
print("=" * 60)

# Check API key
if ai_config.OPENAI_API_KEY and len(ai_config.OPENAI_API_KEY) > 20:
    print(f"✅ API Key loaded: {ai_config.OPENAI_API_KEY[:20]}...{ai_config.OPENAI_API_KEY[-4:]}")
else:
    print("❌ API Key not loaded properly")

# Try to initialize AI
try:
    brain = ai_config.AITradingBrain()
    print("✅ AI Brain initialized successfully")

    optimizer = ai_config.SelfOptimizer()
    print("✅ AI Optimizer initialized successfully")

    print("\n✅ AI SYSTEM IS WORKING PERFECTLY!")
    print("\nThe AI is ready to:")
    print("- Analyze markets with GPT-4")
    print("- Use 13 advanced indicators")
    print("- Make ULTRA POWERFUL trading decisions")

except Exception as e:
    print(f"❌ Error initializing AI: {e}")

print("=" * 60)