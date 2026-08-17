import os
import sys
import json

# Running ``python cli.py`` makes this directory importable, but not its
# parent.  Add the repository root so absolute ``translator_module.*``
# imports used by the agent resolve without requiring a different command.
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(MODULE_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

def main():
    # Load environment variables
    try:
        from dotenv import load_dotenv
        for env_path in (os.path.join(MODULE_DIR, '.env'), os.path.join(REPO_ROOT, '.env')):
            if os.path.isfile(env_path):
                load_dotenv(env_path, override=True)
                break
    except ImportError:
        # Fallback: manual .env parsing if python-dotenv is not installed
        for env_path in (os.path.join(MODULE_DIR, '.env'), os.path.join(REPO_ROOT, '.env')):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, val = line.split('=', 1)
                            os.environ[key.strip()] = val.strip()
                break
            except FileNotFoundError:
                continue

    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_base_url = os.environ.get("LLM_BASE_URL")
    llm_model = os.environ.get("LLM_MODEL")

    if not llm_api_key or llm_api_key == "your_api_key_here":
        print("Warning: It looks like your LLM_API_KEY is not set correctly in the .env file.")
        print("Please update it before running queries.")
        print("-" * 50)

    print("Initializing OKS Intelligent Query Agent...")

    # Initialize the translator
    from translator_module.agent.translator import OksTranslator
    # Resolve repo-root data files relative to this file (works on any OS)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        translator = OksTranslator(
            os.path.join(repo_root, "combined_data", "oks_schema_corpus.xml"),
            os.path.join(repo_root, "combined_data", "all_few_shot.jsonl"),
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model
        )
    except Exception as e:
        print(f"Failed to initialize the translator: {e}")
        return

    print("Ready! Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            query = input("\nEnter your query: ")
            if query.lower().strip() in ['exit', 'quit']:
                print("Goodbye!")
                break
            if not query.strip():
                continue

            print("Thinking...")
            result = translator.translate(query)

            print("\n" + "=" * 60)
            if result.get("status") == "success":
                print("  OKS Query (copy-paste ready):")
                print(f"  {result.get('oks_query')}")
                print("-" * 60)

                explanation = result.get("explanation", "")
                if explanation:
                    print(f"\n  Explanation:\n  {explanation}")
                    print("-" * 60)

                print(f"\n  IR (Intermediate Representation):")
                ir = result.get("ir", {})
                # Print IR without the explanation field to avoid duplication
                ir_display = {k: v for k, v in ir.items() if k != "explanation"}
                print(f"  {json.dumps(ir_display, indent=2)}")
            else:
                print(f"  Error: {result.get('message')}")
            print("=" * 60 + "\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
