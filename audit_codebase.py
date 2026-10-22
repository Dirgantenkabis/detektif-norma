import re
import os
import sys

def audit_emojis():
    # Regex range for emojis
    emoji_pattern = re.compile(
        "[\U00010000-\U0010ffff]|[\u200d\uFE0F\u2600-\u27bf\u2300-\u23ff]",
        re.UNICODE
    )

    files_to_check = ["index.html", "style.css", "game.js", "data.js"]
    total_found = 0

    print("=== AUDIT 1: EMOJI CHECK ===")
    for fname in files_to_check:
        if not os.path.exists(fname):
            continue
        with open(fname, "r", encoding="utf-8") as f:
            lines = f.readlines()
        file_found = 0
        for idx, line in enumerate(lines):
            # Abaikan URL atau karakter aman, cari emoji aktual
            matches = emoji_pattern.findall(line)
            # Filter false positives seperti bullet point \u2022 jika ada
            actual_emojis = [m for m in matches if m not in ["\u2022", "\u2013", "\u2014"]]
            if actual_emojis:
                print(f"[{fname}:{idx+1}] Found emojis: {actual_emojis}")
                file_found += len(actual_emojis)
        if file_found == 0:
            print(f"[OK] {fname}: 0 emojis found.")
        total_found += file_found

    assert total_found == 0, f"FAILED: Found {total_found} emojis!"
    print("PASS: 100% Emoji Free!\n")

def audit_external_resources():
    print("=== AUDIT 2: EXTERNAL CDNs / URLS ===")
    files_to_check = ["index.html", "style.css", "game.js", "data.js"]
    url_pattern = re.compile(r"https?://|//[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    total_found = 0

    for fname in files_to_check:
        if not os.path.exists(fname):
            continue
        with open(fname, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            # Kecualikan namespace XML SVG: http://www.w3.org/2000/svg
            if "w3.org" in line:
                continue
            matches = url_pattern.findall(line)
            if matches:
                print(f"[{fname}:{idx+1}] Found external URL: {line.strip()}")
                total_found += len(matches)

    assert total_found == 0, f"FAILED: Found {total_found} external URLs!"
    print("PASS: 100% Offline (No external URLs/CDNs)!\n")

if __name__ == "__main__":
    audit_emojis()
    audit_external_resources()
