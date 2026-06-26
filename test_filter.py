import json, os, re

base = '/z/repos/AiXBase/XBaseFiles'
results = []

def read_ndjson(db, table):
    path = os.path.join(base, db, f'{table}.ndjson')
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return [r for r in rows if r.get('IsDeleted', 0) == 0]

def validate_identifier(name):
    return bool(re.match(r'^[A-Za-z0-9_]+$', name))

ALLOWED_OPS = {'=', '!=', '<', '<=', '>', '>=', 'LIKE', 'IN', 'NOT IN', 'IS NULL', 'IS NOT NULL'}
OPS_NO_VALUE = {'IS NULL', 'IS NOT NULL'}
OPS_ARRAY = {'IN', 'NOT IN'}

def compile_filter(field, operator, value=None):
    if not validate_identifier(field):
        return None, 'XBASE_FILTER_FIELD_INVALID'
    if operator not in ALLOWED_OPS:
        return None, 'XBASE_FILTER_OPERATOR_UNKNOWN'
    if operator not in OPS_NO_VALUE:
        if value is None:
            return None, 'XBASE_FILTER_VALUE_REQUIRED'
        if operator in OPS_ARRAY:
            if not isinstance(value, list) or len(value) == 0:
                return None, 'XBASE_FILTER_VALUE_REQUIRED'
    return {'field': field, 'operator': operator, 'value': value}, None

def like_to_regex(pattern, case_insensitive=False):
    parts = re.split(r'(%|_)', pattern)
    regex = ''
    for p in parts:
        if p == '%':
            regex += '.*'
        elif p == '_':
            regex += '.'
        else:
            regex += re.escape(p)
    flags = re.IGNORECASE if case_insensitive else 0
    return re.compile('^' + regex + '$', flags)

def apply_single_filter(row, field, operator, value, case_insensitive=False):
    row_val = row.get(field)
    if operator == 'IS NULL':
        return row_val is None
    if operator == 'IS NOT NULL':
        return row_val is not None
    if row_val is None:
        return False
    if operator == '=':
        if isinstance(value, bool):
            return row_val == (1 if value else 0)
        return row_val == value
    if operator == '!=':
        if isinstance(value, bool):
            return row_val != (1 if value else 0)
        return row_val != value
    if operator == '<':
        return row_val < value
    if operator == '<=':
        return row_val <= value
    if operator == '>':
        return row_val > value
    if operator == '>=':
        return row_val >= value
    if operator == 'LIKE':
        pat = like_to_regex(value, case_insensitive)
        return bool(pat.match(str(row_val)))
    if operator == 'IN':
        return row_val in value
    if operator == 'NOT IN':
        return row_val not in value
    return False

def apply_filter_spec(rows, fspec, case_insensitive=False):
    if fspec is None:
        return rows
    field = fspec['field']
    operator = fspec['operator']
    value = fspec['value']
    return [r for r in rows if apply_single_filter(r, field, operator, value, case_insensitive)]

def apply_and_filter(rows, specs):
    for spec in specs:
        rows = apply_filter_spec(rows, spec)
    return rows

def apply_or_filter(rows, specs):
    matched = []
    seen = set()
    for spec in specs:
        for row in apply_filter_spec(rows, spec):
            rid = row['Id']
            if rid not in seen:
                seen.add(rid)
                matched.append(row)
    return matched

def PASS(tid, notes=''):
    results.append((tid, 'PASS', notes))

def FAIL(tid, notes=''):
    results.append((tid, 'FAIL', notes))

def ERROR_OK(tid, code, notes=''):
    results.append((tid, 'PASS', f'Correctly returned {code}. {notes}'.strip()))

db = 'test-qry-filter'
rows = read_ndjson(db, 'Items')
print(f'Loaded {len(rows)} rows from Items')

# QRY-001
fspec, err = compile_filter('Code', '=', 'CODE-1')
if err:
    FAIL('XBASE-QRY-001', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == 1 and r[0]['Code'] == 'CODE-1':
        PASS('XBASE-QRY-001', '1 row returned')
    else:
        FAIL('XBASE-QRY-001', f'Expected 1 row, got {len(r)}')

# QRY-002
fspec, err = compile_filter('Code', '!=', 'CODE-1')
if err:
    FAIL('XBASE-QRY-002', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    expected = len(rows) - 1
    if len(r) == expected:
        PASS('XBASE-QRY-002', f'{len(r)} rows (all except CODE-1)')
    else:
        FAIL('XBASE-QRY-002', f'Expected {expected}, got {len(r)}')

# QRY-003
fspec, err = compile_filter('Value', '<', 50.0)
if err:
    FAIL('XBASE-QRY-003', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    expected_count = len([x for x in rows if x['Value'] is not None and x['Value'] < 50.0])
    if len(r) == expected_count:
        PASS('XBASE-QRY-003', f'{len(r)} rows where Value<50')
    else:
        FAIL('XBASE-QRY-003', f'Expected {expected_count}, got {len(r)}')

# QRY-004
fspec, err = compile_filter('Value', '<=', 1.23)
if err:
    FAIL('XBASE-QRY-004', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == 1 and abs(r[0]['Value'] - 1.23) < 0.001:
        PASS('XBASE-QRY-004', '1 row (Value=1.23 included)')
    else:
        FAIL('XBASE-QRY-004', f'Expected 1 row, got {len(r)}: {[x["Value"] for x in r]}')

# QRY-005
fspec, err = compile_filter('Code', 'LIKE', 'CODE-%')
if err:
    FAIL('XBASE-QRY-005', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == len(rows):
        PASS('XBASE-QRY-005', f'All {len(r)} rows matched CODE-%')
    else:
        FAIL('XBASE-QRY-005', f'Expected {len(rows)}, got {len(r)}')

# QRY-006
fspec, err = compile_filter('Label', 'LIKE', '%Label 1')
if err:
    FAIL('XBASE-QRY-006', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    matches = [x['Label'] for x in r]
    if len(r) == 1 and r[0]['Label'] == 'Label 1':
        PASS('XBASE-QRY-006', f'1 row: {matches}')
    else:
        FAIL('XBASE-QRY-006', f'Expected ["Label 1"], got {matches}')

# QRY-007
fspec, err = compile_filter('Label', 'LIKE', '%abel%')
if err:
    FAIL('XBASE-QRY-007', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == len(rows):
        PASS('XBASE-QRY-007', f'All {len(r)} rows matched %abel%')
    else:
        FAIL('XBASE-QRY-007', f'Expected {len(rows)}, got {len(r)}')

# QRY-008 case-insensitive
fspec, err = compile_filter('Code', 'LIKE', '%code%')
if err:
    FAIL('XBASE-QRY-008', f'Compile error: {err}')
else:
    ci_results = [r for r in rows if like_to_regex('%code%', case_insensitive=True).match(str(r.get('Code', '')))]
    if len(ci_results) == len(rows):
        PASS('XBASE-QRY-008', f'All {len(ci_results)} rows matched case-insensitively')
    else:
        FAIL('XBASE-QRY-008', f'Expected {len(rows)}, got {len(ci_results)}')

# QRY-009
fspec, err = compile_filter('Code', 'IN', ['CODE-1', 'CODE-2', 'CODE-3'])
if err:
    FAIL('XBASE-QRY-009', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == 3:
        PASS('XBASE-QRY-009', f'3 rows: {[x["Code"] for x in r]}')
    else:
        FAIL('XBASE-QRY-009', f'Expected 3, got {len(r)}')

# QRY-010
fspec, err = compile_filter('Code', 'IN', ['CODE-1'])
if err:
    FAIL('XBASE-QRY-010', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == 1:
        PASS('XBASE-QRY-010', '1 row')
    else:
        FAIL('XBASE-QRY-010', f'Expected 1, got {len(r)}')

# QRY-011
fspec, err = compile_filter('Code', 'IN', [])
if err == 'XBASE_FILTER_VALUE_REQUIRED':
    ERROR_OK('XBASE-QRY-011', err)
else:
    FAIL('XBASE-QRY-011', f'Expected XBASE_FILTER_VALUE_REQUIRED, got err={err}')

# QRY-012
big_list = [f'CODE-{i}' for i in range(1, 1001)]
fspec, err = compile_filter('Code', 'IN', big_list)
if err:
    FAIL('XBASE-QRY-012', f'Unexpected error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    # All our CODE-1..CODE-100 are in the big list
    if len(r) == 100:
        PASS('XBASE-QRY-012', f'No error; {len(r)} matching rows from 1000-item IN list')
    else:
        FAIL('XBASE-QRY-012', f'Expected 100 (all CODE-1..CODE-100 match), got {len(r)}')

# QRY-013
fspec, err = compile_filter('Code', 'NOT IN', ['CODE-1', 'CODE-2'])
if err:
    FAIL('XBASE-QRY-013', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == 98:
        PASS('XBASE-QRY-013', f'{len(r)} rows')
    else:
        FAIL('XBASE-QRY-013', f'Expected 98, got {len(r)}')

# QRY-014
fspec, err = compile_filter('Value', 'IS NULL')
if err:
    FAIL('XBASE-QRY-014', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == 10:
        PASS('XBASE-QRY-014', f'{len(r)} null-value rows')
    else:
        FAIL('XBASE-QRY-014', f'Expected 10, got {len(r)}')

# QRY-015
fspec, err = compile_filter('Value', 'IS NOT NULL')
if err:
    FAIL('XBASE-QRY-015', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == 90:
        PASS('XBASE-QRY-015', f'{len(r)} non-null rows')
    else:
        FAIL('XBASE-QRY-015', f'Expected 90, got {len(r)}')

# QRY-016 AND
f1, _ = compile_filter('Code', '=', 'CODE-1')
f2, _ = compile_filter('Value', '=', 1.23)
r = apply_and_filter(rows, [f1, f2])
if len(r) == 1:
    PASS('XBASE-QRY-016', 'AND intersection: 1 row')
else:
    FAIL('XBASE-QRY-016', f'Expected 1, got {len(r)}')

# QRY-017 OR
f1, _ = compile_filter('Code', '=', 'CODE-1')
f2, _ = compile_filter('Code', '=', 'CODE-2')
r = apply_or_filter(rows, [f1, f2])
if len(r) == 2:
    PASS('XBASE-QRY-017', 'OR union: 2 rows')
else:
    FAIL('XBASE-QRY-017', f'Expected 2, got {len(r)}')

# QRY-018 nested (Code="CODE-1" AND Value=1.23) OR Code="CODE-2"
f1, _ = compile_filter('Code', '=', 'CODE-1')
f2, _ = compile_filter('Value', '=', 1.23)
f3, _ = compile_filter('Code', '=', 'CODE-2')
group1 = apply_and_filter(rows, [f1, f2])
group2 = apply_filter_spec(rows, f3)
r = list({x['Id']: x for x in group1 + group2}.values())
if len(r) == 2:
    PASS('XBASE-QRY-018', f'Nested AND/OR: 2 rows {[x["Code"] for x in r]}')
else:
    FAIL('XBASE-QRY-018', f'Expected 2, got {len(r)}')

# QRY-019 injection
fspec, err = compile_filter('Id; DROP TABLE Items--', '=', 1)
if err == 'XBASE_FILTER_FIELD_INVALID':
    ERROR_OK('XBASE-QRY-019', err)
else:
    FAIL('XBASE-QRY-019', f'Expected XBASE_FILTER_FIELD_INVALID, got err={err}')

# QRY-020 unknown operator
fspec, err = compile_filter('Value', 'BETWEEN', 1)
if err == 'XBASE_FILTER_OPERATOR_UNKNOWN':
    ERROR_OK('XBASE-QRY-020', err)
else:
    FAIL('XBASE-QRY-020', f'Expected XBASE_FILTER_OPERATOR_UNKNOWN, got err={err}')

# QRY-021 value omitted
fspec, err = compile_filter('Code', '=', None)
if err == 'XBASE_FILTER_VALUE_REQUIRED':
    ERROR_OK('XBASE-QRY-021', err)
else:
    FAIL('XBASE-QRY-021', f'Expected XBASE_FILTER_VALUE_REQUIRED, got err={err}')

# QRY-022 integer 42
fspec, err = compile_filter('Value', '=', 42)
if err:
    FAIL('XBASE-QRY-022', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    # n*1.23=42 -> n=34.14, no exact match
    if len(r) == 0:
        PASS('XBASE-QRY-022', 'Integer 42 compared numerically; 0 matches (no row has Value=42.0)')
    else:
        FAIL('XBASE-QRY-022', f'Unexpected {len(r)} matches: {[x["Value"] for x in r]}')

# QRY-023 float 3.14
fspec, err = compile_filter('Value', '=', 3.14)
if err:
    FAIL('XBASE-QRY-023', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == 0:
        PASS('XBASE-QRY-023', 'Float 3.14 compared numerically; 0 matches (no row has Value=3.14)')
    else:
        FAIL('XBASE-QRY-023', f'Unexpected {len(r)} matches: {[x["Value"] for x in r]}')

# QRY-024 boolean true -> integer 1
fspec, err = compile_filter('Value', '=', True)
if err:
    FAIL('XBASE-QRY-024', f'Compile error: {err}')
else:
    r = apply_filter_spec(rows, fspec)
    if len(r) == 0:
        PASS('XBASE-QRY-024', 'Boolean true->1 compared numerically; 0 matches (no Value=1.0; row 1 has Value=1.23)')
    else:
        FAIL('XBASE-QRY-024', f'Unexpected {len(r)} matches: {[x["Value"] for x in r]}')

for tid, res, notes in results:
    print(f'| {tid} | {res} | {notes} |')

passed = sum(1 for _, r, _ in results if r == 'PASS')
failed = sum(1 for _, r, _ in results if r == 'FAIL')
print(f'\nFilter tests: {passed} passed, {failed} failed')
