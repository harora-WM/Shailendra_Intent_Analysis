#!/usr/bin/env python3
"""
Test script for Intent Classifier
Tests the classifier with predefined queries
"""

from intent_classifier import IntentClassifier


def test_classifier():
    """Test the classifier with example queries"""
    print("="*80)
    print("TESTING INTENT CLASSIFIER")
    print("="*80)
    print("\nInitializing classifier...")

    try:
        classifier = IntentClassifier()
        print("✅ Classifier initialized successfully!\n")
    except Exception as e:
        print(f"❌ Failed to initialize classifier: {e}")
        return

    # Test queries covering different intent categories
    test_queries = [
        # STATE category
        "How is my application now?",
        "Is payment-api healthy?",
        "Which SLOs are breached?",

        # TREND category
        "What is drifting in last 1h?",
        "Today vs last month",

        # PATTERN category
        "Have we seen this before?",

        # CAUSE category
        "Why is payment-api failing?",
        "Why multiple services unhealthy?",

        # IMPACT category
        "What else breaks if this fails?",
        "Which customers are affected?",

        # ACTION category
        "How do I fix this now?",
        "Should I rollback this change?",

        # PREDICT category
        "What might fail next?",
        "Is this deployment risky?",

        # OPTIMIZE category
        "What is slowing us down?",
        "Which queries are costly?",

        # EVIDENCE category
        "Show evidence for RCA",
        "What happened step-by-step?",

        # Multiple intents
        "What alerts are active and what incidents are open?",
        "Are we meeting our SLOs and what's the trend?",
    ]

    print(f"Running {len(test_queries)} test queries...\n")

    results = []
    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] Testing: {query}")

        try:
            result = classifier.classify(query)
            results.append(result)
            classifier.print_result(result)
        except Exception as e:
            print(f"❌ Error: {e}\n")

        # Add a small delay to avoid rate limiting
        import time
        time.sleep(0.5)

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"\nTotal queries tested: {len(test_queries)}")
    print(f"Successful classifications: {len([r for r in results if 'error' not in r])}")
    print(f"Failed classifications: {len([r for r in results if 'error' in r])}")

    # Intent distribution
    all_primary_intents = []
    for result in results:
        if 'primary_intents' in result:
            all_primary_intents.extend(result['primary_intents'])

    if all_primary_intents:
        print(f"\nTotal primary intents detected: {len(all_primary_intents)}")
        print(f"Unique intents detected: {len(set(all_primary_intents))}")

        # Count frequency
        from collections import Counter
        intent_counts = Counter(all_primary_intents)
        print("\nMost common intents:")
        for intent, count in intent_counts.most_common(5):
            print(f"   {intent}: {count}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_classifier()
