class Reporter:
    def __init__(self):
        print("📊 Reporter initialized.")

    def generate_report(self, results: dict):
        print("Generating report...")
        # Placeholder for actual report generation logic
        zombies = results.get("zombie", [])
        if zombies:
            print(f"Found {len(zombies)} zombie accounts:")
            for i, zombie in enumerate(zombies):
                print(f"  {i+1}. {zombie}")
        else:
            print("No zombie accounts found. Wallet is clean.")
