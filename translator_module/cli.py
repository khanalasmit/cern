import os
import sys
import json

def main():
    # Load environment variables
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path)
    except ImportError:
        # Fallback: manual .env parsing if python-dotenv is not installed
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, val = line.split('=', 1)
                        os.environ.setdefault(key.strip(), val.strip())
        except Exception:
            pass

    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_base_url = os.environ.get("LLM_BASE_URL")
    llm_model = os.environ.get("LLM_MODEL")

    if not llm_api_key or llm_api_key == "your_api_key_here":
        print("Warning: It looks like your LLM_API_KEY is not set correctly in the .env file.")
        print("Please update it before running queries.")
        print("-" * 50)

    print("Initializing OKS Intelligent Query Agent...")

    # Initialize the translator
    from agent.translator import OksTranslator
    # Resolve repo-root data files relative to this file (works on any OS)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        translator = OksTranslator(
            os.path.join(repo_root, "oks_scraped", "oks_schema_examples.xml"),
            os.path.join(repo_root, "oks_scraped", "gold_pairs.jsonl"),
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
