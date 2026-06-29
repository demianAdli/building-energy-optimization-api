# Building Energy System Optimization API

This repository contains a Python/Pyomo implementation of a building energy
system optimization workflow. The model optimizes a building energy system with
photovoltaic generation, wind turbines, battery storage, grid purchases, grid
sales, and unmet-load penalty terms.

The original research model was developed by **Navid Shirzadi**. The
integration, refactoring, and Flask API wrapper in this repository were prepared
by **Alireza Adli** for the CERC/NGCI Urban Simulation Platform research
software context.

## Project Structure

```text
energy_optimization_po.py       # Main Pyomo optimization model
energy_optimization_po_api.py   # Flask API wrapper exposing POST /result
data/Input_Daily_Sum.xlsx       # Required sample input data
docs/                           # Project documentation and notes
requirements.txt                # Python package dependencies
```

## Required Input Data

The model expects the sample workbook at:

```text
data/Input_Daily_Sum.xlsx
```

The workbook is read by `energy_optimization_po.py` and is expected to contain
daily input series for a 365-day optimization horizon. The current model reads
these columns:

- `time`
- `Load`
- `Wind`
- `PV`

API callers may optionally provide `building_load` as a JSON list. If omitted,
the model uses the `Load` series from `data/Input_Daily_Sum.xlsx`.

## Solver Information

The optimization model is built with `Pyomo` and currently uses:

```python
SolverFactory('scip')
```

Install SCIP separately and make sure the `scip` executable is available on
your system `PATH` before running the API. The Python dependencies in
`requirements.txt` do not install the external SCIP solver binary.

If SCIP is not installed or is not on `PATH`, the API will fail when the solver
step is reached.

## Setup

Run the following commands from the repository root.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Verify that SCIP is available:

```bash
scip --version
```

## Run The API

Start the Flask API from the repository root:

```bash
python energy_optimization_po_api.py
```

By default, Flask serves the API at:

```text
http://127.0.0.1:5000
```

The optimization endpoint is:

```text
POST /result
```

## API Usage

Run the model with default parameters and the bundled Excel input data:

```bash
curl -X POST http://127.0.0.1:5000/result \
  -H "Content-Type: application/json" \
  -d "{}"
```

Windows PowerShell equivalent:

```powershell
curl.exe -X POST http://127.0.0.1:5000/result `
  -H "Content-Type: application/json" `
  -d "{}"
```

Example with selected parameter overrides:

```bash
curl -X POST http://127.0.0.1:5000/result \
  -H "Content-Type: application/json" \
  -d '{"area": 5020.0, "grid_purchase_price": 0.08, "grid_selling_price": 0.08}'
```

Windows PowerShell equivalent:

```powershell
curl.exe -X POST http://127.0.0.1:5000/result `
  -H "Content-Type: application/json" `
  -d '{"area": 5020.0, "grid_purchase_price": 0.08, "grid_selling_price": 0.08}'
```

The request body may include any of the parameters defined in
`EnergyOptimizationPyomoPostData` in `energy_optimization_po_api.py`. Omitted
fields use the defaults defined in `pyomo_energy_optimization`.

## Expected Output

A successful request returns HTTP `200` with a JSON object containing:

```json
{
  "Object FU": 0,
  "Cost of Energy (COE)": 0,
  "Number of PV": 0,
  "Number of Wind Turbines": 0,
  "Battery Storage Capacity": 0,
  "Total Capital Cost ($)": 0,
  "Renewable Penetration": 0,
  "Payback Period": 0
}
```

The numeric values above are placeholders showing the response shape. Actual
values depend on the input data, parameter overrides, and solver result.

## Generated Files

Running the optimization creates local output files under `data/`:

- `data/Opt_New.lp`
- `data/results_local_new.csv`

These files are generated artifacts and are intentionally ignored by Git. The
required input workbook `data/Input_Daily_Sum.xlsx` should remain versioned with
the repository.

## Documentation

Additional research documentation and notes are kept in `docs/`.

## Attribution

Research model:

- Navid Shirzadi

Repository integration, refactoring, and API wrapper:

- Alireza Adli
