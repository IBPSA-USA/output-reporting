The Building Performance Output Report standardizes how building performance simulation software reports energy performance results, including end-use and energy-source consumption, regulated vs. unregulated energy use, and on-site generation and export, so that simulation tools, code-compliance review software, and reporting applications can exchange one consistent file format instead of each adopting its own bespoke output structure.

This document provides the data model specification and was developed through a stakeholder consensus process by the IBPSA-USA Building Data Exchange (BDE) Committee, building on a prior BDE review that catalogued dozens of fragmented BEM output-reporting formats across existing protocols and software tools. The standardized end-use and energy-source categories defined here synthesize that same empirical review, corroborated against working-group discussion.

## Ongoing Consensus-Driven Development

Establishing a canonical set of end-use and energy-source categories that works across the diversity of building types, systems, and simulation tools is inherently an iterative undertaking, not a one-time classification exercise. As the specification is put to use, edge cases and ambiguous boundaries surface that the current taxonomy doesn't yet resolve cleanly — these are tracked as [`question`-labeled issues](https://github.com/IBPSA-USA/output-reporting/issues?q=is%3Aissue+is%3Aopen+label%3Aquestion) in the [GitHub repository](https://github.com/IBPSA-USA/output-reporting), and resolving them is ongoing work the working group expects to continue well past the specification's initial release. Anyone is welcome to weigh in — comment on an open question, propose how it should be resolved, or file a new issue for a case the categories don't yet address.

This openness to revision reflects a deliberate Level of Detail (LOD) philosophy, adapted from the LOD scale long used in building information modeling. The canonical top-level end-use and energy-source categories standardize reporting at a coarse, consistent level of detail, so that any two conforming reports can be compared directly at that level. Below the canonical categories, the schema is intentionally open-ended: implementers can define custom subcategories to whatever depth their tools, protocols, or analyses require, without the working group needing to anticipate or standardize every deeper layer in advance. Extending the taxonomy downward, rather than only widening it, is treated as a core feature of the specification rather than a gap to be closed.

<!-- ## Working Group

- Fred Betz (NeuMod Labs)
- Liam Buckley (IES)
- Greg Collins (Zero Envy)
- Jason Glazer (GARD Analytics)
- Neal Kruis (Big Ladder Software)
- Tim McDowell (Salas O'Brien)
- Sagar Rao (NeuMod Labs)
- Parag Rastogi

## Contributors

- Fred Betz (NeuMod Labs)
- Greg Collins (Zero Envy)
- Neal Kruis (Big Ladder Software)
- Kevin Moos (Big Ladder Software)
- Sagar Rao (NeuMod Labs)

## Acknowledgements

This work was funded by the U.S. Department of Energy Building Technologies Office, via IBPSA-USA's Building Data Exchange Committee.
 -->
