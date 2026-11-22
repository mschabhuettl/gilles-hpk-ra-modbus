# Anonymized register findings

> [🇩🇪 Deutsch (primary)](REGISTER_FINDINGS.md) · 🇬🇧 **English**

Extended passive analysis revises several earlier register interpretations. This public summary contains only generalized technical findings. Raw observations remain private; time series, screenshots, specific operating times, durations and installation-specific measurements are not published. This summary alone therefore cannot support independent recalculation of the observed relationships.

## REG56: calculated O₂ target as a strong hypothesis

REG56 remains active during regulation and follows an exhaust-temperature-dependent relationship. Its former description as a brief pulse is obsolete. A broader analysis of repeated natural burner cycles again supports linear interpolation between the configured temperature and O₂ endpoints. Nonzero readings during regulation also closely follow the model in a later observation window with unchanged numeric endpoints. This strengthens the empirical evidence but does not replace a synchronized comparison with Touch:

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

The [Gilles Touch manual from version 5.25](https://shop.baxi.se/documents/Gilles%20Touch%20-%20manual%20v5.25%20(ENG).pdf) describes the O₂ parameters as targets at maximum and minimum output. “Min” and “Max” therefore refer to output points, not the numerical ordering of oxygen values. A higher target at minimum output does not establish swapped registers or incorrect settings. This manufacturer description explains the parameters; it does not verify the reverse-engineered Modbus address of REG56.

Confidence: **strong hypothesis (✓)**. Another Touch page shows “Restsauerstoff” (residual oxygen) with separate “Ist” (actual) and “Soll” (target) columns. In the compared idle state, both that target and REG56 are zero. This identifies a suitable display for comparison; equality at zero confirms neither the register's purpose nor its scale. Confirmation still requires simultaneous comparison at a nonzero target during regulation. The overview's “O2 Wert” instead shows the actual value. No control logic or confirmed target sensor is derived from it.

## Other registers

| Register | Qualitative observation | Conclusion and open question |
|---|---|---|
| REG42 | The shutdown path `7 → 9 → 10 → 0` was recorded again; `7 → 9 → 8 → 9 → 0` also appeared. | The recorded sequence is neither fixed nor numerically increasing. Code 10 remains a cycle state of unknown meaning, not evidence of a flame. A brief step can fall between polls; a code's absence from a recording does not establish its physical absence. |
| REG46 | Code 61 is provisionally associated with the Touch banner “Puffertemperatur erreicht” (buffer temperature reached). The additionally observed code 43 starts during shutdown and extends into standby; the boiler target falls later. | The Touch message for code 43 is missing. An error, overheating, buffer state or “boiler target zero” is not established. Code 43 is displayed neutrally as a raw code; the door position remains unknown in this state. Code 61 still needs an exactly synchronized comparison across a banner change; enum versus bitfield remains unresolved. |
| REG58 / REG62 | The existing HA scale does not clearly match historical Touch identifications and parameter limits. | A factor-of-ten difference is possible. Compare nonzero raw values, HA values and Touch percentages simultaneously before changing the scale. |
| REG64 | The active boiler target can be zero while REG44 still indicates Puffer/Boiler mode. | Zero here means no active boiler target, not necessarily a disabled operating mode. Distinguish mode, combustion phase and current demand. |
| REG66 | The active flue gas target changes within the regulation phase. | Not a fixed binary value; REG42=7 means regulating heat, not necessarily full load. |
| REG68 | Increases and decreases, including recurring zero intervals. Touch shows “aktuelle Einschubmenge” (current feed amount) as a percentage, also zero in the compared idle state. | “Current feed amount” is a specific candidate for the next comparison. Matching at zero confirms neither the function nor a percentage scale. Not a monotonic consumption or runtime counter; do not convert it to fuel quantity or energy. |
| REG72 | In the natural cycles followed up, each high starts during code 3 and ends around the transition from initial combustion to regulation. | This supports association with the startup sequence; the actuator remains unknown. Asynchronous polling cannot establish exact switching order relative to REG42. |
| REG76 | Recurring high intervals also occur with REG42=0. | Activity is not restricted to burner operation. Purpose, periodicity and physical pulse width remain unresolved. |
| REG78 | Long high intervals and standby pulses observed again; return temperature rises while boiler temperature falls. This pattern contradicts its former direct identification as an ash-motor state. | The heat redistribution supports a pump or release hypothesis but does not identify an actuator. The ash-motor identification remains withdrawn. Historical HA IDs remain intact; counted edges are not confirmed ash cycles. |
| REG70 / REG74 | Only zero observed so far. | No conclusion about permanent inactivity or reservation for unused extensions. |

## What the additional Touch pages establish

The parameter pages allow several previously identified configuration registers to be compared again with their labeled Touch fields. Matching nonzero parameters support the existing parameter identifications and their scales. This does not establish the unresolved scales of live values: a primary-air limit and the current primary-air value are different registers.

The I/O pages include door contacts, motor-protection/thermal contacts and lambda heating. Without knowing contact polarity and display logic, a signal's color establishes neither the physical door position nor a running motor. In particular, a green indicator beside “X28-Brennraumtür offen” (combustion chamber door open) is insufficient evidence of the door position. A heat-exchanger-cleaning thermal contact is not a motor output either. Installation options, input states, timing parameters and actual actuator operation must be considered separately; a configured cleaning schedule alone does not establish that the cleaning function is enabled.

An actual O₂ value shown on Touch with “Brenner Aus” (burner off) initially establishes only that the controller also displays that value. The lambda-heating indicator adds operating context but establishes neither electrical heater power nor measurement validity. The idle state therefore supports no conclusions about combustion quality or a defective probe.

The runtime page lists the controller, burner, rotary feeder and dosing separately and includes “Anzahl Zündungen” (number of ignitions). This counter's reset conditions and reference period are unknown. It must therefore not be described as a lifetime or daily counter, nor equated with an HA burner-start counter merely because their displayed values match. This also does not identify a Modbus address.

## Temperature behavior and startup-diagnostic limits

Further warm starts show why comparison with the initial temperature can produce false advisories even with a smoothed trend: the boiler initially cools and then warms substantially. While it remains below its warm starting value, a brief flattening of the trend can raise an advisory despite the rise from its low point. High flue-gas temperatures in the same trace support that the advisory does not establish failed ignition. This identifies neither a particular pump function nor measured heat output.

The diagnosis therefore also tracks the lowest boiler temperature recorded since a valid observed start. The original initial reading remains separate. Required temperature rise is checked against this diagnostic minimum, so sufficient recovery after initial cooling satisfies the criterion. While that rise is still missing, an insufficient smoothed trend and the other startup conditions must also hold. An activation delay and separate trend activation/clearance thresholds suppress brief fluctuations. Exact conditions are documented in the [HA instructions](../home-assistant/README.en.md).

This remains a startup diagnosis with editable review criteria, not proof of flame or general stall monitoring after the required rise has been reached. Gaps or nonnumeric raw readings invalidate the baseline; recovery does not reactivate it. State history and the last-change timestamp cannot reliably distinguish a constant measurement from a held value. The availability indicator therefore establishes neither a fresh Modbus response nor the physical correctness of all readings.

## O₂ evaluation by operating phase

A low, constant standby O₂ value becomes dynamic during a burner cycle and returns to its idle value after shutdown. This supports an idle or inactive measurement state as an explanation; it does not prove a guaranteed indicator of a disabled sensor. Standby values must not be interpreted as a combustion minimum or proof of a defective probe.

Follow-up also shows very low raw O₂ values within recorded phase `7`, including updates after entry into that phase. Accompanying asynchronous snapshots show elevated flue gas temperatures and an active REG56 candidate. O₂ magnitude alone therefore cannot distinguish an inactive state from regulation. These numerically valid heating-phase readings are not removed by an additional lower cutoff. They establish neither a physical cause nor a probe fault, calibration or combustion quality.

The HA evaluation therefore includes O₂ only with recorded phase `7`, a valid numeric raw value and an O₂ state update after entry into that phase. With otherwise valid inputs, the derived source returns `unknown` outside the heating phase, preventing any substitute number from entering statistics. Invalid inputs make it `unavailable`. Its separate minimum replaces the previous unfiltered dashboard metric and can retain heating readings still within the time window during standby. The raw sensor and old statistic retain their history; existing readings are not retrospectively cleaned. The phase filter improves operating context but establishes neither probe calibration nor measurement freshness or combustion quality.

For the checked window, subsequent state history confirms that numeric raw values enter the source only in phase `7`, that it returns to `unknown` on leaving that phase, and that minimum changes account for older low readings leaving the time window. A low filtered minimum is therefore not automatically an included standby value. This checks recorded HA states, not synchronously measured physical states.

## Limitations and next comparisons

HA histories contain detection times of asynchronously polled sensors. An unchanged value is not recorded as a new measurement in a state-change history. Values held on a common time grid are therefore not independent synchronized pairs. Recorded high-state durations establish neither physical motor runtime nor exact periodicity; short pulses can be missed between polls.

A Touch image with inactive actuators only supports matching an idle operating state. It does not identify the unknown binary registers or resolve scaling, because zero remains zero under either candidate scale. Buffer temperatures appearing on Touch also do not establish that those measurements are exported in the tested Modbus map.

The most useful next capture is the actual/target page during natural regulation with nonzero values: it combines the O₂ target, current feed amount and fan displays, allowing REG56, REG58/60/62 and REG68 to be compared together. For the unknown binary registers, the main overview's actual actuator indicators for ignition, dosing, rotary feeder, heat-exchanger cleaning, ash discharge and return pump are also needed. Protection-contact pages do not replace these output displays. REG42=10 needs a matching burner-status display. REG46=43 still lacks the corresponding main-screen message; a natural transition between status codes helps test the message mapping. This requires neither changing heating parameters nor initiating an additional burner cycle.

Current confidence levels and unresolved mappings are listed in the [register map](REGISTER_MAP.en.md); the process is described in [methodology](METHODOLOGY.en.md).

