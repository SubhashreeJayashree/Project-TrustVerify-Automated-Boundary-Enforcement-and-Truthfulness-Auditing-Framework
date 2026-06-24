import argparse
from trust_verify.config import MODELS

def parse_args():
    parser = argparse.ArgumentParser(
        description="Project TrustVerify: Automated AI Safety, Policy Adherence, and Gaslighting Auditing Suite."
    )
    
    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        help="List of model names to run. Supported: gpt-4o-mini, gpt-4o, gemini-1.5-flash, gemini-1.5-pro, mock-secure, mock-vulnerable, mock-weak-honest.",
        default=None
    )
    
    parser.add_argument(
        "--scenarios",
        type=str,
        nargs="+",
        choices=["bedsheet_aggression", "authority_impersonation", "ecommerce_bullying", "all"],
        default=["all"],
        help="List of scenarios to run. Use 'all' (default) to run all registered scenarios."
    )
    
    parser.add_argument(
        "--guardrail",
        action="store_true",
        help="Enable the Blue-Team Defensive Guardrail Middleware Layer."
    )
    
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Demo shortcut: Runs all mock models (mock-secure, mock-vulnerable, mock-weak-honest) against all scenarios."
    )

    args = parser.parse_args()

    # Post-process arguments
    if args.mock:
        args.models = ["mock-secure", "mock-vulnerable", "mock-weak-honest"]
        args.scenarios = ["all"]
    elif not args.models:
        # Default to gpt-4o-mini if OpenAI API key is set, else fall back to mock-vulnerable
        import os
        if os.environ.get("OPENAI_API_KEY"):
            args.models = ["gpt-4o-mini"]
        else:
            print("⚠️ No API keys found. Defaulting to Mock Models. Run with --mock for a full demo.")
            args.models = ["mock-secure", "mock-vulnerable", "mock-weak-honest"]

    if "all" in args.scenarios:
        args.scenarios = ["bedsheet_aggression", "authority_impersonation", "ecommerce_bullying"]

    return args
