# Protocol (v0.1)

- PREAMBLE: 0xAA55 (2 bytes)
- VERSION: 1 byte (0x01)
- MSGTYPE: 1 byte (0x01 TM)
- SEQ: 2 bytes
- TIMESTAMP_MS: 4 bytes
- MODE: 1 byte (0=OP,1=SAFE,2=IDLE)
- BATT_MV: 2 bytes
- TEMP_CENTIDEG: 2 bytes (signed)
- PRESS_PA: 4 bytes
- ALT_CM: 4 bytes
- GYRO: 3x int16
- ACC: 3x int16
- LIGHT: 2 bytes
- COMP_LEN: 1 byte (0=none)
- CRC16: 2 bytes (CRC-16/X25; computed over bytes after preamble)

