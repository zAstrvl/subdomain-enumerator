<div align="center">
# 🔍 Subdomain Enumerator

> A fast, multi-threaded subdomain enumeration tool built with Python.
> Designed strictly for **ethical use** — authorized penetration testing, bug bounty programs, and educational purposes only.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Ethics](https://img.shields.io/badge/Use-Ethical%20Only-red?style=flat-square)
</div>

---

## 📌 Overview

**Subdomain Enumerator** is a lightweight yet powerful CLI tool that discovers subdomains of a target domain using two core techniques:

- **Brute Force / Wordlist Scanning** — Resolves subdomains by querying DNS against a wordlist
- **Zone Transfer (AXFR)** — Attempts to extract all DNS records from misconfigured nameservers

Built with `dnspython` and Python's `concurrent.futures`, it delivers fast, concurrent DNS resolution with clean, color-coded terminal output.

---

## ✨ Features

| Feature | Description |
|---|---|
| ⚡ Multi-threaded scanning | Concurrent DNS queries via `ThreadPoolExecutor` |
| 🌐 Zone Transfer (AXFR) | Detects misconfigured nameservers leaking all DNS records |
| 📋 Multiple record types | Supports `A`, `AAAA`, `CNAME`, `MX`, and more |
| 📦 Built-in wordlist | Works out-of-the-box without any external files |
| 💾 Output to file | Save results with the `-o` flag |
| 🎨 Color-coded output | ANSI-colored terminal output for easy reading |
| 🔧 Fully configurable | Tune threads, timeout, record types via CLI flags |

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/zAstrvl/subdomain-enumerator.git
cd subdomain-enumerator
```

### 2. Install Dependecies

**Python 3.10 or higher is required**

```bash
pip install dnspython
```

---

## 🛠️ Usage

```bash
python subdomain.py -d <target-domain> [options]
```

---

## Arguments

| Flag | Description | Defalut |
|---|---|---|
| -d, --domain | Required. Target domain (e.g. example.com) | — |
| -w, --wordlist | Path to a custom wordlist file | Built-in list |
| -o, --output | Save results to a file | None |
| -t, --threads | Number of concurrent threads | 50 |
| --timeout | DNS query timeout in seconds | 2.0 |
| --types | Comma-separated DNS record types to query	A,AAAA,CNAME | — |
| --zone-transfer | Attempt AXFR zone transfer on all nameservers | Disabled |
| --no-bruteforce | Skip wordlist brute force scan | Disabled |

## 💡 Examples

```bash
# Quick scan using the built-in wordlist
python subdomain.py -d example.com

# Scan with a custom wordlist and save results
python subdomain.py -d example.com -w wordlist.txt -o results.txt

# Attempt zone transfer + brute force
python subdomain.py -d example.com --zone-transfer

# Zone transfer only, skip brute force
python subdomain.py -d example.com --zone-transfer --no-bruteforce

# High-performance scan with custom record types
python subdomain.py -d example.com -t 100 --timeout 3 --types A,AAAA,CNAME,MX
```

---

## 🔬 How It Works

### 1. Brute Force / Wordlist Mode

>The tool iterates over every entry in the wordlist, constructs a fully qualified domain name (FQDN) such as api.example.com, and fires a DNS query for each specified record type. Successful resolutions are printed in real time with their resolved IP addresses or CNAME targets.

### 2. Zone Transfer (AXFR)

>The tool first fetches all NS (nameserver) records for the target domain, then attempts an AXFR zone transfer request against each nameserver. If a nameserver is misconfigured and allows zone transfers, the tool dumps all DNS records — a critical misconfiguration in real-world environments.

---

## 📋 Sample Output

```yaml
╔══════════════════════════════════════════╗
║        🔍 Subdomain Enumerator           ║
║     Ethical & Educational Use Only       ║
╚══════════════════════════════════════════╝

[!] WARNING: This tool should only be used on systems you have legal permission to test.
    Unauthorized use is illegal!

Target domain : example.com
Start time    : 13:04:21

[*] Brute Force starting → example.com
    Record types  : A, AAAA, CNAME
    Threads       : 50
    Timeout       : 2.0s
    Word count  : 68

  [+] FOUND: www.example.com
      A      → 93.184.216.34

  [+] FOUND: mail.example.com
      A      → 93.184.216.50
      MX     → mail.example.com

  Progress: 68/68 (100.0%)

─────────────────────────────────────────────
[✔] Total found: 2 subdomains
[✔] Results saved to: results.txt

⏱  Total time: 3.84 seconds
```

---

## 📚 Recommended Wordlists

>For more comprehensive scans, pair this tool with well-known community wordlists:

>   [SecLists](https://github.com/danielmiessler/SecLists/tree/master/Discovery/DNS) — DNS — Industry-standard DNS wordlists
>   [Assetnote](https://wordlists.assetnote.io/) Wordlists — Large-scale, data-driven subdomain lists

---

## ⚠️ Legal Disclaimer

>This tool is intended for authorized security testing and educational purposes only. Unauthorized use against systems you do not own or have explicit written permission to test is illegal and may violate laws such as the Computer Fraud and Abuse Act (CFAA), the UK Computer Misuse Act, and equivalent legislation in other jurisdictions. The author assumes no liability for any misuse or damage caused by this tool. Always obtain proper authorization before conducting any security assessment.

---