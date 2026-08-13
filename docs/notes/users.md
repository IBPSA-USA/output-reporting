# Users

## Status

This document characterizes who uses the Output Reporting schema and its eventual generated
reports — their goals, what they read or produce, and what they need from the schema. It is a
stub: the four user types below are placeholders to be fleshed out with working-group input.
Treat any characterization here as provisional until expanded.

## User Types

### Building Owners

*To be characterized.*

### Authorities Having Jurisdiction (AHJs)

*To be characterized.*

### Software Developers

*To be characterized.*

### Building Performance Modelers

*To be characterized.*

## Example Use Cases

Concrete scenarios grounding the user types above in specific tasks — what a user is trying
to accomplish, and what they need from the schema or a generated report to do it. Stub for
now; to be filled in alongside the user types.

### Simulation Software to AHJ Reporting/Review Software (Primary Use Case)

**Primary user types:** Software Developers (on both ends — simulation-software export and
AHJ-side review/reporting software), AHJs (consuming the result for review)

This is the core pipeline the schema exists to standardize: a building energy simulation
tool exports an Output Reporting-conformant file directly from its own results, and an AHJ's
reporting/review software ingests that file to perform compliance review — automated QA/QC
checks, code-compliance verification — without manual re-entry or bespoke per-tool parsing.
Building Performance Modelers are upstream of this pipeline (they run the simulation that
produces the underlying results) but are not its primary actors; the goal is for the export
and review steps themselves to be software-to-software and largely automated, rather than
routed through a modeler manually assembling or transcribing a report.

All other use cases in this document are secondary to this one — they should be understood as
variations on, or extensions of, this primary flow, not alternatives to it.

### Assembling a Custom Report from Multiple Software Tools

**Needs review** — drafted unilaterally, not yet vetted by the working group.

**Primary user type:** Building Performance Modelers

A sophisticated or high-end energy model — e.g., a complex mixed-use building, a LEED or
utility incentive submission, or a design-assist study — is often not produced by a single
BEM engine end to end. Different subsystems get modeled in specialized tools: whole-building
loads and HVAC in one engine, daylighting/glare in another, on-site PV or battery storage in a
dedicated tool, or a custom process-load calculation in a spreadsheet. The modeler needs to
assemble a single schema-conformant output file that merges these disparate tool outputs into
one coherent energy-source/end-use breakdown, rather than relying on a single vendor's export
routine to produce the whole file automatically.

This stresses:

- **Custom end uses and energy sources** (`is_custom`) for tool-specific breakdowns that don't
  map cleanly onto the standard categories in `end_uses.md`.
- **Hierarchical nesting** flexible enough to absorb inconsistent granularity between tools —
  one tool might report a single "HVAC" total, another might break ten subcategories out of
  the same building system.
- **Consistent handling of differing native timesteps/units** across tools (e.g., one engine
  reporting hourly, another only annual) when merged into one `TimeIntervals`-based file.
- An open question not yet addressed anywhere in this schema: whether to record *provenance*
  per end use (which tool produced which piece), so a reviewer can tell that, say, the
  daylighting energy came from a different model than the HVAC energy it's merged alongside.

*More use cases to be added.*
