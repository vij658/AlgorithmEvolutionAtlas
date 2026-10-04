# 39. Consistent hashing

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#39-consistent-hashing)

## How it works

Place servers and keys on the same hash ring; each key belongs to the next server clockwise. Adding or removing a server moves only the keys in its arc (about 1/n of them), and virtual nodes even out the load.

## In depth (from the catalog page)

Spreading keys over N servers with `hash(key) % N` has an ugly property: change N and almost every key moves, so adding one server to a cache cluster empties the cache. Consistent hashing (Karger et al., 1997) places servers and keys on the same circle of hash values, and each key belongs to the first server clockwise from it. A new server takes over only the arc just before it, about 1/N of the keys, and keys move only *to* the new server. Giving each server many positions on the circle (virtual nodes) evens out the arcs. Dynamo does exactly this: each node is assigned to multiple points in the ring.

```java
static long hashString(String s) {                     // FNV-1a, then the mixer from entry 38
    long h = 0xcbf29ce484222325L;
    for (byte b : s.getBytes(StandardCharsets.UTF_8)) { h ^= (b & 0xff); h *= 0x100000001b3L; }
    return mix(h);
}

static final class Ring {
    private final TreeMap<Long, String> ring = new TreeMap<>();
    private final int vnodes;
    Ring(int vnodes) { this.vnodes = vnodes; }
    void addNode(String node) { for (int i = 0; i < vnodes; i++) ring.put(hashString(node + "#" + i), node); }
    String nodeFor(String key) {
        Map.Entry<Long, String> e = ring.ceilingEntry(hashString(key));
        return (e != null ? e : ring.firstEntry()).getValue();   // wrap around the ring
    }
}
```

> **Verified.** With 100,000 keys, going from 10 to 11 servers moved 90.9% of the keys under `hash % N`, which is the expected 10/11. On the ring it moved 8.9% with 200 virtual nodes per server, close to the ideal 1/11 = 9.1%, and 9.6% with a single point per server. Every key that moved on the ring moved to the new server, never between old ones. The busiest server held 1.12 times the mean load with 200 virtual nodes per server and 1.58 times with one.

<!-- -->

> **Pitfall.** The ring is only as even as the hash is uniform, so use a hash with good mixing (not a bare `String.hashCode`). Consistent hashing also balances *keys*, not *load*: one hot key still lands on one server. Dynamo-style systems typically replicate each key on the next few distinct servers clockwise, so a failure doesn't lose data.

**Use it for** distributed caches, sharded databases, request routing to a stateful backend (so the same user hits the same instance), and any cluster where members come and go and moving data is expensive.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/39-consistent-hashing
java ConsistentHashing.java
```

JDK 17 or newer, no build step. It prints 18,523 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
10 -> 11 nodes, 100,000 keys: modulo hashing moved 90.9% of keys; consistent hashing moved 8.9% (200 virtual nodes) and 9.6% (1 virtual node)
busiest node's load over the mean: 1.12 with 200 virtual nodes per server, 1.58 with 1
ConsistentHashing: 18523 checks passed
```

## References

- Karger, Lehman, Leighton, Panigrahy, Levine and Lewin, [Consistent hashing and random trees](https://doi.org/10.1145/258533.258660) (STOC 1997). DeCandia et al., [Dynamo: Amazon's Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) (SOSP 2007): consistent hashing with each node assigned to multiple points in the ring, and replication of each key at the N−1 clockwise successors, using a preference list that skips positions so it holds only distinct physical nodes.
