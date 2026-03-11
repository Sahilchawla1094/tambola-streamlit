"""
game.py — Tambola ticket generation and prize checking.
"""
import random

PRIZES = [
    ("EARLY_FIVE",   "🏃", "Early Five",    "First to mark any 5 numbers"),
    ("TOP_LINE",     "🔝", "Top Line",       "All 5 numbers in the top row"),
    ("MIDDLE_LINE",  "➡️", "Middle Line",    "All 5 numbers in the middle row"),
    ("BOTTOM_LINE",  "⬇️", "Bottom Line",    "All 5 numbers in the bottom row"),
    ("FOUR_CORNERS", "🔲", "Four Corners",   "All 4 corner numbers"),
    ("FULL_HOUSE",   "🏠", "Full House",     "All 15 numbers — Grand Prize!"),
]
PRIZE_IDS = [p[0] for p in PRIZES]
PRIZE_MAP  = {p[0]: {"emoji":p[1],"name":p[2],"desc":p[3]} for p in PRIZES}

# ── Ticket generation ──────────────────────────────────────────────────────────

def _col_range(col: int) -> list[int]:
    if col == 0: return list(range(1, 10))
    if col == 8: return list(range(80, 91))
    return list(range(col * 10, col * 10 + 10))

def generate_ticket() -> list[list[int]]:
    """Returns 3×9 grid; 0 = blank cell."""
    for _ in range(300):
        mask = [[False]*9 for _ in range(3)]
        col_counts = [0]*9
        ok = True
        for r in range(3):
            avail = [c for c in range(9) if col_counts[c] < 3]
            if len(avail) < 5: ok = False; break
            chosen = random.sample(avail, 5)
            for c in chosen:
                mask[r][c] = True
                col_counts[c] += 1
        if not ok or any(cc == 0 for cc in col_counts): continue
        grid = [[0]*9 for _ in range(3)]
        for c in range(9):
            rows = [r for r in range(3) if mask[r][c]]
            pool = random.sample(_col_range(c), len(rows))
            pool.sort()
            for i, r in enumerate(rows):
                grid[r][c] = pool[i]
        return grid
    raise RuntimeError("Ticket generation failed")

def all_numbers(grid: list) -> list[int]:
    return [n for row in grid for n in row if n > 0]

def corner_numbers(grid: list) -> list[int]:
    top = [n for n in grid[0] if n > 0]
    bot = [n for n in grid[2] if n > 0]
    return [top[0], top[-1], bot[0], bot[-1]]

def check_prize(prize_id: str, grid: list, called: set) -> bool:
    match prize_id:
        case "EARLY_FIVE":
            return sum(1 for n in all_numbers(grid) if n in called) >= 5
        case "TOP_LINE":
            return all(n in called for n in grid[0] if n > 0)
        case "MIDDLE_LINE":
            return all(n in called for n in grid[1] if n > 0)
        case "BOTTOM_LINE":
            return all(n in called for n in grid[2] if n > 0)
        case "FOUR_CORNERS":
            return all(n in called for n in corner_numbers(grid))
        case "FULL_HOUSE":
            return all(n in called for n in all_numbers(grid))
    return False

def claimable_prizes(grid: list, called: set, awarded: dict) -> list[str]:
    return [p for p in PRIZE_IDS if p not in awarded and check_prize(p, grid, called)]

# ── Room state helpers ─────────────────────────────────────────────────────────

def new_room(code: str, host_name: str) -> dict:
    bag = list(range(1, 91))
    random.shuffle(bag)
    return {
        "code":           code,
        "host_name":      host_name,
        "game_state":     "lobby",   # lobby | playing | over
        "players":        [],        # [{id, name}]
        "tickets":        {},        # player_id → grid
        "called_numbers": [],
        "number_bag":     bag,
        "awarded_prizes": {},        # prize_id → winner_name
        "winners":        [],        # [{player_name, prize_id}]
        "claims_pending": [],        # [{player_id, player_name, prize_id}]
    }
