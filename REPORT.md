# Food Ingredient Purchase Optimizer — Project Report

**Report date:** October 3, 2026  
**Live application:** https://food-purchase-optimizer.streamlit.app/  
**Source repository:** https://github.com/ashannagarivishnuvardhangoud-code/food-purchase-optimizer

## Executive summary

The Food Ingredient Purchase Optimizer is an interactive planning prototype for choosing ingredients under a fixed purchasing budget. It lets a user edit ingredient assumptions, select an optimization objective, and compare a fast greedy heuristic with an exact 0/1 knapsack solution. The interface presents a light visual theme, an animated 3D hero scene, interactive charts, and step-by-step algorithm explanations. The project is intended to make budget trade-offs and algorithm behavior understandable; its sample estimates are not a substitute for live supplier, demand, or inventory data.

## Product scope and user experience

The dashboard starts with an editable ingredient library. Each row includes a name, category, cost, quantity, estimated benefit, priority, expected waste percentage, shelf life, and the menus it supports. Users can filter and sort the library, change the budget and objective, and run Greedy, Knapsack, or both algorithms against the same data. The playground can restore the curated 14-item sample set or generate a randomized dataset.

The visual design combines a custom CSS 3D ingredient scene with a draggable Plotly 3D scatter plot. The plot maps cost, number of supported menus, and expected waste, with color and hover details for ingredient categories and properties. Other visual summaries show budget allocation, expected waste before and after a plan, menu coverage, and selected versus rejected items. A sorting lab and algorithm traces expose comparisons, swaps, decisions, and dynamic-programming checkpoints.

## Technical architecture

The application is built with Python and Streamlit. Pandas prepares tabular data, Plotly renders interactive charts, and SQLite stores ingredient edits and optimization run history. The data and algorithm functions are separated into `optimizer.py`; `app.py` handles the dashboard, controls, session state, explanations, and charts. Dependencies are listed in `requirements.txt`.

For a local run, install the requirements and launch Streamlit from the application directory:

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

On first launch, the application creates `food_optimizer.sqlite3` beside the app and seeds the sample ingredients. The deployed application is hosted on Streamlit Community Cloud from this GitHub repository. Its SQLite file is local to the running app, so the repository does not configure an external durable database; cloud data edits and run history should be treated as potentially temporary across restarts or redeployments.

## Optimization model

Ingredient cost is the budget weight. Each item's value is a non-negative integer score derived from its menu coverage, benefit, priority, and waste percentage. The interface offers four documented weighted objectives: Maximum Menu Coverage, Minimum Waste, Maximum Value, and Balanced Optimization. High, Medium, and Low priority map to 3, 2, and 1 points. The weights make the trade-offs visible, but they are prototype assumptions rather than calibrated business forecasts.

- **Greedy:** ranks candidates by a selected value-to-cost, coverage-to-cost, waste-avoidance-to-cost, or balanced-score ratio, then takes each item that still fits. It is easy to trace, but its result is a heuristic and may miss the best combination. Its visible insertion-sort ordering has O(n²) worst-case time.
- **0/1 Knapsack:** uses integer rupee capacity and dynamic programming to maximize the chosen additive item score. Each ingredient can be selected at most once. It is optimal for that score formulation and input, with O(n × B) time for `n` items and budget capacity `B`; the implementation also records item decisions for reconstruction and explanation.
- **Insertion-sort lab:** sorts the current rows using adjacent swaps and reports measured comparisons, swaps, and elapsed time. Its worst-case time is O(n²).

The app evaluates a resulting plan with total spend and remaining budget, supported-menu coverage, and spend-weighted expected waste. Expected waste is calculated from each selected ingredient's cost multiplied by its entered waste percentage. It is an estimate based on user-provided inputs, not observed spoilage.

## Interpretation and limitations

An example default dashboard state observed during deployment showed a ₹5,000 budget, 14 sample ingredients, 12 selected items, ₹4,930 planned spend, 12 of 12 menus covered, and 5.5% expected waste (about ₹273). These figures describe that sample state only; results change when data, objective, or budget changes.

The exact algorithm guarantees the highest additive score under the modeled integer-budget constraint, not the best outcome for every displayed metric or a real purchasing plan. The model assumes fixed item costs and one-time selection, and does not account for price changes, demand forecasts, package-size constraints, supplier lead times, nutrition, perishability interactions, or uncertain waste. Those would require richer data and a validated business model.

## Conclusion

The project provides a hands-on demonstration of ingredient planning, budget-constrained optimization, and algorithm comparison in a polished interactive dashboard. Its strongest use today is exploration and education: adjust assumptions, inspect the resulting plan, and see why greedy and exact knapsack can differ. A production deployment would benefit from a durable database and validation against real procurement outcomes.
