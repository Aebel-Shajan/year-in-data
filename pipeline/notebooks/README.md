# Note books

The purpose of this folder is to test out pipelines before implementing them in 
transformations package.

## Process:

1) Use python notebooks to look through data
2) Write unit testable transformations + schemas
3) Create assets in dagster orchestration layer
4) Create route to expose final data to api


## Setup

Make sure we are working inside a virtual environment and the "ipykernel" dev dependency is installed.

Install dev dependency with:
```bash
pip install -e ".[dev]"
```

I prefer using sql over pandas for querying results. I use the `ipython-sql` python package to query sql tables from python notebooks (.ipynb files).

Make sure to restart jupyter kernel when you make changes to editable packages. e.g. transformations, app, orchestrator

I use "nbstripout" to remove the output in python notebooks. It works using git filters.
Make sure to do:
```bash
nbstripout --install
```
to set up the .git file for this repo.
