# Compare Buildings

Install and run poetry

```bash
pip install poetry
poetry install
```

## Committing

Before pushing changes to GitHub, run `pre-commit` to format the code consistently and to strip the output from ipynb files. This will allow for easy diffing of the `.ipynb` files.

```bash
pre-commit run --all-files
```

## Running

The instructions are contained in the `analysis.ipynb` file.

## Releasing

Run the `analysis.ipynb` file and verify that is runs to completion without errors. In the command line run

```bash
poetry run jupyter nbconvert --to pdf --execute analysis.ipynb --output compare_building_data.pdf
```

Release the source code and upload the `compare_building_data.pdf` file to the release.
