#!/usr/bin/env python3
"""
Gilles Touch Modbus Snapshot
============================
Reads all 40 logical values once and prints them with labels.
Useful for comparing the live state against a Touch-screen screenshot.

Usage:
    python3 gilles_snapshot.py [HOST]
"""

import os
import sys
from pymodbus.client import ModbusTcpClient

HOST = os.environ.get('GILLES_HOST', '192.0.2.1')  # RFC5737 doc IP
PORT = 502
SLAVE_ID = 1

if len(sys.argv) > 1:
    HOST = sys.argv[1]

LABELS = {
    0: 'sProzFoerderSchnecke',     2: 'sPrimaerMax',
    4: 'sPrimaerMin',              6: 'sSekundaerMax',
    8: 'sSekundaerMin',           10: 'sSaugzugMax',
    12: 'sSaugzugMin',            14: 'sO2Max',
    16: 'sO2Min',                 18: 'sKesselSollTag',
    20: 'sAschenaustrDauer',      22: 'sAschenaustrPause',
    24: 'sStartSekundaer',        26: 'sZuendEinschub',
    28: 'sTempDiffStart',         30: 'sTempDiffStop',
    32: 'sTempDiffTeillast',      34: 'sKesselSollNacht',
    36: 'sAbgasTempSollMin',      38: 'sAbgasTempMax',
    40: 'sAbgasTempMaxLimit',
    42: 'BrennPhase',             44: 'BoilerStatus',
    46: 'StatusBitmap',
    48: 'KesselTemp_Ist',         50: 'AbgasTemp_Ist',
    52: 'RuecklaufTemp_Ist',      54: 'O2_Ist',
    56: '?REG56',                 58: 'PrimaerIst',
    60: 'SekundaerIst',           62: 'SaugzugIst',
    64: 'KesselSoll_Live',        66: 'AbgasSoll_Live',
    68: '?Zaehler',               72: '?BinarFlag',
    78: 'AscheaustragungAktiv',
}


def main():
    print(f'Connecting to {HOST}:{PORT} ...')
    client = ModbusTcpClient(HOST, port=PORT, timeout=5, retries=1)
    if not client.connect():
        print('ERROR: could not connect')
        sys.exit(1)

    try:
        response = client.read_holding_registers(
            address=0, count=80, device_id=SLAVE_ID
        )
        if response is None or response.isError():
            print(f'ERROR: Modbus read failed: {response}')
            sys.exit(1)
        regs = response.registers
    finally:
        client.close()

    print()
    print(f'{"Addr":<6}{"Name":<24}{"Raw":>10}{"/10":>10}')
    print('-' * 50)

    for i in range(0, len(regs), 2):
        v = (regs[i] << 16) | regs[i + 1]
        if v >= 2**31:
            v -= 2**32
        label = LABELS.get(i, f'REG[{i}]')
        print(f'{i:<6}{label:<24}{v:>10}{v / 10:>10.1f}')


if __name__ == '__main__':
    main()
