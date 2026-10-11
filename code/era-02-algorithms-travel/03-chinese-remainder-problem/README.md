# The Chinese Remainder Problem: the program

*Era 2 · topic 3 · 3rd–5th century CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/03-chinese-remainder-problem/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/03-chinese-remainder-problem/chinese-remainder-problem.html) · [All era 2 programs](../README.md)

## How it works

```text
"Counted in threes, 2 are left; in fives, 3; in sevens, 2. How many?" Sunzi does not search. He keeps one ready-made
number for each divisor: 70, 21 and 15. Each is a multiple of the other two divisors that leaves 1 for its own
(70 = 2 x 35 leaves 1 when divided by 3, and is divisible by 5 and 7). So 2 x 70 + 3 x 21 + 2 x 15 leaves 2, 3 and 2,
and casting out 105 = 3 x 5 x 7 as often as possible gives the smallest answer, 23.
Finding the ready-made numbers for other divisors is the hard part: for each divisor m and the product M of the
others, find k with M k leaving 1 when divided by m. Qin Jiushao's dayan qiuyi ("finding one") rule does it on the
counting board: put M (reduced by m) at the upper right, m at the lower right, 1 at the upper left; divide the lower
number by the upper and the upper by the lower in turn, adding each quotient times the left-hand number to the
other left-hand place, until the upper right is 1. The upper left is then k. It is Euclid's algorithm with a
running record of the quotients: what is now called the extended Euclidean algorithm.
```

## What the program does

```text
1. Solves Sunzi's problem by his rule and by search, and checks that all 105 triples of remainders have exactly one
   answer below 105.
2. Runs the dayan rule step by step for Sunzi's multipliers and for a calendar congruence in Qin's book
   (377873 x leaves 1 when divided by 499067), and checks it against the extended Euclidean algorithm on
   100,000 random cases.
3. Solves systems whose divisors share factors, by Qin's idea of replacing them with coprime divisors, against a
   brute-force search.
4. Measures search against the rule as the cycles grow.
5. Full circle: RSA decryption by the remainder theorem (as in PKCS #1, RFC 8017) against plain decryption, with
   the cost in word multiplications.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ChineseRemainder.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Chinese Remainder Theorem](https://legacy-www.math.harvard.edu/~knill/seminars/chinese/chinese.pdf) — Oliver Knill, Math Circle slides, Harvard, 15 April 2014 | Sunzi's problem worked visually, with a timeline to Qin Jiushao's "full algorithm" |
| Start | [Non-Western Perspectives, Part 2: Mathematics from China and Africa (Worksheet 11)](https://sites.oxy.edu/ron/math/400/19/ws/ws11.pdf) — Senior Colloquium: History of Mathematics, worksheet (Fall 2019), Occidental College site; instructor not named | Students rework Sunzi's 140 + 63 + 30 − 210 solution |
| Start | [Chinese remainder theorem](https://www.britannica.com/print/article/112749) — Encyclopaedia Britannica | Short statement of the theorem, Sun Zi and Qin Jiushao |
| Deeper | [Histories of Numbers](https://www.gresham.ac.uk/watch-now/numbers-cultures) — Gresham College, Karine Chemla (CNRS), 20 October 2021 (video and transcript) | The *Sunzi Suanjing* as the text that explains rod numerals on a calculating surface; Qin Jiushao's *Shu shu jiu zhang*. The remainder problem itself is not discussed |
| Deeper | [Chinese Remainder Theorem (中國剩餘定理), Lecture Notes Set #04, AMA1D01C](https://polyu.edu.hk/ama/profile/hwlee/AMA1D01C/lec04.pdf) — Hong Kong Polytechnic University, Dept. of Applied Mathematics (in Chinese) | The original Chinese text, why 70/21/15 work, and Qin's *dayan qiuyi* procedure with worked examples |
| Deeper | [Sun Zi](https://mathshistory.st-andrews.ac.uk/Biographies/Sun_Zi/) — MacTutor | The problem and the rule in translation, and the full argument over dating |
| Deeper | [Qin Jiushao](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/) — MacTutor | The 1247 generalisation, non-coprime moduli, and the calendar experts |
| Deeper | [RFC 8017: PKCS #1: RSA Cryptography Specifications Version 2.2](https://rfc-editor.org/rfc/rfc8017) — K. Moriarty (ed.), B. Kaliski, J. Jonsson, A. Rusch, November 2016 | Section 3.2 (the key as p, q, dP, dQ, qInv) and 5.1.2 (decryption by remainders) |
| Scholar | [Historical development of the Chinese remainder theorem](https://link.springer.com/doi/10.1007/BF00357063) — Shen Kangsheng, *Archive for History of Exact Sciences* 38(4) (1988) 285–305 | The standard history, from calendars to Qin's *dayan* rule. A full-text PDF is on a University of Kentucky course page |
| Scholar | [Indeterminate Analysis of the First Degree outside China (Ch. 14)](https://legacy-www.math.harvard.edu/~knill/crt/lib/Libbrecht14.pdf) — Ulrich Libbrecht, *Chinese Mathematics in the Thirteenth Century* (PDF on Knill's Harvard CRT site) | Sunzi to Qin compared with India and Fibonacci, who solved congruences case by case |
| Scholar | [Multivariable Chinese remainder theorem](https://link.springer.com/doi/10.1007/s12045-015-0171-x) — B. Sury, *Resonance* 20(3) (2015) 206–216 | History in the abstract (Sunzi, calendars, Aryabhata, Qin), then generalisations |
| Scholar | [孫子剩餘定理與高斯剩餘定理](https://web.math.sinica.edu.tw/media/pdf/d353/35308.pdf) — Wang Yixun, *數學傳播* 35(3) (2011) 64–79, Academia Sinica (in Chinese) | Quotes the original problem and rule in full and compares them with Gauss's method |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
