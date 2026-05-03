"""
Subdomain Enumerator - Ethical / Educational Use Only
Use only on domains you have explicit permission to test.
"""

import dns.resolver
import dns.zone
import dns.query
import dns.exception
import argparse
import concurrent.futures
import sys
import os
from datetime import datetime

# ─────────────────────────────────────────────
# ANSI Color Codes for Terminal Output
# ─────────────────────────────────────────────
class Color:
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

def banner():
    print(f"""{Color.CYAN}{Color.BOLD}
╔══════════════════════════════════════════╗
║        🔍 Subdomain Enumerator           ║
║     Ethical & Educational Use Only       ║
╚══════════════════════════════════════════╝
{Color.RESET}""")

# ─────────────────────────────────────────────
# DNS Resolution Function
# ─────────────────────────────────────────────
def resolve_subdomain(subdomain: str, domain: str, record_types: list, timeout: float) -> dict | None:
    """
    Resolves the given subdomain with the specified DNS record types.
    Returns a dictionary with the results if successful, otherwise None.
    """
    fqdn = f"{subdomain}.{domain}"
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout

    results = {}
    found = False

    for rtype in record_types:
        try:
            answers = resolver.resolve(fqdn, rtype)
            results[rtype] = [str(r) for r in answers]
            found = True
        except (dns.resolver.NXDOMAIN,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers,
                dns.exception.Timeout):
            pass
        except Exception:
            pass

    return {"fqdn": fqdn, "records": results} if found else None

# ─────────────────────────────────────────────
# Zone Transfer Denemesi
# ─────────────────────────────────────────────
def try_zone_transfer(domain: str) -> list[str]:
    """
    Sends a request to the domain's authoritative nameservers to perform a zone transfer.
    If successful, lists all the records in the zone.
    """
    found_subdomains = []
    print(f"\n{Color.YELLOW}[*] Trying Zone Transfer: {domain}{Color.RESET}")

    try:
        ns_records = dns.resolver.resolve(domain, "NS")
        nameservers = [str(ns) for ns in ns_records]
    except Exception as e:
        print(f"{Color.RED}[-] NS records could not be retrieved: {e}{Color.RESET}")
        return found_subdomains

    for ns in nameservers:
        ns_clean = ns.rstrip(".")
        print(f"  {Color.CYAN}[>] NS: {ns_clean}{Color.RESET}")
        try:
            zone = dns.zone.from_xfr(dns.query.xfr(ns_clean, domain, timeout=5))
            print(f"  {Color.GREEN}[+] Zone Transfer SUCCESSFUL → {ns_clean}{Color.RESET}")
            for name in zone.nodes.keys():
                record = str(name)
                if record != "@":
                    full = f"{record}.{domain}"
                    found_subdomains.append(full)
                    print(f"      {Color.GREEN}✔ {full}{Color.RESET}")
        except dns.exception.FormError:
            print(f"  {Color.RED}[-] Zone Transfer rejected: {ns_clean}{Color.RESET}")
        except Exception as e:
            print(f"  {Color.RED}[-] Error ({ns_clean}): {e}{Color.RESET}")

    return found_subdomains

# ─────────────────────────────────────────────
# Wordlist Loading Function
# ─────────────────────────────────────────────
def load_wordlist(path: str) -> list[str]:
    """Loads the wordlist file, filtering out empty lines and comments."""
    if not os.path.isfile(path):
        print(f"{Color.RED}[!] Wordlist not found: {path}{Color.RESET}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        words = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

    print(f"{Color.CYAN}[*] {len(words)} words loaded.{Color.RESET}")
    return words

# ─────────────────────────────────────────────
# Brute Force / Wordlist Scanning
# ─────────────────────────────────────────────
def brute_force_scan(
    domain: str,
    wordlist: list[str],
    record_types: list[str],
    threads: int,
    timeout: float,
    output_file: str | None
) -> list[dict]:
    """
    Performs a multi-threaded DNS query using the wordlist.
    Writes the found subdomains to the screen and (optionally) to a file.
    """
    found = []
    total = len(wordlist)
    checked = 0

    print(f"\n{Color.YELLOW}[*] Brute Force starting → {domain}")
    print(f"    Record types : {', '.join(record_types)}")
    print(f"    Thread count : {threads}")
    print(f"    Timeout       : {timeout}s")
    print(f"    Word count : {total}{Color.RESET}\n")

    out_handle = open(output_file, "w") if output_file else None

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(resolve_subdomain, word, domain, record_types, timeout): word
            for word in wordlist
        }

        for future in concurrent.futures.as_completed(futures):
            checked += 1
            result = future.result()

            # Progress indicator (every 100th check)
            if checked % 100 == 0 or checked == total:
                pct = (checked / total) * 100
                print(f"\r  {Color.CYAN}Progress: {checked}/{total} ({pct:.1f}%){Color.RESET}", end="", flush=True)

            if result:
                found.append(result)
                fqdn = result["fqdn"]
                records = result["records"]

                # Print to screen
                print(f"\n  {Color.GREEN}[+] BULUNDU: {fqdn}{Color.RESET}")
                for rtype, values in records.items():
                    for val in values:
                        print(f"      {Color.YELLOW}{rtype:6}{Color.RESET} → {val}")

                # Write to file
                if out_handle:
                    out_handle.write(f"{fqdn}\n")
                    for rtype, values in records.items():
                        for val in values:
                            out_handle.write(f"  {rtype}: {val}\n")
                    out_handle.write("\n")

    if out_handle:
        out_handle.close()

    print(f"\n\n{Color.BOLD}{'─'*45}{Color.RESET}")
    print(f"{Color.GREEN}[✔] Total found: {len(found)} subdomains{Color.RESET}")
    if output_file:
        print(f"{Color.CYAN}[✔] Results saved to: {output_file}{Color.RESET}")

    return found

# ─────────────────────────────────────────────
# Built-in Mini Wordlist (Fallback if file not found)
# ─────────────────────────────────────────────
BUILTIN_WORDLIST = [
    "www", "mail", "ftp", "smtp", "pop", "imap", "webmail",
    "admin", "portal", "vpn", "remote", "api", "dev", "staging",
    "test", "beta", "app", "mobile", "cdn", "static", "assets",
    "blog", "shop", "store", "login", "auth", "sso", "oauth",
    "docs", "help", "support", "status", "monitor", "grafana",
    "jenkins", "gitlab", "git", "svn", "jira", "confluence",
    "ns1", "ns2", "dns", "mx", "mx1", "mx2", "relay",
    "db", "database", "mysql", "postgres", "redis", "mongo",
    "backup", "files", "upload", "download", "media", "img",
    "secure", "ssl", "owa", "exchange", "autodiscover",
    "cpanel", "whm", "plesk", "webdisk", "ftp2",
    "intranet", "internal", "corp", "office", "hr", "erp",
    "dashboard", "panel", "manage", "console", "cloud",
]

# ─────────────────────────────────────────────
# CLI Arguments
# ─────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="Subdomain Enumerator — Ethical / Educational Use Only",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-d", "--domain",   required=True,  help="Target domain (e.g., example.com)")
    parser.add_argument("-w", "--wordlist",                  help="Wordlist file path")
    parser.add_argument("-o", "--output",                    help="Save results to file (filename)")
    parser.add_argument("-t", "--threads",  type=int, default=50,   help="Number of threads (default: 50)")
    parser.add_argument("--timeout",        type=float, default=2.0, help="DNS timeout (default: 2.0)")
    parser.add_argument("--no-bruteforce",  action="store_true",    help="Skip brute force")
    parser.add_argument("--zone-transfer",  action="store_true",    help="Attempt zone transfer")
    parser.add_argument(
        "--types",
        default="A,AAAA,CNAME",
        help="DNS record types, comma-separated (default: A,AAAA,CNAME)"
    )
    return parser.parse_args()

# ─────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────
def main():
    banner()

    # Ethical Use Warning
    print(f"{Color.RED}{Color.BOLD}[!] WARNING: This tool should only be used on systems you have legal permission to test.")
    print(f"    Unauthorized use is illegal!{Color.RESET}\n")

    args = parse_args()
    domain       = args.domain.strip().lower()
    record_types = [r.strip().upper() for r in args.types.split(",")]
    start_time   = datetime.now()

    print(f"{Color.BOLD}Target domain : {Color.CYAN}{domain}{Color.RESET}")
    print(f"{Color.BOLD}Start time    : {start_time.strftime('%H:%M:%S')}{Color.RESET}")

    # 1) Zone Transfer
    if args.zone_transfer:
        zt_results = try_zone_transfer(domain)
        if not zt_results:
            print(f"{Color.YELLOW}[*] Zone transfer results not found.{Color.RESET}")

    # 2) Brute Force / Wordlist
    if not args.no_bruteforce:
        if args.wordlist:
            wordlist = load_wordlist(args.wordlist)
        else:
            print(f"{Color.YELLOW}[*] Wordlist not specified → using built-in list ({len(BUILTIN_WORDLIST)} words).{Color.RESET}")
            wordlist = BUILTIN_WORDLIST

        brute_force_scan(
            domain       = domain,
            wordlist     = wordlist,
            record_types = record_types,
            threads      = args.threads,
            timeout      = args.timeout,
            output_file  = args.output
        )

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n{Color.BOLD}⏱  Total time: {elapsed:.2f} seconds{Color.RESET}\n")

if __name__ == "__main__":
    main()
