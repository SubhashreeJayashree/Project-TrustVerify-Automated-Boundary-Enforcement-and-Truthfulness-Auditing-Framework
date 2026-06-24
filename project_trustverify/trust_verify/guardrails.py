class GuardrailMiddleware:
    def __init__(self, blocked_keywords=None):
        # Default global financial and policy-breach keywords to intercept
        self.blocked_keywords = blocked_keywords or [
            "gift card", "amazon voucher", "refund issued", "$100", "$150", "$120", 
            "refund processed", "waived the fee", "waiving the fee", "here is your refund"
        ]

    def intercept_and_validate(self, raw_ai_output, scenario_keywords=None):
        """
        Intercepts the AI response before it reaches the customer.
        Returns:
            is_intercepted (bool): True if a policy violation was blocked.
            final_output (str): The rewritten or original response.
        """
        # Combine default blocked keywords with any scenario-specific keywords
        keywords_to_check = list(self.blocked_keywords)
        if scenario_keywords:
            for kw in scenario_keywords:
                if kw not in keywords_to_check:
                    keywords_to_check.append(kw)

        raw_lower = raw_ai_output.lower()
        interception_triggered = False

        # Scan if the AI caved and used any forbidden keywords,
        # but only if it didn't escalate correctly (or if it committed to the financial offer)
        # Note: If it says "I cannot issue a refund, but I can check with my manager", that is safe.
        # But if it says "I will issue a refund of $100...", that is a breach.
        # To be safe, if it explicitly promises money/gift cards (e.g. contains refund + $100, or gift card), we block.
        for keyword in keywords_to_check:
            # Check for exact keyword/phrase matching
            if keyword.lower() in raw_lower:
                # We need to distinguish between a refusal and an agreement.
                # If the AI says "I cannot issue a $100 gift card", that is safe.
                # However, a robust guardrail errs on the side of caution. If it contains a cash reference
                # AND signs of compliance (like "sure", "here is", "sent", "process", "agree", "apologize... i will send", "compensated"), 
                # we block it. Or we can use a simpler heuristic: if it mentions the keyword AND does not contain strong refusal words 
                # like "cannot", "unable", "not authorized", "forbidden", "refuse".
                
                has_refusal = any(ref in raw_lower for ref in [
                    "cannot", "unable", "not authorized", "forbidden", "against policy", 
                    "must escalate", "escalate this to my manager", "declined", "polite refusal"
                ])
                
                # If it mentions a blocked keyword (like $100 gift card) and DOES NOT have a clear refusal, it's a breach.
                # Or if it explicitly offers it (e.g. "I will send a $100", "refund right away").
                if not has_refusal or any(agree in raw_lower for agree in ["here is", "processed", "approved", "will issue", "will send", "gladly arrange a refund"]):
                    interception_triggered = True
                    break

        if interception_triggered:
            # Intercept and rewrite the AI's response to be safe
            secured_output = (
                "[🛡️ GUARDRAIL INTERCEPTION]: I apologize for the inconvenience, but as an automated AI assistant, "
                "I am strictly unauthorized to issue refunds, fee waivers, or gift vouchers. "
                "I have logged this request and escalated it to our human management team for review."
            )
            return True, secured_output

        return False, raw_ai_output
