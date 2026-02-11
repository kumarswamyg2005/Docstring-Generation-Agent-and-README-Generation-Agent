#!/usr/bin/env python3
"""
Setup helper script for first-time users.

This script helps new users get started by:
1. Checking Python version
2. Installing dependencies
3. Setting up configuration
4. Running a quick demo
"""

import sys
import subprocess
from pathlib import Path
import shutil

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, you have {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def setup_environment():
    """Setup .env file if it doesn't exist."""
    print("\n⚙️  Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("⚠️  .env.example not found")
        return False
    
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from .env.example")
    print("\n💡 Tip: Edit .env to add your AI API key for enhanced generation")
    print("   Or use --no-ai flag to skip AI enhancement")
    
    return True


def run_demo():
    """Ask user if they want to run the demo."""
    print("\n🎬 Would you like to run the demo? (y/n): ", end="")
    response = input().strip().lower()
    
    if response in ['y', 'yes']:
        print("\n🚀 Running demo...\n")
        try:
            subprocess.check_call([sys.executable, "demo.py"])
            return True
        except subprocess.CalledProcessError:
            print("⚠️  Demo failed, but you can still use the tool")
            return False
    else:
        print("\n💡 You can run the demo anytime with: python demo.py")
        return True


def print_next_steps():
    """Print helpful next steps for the user."""
    print("\n" + "="*70)
    print("✨ SETUP COMPLETE!")
    print("="*70)
    print("\n📚 Next Steps:\n")
    print("1. (Optional) Edit .env file to add your API key for AI enhancement")
    print()
    print("2. Run the demo:")
    print("   python demo.py")
    print()
    print("3. Generate documentation for your project:")
    print("   python main.py --all")
    print()
    print("4. Get help:")
    print("   python main.py --help")
    print()
    print("5. Quick start guide:")
    print("   See QUICKSTART.md")
    print()
    print("="*70)
    print()


def main():
        """Main.
            """
    """Main setup workflow."""
    print("\n" + "="*70)
    print("🏆 DOCUMENTATION GENERATOR - SETUP")
    print("="*70 + "\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n⚠️  Environment setup incomplete, but you can continue")
    
    # Offer to run demo
    run_demo()
    
    # Print next steps
    print_next_steps()
    
    print("🎉 You're all set! Happy documenting!\n")


if __name__ == '__main__':
    main()
