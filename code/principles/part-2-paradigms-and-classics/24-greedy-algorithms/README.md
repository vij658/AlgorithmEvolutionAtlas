# 24. Greedy algorithms and the exchange argument

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#24-greedy-algorithms-and-the-exchange-argument)

## How it works

Take the locally best choice and never look back. It is only correct when an exchange argument shows any optimal solution can be turned into the greedy one without getting worse; interval scheduling and Huffman coding pass, and coin change with odd denominations is the counterexample.

## In depth (from the catalog page)

Take the locally best choice at every step and never undo it. Greedy algorithms are fast and short, and they are correct only for problems whose structure makes the local choice safe. The standard proof is an *exchange argument*: take any optimal solution that disagrees with greedy's first choice, swap greedy's choice in, and show the result is no worse. If you can't produce that argument, test the greedy rule against brute force on small inputs, because plausible greedy rules are wrong surprisingly often.

```java
static int maxNonOverlapping(int[][] intervals) {      // each {start, end}; touching ends are allowed
    int[][] s = intervals.clone();
    Arrays.sort(s, Comparator.comparingInt(x -> x[1]));   // earliest finish first
    int count = 0, lastEnd = Integer.MIN_VALUE;
    for (int[] iv : s)
        if (iv[0] >= lastEnd) { count++; lastEnd = iv[1]; }
    return count;
}

record Node(long weight, int order, char symbol, Node left, Node right) {}

static Map<Character, String> huffman(Map<Character, Long> freq) {
    PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingLong(Node::weight).thenComparingInt(Node::order));
    int order = 0;
    for (Map.Entry<Character, Long> e : new TreeMap<>(freq).entrySet())
        pq.add(new Node(e.getValue(), order++, e.getKey(), null, null));
    while (pq.size() > 1) {
        Node a = pq.poll(), b = pq.poll();              // merge the two lightest subtrees
        pq.add(new Node(a.weight() + b.weight(), order++, '\0', a, b));
    }
    Map<Character, String> codes = new TreeMap<>();
    assign(pq.poll(), "", codes);
    return codes;
}

private static void assign(Node n, String prefix, Map<Character, String> out) {
    if (n.left() == null) { out.put(n.symbol(), prefix.isEmpty() ? "0" : prefix); return; }
    assign(n.left(), prefix + "0", out);
    assign(n.right(), prefix + "1", out);
}
```

> **Verified.** Earliest-finish-first matched an enumeration of every subset on 1,000 random sets of up to 12 intervals. The tempting rule "take the earliest start" fails on {[0, 10], [1, 2], [3, 4]}: it finds 1 meeting where the optimum is 2. Huffman on the textbook frequencies 45, 13, 12, 16, 9 and 5 (per 100 symbols) needs 224 bits, which is 2.24 bits per symbol, against 300 bits for fixed 3-bit codes and an entropy of 2.2199 bits (entry 16). The codes were prefix-free, and the average length stayed between the entropy and the entropy plus one bit. On 500 random sets of 2 to 7 weights, Huffman's total cost equalled the best of every possible merge order. Greedy change-making with coins 1, 5, 10, 25 matched the dynamic program of entry 23 for every amount from 1 to 1,000, but with coins 1, 3, 4 and amount 6 greedy takes three coins (4 + 1 + 1) where the optimum is two (3 + 3).

<!-- -->

> **Pitfall.** A greedy rule that works on your examples is not a proof. Coin systems like 1, 5, 10, 25 are special; change the denominations and greedy quietly stops being optimal.

**Use it for** interval scheduling, minimum spanning trees (entry 37), shortest paths with non-negative weights (entry 33) and compression: Huffman codes sit inside DEFLATE (gzip, zip, PNG) and JPEG. Greedy is also the usual first approximation when the exact problem is too hard.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/24-greedy-algorithms
java GreedyAlgorithms.java
```

JDK 17 or newer, no build step. It prints 2,534 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
Huffman: 224 bits per 100 symbols (2.24 bits/symbol), entropy 2.2199; fixed 3-bit codes need 300
GreedyAlgorithms: 2534 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
