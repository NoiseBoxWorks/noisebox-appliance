# NoiseBox Appliance- An Open-source Tool to Obscure Your Online Footprint

Read the full [NoiseBox Manifesto](Manifesto.md) to learn more about the mission behind outbound data poisoning.

NoiseBox is a privacy-hardened, Python-based web crawling script designed to run on scheduled intervals in a virtualized or native Linux environment to counter online data profiling.

**NoiseBox** disrupts the ability of ISPs and data brokers to profile your online footprint. By automatically rotating through seed files containing randomized, disassociated web URLs, it crawls nested links and background targets to continuously mask your normal web activity. 

This background noise confuses downstream data aggregators, rendering personal browsing data unmarketable.

## Features
* **Automated Rotation:** Cycles through multiple randomized seed lists to diversify traffic patterns.
* **Variable sleep/active schedule:** to mimic human use patterns.
* **Recursive Link Crawling:** Follows first- and second-level links from seed targets before looping.
* **Privacy-First Design:** Optimized for isolated Linux environments to prevent tracking leakage.

## Project Structure
* `appliance.py` - Core web crawling and scheduling script.
* `seeds_alpha.txt` - Primary target URL seed list.
* `seeds_beta.txt` - Secondary target URL seed list.
* `seeds_gamma.txt` - Tertiary target URL seed list.

## Requirements & Setup
1. A Linux environment (native or virtualized).
2. Python 3 installed with required networking libraries.

## Usage
Ensure your seed lists are populated and your privacy/VPN or proxy stack is active, then execute the appliance script:

```bash
python3 appliance.py

---

