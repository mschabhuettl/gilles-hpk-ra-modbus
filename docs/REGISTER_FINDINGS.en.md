# Anonymized register findings

> [🇩🇪 Deutsch (primary)](REGISTER_FINDINGS.md) · 🇬🇧 **English**

Extended passive analysis revises several earlier register interpretations. This public summary contains only generalized technical findings. Raw observations remain private; time series, screenshots, specific operating times, durations and installation-specific measurements are not published. This summary alone therefore cannot support independent recalculation of the observed relationships.

## REG56: calculated O₂ target as a strong hypothesis

REG56 remains active during regulation and follows an exhaust-temperature-dependent relationship. Its former description as a brief pulse is obsolete. Linear interpolation between the configured temperature and O₂ endpoints qualitatively matches the observed behavior:

```text
T       = REG50 × 0.1              # Actual flue gas temperature
T_low   = REG36 × 0.1              # sAbgasTempSollMin
T_high  = REG38 × 0.1              # sAbgasTempMax
O_low   = REG16 × 0.1              # sO2Min: O₂ at lower temperature endpoint
O_high  = REG14 × 0.1              # sO2Max: O₂ at upper temperature endpoint

O2_target_candidate = O_low + (T − T_low) × (O_high − O_low) / (T_high − T_low)
REG56 × 0.1 ≈ O2_target_candidate
```

This requires `T_high ≠ T_low`. The names `sO2Min` and `sO2Max` identify parameters here; they do not guarantee the numerical ordering of the O₂ values. Clamping outside the observed regulation range, other parameter combinations and behavior in other phases remain unresolved. The formula is a model to test, not verified controller logic.

Confidence: **strong hypothesis (✓)**. Confirmation still requires a simultaneous comparison with a Touch value explicitly labeled as the O₂ target. The overview's “O2 Wert” is the actual value and does not confirm this hypothesis. No control logic or confirmed target sensor is derived from it.

## Other registers

| Register | Qualitative observation | Conclusion and open question |
|---|---|---|
| REG46 | The status code can change while the operating mode remains constant. Comparing the same stable state provisionally associates code 61 with the Touch banner “Puffertemperatur erreicht” (buffer temperature reached). | Not a general “Puffer/Boiler active” code. Unaligned clocks prevent an exactly synchronized confirmation; another comparison across a banner change is needed. Enum versus bitfield remains unresolved. |
| REG58 / REG62 | The existing HA scale does not clearly match historical Touch identifications and parameter limits. | A factor-of-ten difference is possible. Compare nonzero raw values, HA values and Touch percentages simultaneously before changing the scale. |
| REG66 | The active flue gas target changes within the regulation phase. | Not a fixed binary value; REG42=7 means regulating heat, not necessarily full load. |
| REG68 | Increases and decreases, including recurring zero intervals. | Not a monotonic consumption or runtime counter. Command, modulation or release are candidates; do not convert it to fuel quantity or energy. |
| REG72 | Activity associated with ignition and initial combustion. | An ignition-related output is plausible; the actuator is unknown. |
| REG76 | Recurring high intervals. | The former “permanently inactive” classification is withdrawn. Purpose, periodicity and physical pulse width remain unresolved. |
| REG78 | A long high interval contradicts its former direct identification as an ash-motor state. | Ash-motor identification withdrawn; pump or release remain unconfirmed candidates. Historical HA IDs remain intact; counted edges are not confirmed ash cycles. |
| REG70 / REG74 | Only zero observed so far. | No conclusion about permanent inactivity or reservation for unused extensions. |

## Limitations and next comparisons

HA histories contain detection times of asynchronously polled sensors. An unchanged value is not recorded as a new measurement in a state-change history. Values held on a common time grid are therefore not independent synchronized pairs. Recorded high-state durations establish neither physical motor runtime nor exact periodicity; short pulses can be missed between polls.

A Touch image with inactive actuators only supports matching an idle operating state. It does not identify the unknown binary registers or resolve scaling, because zero remains zero under either candidate scale. Buffer temperatures appearing on Touch also do not establish that those measurements are exported in the tested Modbus map.

During naturally occurring heating operation, compare the O₂ target, primary air and induced draft alongside ignition, dosing, rotary feeder, heat-exchanger cleaning, ash discharge and return-pump indicators with the raw registers. A natural change of status banner is particularly useful for REG46. This requires neither changing heating parameters nor initiating an additional burner cycle.

Current confidence levels and unresolved mappings are listed in the [register map](REGISTER_MAP.en.md); the process is described in [methodology](METHODOLOGY.en.md).
