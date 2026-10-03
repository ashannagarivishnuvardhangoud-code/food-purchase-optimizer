"""Core data, persistence, and algorithms for the Food Ingredient Optimizer."""

from __future__ import annotations

import json
import random
import sqlite3
import time
from pathlib import Path
from typing import Any


DB_PATH = Path(__file__).with_name("food_optimizer.sqlite3")
MENU_CATALOG = [
    "Biryani", "Curries", "Rice bowls", "Pasta", "Salads", "Wraps",
    "Grilled plates", "Comfort meals", "Breakfast", "Soups", "Stir-fry", "Snacks",
]
CATEGORIES = ["Produce", "Grains", "Protein", "Dairy", "Pantry", "Other"]
PRIORITIES = ["High", "Medium", "Low"]

SAMPLE_INGREDIENTS = [
    {"name": "Rice", "category": "Grains", "cost": 800, "quantity": 5, "benefit": 82, "priority": "High", "waste_pct": 4.0, "shelf_life": 180, "menus": ["Biryani", "Rice bowls", "Curries", "Comfort meals", "Breakfast", "Soups", "Stir-fry", "Snacks"]},
    {"name": "Tomatoes", "category": "Produce", "cost": 350, "quantity": 2, "benefit": 54, "priority": "Medium", "waste_pct": 8.0, "shelf_life": 7, "menus": ["Curries", "Pasta", "Salads", "Wraps", "Comfort meals"]},
    {"name": "Chicken", "category": "Protein", "cost": 1200, "quantity": 2, "benefit": 96, "priority": "High", "waste_pct": 6.0, "shelf_life": 3, "menus": ["Biryani", "Curries", "Rice bowls", "Wraps", "Grilled plates", "Comfort meals", "Soups", "Stir-fry", "Snacks", "Pasta"]},
    {"name": "Potatoes", "category": "Produce", "cost": 500, "quantity": 3, "benefit": 63, "priority": "High", "waste_pct": 5.0, "shelf_life": 21, "menus": ["Curries", "Salads", "Comfort meals", "Breakfast", "Soups", "Snacks", "Biryani"]},
    {"name": "Onions", "category": "Produce", "cost": 250, "quantity": 2, "benefit": 66, "priority": "Medium", "waste_pct": 3.0, "shelf_life": 21, "menus": ["Biryani", "Curries", "Rice bowls", "Pasta", "Wraps", "Comfort meals"]},
    {"name": "Paneer", "category": "Dairy", "cost": 700, "quantity": 1, "benefit": 70, "priority": "High", "waste_pct": 7.0, "shelf_life": 5, "menus": ["Curries", "Rice bowls", "Wraps", "Grilled plates", "Comfort meals", "Snacks"]},
    {"name": "Lentils", "category": "Grains", "cost": 480, "quantity": 2, "benefit": 69, "priority": "High", "waste_pct": 2.5, "shelf_life": 150, "menus": ["Curries", "Rice bowls", "Comfort meals", "Breakfast", "Soups", "Snacks"]},
    {"name": "Spinach", "category": "Produce", "cost": 180, "quantity": 1, "benefit": 42, "priority": "Medium", "waste_pct": 12.0, "shelf_life": 4, "menus": ["Curries", "Salads", "Wraps", "Breakfast"]},
    {"name": "Bell peppers", "category": "Produce", "cost": 320, "quantity": 2, "benefit": 48, "priority": "Medium", "waste_pct": 9.0, "shelf_life": 6, "menus": ["Pasta", "Salads", "Wraps", "Grilled plates", "Stir-fry"]},
    {"name": "Yogurt", "category": "Dairy", "cost": 260, "quantity": 1, "benefit": 46, "priority": "Medium", "waste_pct": 6.0, "shelf_life": 8, "menus": ["Curries", "Rice bowls", "Wraps", "Grilled plates", "Breakfast"]},
    {"name": "Spice blend", "category": "Pantry", "cost": 160, "quantity": 1, "benefit": 58, "priority": "High", "waste_pct": 1.5, "shelf_life": 365, "menus": ["Biryani", "Curries", "Rice bowls", "Comfort meals", "Soups", "Stir-fry", "Snacks"]},
    {"name": "Pasta", "category": "Grains", "cost": 420, "quantity": 3, "benefit": 56, "priority": "Medium", "waste_pct": 3.5, "shelf_life": 240, "menus": ["Pasta", "Comfort meals", "Salads", "Soups", "Snacks"]},
    {"name": "Mushrooms", "category": "Produce", "cost": 390, "quantity": 1, "benefit": 51, "priority": "Low", "waste_pct": 14.0, "shelf_life": 4, "menus": ["Pasta", "Salads", "Grilled plates", "Soups", "Stir-fry"]},
    {"name": "Cooking oil", "category": "Pantry", "cost": 300, "quantity": 1, "benefit": 52, "priority": "Medium", "waste_pct": 1.0, "shelf_life": 365, "menus": ["Biryani", "Curries", "Rice bowls", "Pasta", "Grilled plates", "Comfort meals", "Breakfast", "Soups", "Stir-fry", "Snacks"]},
]


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                category TEXT NOT NULL,
                cost INTEGER NOT NULL CHECK(cost > 0),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                coverage INTEGER NOT NULL DEFAULT 0 CHECK(coverage >= 0),
                menus_supported TEXT NOT NULL DEFAULT '[]',
                priority TEXT NOT NULL,
                waste_pct REAL NOT NULL CHECK(waste_pct >= 0 AND waste_pct <= 100),
                shelf_life INTEGER NOT NULL CHECK(shelf_life > 0),
                benefit REAL NOT NULL CHECK(benefit >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS optimization_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                algorithm TEXT NOT NULL,
                budget INTEGER NOT NULL,
                priority TEXT NOT NULL,
                total_cost INTEGER NOT NULL,
                coverage_pct REAL NOT NULL,
                waste_pct REAL NOT NULL,
                score REAL NOT NULL,
                selected_ids TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '{}'
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
        if count == 0:
            for item in SAMPLE_INGREDIENTS:
                _insert_ingredient(conn, item)


def _insert_ingredient(conn: sqlite3.Connection, item: dict[str, Any]) -> int:
    menus = list(dict.fromkeys(menu for menu in item.get("menus", []) if menu in MENU_CATALOG))
    coverage = len(menus) if menus else int(item.get("coverage", 0))
    cursor = conn.execute(
        """INSERT INTO ingredients
           (name, category, cost, quantity, coverage, menus_supported, priority, waste_pct, shelf_life, benefit)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            item["name"].strip(), item["category"], int(item["cost"]), int(item["quantity"]),
            coverage, json.dumps(menus), item["priority"], float(item["waste_pct"]),
            int(item["shelf_life"]), float(item["benefit"]),
        ),
    )
    return int(cursor.lastrowid)


def list_ingredients() -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM ingredients ORDER BY name COLLATE NOCASE").fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["menus"] = json.loads(item.pop("menus_supported", "[]"))
        except (TypeError, json.JSONDecodeError):
            item["menus"] = []
            item.pop("menus_supported", None)
        result.append(item)
    return result


def create_ingredient(item: dict[str, Any]) -> int:
    with _connect() as conn:
        return _insert_ingredient(conn, item)


def update_ingredient(ingredient_id: int, item: dict[str, Any]) -> None:
    menus = list(dict.fromkeys(menu for menu in item.get("menus", []) if menu in MENU_CATALOG))
    with _connect() as conn:
        conn.execute(
            """UPDATE ingredients SET name=?, category=?, cost=?, quantity=?, coverage=?, menus_supported=?,
               priority=?, waste_pct=?, shelf_life=?, benefit=? WHERE id=?""",
            (item["name"].strip(), item["category"], int(item["cost"]), int(item["quantity"]),
             len(menus), json.dumps(menus), item["priority"], float(item["waste_pct"]),
             int(item["shelf_life"]), float(item["benefit"]), ingredient_id),
        )


def delete_ingredient(ingredient_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM ingredients WHERE id=?", (ingredient_id,))


def reset_sample_data() -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM ingredients")
        for item in SAMPLE_INGREDIENTS:
            _insert_ingredient(conn, item)


def replace_with_random_data(seed: int | None = None, count: int = 16) -> None:
    rng = random.Random(seed)
    names = [
        ("Sweet corn", "Produce"), ("Black beans", "Grains"), ("Tofu", "Protein"),
        ("Carrots", "Produce"), ("Cucumber", "Produce"), ("Cheddar", "Dairy"),
        ("Oats", "Grains"), ("Broccoli", "Produce"), ("Fish fillet", "Protein"),
        ("Chickpeas", "Grains"), ("Coconut milk", "Dairy"), ("Noodles", "Grains"),
        ("Lime", "Produce"), ("Peanut butter", "Pantry"), ("Garlic", "Produce"),
        ("Eggs", "Protein"), ("Quinoa", "Grains"), ("Avocado", "Produce"),
    ]
    rng.shuffle(names)
    items = []
    for name, category in names[:count]:
        menu_count = rng.randint(2, 7)
        items.append({
            "name": name, "category": category, "cost": rng.randrange(120, 1301, 10),
            "quantity": rng.randint(1, 5), "benefit": rng.randint(28, 95),
            "priority": rng.choice(PRIORITIES), "waste_pct": round(rng.uniform(1, 18), 1),
            "shelf_life": rng.choice([3, 5, 7, 14, 30, 90, 180]),
            "menus": rng.sample(MENU_CATALOG, menu_count),
        })
    with _connect() as conn:
        conn.execute("DELETE FROM ingredients")
        for item in items:
            _insert_ingredient(conn, item)


def save_run(result: dict[str, Any]) -> None:
    with _connect() as conn:
        conn.execute(
            """INSERT INTO optimization_runs
               (algorithm, budget, priority, total_cost, coverage_pct, waste_pct, score, selected_ids, details)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (result["algorithm"], result["budget"], result["priority"], result["metrics"]["total_cost"],
             result["metrics"]["coverage_pct"], result["metrics"]["waste_pct"], result["metrics"]["score"],
             json.dumps(result["selected_ids"]), json.dumps(result.get("summary", {}))),
        )


def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM optimization_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def utility(item: dict[str, Any], objective: str) -> int:
    """Return an integer-valued objective so the DP has deterministic ties."""
    coverage = float(item.get("coverage", 0))
    benefit = float(item.get("benefit", 0))
    waste = float(item.get("waste_pct", 0))
    priority = {"High": 3, "Medium": 2, "Low": 1}.get(item.get("priority"), 1)
    if objective == "Maximum Menu Coverage":
        raw = coverage * 100 + benefit * 4 + priority * 12 - waste * 1.3
    elif objective == "Minimum Waste":
        raw = benefit * 15 + coverage * 15 + priority * 5 - waste * 45
    elif objective == "Maximum Value":
        raw = benefit * 100 + coverage * 12 + priority * 10 - waste * 2
    else:  # Balanced Optimization
        raw = benefit * 52 + coverage * 48 + priority * 16 - waste * 4
    return max(0, int(round(raw * 10)))


def _greedy_ratio(item: dict[str, Any], strategy: str, objective: str) -> float:
    cost = max(1, int(item["cost"]))
    if strategy == "Highest Coverage / Cost":
        numerator = float(item.get("coverage", 0))
    elif strategy == "Highest Value / Cost":
        numerator = float(item.get("benefit", 0))
    elif strategy == "Lowest Waste / Cost":
        numerator = 100 - float(item.get("waste_pct", 0))
    else:
        numerator = utility(item, objective) / 10
    return numerator / cost


def run_greedy(items: list[dict[str, Any]], budget: int, strategy: str, objective: str) -> dict[str, Any]:
    started = time.perf_counter_ns()
    ordered, comparisons, _ = _insertion_sort(items, lambda x: _greedy_ratio(x, strategy, objective), reverse=True)
    remaining = int(budget)
    selected: list[dict[str, Any]] = []
    decisions = []
    for rank, item in enumerate(ordered, 1):
        ratio = _greedy_ratio(item, strategy, objective)
        fits = int(item["cost"]) <= remaining and ratio > 0
        if fits:
            selected.append(item)
            remaining -= int(item["cost"])
            why = f"Ranked #{rank} by {strategy.lower()} and fit the ₹{remaining + int(item['cost']):,} remaining budget at this step."
            decision = "Selected"
        else:
            if ratio <= 0 and int(item["cost"]) <= remaining:
                why = "Its score under this ratio is zero, so it adds no coverage, value, or waste-avoidance benefit."
                decision = "Rejected · no positive ratio"
            else:
                why = f"₹{int(item['cost']):,} cost exceeds the ₹{remaining:,} remaining budget after higher-ranked feasible picks."
                decision = "Rejected · over remaining budget"
        decisions.append({
            "step": rank, "id": item["id"], "name": item["name"], "cost": int(item["cost"]),
            "benefit": item["benefit"], "ratio": ratio,
            "remaining": remaining, "decision": decision, "why": why,
        })
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    return {
        "algorithm": "Greedy", "selected_ids": [item["id"] for item in selected],
        "decisions": decisions, "comparisons": comparisons, "elapsed_ms": elapsed_ms,
        "strategy": strategy,
    }


def _insertion_sort(items: list[dict[str, Any]], score_fn, reverse: bool = False) -> tuple[list[dict[str, Any]], int, int]:
    ordered = list(items)
    comparisons = 0
    swaps = 0
    for index in range(1, len(ordered)):
        current = index
        while current > 0:
            comparisons += 1
            left = score_fn(ordered[current - 1])
            right = score_fn(ordered[current])
            out_of_order = left < right if reverse else left > right
            if not out_of_order:
                break
            ordered[current - 1], ordered[current] = ordered[current], ordered[current - 1]
            swaps += 1
            current -= 1
    return ordered, comparisons, swaps


def sort_items(items: list[dict[str, Any]], criterion: str, direction: str = "Best first") -> dict[str, Any]:
    def criterion_value(item: dict[str, Any]):
        if criterion == "Cost":
            return float(item["cost"])
        if criterion == "Coverage":
            return float(item["coverage"])
        if criterion == "Waste":
            return float(item["waste_pct"])
        if criterion == "Value":
            return float(item["benefit"])
        if criterion == "Value / Cost ratio":
            return float(item["benefit"]) / max(1, float(item["cost"]))
        if criterion == "Priority":
            return {"High": 3, "Medium": 2, "Low": 1}.get(item["priority"], 0)
        return float(item["cost"])

    reverse = direction == "Best first" and criterion not in ("Cost", "Waste")
    if direction == "Best first" and criterion in ("Cost", "Waste"):
        reverse = False
    if direction == "Lowest first":
        reverse = False
    if direction == "Highest first":
        reverse = True

    started = time.perf_counter_ns()
    ordered, comparisons, swaps = _insertion_sort(items, criterion_value, reverse=reverse)
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    return {"items": ordered, "comparisons": comparisons, "swaps": swaps, "elapsed_ms": elapsed_ms}


def run_knapsack(items: list[dict[str, Any]], budget: int, objective: str) -> dict[str, Any]:
    """Exact 0/1 knapsack DP with rupee capacity and an item-by-capacity trace."""
    started = time.perf_counter_ns()
    capacity = max(0, int(budget))
    dp = [0] * (capacity + 1)
    decision_rows: list[bytearray] = []
    snapshots: list[list[int]] = []
    trace_capacities = sorted(set([0, capacity, *[round(capacity * fraction) for fraction in (.2, .4, .6, .8)]]))
    cells_calculated = 0
    for item in items:
        cost = int(item["cost"])
        value = utility(item, objective)
        chose = bytearray(capacity + 1)
        for cap in range(capacity, cost - 1, -1):
            cells_calculated += 1
            candidate = dp[cap - cost] + value
            if candidate > dp[cap]:
                dp[cap] = candidate
                chose[cap] = 1
        decision_rows.append(chose)
        snapshots.append([dp[checkpoint] for checkpoint in trace_capacities])

    selected_ids: list[int] = []
    cap = capacity
    for index in range(len(items) - 1, -1, -1):
        if decision_rows[index][cap]:
            selected_ids.append(items[index]["id"])
            cap -= int(items[index]["cost"])
    selected_ids.reverse()
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    return {
        "algorithm": "0/1 Knapsack", "selected_ids": selected_ids,
        "dp_rows": snapshots, "dp_capacities": trace_capacities, "cells_calculated": cells_calculated,
        "elapsed_ms": elapsed_ms, "optimal_value": dp[capacity],
    }


def evaluate(items: list[dict[str, Any]], selected_ids: list[int], budget: int) -> dict[str, Any]:
    selected_id_set = set(selected_ids)
    selected = [item for item in items if item["id"] in selected_id_set]
    total_cost = sum(int(item["cost"]) for item in selected)
    total_coverage = sum(int(item.get("coverage", 0)) for item in selected)
    max_coverage = sum(int(item.get("coverage", 0)) for item in items)
    covered_menus = sorted({menu for item in selected for menu in item.get("menus", [])}, key=MENU_CATALOG.index)
    waste_exposure = sum(int(item["cost"]) * float(item["waste_pct"]) / 100 for item in selected)
    baseline_exposure = sum(int(item["cost"]) * float(item["waste_pct"]) / 100 for item in items)
    selected_cost = max(1, total_cost)
    baseline_cost = max(1, sum(int(item["cost"]) for item in items))
    waste_pct = waste_exposure / selected_cost * 100 if selected else 0.0
    baseline_waste_pct = baseline_exposure / baseline_cost * 100 if items else 0.0
    coverage_pct = len(covered_menus) / len(MENU_CATALOG) * 100 if MENU_CATALOG else 0.0
    coverage_units_pct = total_coverage / max(1, max_coverage) * 100 if items else 0.0
    spend_pct = total_cost / max(1, int(budget)) * 100
    score = 0.65 * coverage_pct + 0.25 * max(0.0, 100 - waste_pct) + 0.10 * min(100, spend_pct)
    return {
        "selected": selected, "total_cost": total_cost, "remaining": int(budget) - total_cost,
        "coverage_count": len(covered_menus), "coverage_pct": coverage_pct,
        "coverage_units": total_coverage, "coverage_units_pct": coverage_units_pct,
        "covered_menus": covered_menus, "waste_pct": waste_pct,
        "baseline_waste_pct": baseline_waste_pct,
        "waste_exposure": waste_exposure, "baseline_exposure": baseline_exposure,
        "items_selected": len(selected), "score": score, "spend_pct": spend_pct,
        "total_budget": int(budget),
    }
