#!/usr/bin/env python3
"""
Setup Verification Script
Run this to verify all dependencies and files are in place
"""

import sys
import os
from pathlib import Path


def check_file(filepath: str) -> bool:
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {filepath}")
        return True
    else:
        print(f"❌ {filepath} - MISSING")
        return False


def check_import(module_name: str) -> bool:
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError:
        print(f"❌ {module_name} - NOT INSTALLED")
        return False


def main():
    print("="*60)
    print("🔍 COGNITIVE AGENT SETUP VERIFICATION")
    print("="*60)
    
    all_good = True
    
    # Check Python version
    print("\n📦 Python Version:")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.10+")
        all_good = False
    
    # Check required files
    print("\n📁 Required Files:")
    required_files = [
        "models.py",
        "perception.py",
        "memory.py",
        "decision_making.py",
        "action.py",
        "main.py",
        "mcp_browser_server.py",
        "pyproject.toml",
        "env_example.txt",
        "README.md",
    ]
    
    for file in required_files:
        if not check_file(file):
            all_good = False
    
    # Check required packages
    print("\n📚 Required Packages:")
    required_packages = [
        "pydantic",
        "dotenv",
        "google.generativeai",
        "mcp",
        "asyncio",
    ]
    
    for package in required_packages:
        if not check_import(package):
            all_good = False
    
    # Check environment file
    print("\n🔑 Environment Setup:")
    if Path(".env").exists():
        print("✅ .env file exists")
        with open(".env") as f:
            content = f.read()
            if "GEMINI_API_KEY" in content and "your_api_key_here" not in content:
                print("✅ GEMINI_API_KEY appears to be set")
            else:
                print("⚠️  GEMINI_API_KEY may not be configured")
                print("   Edit .env and add your API key")
    else:
        print("❌ .env file missing")
        print("   Copy env_example.txt to .env and add your API key")
        all_good = False
    
    # Check documentation
    print("\n📖 Documentation:")
    doc_files = [
        "README.md",
        "QUICKSTART.md",
        "PROMPT_EVALUATION.md",
        "PROJECT_SUMMARY.md",
    ]
    
    for doc in doc_files:
        check_file(doc)
    
    # Final verdict
    print("\n" + "="*60)
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print("="*60)
        print("\n🚀 You're ready to run the agent:")
        print("   python main.py")
        print("\n📚 Or read the quick start guide:")
        print("   cat QUICKSTART.md")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("="*60)
        print("\n🔧 To fix missing packages:")
        print("   pip install pydantic python-dotenv google-generativeai mcp")
        print("\n🔑 To set up environment:")
        print("   cp env_example.txt .env")
        print("   nano .env  # Add your GEMINI_API_KEY")
        return 1


if __name__ == "__main__":
    sys.exit(main())

