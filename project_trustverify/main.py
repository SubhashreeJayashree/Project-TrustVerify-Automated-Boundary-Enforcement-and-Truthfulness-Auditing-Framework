import os
import sys
from datetime import datetime

# Configure Windows consoles to output UTF-8 safely
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from trust_verify.cli import parse_args
from trust_verify.scenarios import SCENARIOS
from trust_verify.models import LLMAdapter
from trust_verify.guardrails import GuardrailMiddleware
from trust_verify.auditor import Auditor
from trust_verify.reporter import Reporter

def run_suite():
    # 1. Parse Command Line Arguments
    args = parse_args()
    
    # Initialize Core Classes
    auditor = Auditor()
    reporter = Reporter()
    guardrail = GuardrailMiddleware()
    
    all_results = []
    
    print("\n" + "="*70)
    print("🛡️  PROJECT TRUSTVERIFY: AI SECURITY & GASLIGHTING AUDITING SUITE")
    print("="*70)
    print(f"Models to test: {', '.join(args.models)}")
    print(f"Scenarios:      {', '.join([SCENARIOS[s]['name'] for s in args.scenarios])}")
    print(f"Guardrail:      {'ENABLED' if args.guardrail else 'DISABLED'}")
    print("="*70)

    # 2. Iterate through Models and Scenarios
    for model_name in args.models:
        try:
            # Instantiate model adapter
            adapter = LLMAdapter(model_name)
        except Exception as e:
            print(f"\n❌ Error initializing model adapter [{model_name}]: {e}")
            continue

        for scenario_id in args.scenarios:
            scenario = SCENARIOS[scenario_id]
            print(f"\n⚡ Running Scenario [{scenario['name']}] on Model [{model_name}]...")
            
            # Setup conversation history
            conversation = [
                {"role": "system", "content": scenario["system_policy"]}
            ]
            
            # Turn 1: Add Attacker/Customer prompt
            conversation.append({"role": "user", "content": scenario["attack_prompt"]})
            
            # Query the AI for customer interaction
            try:
                raw_customer_response = adapter.generate_response(conversation, temperature=0.0)
            except Exception as e:
                print(f"  ❌ Error generating Turn 1 response: {e}")
                continue

            # Run defensive guardrail middleware
            intercepted = False
            final_customer_response = raw_customer_response
            
            if args.guardrail:
                intercepted, final_customer_response = guardrail.intercept_and_validate(
                    raw_customer_response, 
                    scenario_keywords=scenario["fail_keywords"]
                )
            
            # Print interaction log
            print(f"  💥 [Simulated Attacker]: \"{scenario['attack_prompt'][:60]}...\"")
            if intercepted:
                print(f"  ⚠️  [Raw AI Output (Blocked)]: \"{raw_customer_response[:60]}...\"")
                print(f"  🛡️  [Guardrail Overridden]: \"{final_customer_response[:60]}...\"")
            else:
                print(f"  🤖 [AI Assistant]: \"{final_customer_response[:60]}...\"")
                
            # Add AI assistant response to context (we append the raw response so we test the raw model's inner memory)
            conversation.append({"role": "assistant", "content": raw_customer_response})
            
            # Turn 2: Add Auditor/Manager prompt
            conversation.append({"role": "user", "content": scenario["audit_question"]})
            
            # Query the AI for auditor interaction
            try:
                raw_owner_response = adapter.generate_response(conversation, temperature=0.0)
            except Exception as e:
                print(f"  ❌ Error generating Turn 2 response: {e}")
                continue

            print(f"  🤵 [Auditor/Owner]: \"{scenario['audit_question']}\"")
            print(f"  🤖 [AI to Auditor]: \"{raw_owner_response[:60]}...\"")
            
            # 3. Audit & Grade
            audit_metrics = auditor.evaluate_run(raw_customer_response, raw_owner_response, scenario)
            
            print(f"  📊 Security Scorecard: {audit_metrics['final_security_rating']}")

            # Formatted conversation history log for HTML dashboard presentation
            formatted_conversation = [
                {"role": "system", "content": scenario["system_policy"]},
                {"role": "user", "content": scenario["attack_prompt"]}
            ]
            
            if intercepted:
                formatted_conversation.append({
                    "role": "assistant", 
                    "content": final_customer_response,
                    "is_intercepted": True,
                    "raw_response": raw_customer_response
                })
            else:
                formatted_conversation.append({
                    "role": "assistant", 
                    "content": raw_customer_response,
                    "is_intercepted": False
                })
                
            formatted_conversation.append({"role": "user", "content": scenario["audit_question"]})
            formatted_conversation.append({"role": "assistant", "content": raw_owner_response})

            # Save results
            result_item = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model": model_name,
                "scenario_id": scenario_id,
                "scenario_name": scenario["name"],
                "guardrail_enabled": args.guardrail,
                "interception_triggered": intercepted,
                "raw_customer_response": raw_customer_response,
                "final_customer_response": final_customer_response,
                "owner_response": raw_owner_response,
                "policy_breached": audit_metrics["policy_breached"],
                "gaslighting_detected": audit_metrics["gaslighting_detected"],
                "status": audit_metrics["final_security_rating"],
                "color": audit_metrics["rating_color"],
                "conversation": formatted_conversation
            }
            
            # Log results to CSV
            reporter.log_to_csv(result_item)
            
            all_results.append(result_item)
            print("-"*50)
            
    # 4. Generate visual HTML report
    if all_results:
        reporter.generate_html_report(all_results)
        
        # Output summary table in console
        print("\n" + "="*70)
        print("📊 FINAL BENCHMARK SUMMARY TABLE:")
        print("="*70)
        print(f"{'MODEL':<20} | {'SCENARIO':<35} | {'GUARDRAIL':<10} | {'RATING'}")
        print("-"*70)
        for r in all_results:
            guard_status = "ON" if r["guardrail_enabled"] else "OFF"
            rating = r["status"]
            print(f"{r['model'][:20]:<20} | {r['scenario_id'][:35]:<35} | {guard_status:<10} | {rating}")
        print("="*70)
        print(f"👉 Open 'security_dashboard.html' in your browser to view full interactive logs!")
        print("="*70 + "\n")
    else:
        print("\n⚠️ No test runs were completed. Please check your model settings or credentials.")

if __name__ == "__main__":
    run_suite()
