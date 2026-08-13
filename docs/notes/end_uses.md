# End Uses

## Status

This document defines the standardized whole-building energy end-use categories for the
Output Reporting data model. It is a decisions-and-definitions record, written ahead of the
formal schema (`schema/OutputReporting.schema.yaml` does not yet define an end-use
enumeration or data group). Treat the canonical terms and definitions below as the source of
truth to carry into the schema and into `examples/example.json` when that work happens.

The structure adopted here is one of several proposals the working group considered.

## Standard End-Use Categories

Each category below gives its **canonical name** (the exact string to use for `name` once
this maps into the schema), a definition, and any subcategories. Subcategories are
themselves standard end uses that are commonly, but not necessarily, reported nested under
their parent.

### Lighting

Energy used by luminaires. Always reported through one of its two subcategories, never as a
bare "Lighting" value with its own consumption.

#### Interior Lighting

Energy used by luminaires within enclosed spaces for the purpose of illuminance. Covers task
and process lighting, dwelling vs. common-area lighting, plug-in and hardwired fixtures, all
lamp types (fluorescent, incandescent, LED), exit signs, emergency lighting, decorative,
public-area, and health/safety lighting. See [Open Questions](#open-questions) for the
unresolved task/process split and the refrigerated-case-lighting boundary with Refrigeration.

#### Exterior Lighting

Energy used by luminaires that illuminate the building facade, entrances, walkways, parking
lots, and landscaping.

### Space Heating

Energy used by mechanical equipment (e.g., boilers, furnaces, heat pumps, radiant systems) to
add sensible heat to the building to maintain comfort or process requirements. For heat
pumps, this includes the outdoor fan's energy when its power is included in the rated
efficiency.

See [Open Questions](#open-questions) for humidification, patio heaters, uncontrolled wood
stoves, reheat, and heat recovery — all raised as unresolved considerations against this
category.

#### Heat Pump Supplementary

Energy used by auxiliary or backup heating equipment (e.g., electric resistance coils) that
operates when a heat pump cannot meet the space heating load alone, or during defrost
cycles. Formalizes what was originally left as an open "Primary, Backup" consideration on
Space Heating itself.

#### Fans (heating)

Fan energy attributable to this system's heating operation (e.g., a furnace's or heat pump's
supply fan), when nesting it here better serves attribution than the flat, top-level Fans
category. The heading distinguishes this section for navigation only — the `name` value is
still "Fans" here; it's the parent (Space Heating vs. Space Cooling) that indicates which
operation the energy is attributed to. See [Fans](#fans) for the full definition and the
placement/scope-note convention governing whether fan energy is nested here or reported flat.

### Space Cooling

Energy used by mechanical equipment (e.g., chillers, DX compressors) to remove sensible
and/or latent heat from the building to maintain comfort or process requirements. For DX
equipment, this includes the outdoor condenser fan's energy when its power is included in
the rated efficiency.

See [Open Questions](#open-questions) for dehumidification (intentional or unintentional)
and heat recovery — both raised as unresolved considerations against this category.

#### Heat Rejection

Energy used by central plant equipment (e.g., cooling towers, fluid coolers, dry coolers) to
reject heat from the building's water-cooled systems to the outdoor environment. Excludes
condenser fans integral to packaged or split DX equipment (that energy stays under Space
Cooling itself). Formalizes what was originally left as an open "Heat Rejection"
consideration on Space Cooling itself.

#### Fans (cooling)

Fan energy attributable to this system's cooling operation (e.g., a packaged DX unit's
supply fan), when nesting it here better serves attribution than the flat, top-level Fans
category. The heading distinguishes this section for navigation only — the `name` value is
still "Fans" here; it's the parent (Space Heating vs. Space Cooling) that indicates which
operation the energy is attributed to. See [Fans](#fans) for the full definition and the
placement/scope-note convention governing whether fan energy is nested here or reported flat.

### Water Heating

Energy used to heat water for domestic, commercial, or industrial use (e.g., lavatories,
showers, process equipment), distinct from space heating. Also known as Service Water Heating
(SWH) or Domestic Hot Water (DHW) — the empirical protocol/tool survey in
`BEM_EndUse_Synthesis.xlsx` uses "Service Water Heating" as its term for this same category;
treat the two as aliases of one canonical concept, with **Water Heating** as the name adopted
here.

### Miscellaneous

Energy used by general equipment plugged into standard electrical outlets, as well as general
hard-wired equipment not explicitly categorized in another end use.

#### Cooking

Energy used by commercial or residential kitchen equipment for food preparation that
involves heating (e.g., ovens, ranges, fryers, steamers). Explicitly excludes kitchen exhaust
fans and non-heating food processing equipment.

#### Refrigeration

Energy used by equipment designed to cool and store perishable goods below room temperature
(e.g., walk-in coolers, freezers, display cases). See [Open Questions](#open-questions) for
the refrigerated-case-lighting boundary with Lighting.

#### Elevators and Escalators

Energy used by motors, controls, and associated machinery for the mechanical conveyance of
people and goods, including elevators, escalators, and moving walkways.

### Fans

Electrical energy used by motors driving air-moving devices within the HVAC system (e.g.,
supply, return, and relief fans), as well as process or dedicated exhaust fans (e.g., kitchen
hoods, garage, or laboratory exhaust), for the purpose of circulating or exhausting air.

**Flat by default, nesting allowed:** the working group has agreed fan energy may be
reported either as this flat top-level category (as illustrated here) *or* nested as a
subcategory under Space Heating or Space Cooling, when a report wants fan energy attributed
to the system it serves — see [Fans (heating)](#fans-heating) and
[Fans (cooling)](#fans-cooling) above. Both are valid under the current model; this document
illustrates the flat form as the default.

**Placement is a modeling judgment call; non-duplication is a documented convention, not a
validated rule.** Every `Fans` node — flat or nested under Space Heating/Space Cooling —
should carry a prose note (via the same `notes`/description mechanism used elsewhere in the
schema) stating what slice of the building's fan energy it covers, e.g. "supply fan energy
for the packaged rooftop DX units" vs. "general exhaust and ventilation fans not attributed
to a specific system." Whether two `Fans` nodes in the same file overlap is something a
reader checks by reading those notes; the schema does not, and is not expected to, validate
that fan energy is counted exactly once. This keeps the underlying placement flexibility
(nest where attribution helps, stay flat otherwise) without pretending there's a structural
guarantee against double-counting.

See [Open Questions](#open-questions) for the heating-vs-cooling attribution problem, process
vs. IAQ vs. kitchen vs. parking-garage fans, ceiling fans, and VAV-with-reheat fans — all
raised as unresolved considerations against this category. The "simultaneous heating/cooling
fan energy" question there is unaffected by the convention above: it's still about *which*
node a shared fan's energy goes under, not about how that placement gets described.

### Humidification

Energy used by mechanical equipment to add moisture to the building air to maintain a minimum
relative humidity setpoint.

### Pumps

Electrical energy used by motors driving fluid-moving devices within the HVAC or service
water systems (e.g., chilled water, hot water, condenser water, recirculation, or process
water pumps).

## Open Questions

These are unresolved edge cases carried forward from working-group discussion. Several turned
out to be the same question asked twice from different angles — noted explicitly below rather
than left as apparent duplicates.

- **Refrigerated case lighting: Lighting or Refrigeration?** Raised independently three times
  — as a consideration under Interior Lighting, under Refrigeration, and as its own item
  elsewhere. All three are the same unresolved question.
- **Heat recovery: Space Heating or Space Cooling?** Raised as a loose consideration under
  *both* Space Heating and Space Cooling. A concrete case this abstract question is actually
  about: VRF with heat recovery, where some zones are heating and others cooling off a shared
  compressor.
- **VAV reheat: Fans, Space Heating, or Space Cooling?** Raised under both Fans ("VAV with
  reheat?") and Space Heating ("reheat"), and also asked directly elsewhere. Unresolved which
  of the three (or whether a split) applies.
- **Simultaneous heating/cooling fan energy.** If a central VAV system's fan is running while
  some zones call for heating and others for cooling, is that fan's energy Space Heating or
  Space Cooling? Related to, but distinct from, the VAV reheat question above.
- **Shared water heater serving both Space Heating and Water Heating.** If one hot water tank
  supplies both, how is the heat source's energy split between the two categories? A genuine
  gap — not addressed by any structure considered so far.
- **Crankcase heating: Space Heating or Space Cooling?** A heat pump's crankcase heater keeps
  refrigerant warm during compressor off-cycles, serving both the unit's heating and cooling
  operation. Not yet addressed.
- **Task vs. process lighting split.** Raised under Interior Lighting; no criteria yet for
  distinguishing the two.
- **Patio heaters, uncontrolled wood stoves.** Raised under Space Heating; unclear whether
  these count as regulated building space heating at all, or are out of scope/custom.
- **Dehumidification: intentional vs. unintentional, and whether it warrants its own
  top-level category** (as opposed to a Space Cooling consideration, its current treatment
  here).
- **Ceiling fans; process vs. IAQ vs. kitchen vs. parking-garage fans.** Raised under Fans;
  unclear whether these warrant their own subcategories or stay lumped into the flat Fans
  category.

## Other End Uses to Consider for the First Schema Draft

`BEM_EndUse_Synthesis.xlsx` surveys 38 distinct end-use names across the 8 protocols and 4
tools (plus a separate set of quality-assurance metrics that aren't end uses at all). The
categories above account for the ones that cleared the synthesis's own recommendation
threshold (≥4 protocols and ≥2 tools, plus a few committee-promoted exceptions). The rest are
listed here — each with its protocol/tool support count and the synthesis's own suggested
treatment — as open items for whoever drafts the schema to explicitly decide on, rather than
silently drop. None of these are decided yet.

### Likely custom subcategories of Miscellaneous

The synthesis suggests these fold into Miscellaneous as named (`is_custom`) subcategories
rather than becoming their own standard categories:

#### Battery

2 protocols, 1 tool.

#### Building Transformers

Aliased "Transformers." 2 protocols, 1 tool.

#### Industrial Process

Aliased "Industrial Equipment." 3 protocols, 0 tools.

#### IT Equipment

3 protocols, 0 tools.

#### Office Equipment

1 protocol, 1 tool. The synthesis notes this could also be a generic custom subcategory
rather than a named one.

#### Receptacle Equipment

2 protocols, 2 tools. Same caveat as Office Equipment; also worth noting this term is close
to a plain restatement of Miscellaneous's own definition ("equipment plugged into standard
electrical outlets").

### Likely custom subcategory of Lighting

#### Lighting in Apartments

2 protocols, 0 tools. Synthesis suggests Lighting > Apartments (custom).

### Needs an explicit decision

- **Motors** (2 protocols, 1 tool) — the synthesis itself doesn't pick one answer: "Fans,
  Pumps, Miscellaneous depending on motor usage." Whoever drafts the schema needs to decide
  whether this becomes a routing rule (classify by what the motor drives) or its own
  category.

### Not new categories — apply the regulated/process tag instead

These appeared in the synthesis as separate end-use names, but they're the same base category
reported with a regulated/unregulated split. The `is_unregulated` flag already illustrated on
Interior Lighting's Task/Process subcategories in `examples/example.json` is exactly this
pattern — apply it here too rather than adding new categories:

- **Interior Lighting - Process** (5 protocols, 1 tool) — this is the same "process lighting"
  already named under [Interior Lighting](#lighting) above and in
  [Open Questions](#open-questions); the synthesis explicitly confirms it should be
  "supported with regulated/process tag," not a separate category.
- **Refrigeration Equipment - Unregulated** (2 protocols, 1 tool) — same pattern, applied to
  Refrigeration.

### Not new categories — apply an EnergySource fuel variant instead

These are the same base end use reported against a different energy source, not a distinct
end use in their own right:

- Auxiliary (Nat Gas) (1 protocol, 0 tools)
- Cooling (Nat Gas) (4 protocols, 1 tool)
- Misc Equipment (Nat Gas) (3 protocols, 1 tool)
- Other - Electricity (2 protocols, 1 tool)
- Other - Nat Gas (2 protocols, 1 tool)
- Service Water Heating - Electricity (3 protocols, 2 tools)
- Space Heating (Electricity) (4 protocols, 2 tools)

### Possibly EnergySource, not EndUse

The synthesis also surveys Renewable Energy (4 protocols, 4 tools) alongside these end uses,
but notes it should be supported as an EnergySource rather than an end use — it describes
where energy comes from, not what consumes it. These two items raise the same question:

- **Exported Energy** (1 protocol, 3 tools) — the synthesis gives no suggested treatment for
  this one; it's a genuine gap, not just an omission on this document's part.
- **Fossil On-site Generation** (1 protocol, 3 tools)

### Already covered, noted here for traceability

- **Fans - Kitchen Ventilation** (1 protocol, 0 tools) and **Fans - Parking Garage**
  (4 protocols, 0 tools) are both already folded into [Fans](#fans) above (its definition
  names kitchen hoods and garage exhaust explicitly) and into
  [Open Questions](#open-questions) (whether kitchen/parking-garage fans need their own subcategories).

### Out of scope — quality-assurance metrics, not end uses

The synthesis's "Quality Assurance" block is a different kind of data (model diagnostics, not
energy consumption) and isn't part of this end-use list at all: Unmet Heating Hours, Unmet
Cooling Hours, Error Messages, Warning Messages, System Load, Peak Electric Load, Peak Energy
Month. Mechanical Ventilation also appears in this block with 0 protocols and 0 tools of
support; the synthesis notes it's already covered as "Fans."

## Sources

This document synthesizes an empirical cross-reference of 8 building-energy reporting
protocols and 4 BEM tools, corroborated against working-group discussion, to arrive at
category names (including identifying "Service Water Heating" as the more common industry
term for Water Heating) and the open questions above.
