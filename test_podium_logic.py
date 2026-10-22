# Uji logika podium & lencana
groups = [
    {"nama": "Tim Elang", "skor": 20, "correctCount": 4, "correctTimes": [10, 12, 14, 16], "warna": "#E74C3C"},
    {"nama": "Tim Harimau", "skor": 20, "correctCount": 3, "correctTimes": [8, 9, 10], "warna": "#F39C12"},
    {"nama": "Tim Kancil", "skor": 15, "correctCount": 2, "correctTimes": [5, 6], "warna": "#27AE60"},
    {"nama": "Tim Banteng", "skor": 10, "correctCount": 1, "correctTimes": [4], "warna": "#2980B9"},
    {"nama": "Tim Rusa", "skor": 10, "correctCount": 0, "correctTimes": [], "warna": "#8E44AD"}
]

def calc_avg(times):
    return sum(times) / len(times) if times else 0.0

for g in groups:
    g["avgTime"] = calc_avg(g["correctTimes"])

def sort_key(g):
    time_score = g["avgTime"] if g["avgTime"] > 0 else 999999
    return (-g["skor"], time_score)

sorted_groups = sorted(groups, key=sort_key)

for idx, g in enumerate(sorted_groups):
    if idx > 0:
        prev = sorted_groups[idx - 1]
        if g["skor"] == prev["skor"]:
            g["displayRank"] = prev["displayRank"]
        else:
            g["displayRank"] = idx + 1
    else:
        g["displayRank"] = 1

max_score = max(g["skor"] for g in sorted_groups) if sorted_groups else 0
fastest_pool = [g for g in sorted_groups if g["correctCount"] >= 3 and g["avgTime"] > 0]
min_avg = min((g["avgTime"] for g in fastest_pool), default=None)

for g in sorted_groups:
    badges = []
    if g["skor"] == max_score and max_score > 0:
        badges.append("Skor Tertinggi")
    if min_avg is not None and g["correctCount"] >= 3 and abs(g["avgTime"] - min_avg) < 0.001:
        badges.append("Tercepat")
    g["badges"] = badges
    print(f"#{g['displayRank']} | {g['nama']} | Skor: {g['skor']} | Avg: {g['avgTime']:.1f}s | Badges: {badges}")
