# Publish Anaconda Package

A Github Action to publish your software package to an Anaconda repository.

### Example workflow to publish to conda every time you make a new release

```yaml
name: publish_conda

on:
  release:
    types: [published]
  workflow_dispatch:
  push:
    tags:
      - '[0-9]+.[0-9]+.[0-9]+*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: publish-to-conda
      uses: ./.github/actions/publish-conda-action
      with:
        subdir: 'conda'
        anacondatoken: ${{ secrets.ANACONDA_TOKEN }}
        platforms: 'noarch'

```

### Example project structure

```
.
├── LICENSE
├── README.md
├── setup.py
├── myproject
│   ├── __init__.py
│   └── myproject.py
├── conda
│   ├── conda_build_config.yaml
│   └── meta.yaml
├── .github
│   └── workflows
│       └── publish_conda.yml
├── .gitignore
```

### ANACONDA_TOKEN

1. Get an Anaconda token (with read and write API access) at `anaconda.org/USERNAME/settings/access`
2. Add it to the Secrets of the Github repository as `ANACONDA_TOKEN`

### Supported anaconda channels
- conda-forge
- taurus-org
- tango-controls
