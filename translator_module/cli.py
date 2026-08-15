import json
import os
import sys
from pathlib import Path


MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parent


def _reexec_with_repo_venv() -> None:
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    if not venv_python.is_file():
        return

    current_python = Path(sys.executable).resolve()
    if current_python == venv_python.resolve():
        return

    os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])


_reexec_with_repo_venv()

def main():
    # Load environment variables
    try:
        from dotenv import load_dotenv
        for env_path in (MODULE_DIR / ".env", REPO_ROOT / ".env"):
            if env_path.is_file():
                # Project configuration must take precedence over any stale
                # LLM_* variables exported by a previous shell session.
                load_dotenv(env_path, override=True)
                break
    except ImportError:
        # Fallback: manual .env parsing if python-dotenv is not installed
        for env_path in (MODULE_DIR / ".env", REPO_ROOT / ".env"):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, val = line.split('=', 1)
                            os.environ[key.strip()] = val.strip()
                break
            except Exception:
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
    from agent.translator import OksTranslator
    try:
        schema_xml_path = REPO_ROOT / "oks_scraped" / "oks_schema_examples.xml"
        gold_pairs_path = REPO_ROOT / "oks_scraped" / "gold_pairs.jsonl"
        translator = OksTranslator(
            str(schema_xml_path),
            str(gold_pairs_path),
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
