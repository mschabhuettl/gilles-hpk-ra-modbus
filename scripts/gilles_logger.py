#!/usr/bin/env python3
"""
Gilles Touch Modbus Logger v3.1
================================
Long-running change-detection logger for Gilles Touch controllers.

Polls all 40 logical values every 10 seconds.
Logs only changes plus a full snapshot every 10 minutes.
Writes a parallel CSV file with all values for later analysis.

v3.1 changes:
- REG[42] now identified as BrennPhase (burner cycle phase enum)
- REG[58]=PrimaerIst, REG[60]=SekundaerIst, REG[62]=SaugzugIst (CORRECTED — REG[62] is NOT the door)
- REG[66]=AbgasSoll_Live (confirmed)
- REG[78]=AscheaustragungAktiv (confirmed)
- REG[44] adds Automatik=5 code

Usage:
    python3 gilles_logger.py [HOST]

This script is READ-ONLY. Only uses Modbus FC03 (Read Holding Registers).
"""

import os
import sys
import csv
import time
from datetime import datetime
from pymodbus.client import ModbusTcpClient

HOST = os.environ.get('GILLES_HOST', '192.0.2.1')
PORT = 502
SLAVE_ID = 1
POLL_INTERVAL = 10
SNAPSHOT_INTERVAL = 600
LOGFILE = 'gilles_log.txt'
CSVFILE = 'gilles_data.csv'
TEMP_NOISE_THRESHOLD = 0.5  # °C

if len(sys.argv) > 1:
    HOST = sys.argv[1]


# === Register identification (see docs/REGISTER_MAP.md) ===
LABELS = {
    0:  'sProzFoerderSchnecke',
    2:  'sPrimaerMax',
    4:  'sPrimaerMin',
    6:  'sSekundaerMax',
    8:  'sSekundaerMin',
    10: 'sSaugzugMax',
    12: 'sSaugzugMin',
    14: 'sO2Max',
    16: 'sO2Min',
    18: 'sKesselSollTag',
    20: 'sAschenaustrDauer',
    22: 'sAschenaustrPause',
    24: 'sStartSekundaer',
    26: 'sZuendEinschub',
    28: 'sTempDiffStart',
    30: 'sTempDiffStop',
    32: 'sTempDiffTeillast',
    34: 'sKesselSollNacht',
    36: 'sAbgasTempSollMin',
    38: 'sAbgasTempMax',
    40: 'sAbgasTempMaxLimit',
    42: 'BrennPhase',
    44: 'BoilerStatus',
    46: 'StatusBitmap',
    48: 'KesselTemp_Ist',
    50: 'AbgasTemp_Ist',
    52: 'RuecklaufTemp_Ist',
    54: 'O2_Ist',
    56: '?REG56',
    58: 'PrimaerIst',
    60: 'SekundaerIst',
    62: 'SaugzugIst',
    64: 'KesselSoll_Live',
    66: 'AbgasSoll_Live',
    68: '?Zaehler',
    70: '?REG70',
    72: '?BinarFlag',
    74: '?REG74',
    76: '?REG76',
    78: 'AscheaustragungAktiv',
}

SCALES = {
    0: ('%', 10), 2: ('%', 10), 4: ('%', 10), 6: ('%', 10),
    8: ('%', 10), 10: ('%', 10), 12: ('%', 10),
    14: ('%', 10), 16: ('%', 10),
    18: ('°C', 10), 20: ('s', 10), 24: ('%', 10),
    26: ('s', 10),
    28: ('°C', 10), 30: ('°C', 10), 32: ('°C', 10),
    34: ('°C', 10),
    36: ('°C', 10), 38: ('°C', 10), 40: ('°C', 10),
    48: ('°C', 10), 50: ('°C', 10), 52: ('°C', 10),
    54: ('%', 10),
    56: ('%', 10), 58: ('%', 10), 60: ('%', 10), 62: ('%', 10),
    64: ('°C', 10), 66: ('°C', 10),
}

# Registers whose changes are filtered by TEMP_NOISE_THRESHOLD
NOISY_TEMPS = {48, 50, 52}

# Enum translations: register address -> (code -> human-readable name)
ENUMS = {
    42: {  # BrennPhase
        0: 'Standby',
        1: 'Vorluften',
        3: 'Zundung',
        5: 'Zundung-Spaet',
        6: 'Anbrennphase',
        7: 'Heizen regeln',
        8: 'Ausbrennen',
        9: 'Auskuehlen',
    },
    44: {  # BoilerStatus
        1: 'Handbetrieb',
        3: 'Puffer/Boiler',
        5: 'Automatik',
        # Other codes (Steuerung Aus, Zeitbetrieb, Puffer/Boiler Gluterhaltung, Notbetrieb)
        # not yet observed
    },
    46: {  # StatusBitmap (partial)
        0:  'normal',
        35: 'Brennraumtuer offen',
        61: 'Puffer/Boiler-Modus aktiv',
    },
    72: {  # ?BinarFlag
        0: 'aus',
        1: 'ein',
    },
    78: {  # AscheaustragungAktiv
        0: 'Pause',
        1: 'AKTIV',
    },
}

# Registers that are "important events" -- always log changes, prefix EVENT
EVENT_REGISTERS = {42, 44, 46, 64, 78}


def read_all(host=HOST, port=PORT):
    """Read all 80 registers as 40 int32 values. Returns None on error."""
    client = ModbusTcpClient(host, port=port, timeout=5, retries=1)
    if not client.connect():
        return None
    try:
        response = client.read_holding_registers(
            address=0, count=80, device_id=SLAVE_ID
        )
        if response is None or response.isError():
            return None
        if not hasattr(response, 'registers'):
            return None
        regs = response.registers
        values = []
        for i in range(0, len(regs), 2):
            v = (regs[i] << 16) | regs[i + 1]
            if v >= 2**31:
                v -= 2**32
            values.append(v)
        return values
    except Exception:
        return None
    finally:
        client.close()


def fmt_value(addr, raw):
    """Display a register value. Enums get the human-readable name."""
    if addr in ENUMS:
        name = ENUMS[addr].get(raw)
        if name:
            return f'{name}({raw})'
        return f'unknown({raw})'
    if addr in SCALES:
        unit, divisor = SCALES[addr]
        return f'{raw / divisor:.1f}{unit}'
    return str(raw)


def fmt_reg(addr, raw):
    label = LABELS.get(addr, f'REG[{addr}]')
    return f'{label}({addr})={fmt_value(addr, raw)}'


def is_significant_change(addr, prev, curr):
    if addr in EVENT_REGISTERS:
        return True
    if addr in NOISY_TEMPS:
        scale = SCALES.get(addr, (None, 10))[1]
        return abs(curr - prev) >= TEMP_NOISE_THRESHOLD * scale
    return True


def log(msg, fh):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line, flush=True)
    fh.write(line + '\n')


def write_csv_row(csv_writer, vals):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    csv_writer.writerow([ts] + vals)


def main():
    prev = None
    last_snapshot = 0
    fail_count = 0

    csv_is_new = not os.path.exists(CSVFILE)
    csv_fh = open(CSVFILE, 'a', buffering=1, newline='')
    csv_writer = csv.writer(csv_fh)
    if csv_is_new:
        header = ['timestamp'] + [
            f'{LABELS.get(i*2, f"REG{i*2}")}_{i*2}' for i in range(40)
        ]
        csv_writer.writerow(header)

    with open(LOGFILE, 'a', buffering=1) as fh:
        log(f'=== Gilles Logger v3.1 started -- host={HOST} ===', fh)

        try:
            while True:
                vals = read_all()
                now = time.time()

                if vals is None:
                    fail_count += 1
                    if fail_count <= 3 or fail_count % 30 == 0:
                        log(f'!! Modbus read failed (#{fail_count})', fh)
                    time.sleep(POLL_INTERVAL)
                    continue

                if fail_count > 0:
                    log(f'>> Connection recovered after {fail_count} failures', fh)
                    fail_count = 0

                write_csv_row(csv_writer, vals)

                if prev is None:
                    snapshot = ', '.join(fmt_reg(i * 2, v) for i, v in enumerate(vals))
                    log(f'INITIAL: {snapshot}', fh)
                    last_snapshot = now
                else:
                    events = []
                    changes = []
                    for i, v in enumerate(vals):
                        if v == prev[i]:
                            continue
                        addr = i * 2
                        label = LABELS.get(addr, f'REG[{addr}]')
                        change_str = (
                            f'{label}({addr}): '
                            f'{fmt_value(addr, prev[i])} -> {fmt_value(addr, v)}'
                        )
                        if addr in EVENT_REGISTERS:
                            events.append(change_str)
                        elif is_significant_change(addr, prev[i], v):
                            changes.append(change_str)

                    if events:
                        log('EVENT: ' + ' | '.join(events), fh)
                    if changes:
                        log('CHANGE: ' + ' | '.join(changes), fh)

                    if now - last_snapshot >= SNAPSHOT_INTERVAL:
                        snapshot = ', '.join(fmt_reg(i * 2, v) for i, v in enumerate(vals))
                        log(f'SNAPSHOT: {snapshot}', fh)
                        last_snapshot = now

                prev = vals
                time.sleep(POLL_INTERVAL)
        finally:
            csv_fh.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nStopped by user.')
