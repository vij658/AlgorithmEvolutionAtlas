# TCP Congestion Control: the program

*Era 7 · topic 10 · 1986–1989* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/10-tcp-congestion-control/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/10-tcp-congestion-control/tcp-congestion-control.html) · [All era 7 programs](../README.md)

## How it works

```text
Many senders share one link through a router with a small buffer. A sender that keeps a fixed number of packets
in flight, and resends everything when an acknowledgement is late, can fill the buffer, lose packets, time out,
and resend copies that are still on their way: the link stays busy carrying duplicates while useful throughput
falls. Jacobson's rules make each sender adjust: start with one packet and double each round trip ("slow start");
once past a threshold, add about one packet per round trip ("additive increase"); on a loss, take it as a sign of
congestion, halve the threshold and start again from one packet. Retransmission timers use the measured round-trip
time plus four times its measured variation, doubling after each timeout. Chiu and Jain showed why "increase by
adding, decrease by multiplying" is the right shape: it is the combination that drives senders sharing a link
towards both full use and equal shares, from any start.
```

## What the program does

```text
1. A packet-level simulation: 1 to 64 senders through one bottleneck link with a 120-packet buffer. Senders with a
   fixed window and a fixed resend-everything rule, against senders following Jacobson's rules (slow start,
   congestion avoidance, fast retransmit, timers based on the round trip's variation, with backoff).
2. Chiu and Jain's model: two users adjusting their rates after each signal of over- or under-use, with the four
   combinations of additive and multiplicative increase and decrease.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java TcpCongestion.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [CS791 notes: Chiu–Jain and Jacobson](https://cs-web.bu.edu/fac/byers/courses/791/F99/scribe_notes/cs791-notes-990914.html) — J. Byers, Boston University (1999) | A short walk through both papers, with their weak points |
| Deeper | [RFC 5681: TCP Congestion Control](https://rfc-editor.org/rfc/rfc5681) — IETF (2009) | The rules as the Internet standard states them today |
| Scholar | [Congestion Avoidance and Control](https://www.cs.princeton.edu/courses/archive/fall08/cos561/papers/jacobson88.pdf) — V. Jacobson, M. Karels (1988) | The collapse, the seven algorithms, and the reasoning behind them |
| Scholar | [Analysis of the Increase and Decrease Algorithms for Congestion Avoidance](https://sites.cs.ucsb.edu/~ravenben/classes/papers/cj89.pdf) — D.-M. Chiu, R. Jain, *Computer Networks and ISDN Systems* (1989) | Why additive increase and multiplicative decrease converge to fairness |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
