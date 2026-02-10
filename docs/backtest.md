# Backtest 

This document describes the **backtesting layer**: how fills are translated into ledger updates,
how equity/returns is computed, and which configuration controls the simulation assumptions.

## Purpose
- Simulate trading over historical data using a ledger/accounting model.
- Apply execution assumptions (fills, fees, slippage) and update portfolio state.
- Produce reports/artifacts (trades, equity curve, summary metrics).

## Responsibilities (layer separation)
- Strategy: decides *what* to do (signals + sizing intent).
- Execution: decides *how* it fills (price + costs).
- Backtest: records fills into a ledger and computes cash/position/equity + PnL.

---

### Ledger model (conceptual)

A typical ledger tracks:

- cash balance (quote currency)

- position quantity (base units)

- average entry price (optional)

- equity = cash + position_qty * current_price

- trades table (fills)

On each fill:

- Update cash (subtract for buys, add for sells)

- Update position quantity

- Record fees and slippage

- Record a trade row (timestamp, side, qty, price, notional, fees)


### Common pitfalls
Currency confusion: `initial_cash` is quote currency; position qty is base units.

Annualization mismatch: wrong `periods_per_year` makes Sharpe/annual vol meaningless.

Irregular sampling: if bars are irregular, “per period” metrics become approximate; document assumptions.