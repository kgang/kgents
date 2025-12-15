"""
Agent Town Monetization Demo

Demonstrates the complete payment flow:
1. Tourist user hits paywall
2. Upgrades to Resident tier
3. Gets access to LOD 3 actions
4. Uses monthly allowance
5. Exhausts allowance and needs credits
6. Purchases credit pack
7. Uses credits for additional actions

Run with: python -m impl.claude.agents.town.demo.monetization_demo
"""

import asyncio
from datetime import datetime, timedelta

from agents.town.budget_store import InMemoryBudgetStore, UserBudgetInfo
from agents.town.paywall import ActionType, PaywallCheck, check_paywall
from protocols.api.payments import (
    MockPaymentClient,
    handle_payment_succeeded,
    handle_subscription_created,
)


async def main() -> None:
    """Run monetization demo."""
    print("=" * 80)
    print("AGENT TOWN MONETIZATION DEMO")
    print("=" * 80)
    print()

    # Initialize systems
    budget_store = InMemoryBudgetStore()
    payment_client = MockPaymentClient()

    # Step 1: Tourist user tries to access LOD 3
    print("Step 1: Tourist tries to access LOD 3")
    print("-" * 80)

    user_id = "demo_user"
    budget = await budget_store.create_budget(user_id, "TOURIST")
    print(f"Created TOURIST budget for {user_id}")
    print(f"  Tier: {budget.subscription_tier}")
    print(f"  Credits: {budget.credits}")
    print()

    # Try LOD 3 (should be blocked)
    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_3)
    result = check_paywall(check)

    print("Attempting LOD 3 action...")
    print(f"  Allowed: {result.allowed}")
    if not result.allowed:
        print(f"  Reason: {result.reason}")
        print(f"  Upgrade options available: {len(result.upgrade_options)}")
        for i, option in enumerate(result.upgrade_options, 1):
            if option.type == "subscription":
                print(
                    f"    {i}. Subscribe to {option.tier} - ${option.price_usd:.2f}/month"
                )
                print(f"       Unlocks: {option.unlocks}")
            else:
                print(
                    f"    {i}. Buy {option.credits} credits - ${option.price_usd:.2f}"
                )
    print()

    # Step 2: User upgrades to RESIDENT tier
    print("Step 2: User upgrades to RESIDENT")
    print("-" * 80)

    # Create checkout session
    checkout = payment_client.create_subscription_checkout(
        user_id=user_id,
        tier="RESIDENT",
        success_url="https://agenttown.ai/success",
        cancel_url="https://agenttown.ai/cancel",
    )

    print("Created Stripe checkout session:")
    print(f"  Session ID: {checkout.session_id}")
    print(f"  Checkout URL: {checkout.session_url}")
    print(f"  Expires at: {checkout.expires_at}")
    print()

    # Simulate webhook after successful payment
    print("Simulating webhook: subscription.created")
    webhook_data = {
        "object": {
            "id": "sub_resident_123",
            "metadata": {
                "user_id": user_id,
                "tier": "RESIDENT",
            },
            "current_period_end": int(
                (datetime.now() + timedelta(days=30)).timestamp()
            ),
        }
    }

    webhook_result = handle_subscription_created(webhook_data)
    print("Webhook processed:")
    print(f"  User: {webhook_result['user_id']}")
    print(f"  Tier: {webhook_result['tier']}")
    print(f"  Renews: {webhook_result['renews_at']}")
    print()

    # Update budget store
    await budget_store.update_subscription(
        user_id, webhook_result["tier"], webhook_result["renews_at"]
    )
    budget_or_none = await budget_store.get_budget(user_id)
    assert budget_or_none is not None
    budget = budget_or_none
    print("Budget updated:")
    print(f"  Tier: {budget.subscription_tier}")
    print(f"  Renews: {budget.subscription_renews_at}")
    print()

    # Step 3: User can now access LOD 3
    print("Step 3: User accesses LOD 3 (included in subscription)")
    print("-" * 80)

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_3)
    result = check_paywall(check)

    print("Attempting LOD 3 action...")
    print(f"  Allowed: {result.allowed}")
    print(f"  Cost: {result.cost_credits} credits")
    print(f"  Uses included: {result.uses_included}")
    print()

    # Use 10 LOD 3 actions
    print("Using 10 LOD 3 actions...")
    for i in range(10):
        await budget_store.record_action(user_id, "lod3", 0)

    budget_or_none = await budget_store.get_budget(user_id)
    assert budget_or_none is not None
    budget = budget_or_none
    print(f"Monthly usage: {budget.monthly_usage}")
    print(f"LOD 3 remaining: {budget.monthly_remaining('lod3', lod_level=3)}")
    print()

    # Step 4: User exhausts monthly allowance
    print("Step 4: User exhausts monthly allowance (50 LOD 3 actions)")
    print("-" * 80)

    # Use remaining 40 actions
    for i in range(40):
        await budget_store.record_action(user_id, "lod3", 0)

    budget_or_none = await budget_store.get_budget(user_id)
    assert budget_or_none is not None
    budget = budget_or_none
    print(f"Monthly usage: {budget.monthly_usage}")
    print(f"LOD 3 remaining: {budget.monthly_remaining('lod3', lod_level=3)}")
    print()

    # Try one more LOD 3 (should require credits)
    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_3)
    result = check_paywall(check)

    print("Attempting LOD 3 action (monthly allowance exhausted)...")
    print(f"  Allowed: {result.allowed}")
    print(f"  Cost: {result.cost_credits} credits")
    print(f"  Uses included: {result.uses_included}")

    if not result.allowed:
        print(f"  Reason: {result.reason}")
        print("  Need to purchase credits")
    print()

    # Step 5: User purchases credit pack
    print("Step 5: User purchases STARTER credit pack (500 credits)")
    print("-" * 80)

    checkout = payment_client.create_credit_pack_checkout(
        user_id=user_id,
        pack="STARTER",
        success_url="https://agenttown.ai/success",
        cancel_url="https://agenttown.ai/cancel",
    )

    print("Created Stripe checkout session:")
    print(f"  Session ID: {checkout.session_id}")
    print(f"  Checkout URL: {checkout.session_url}")
    print()

    # Simulate webhook after successful payment
    print("Simulating webhook: payment_intent.succeeded")
    webhook_data = {
        "object": {
            "id": "pi_credits_123",
            "metadata": {
                "user_id": user_id,
                "credits": "500",
                "pack": "STARTER",
            },
        }
    }

    webhook_result = handle_payment_succeeded(webhook_data)
    print("Webhook processed:")
    print(f"  User: {webhook_result['user_id']}")
    print(f"  Credits: {webhook_result['credits']}")
    print()

    # Add credits to budget
    await budget_store.add_credits(user_id, webhook_result["credits"])
    budget_or_none = await budget_store.get_budget(user_id)
    assert budget_or_none is not None
    budget = budget_or_none
    print("Budget updated:")
    print(f"  Credits: {budget.credits}")
    print()

    # Step 6: User uses credits for LOD 3
    print("Step 6: User uses credits for LOD 3 actions")
    print("-" * 80)

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_3)
    result = check_paywall(check)

    print("Attempting LOD 3 action with credits...")
    print(f"  Allowed: {result.allowed}")
    print(f"  Cost: {result.cost_credits} credits")
    print(f"  Uses included: {result.uses_included}")
    print()

    # Use 5 LOD 3 actions with credits
    print("Using 5 LOD 3 actions (10 credits each)...")
    for i in range(5):
        await budget_store.record_action(user_id, "lod3", 10)

    budget_or_none = await budget_store.get_budget(user_id)
    assert budget_or_none is not None
    budget = budget_or_none
    print(f"Credits remaining: {budget.credits}")
    print()

    # Step 7: User tries LOD 4 (not included in RESIDENT)
    print("Step 7: User tries LOD 4 (requires credits)")
    print("-" * 80)

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_4)
    result = check_paywall(check)

    print("Attempting LOD 4 action...")
    print(f"  Allowed: {result.allowed}")
    print(f"  Cost: {result.cost_credits} credits")
    print(f"  Uses included: {result.uses_included}")
    print()

    # Use LOD 4 (100 credits)
    if result.allowed:
        print("Using LOD 4 action (100 credits)...")
        await budget_store.record_action(user_id, "lod4", 100)
        budget_or_none = await budget_store.get_budget(user_id)
        assert budget_or_none is not None
        budget = budget_or_none
        print(f"Credits remaining: {budget.credits}")
    print()

    # Final summary
    print("=" * 80)
    print("DEMO COMPLETE - FINAL STATE")
    print("=" * 80)
    budget_or_none = await budget_store.get_budget(user_id)
    assert budget_or_none is not None
    budget = budget_or_none
    print(f"User: {budget.user_id}")
    print(f"Tier: {budget.subscription_tier}")
    print(f"Credits: {budget.credits}")
    print(f"Monthly usage: {budget.monthly_usage}")
    print()
    print("Key insights:")
    print("  - Tourist users hit paywall for LOD 3+")
    print("  - Subscription tiers provide monthly allowances")
    print("  - Credits enable pay-per-use after allowance exhausted")
    print("  - Higher LOD levels require higher tier or more credits")
    print("  - All pricing is margin-safe per unified-v2.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())
