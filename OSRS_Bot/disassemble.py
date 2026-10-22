import struct, os

with open('StrongholdScript.class', 'rb') as f:
    data = f.read()

magic, minor, major, cp_count = struct.unpack('>IHHH', data[:10])
pos = 10
cp = [None] * cp_count
i = 1
while i < cp_count:
    tag = data[pos]
    pos += 1
    if tag == 1:
        length = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        val = data[pos:pos+length].decode('utf-8', errors='replace')
        pos += length
        cp[i] = ('Utf8', val)
    elif tag in (7, 8, 16, 19, 20):
        val = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        cp[i] = (tag, val)
    elif tag in (3, 4):
        val = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        cp[i] = (tag, val)
    elif tag in (5, 6):
        pos += 8
        i += 1
    elif tag in (9, 10, 11, 12, 17, 18):
        val = struct.unpack('>HH', data[pos:pos+4])
        pos += 4
        cp[i] = (tag, val)
    elif tag == 15:
        pos += 3
    i += 1

def cp_str(idx):
    if not idx or idx >= len(cp) or not cp[idx]: return str(idx)
    t = cp[idx]
    if t[0] == 'Utf8': return t[1]
    if t[0] == 8: return f'"{cp_str(t[1])}"'
    if t[0] == 7: return cp_str(t[1])
    if t[0] in (9, 10, 11): return f'{cp_str(t[1][0])}.{cp_str(t[1][1])}'
    if t[0] == 12: return f'{cp_str(t[1][0])}:{cp_str(t[1][1])}'
    return str(t)

access_flags, this_class, super_class, interfaces_count = struct.unpack('>HHHH', data[pos:pos+8])
pos += 8 + interfaces_count * 2
fields_count = struct.unpack('>H', data[pos:pos+2])[0]
pos += 2
for _ in range(fields_count):
    f_access, f_name, f_desc, f_attrs = struct.unpack('>HHHH', data[pos:pos+8])
    pos += 8
    for _ in range(f_attrs):
        attr_name, attr_len = struct.unpack('>HI', data[pos:pos+6])
        pos += 6 + attr_len

methods_count = struct.unpack('>H', data[pos:pos+2])[0]
pos += 2
for _ in range(methods_count):
    m_access, m_name, m_desc, m_attrs = struct.unpack('>HHHH', data[pos:pos+8])
    pos += 8
    name = cp_str(m_name)
    for _ in range(m_attrs):
        attr_name, attr_len = struct.unpack('>HI', data[pos:pos+6])
        attr_name_str = cp_str(attr_name)
        if attr_name_str == 'Code' and name in ['claimBoots', 'handleDialogue']:
            print(f'=== Method: {name} ===')
            code_pos = pos + 6
            max_stack, max_locals, code_len = struct.unpack('>HHI', data[code_pos:code_pos+8])
            code = data[code_pos+8:code_pos+8+code_len]
            offset = 0
            while offset < code_len:
                op = code[offset]
                if op == 0xb6:
                    cpid = struct.unpack('>H', code[offset+1:offset+3])[0]
                    print(f'{offset:4d}: invokevirtual {cp_str(cpid)}')
                    offset += 3
                elif op == 0xb7:
                    cpid = struct.unpack('>H', code[offset+1:offset+3])[0]
                    print(f'{offset:4d}: invokespecial {cp_str(cpid)}')
                    offset += 3
                elif op == 0xb8:
                    cpid = struct.unpack('>H', code[offset+1:offset+3])[0]
                    print(f'{offset:4d}: invokestatic {cp_str(cpid)}')
                    offset += 3
                elif op == 0xba:
                    cpid = struct.unpack('>H', code[offset+1:offset+3])[0]
                    print(f'{offset:4d}: invokedynamic {cp_str(cpid)}')
                    offset += 5
                elif op in (0x12, 0x13):
                    cpid = code[offset+1] if op == 0x12 else struct.unpack('>H', code[offset+1:offset+3])[0]
                    print(f'{offset:4d}: ldc {cp_str(cpid)}')
                    offset += (2 if op == 0x12 else 3)
                elif op == 0xb4:
                    cpid = struct.unpack('>H', code[offset+1:offset+3])[0]
                    print(f'{offset:4d}: getfield {cp_str(cpid)}')
                    offset += 3
                elif op == 0xb5:
                    cpid = struct.unpack('>H', code[offset+1:offset+3])[0]
                    print(f'{offset:4d}: putfield {cp_str(cpid)}')
                    offset += 3
                elif op == 0xb2:
                    cpid = struct.unpack('>H', code[offset+1:offset+3])[0]
                    print(f'{offset:4d}: getstatic {cp_str(cpid)}')
                    offset += 3
                else:
                    offset += 1
        pos += 6 + attr_len
