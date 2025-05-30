import subprocess
import time
import sys

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False

def main():
    print("🚀 Setting up Document Q&A Assistant...")
    
    # Pull required models
    print("\n📥 Pulling required models...")
    models = ["mistral", "nomic-embed-text"]
    
    for model in models:
        print(f"\nPulling {model}...")
        if not run_command(f"ollama pull {model}"):
            print(f"❌ Failed to pull {model}")
            sys.exit(1)
        print(f"✅ Successfully pulled {model}")

    print("\n🎉 Setup complete! You can now run the application with:")
    print("docker-compose up --build")

if __name__ == "__main__":
    main()