# Horner's Method, Nearly Six Centuries Early: the program

*Era 2 · topic 9 · 1247 CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/09-qin-jiushao/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/09-qin-jiushao/qin-jiushao.html) · [All era 2 programs](../README.md)

## How it works

```text
To find a root of an equation of any degree, find it one digit at a time, as in a square root. Suppose the root
lies between 20 and 30: its first digit is 2. Replace x by y + 20 everywhere. The new polynomial in y has a root
between 0 and 10, and its next digit is found the same way. The shift x -> y + d is done on the counting board by
repeated "multiply and add" down the column of coefficients (now called synthetic division), so no power of x is
ever computed. Evaluating a polynomial the same way, a_n x + a_(n-1), times x, plus a_(n-2), ..., takes one
multiplication per degree: Horner's rule. Ruffini (about 1805) and Horner (1819) found it again in Europe.
```

## What the program does

```text
1. Counts the multiplications for evaluating a polynomial of degree 10 three ways.
2. Finds roots digit by digit, with exact decimal arithmetic, for a cubic worked by Joyce, a quartic and the
   degree-10 "circular city" equation from the Shushu jiuzhang (as given in the Dictionary of Scientific
   Biography), and the fifth root of 2; it prints the shifted polynomial after each digit.
3. Checks the method on 5,000 random polynomials built with a known root.
4. Compares digits per step: digit by digit, bisection, and Newton's method.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java QinJiushao.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Qin Jiushao](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/) — MacTutor | Life, the 1247 treatise, the degree-10 equation, and the remainder theorem with non-coprime moduli |
| Start | [Qin Jiushao](https://www.britannica.com/print/article/111675) — Encyclopaedia Britannica | Short biography; the earliest surviving description of the root-finding method |
| Start | [Qin Jiushao (1202–1261)](https://mathshistory.st-andrews.ac.uk/Strick/qin_jiushao.pdf) — H. K. Strick, trans. J. O'Connor, MacTutor | Illustrated article with a worked shift-the-root example (x = y + 2) and Sun Zi's 3-5-7 problem |
| Deeper | [The Chinese algorithm for solving equations](https://mathcs.clarku.edu/~djoyce/ma105/chinalg.html) — David E. Joyce, Clark University (course MA105) | Worked digit-by-digit solution of a cubic and a fifth root, with a note on how it ran on a counting board, compared with bisection and Newton's method |
| Deeper | [Equations in China: Two Millennia of Innovation, Transmission and Retransmission](https://hkumath.hku.hk/~mks/ESU8_MKSiu_Equations_RevisedDraft_Mar12_2019.pdf) — Man-Keung Siu, University of Hong Kong | Places Qin's *zengcheng kaifangfa* in the long Chinese history of equations |
| Deeper | [On the Algorithmic Significance and Analysis of the Method of DaYan Deriving One](https://arxiv.org/pdf/1610.01175) — Guangwu Xu and Bao Li, arXiv | Qin's inverse procedure restated as a 2×2 state-matrix algorithm and compared with extended Euclid |
| Scholar | [Historical development of the Chinese remainder theorem](https://link.springer.com/doi/10.1007/BF00357063) — Shen Kangsheng, *Archive for History of Exact Sciences* 38(4):285–305 (1988) | The calendar origin (*shangyuan*) and a step-by-step reading of the Dayan rule. Full text on a University of Kentucky course site |
| Scholar | [Traditional Chinese Mathematics in the 19th Century Western World](https://thjcs.site.nthu.edu.tw/p/16-1452-41351.php?Lang=en) — Wang Xiaoqin (2003), National Tsing Hua University journal site | How Wylie, Biernatzki, Cantor and Matthiessen received the Dayan rule in Europe |
| Scholar | [Ch'in Chiu-shao](https://mathshistory.st-andrews.ac.uk/DSB/Qin_Jiushao.pdf) — Ho Peng-yoke, *Dictionary of Scientific Biography* (via MacTutor) | Standard reference entry: the root-finding method, the *ta-yen ch'iu-i shu*, the zero symbol, the degree-10 equation |
| Scholar | [Chinese Mathematics in the Thirteenth Century, ch. 14](https://legacy-www.math.harvard.edu/~knill/crt/lib/Libbrecht14.pdf) — Ulrich Libbrecht (MIT Press, 1973), excerpt in [Oliver Knill's CRT library](https://legacy-www.math.harvard.edu/~knill/crt/lib.html), Harvard | The standard English study of the *Shushu jiuzhang*. This chapter surveys first-degree indeterminate analysis outside China and says the problem "finds its culminating point in the work of Ch'in Chiu-shao (1247)" |
| Scholar | [s_sin.c (IBM Accurate Mathematical Library)](https://codebrowser.dev/glibc/glibc/sysdeps/ieee754/dbl-64/s_sin.c.html) — GNU C library source, on codebrowser.dev | Polynomials written in nested (Horner) form inside do_sin |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
