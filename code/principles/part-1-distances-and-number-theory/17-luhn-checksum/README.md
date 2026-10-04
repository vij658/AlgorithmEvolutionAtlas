# 17. Luhn checksum

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#17-luhn-checksum)

## How it works

From the right, double every second digit (subtracting 9 if the result exceeds 9) and add everything; a valid number sums to a multiple of 10. It catches every single-digit error and almost every swap of adjacent digits (all except 09 ↔ 90). It is not protection against tampering.

## In depth (from the catalog page)

Double every second digit from the right, add up the digits, and check that the total is divisible by 10. It is a cheap check digit for accidental typing errors.

```java
static boolean luhn(String digits) {
    int sum = 0;
    boolean dbl = false;
    for (int i = digits.length() - 1; i >= 0; i--) {
        char ch = digits.charAt(i);
        if (ch == ' ') continue;
        int d = ch - '0';
        if (dbl) { d *= 2; if (d > 9) d -= 9; }
        sum += d;
        dbl = !dbl;
    }
    return sum % 10 == 0;
}
```

> **Verified.** `79927398713` passes and `79927398710` fails. The standard test number `4111 1111 1111 1111` passes, and changing its last digit makes it fail. For 200 random 16-digit numbers with a computed check digit, every one of the 16 × 9 single-digit substitutions was caught, and every adjacent swap was caught except 09 ↔ 90.

It guards against typos, not tampering: anyone can compute a valid Luhn number, and a valid number does not prove an account exists. The code above assumes digits and spaces only, so validate the characters first.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/17-luhn-checksum
java LuhnChecksum.java
```

JDK 17 or newer, no build step. It prints 31,709 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
LuhnChecksum: 31709 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
