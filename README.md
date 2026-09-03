Building Performance Output Report Data Model Specification
=============================================================

[![Build and Test](https://github.com/IBPSA-USA/output-reporting/actions/workflows/build-and-test.yaml/badge.svg)](https://github.com/IBPSA-USA/output-reporting/actions/workflows/build-and-test.yaml)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](LICENSE.txt)

An open source data model specification for building performance output reports, developed through a stakeholder consensus process by the IBPSA-USA Building Data Exchange (BDE) Committee.

The specification standardizes how building performance simulation software reports energy performance results — including end-use and energy-source consumption, regulated vs. unregulated energy use, and on-site generation and export — so that simulation tools, code-compliance review software, and reporting applications can exchange one consistent file format instead of each adopting its own bespoke output structure.

📖 **Read the published specification: https://ibpsa-usa.github.io/output-reporting/**

This work is funded by the U.S. Department of Energy Building Technologies Office, via IBPSA-USA's Building Data Exchange Committee.

## Repository layout

| Path | Contents |
| --- | --- |
| [`schema/`](schema/) | The data model schema, defined in [lattice](https://github.com/bigladder/lattice)'s YAML meta-schema format. |
| [`docs/BuildingPerformanceOutputReport.md.j2`](docs/BuildingPerformanceOutputReport.md.j2) | Jinja2 template used to render the schema into the human-readable specification document. |
| [`docs/web/`](docs/web/) | Site content and configuration (About page, theming, logo) for the published documentation site. |
| [`examples/`](examples/) | Example data files conforming to the schema. |
| `dodo.py` | Build tasks (schema validation, documentation generation), run via [doit](https://pydoit.org/). |

This repository is built on [lattice](https://github.com/bigladder/lattice), Big Ladder Software's schema-and-documentation toolchain, which is also used by related standards such as [ASHRAE 205](https://github.com/open205/schema-205).

## Building locally

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and [doit](https://pydoit.org/) for build automation.

```console
# Install dependencies
uv sync

# Run all build tasks (validate example files, generate web docs)
uv run doit

# Run an individual task
uv run doit validate_example_files
uv run doit generate_web_docs

# List available tasks
uv run doit list
```

Generated web documentation is written to `.lattice/docs/web/public`.

## Contributing

This specification is developed by the IBPSA-USA BDE Output Reporting Working Group through regular meetings and consensus review. See the [working group and contributor list](https://ibpsa-usa.github.io/output-reporting/) on the published site for current participants.

Questions, proposed schema changes, and issues with the specification or example files are welcome via [GitHub Issues](https://github.com/IBPSA-USA/output-reporting/issues).
