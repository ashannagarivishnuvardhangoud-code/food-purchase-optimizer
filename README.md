# food-purchase-optimizer

Food purchasing optimizer for menu planning under a fixed budget. Compare greedy heuristics with exact 0/1 knapsack, explore cost, menu coverage, and waste in a rotatable 3D chart, manage ingredient data, and review transparent buy-or-skip decisions. Built with Python, Streamlit, Plotly, and SQLite.

## Features

- Edit ingredient prices, benefits, priority, menu coverage, and expected waste.
- Compare a ratio-based greedy heuristic with exact 0/1 knapsack optimization.
- Rotate and inspect an interactive 3D chart of ingredient trade-offs.
- Explore algorithm behavior through an insertion-sort lab and greedy decision trace.
- Save ingredient edits and optimization history in a local SQLite database.

## Run locally

Python 3.10 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser. On first launch, it creates `food_optimizer.sqlite3` beside `app.py` and seeds sample ingredients. Use **Reset sample data** in the playground to restore the original rows.

## Optimization notes

- Ingredient cost is the 0/1 knapsack weight; benefit, priority, coverage, and waste feed the selected objective score.
- Menu coverage is based on the union of named menus supported by selected ingredients.
- Expected waste is a spend-weighted estimate: ingredient cost multiplied by the entered waste percentage.
- Knapsack is exact for integer-rupee capacities and the additive score shown in the controls. Runtime is O(n × B), where B is the rupee budget.
- The sorting lab uses adjacent-swap insertion sort, so its worst-case runtime is O(n²).
- Greedy is a ratio-based heuristic and does not guarantee an optimal 0/1 combination.

The SQLite database is generated at runtime and is intentionally excluded from version control.
