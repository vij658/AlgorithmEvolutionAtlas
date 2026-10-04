# 30. Floyd's cycle detection and Pollard's rho

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#30-floyds-cycle-detection-and-pollards-rho)

## How it works

Floyd's tortoise and hare: one pointer moves one step, the other two; if there is a cycle they meet inside it, and restarting one pointer from the head finds the cycle's start in O(1) memory. Pollard's rho uses the same idea on x → x² + c mod n to find a factor.

## In depth (from the catalog page)

Floyd's "tortoise and hare" runs two pointers over a sequence, one step and two steps at a time. If there is a cycle they must meet inside it, using O(1) memory. To find where the cycle starts, reset one pointer to the head and move both one step at a time: if the tail has μ nodes, then μ steps from the head and μ steps from the meeting point both end on the cycle's first node. Pollard's rho (1975) turns the same idea into a factoring method. The sequence `x → x² + c mod n` must repeat modulo an unknown prime factor p after roughly √p steps (the birthday bound of entry 13), but not yet modulo n, so `gcd(|x − y|, n)` turns into a factor as soon as the tortoise and hare agree modulo p.

```java
static final class ListNode {
    final int val;
    ListNode next;
    ListNode(int v) { val = v; }
}

static ListNode cycleStart(ListNode head) {            // node where the cycle begins, or null
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) {                             // met inside the cycle
            slow = head;
            while (slow != fast) { slow = slow.next; fast = fast.next; }
            return slow;
        }
    }
    return null;
}

static long pollardRho(long n) {                       // n composite and < 3e9 so products fit in a long
    if (n % 2 == 0) return 2;
    for (long c = 1; ; c++) {
        long x = 2, y = 2, d = 1;
        while (d == 1) {
            x = (x * x + c) % n;
            y = (y * y + c) % n;
            y = (y * y + c) % n;                        // the hare moves two steps
            d = gcd(Math.abs(x - y), n);                // gcd from entry 1
        }
        if (d != n) return d;                           // d == n: the walk closed too soon, retry with another c
    }
}
```

> **Verified.** `cycleStart` found the right node on 5,580 generated lists, with tails of 0 to 29 nodes and cycles of 2 to 42 nodes, plus a one-node self-loop, and it returns null on acyclic lists and on null. `pollardRho` splits 8051 into 83 × 97 and 10403 into 101 × 103. On 200 products of two random primes between 20,000 and 46,000 it averaged 132 iterations, where trial division by odd numbers would need about 14,320 divisions. An iteration costs a few multiplications and a gcd, so the saving in time is smaller than that ratio, but it is large and it grows with the size of the smaller factor.

<!-- -->

> **Pitfall.** `pollardRho` never returns on a prime `n`, because there is no factor to find, so test primality first with `BigInteger.isProbablePrime`. The `long` version needs n below about 3.03×10⁹ for the same overflow reason as `modPow` in entry 11; beyond that use `BigInteger`.

**Use it for** cycle checks on linked lists and iterators in O(1) memory, finding the period of a pseudo-random generator or any iterated function, detecting an infinite loop in a state machine, and factoring or discrete-logarithm attacks on small numbers and small groups. The square-root cost of rho is the same effect that rates a 256-bit elliptic-curve group at about 128 bits of security.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/30-floyd-cycle-detection-and-pollard-rho
java CycleDetection.java
```

JDK 17 or newer, no build step. It prints 5,785 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
semiprimes of two random primes between 20,000 and 46,000: Pollard rho averaged 132 iterations, trial division would need about 14320 divisions
CycleDetection: 5785 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
