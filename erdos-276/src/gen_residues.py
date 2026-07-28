#!/usr/bin/env python3
"""Generate the sieve input: all primes p <= 2*10^6 plus the 5 Table-2 primes
above that bound, with x0 mod p and x1 mod p. Binary little-endian uint64
triples (p, x0 mod p, x1 mod p). Deterministic."""
import struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 2_000_000

q = int((ROOT / "data" / "q_decimal.txt").read_text().strip())
x0, x1 = 1 + q * q, 2 * q + q * q

big_table_primes = []
for line in (ROOT / "data" / "table2_quadruples.tsv").read_text().splitlines():
    if line.startswith("#") or not line.strip():
        continue
    p = int(line.split()[0])
    if p > LIMIT:
        big_table_primes.append(p)

sieve = bytearray([1]) * (LIMIT + 1)
sieve[0] = sieve[1] = 0
for i in range(2, int(LIMIT ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
primes = [i for i in range(LIMIT + 1) if sieve[i]]
print(f"primes <= {LIMIT}: {len(primes)}; big table primes appended: {big_table_primes}")

out = ROOT / "data" / "sieve_input.bin"
with open(out, "wb") as f:
    for p in primes + sorted(big_table_primes):
        f.write(struct.pack("<QQQ", p, x0 % p, x1 % p))
print(f"wrote {out} ({out.stat().st_size} bytes, {len(primes)+len(big_table_primes)} triples)")
