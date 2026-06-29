# Building Energy System Optimization API

This repository contains a Python/Pyomo implementation of a building energy system optimization workflow. The model evaluates an optimized energy system configuration for a building using photovoltaic generation, wind generation, battery storage, grid purchase/sale, and unmet-load penalty terms.

The original research model was developed by **Navid Shirzadi**. This repository contains the refactored Python implementation and API integration work by **Alireza Adli** for use in a research software/platform integration context.

## What The Project Does

The optimization model estimates an energy system configuration for a building and returns summary indicators including:

- Objective function value
- Cost of energy
- Number of PV panels
- Number of wind turbines
- Battery storage capacity
- Total capital cost
- Renewable penetration
- Payback period

The model uses `Pyomo` for mathematical optimization and exposes a Flask API endpoint for running the workflow through HTTP requests.

## Repository Structure

```text
energy_optimization_po.py       # Pyomo optimization model
energy_optimization_po_api.py   # Flask API wrapper
data/Input_Daily_Sum.xlsx       # Required input data
docs/                           # Project documentation
requirements.txt                # Python dependencies
```
