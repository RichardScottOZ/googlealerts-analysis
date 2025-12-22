#!/usr/bin/env python3
"""
Configuration Validator

This script checks your setup and helps diagnose common configuration issues.
Run this before your first analysis to ensure everything is configured correctly.
"""

import os
import sys
from pathlib import Path

# Conditional import for dotenv (may not be installed yet)
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_status(message, status):
    """Print a status message."""
    icon = "✅" if status else "❌"
    print(f"{icon} {message}")


def check_file_exists(filename, required=True):
    """Check if a file exists."""
    exists = Path(filename).exists()
    status_text = "Required" if required else "Optional"
    
    if exists:
        print_status(f"{filename} found", True)
        return True
    else:
        print_status(f"{filename} not found ({status_text})", not required)
        return False


def check_environment_variable(var_name, required=True):
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    
    if value and value != f"your_{var_name.lower()}_here":
        print_status(f"{var_name} is set", True)
        return True
    else:
        status_text = "Required" if required else "Optional"
        print_status(f"{var_name} not set ({status_text})", not required)
        return False


def check_module_import(module_name):
    """Check if a Python module can be imported."""
    try:
        __import__(module_name)
        print_status(f"Module '{module_name}' can be imported", True)
        return True
    except ImportError:
        print_status(f"Module '{module_name}' cannot be imported", False)
        return False


def validate_setup():
    """Run all validation checks."""
    print_header("Google Alerts Analysis - Configuration Validator")
    
    issues = []
    
    # Check Python version
    print_header("Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro}", True)
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} (3.8+ recommended)", False)
        issues.append("Python version should be 3.8 or higher")
    
    # Check required files
    print_header("Required Files")
    files_ok = True
    
    if not check_file_exists("gmail_fetcher.py"):
        issues.append("gmail_fetcher.py is missing")
        files_ok = False
    
    if not check_file_exists("llm_categorizer.py"):
        issues.append("llm_categorizer.py is missing")
        files_ok = False
    
    if not check_file_exists("analyze_alerts.py"):
        issues.append("analyze_alerts.py is missing")
        files_ok = False
    
    if not check_file_exists("requirements.txt"):
        issues.append("requirements.txt is missing")
        files_ok = False
    
    # Check optional but recommended files
    print_header("Configuration Files")
    
    has_env = check_file_exists(".env", required=False)
    if not has_env:
        has_env_example = check_file_exists(".env.example", required=False)
        if has_env_example:
            print("  💡 Tip: Copy .env.example to .env and add your API keys")
            issues.append("Create .env file from .env.example")
    
    has_credentials = check_file_exists("credentials.json", required=False)
    if not has_credentials:
        print("  💡 Tip: Download OAuth credentials from Google Cloud Console")
        issues.append("Download credentials.json from Google Cloud Console")
    
    # Check environment variables (if .env exists)
    if has_env:
        print_header("Environment Variables")
        if HAS_DOTENV:
            load_dotenv()
        else:
            print("  ⚠️  Warning: python-dotenv not installed, cannot load .env file")
            print("  💡 Tip: Run 'pip install python-dotenv'")
        
        has_openai = check_environment_variable("OPENAI_API_KEY", required=False)
        has_gemini = check_environment_variable("GEMINI_API_KEY", required=False)
        
        if not has_openai and not has_gemini:
            print("  ⚠️  Warning: No LLM API key configured")
            issues.append("Set either OPENAI_API_KEY or GEMINI_API_KEY in .env")
        
        check_environment_variable("LLM_PROVIDER", required=False)
        check_environment_variable("LLM_MODEL", required=False)
    
    # Check Python dependencies
    print_header("Python Dependencies")
    deps_ok = True
    
    required_modules = [
        "pydantic",
        "dotenv",
        "google.auth",
        "google_auth_oauthlib",
        "googleapiclient",
    ]
    
    for module in required_modules:
        if not check_module_import(module):
            deps_ok = False
    
    # Check optional LLM modules
    has_openai_module = check_module_import("openai")
    has_gemini_module = check_module_import("google.generativeai")
    
    if not has_openai_module and not has_gemini_module:
        print("  ⚠️  Warning: No LLM client library installed")
        issues.append("Install openai or google-generativeai package")
    
    if not deps_ok:
        print("  💡 Tip: Run 'pip install -r requirements.txt' to install dependencies")
    
    # Summary
    print_header("Validation Summary")
    
    if not issues:
        print("\n✅ All checks passed! Your setup looks good.\n")
        print("Next steps:")
        print("  1. Run 'python demo.py' to see a demonstration")
        print("  2. Run 'python analyze_alerts.py' to analyze real alerts")
        print()
        return True
    else:
        print("\n⚠️  Some issues need attention:\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
        print("Quick fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Create .env file: cp .env.example .env")
        print("  • Add API keys to .env file")
        print("  • Download credentials.json from Google Cloud Console")
        print()
        print("See SETUP.md for detailed instructions.")
        print()
        return False


if __name__ == '__main__':
    try:
        success = validate_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        sys.exit(1)
