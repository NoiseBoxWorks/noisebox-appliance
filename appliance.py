import random
import time
import glob
import itertools
from collections import deque
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

def load_seeds(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"[!] {filename} not found.")
        return []

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
]

# Global tracker for daily jitter offset so it stays consistent throughout the day
current_day_seed = None
jitter_offset_minutes = 0

def get_daily_jitter():
    global current_day_seed, jitter_offset_minutes
    now = datetime.now(ZoneInfo("America/Denver"))
    today_date = now.date()
    
    # Generate a new random offset (-25 to +25 minutes) once per day
    if current_day_seed != today_date:
        current_day_seed = today_date
        # Seed pseudo-random generator with date string so it's stable for the day
        random.seed(str(today_date))
        jitter_offset_minutes = random.randint(-25, 25)
        random.seed() # Reset to true random for dwell times/user agents
        print(f"[*] Daily schedule jitter applied: shifting active windows by {jitter_offset_minutes} minutes today.")
    
    return jitter_offset_minutes

def is_active_hours():
    now = datetime.now(ZoneInfo("America/Denver"))
    offset = get_daily_jitter()
    
    # Convert current time to total minutes past midnight, adjust by jitter
    total_minutes = (now.hour * 60) + now.minute + offset
    adjusted_hour = (total_minutes // 60) % 24
    
    # Base windows: Morning (7-11), Evening (16-23), Night Owl (3-5)
    morning = 7 <= adjusted_hour < 11
    evening = 16 <= adjusted_hour < 23
    night_owl = 3 <= adjusted_hour < 5
    
    return morning or evening or night_owl

def crawl_appliance():
    # Automatically find all seed files matching seeds_*.txt
    seed_files = sorted(glob.glob("seeds_*.txt"))
    if not seed_files:
        seed_files = ["seeds.txt"]

    print(f"[*] Found {len(seed_files)} seed file(s) for rotation: {seed_files}")
    seed_cycle = itertools.cycle(seed_files)
    
    current_seed_file = next(seed_cycle)
    seeds = load_seeds(current_seed_file)
    print(f"[*] Loaded {len(seeds)} initial seeds from {current_seed_file}.")

    queue = deque()
    for seed in seeds:
        queue.append((seed, 0))

    visited = set()
    max_depth = 2
    max_queue_size = 200

    while True:
        if not is_active_hours():
            print("[*] Outside custom active windows (with jitter). Sleeping for 20 minutes before re-checking clock...")
            time.sleep(1200)
            continue

        if not queue:
            current_seed_file = next(seed_cycle)
            print(f"[*] Queue empty. Rotating to next seed file: {current_seed_file}...")
            seeds = load_seeds(current_seed_file)
            for seed in seeds:
                queue.append((seed, 0))
            visited.clear()
            time.sleep(30)
            continue

        url, depth = queue.popleft()

        if url in visited:
            continue

        visited.add(url)
        
        # Expanded browser-like headers
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }

        try:
            print(f"[*] Fetching (Depth {depth}) [{current_seed_file}]: {url}")
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string if soup.title else "No Title"
                print(f"    [+] Success | Title: {title.strip()} | Status: {response.status_code}")

                if depth < max_depth:
                    links_found = 0
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href']
                        full_url = urljoin(url, href)
                        parsed = urlparse(full_url)

                        if parsed.scheme in ('http', 'https') and full_url not in visited:
                            if len(full_url) < 200 and not full_url.endswith(('.png', '.jpg', '.jpeg', '.pdf', '.zip', '.css', '.js')):
                                if len(queue) < max_queue_size:
                                    queue.append((full_url, depth + 1))
                                    links_found += 1
                    print(f"    [+] Discovered and queued {links_found} new links.")
            else:
                print(f"    [-] Target returned status: {response.status_code}")

        except Exception as e:
            print(f"    [!] Request error: {e}")

        delay = random.randint(20, 60)
        time.sleep(delay)

if __name__ == "__main__":
    print("[*] Rotating crawler started with scheduled jitter enabled. Press Ctrl+C to stop.")
    try:
        crawl_appliance()
    except KeyboardInterrupt:
        print("\n[*] NoiseBox stopped by user.")
