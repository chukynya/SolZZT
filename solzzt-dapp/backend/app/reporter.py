class Reporter:
    def __init__(self):
        pass

    def generate_report(self, sniffer_results: dict):
        """
        Generates and prints a structured report based on sniffer results.
        """
        found_zombie_accounts = len(sniffer_results.get("zombie", []))
        found_dust_accounts = len(sniffer_results.get("dust", []))
        total_recoverable_sol = sniffer_results.get("total_recoverable_sol", 0.0)

        print("\n--- SolZZT Agent Report ---")
        print(f"Found {found_zombie_accounts} Zombie Accounts.")
        print(f"Found {found_dust_accounts} Dust Accounts.")
        print(f"Total Liquidity Trapped: {total_recoverable_sol:.6f} SOL.")
        print("\nAgent Recommendation: EXECUTE RECYCLE.")
        print("---------------------------\n")

# Example Usage (for testing)
def main():
    # Example results from the Sniffer module
    example_sniffer_results = {
        "zombie": ["Addr1", "Addr2", "Addr3"],
        "dust": [{"address": "DustAddr1", "value_usd": 0.005}, {"address": "DustAddr2", "value_usd": 0.008}],
        "active": [{"address": "ActiveAddr1", "value_usd": 10.5}],
        "total_recoverable_sol": 0.002039 * 3
    }

    reporter = Reporter()
    reporter.generate_report(example_sniffer_results)

if __name__ == "__main__":
    main()