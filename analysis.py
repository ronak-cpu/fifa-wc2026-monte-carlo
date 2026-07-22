name: Run Monte Carlo Simulation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  simulate:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run simulation (10,000 iterations)
      run: python simulation.py --n_sims 10000 --seed 42 --audit

    - name: Upload outputs
      uses: actions/upload-artifact@v4
      with:
        name: simulation-outputs
        path: outputs/
