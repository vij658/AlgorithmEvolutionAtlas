# Fast Matrix Multiplication: the program

*Era 6 · topic 5 · 1969* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/05-strassen/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/05-strassen/strassen.html) · [All era 6 programs](../README.md)

## How it works

```text
Two 2 x 2 matrices are multiplied, by the rule taught in school, with 8 multiplications:
    [a b] [e f]   [ae+bg  af+bh]
    [c d] [g h] = [ce+dg  cf+dh]
Strassen found seven products that are enough:
    m1 = (a+d)(e+h)   m2 = (c+d)e   m3 = a(f-h)   m4 = d(g-e)   m5 = (a+b)h   m6 = (c-a)(e+f)   m7 = (b-d)(g+h)
    ae+bg = m1+m4-m5+m7   af+bh = m3+m5   ce+dg = m2+m4   cf+dh = m1-m2+m3+m6
The letters may themselves be blocks of a bigger matrix, because the formulas never use ab = ba. So a matrix of
size 2^k is cut into four blocks, seven products of half size are made, each the same way, down to single numbers:
7^k multiplications instead of 8^k, that is n^2.807 instead of n^3. One saved multiplication, repeated at every
level, changes the exponent.
```

## What the program does

```text
1. Checks the seven-product formulas exactly, as bilinear forms, and on random numbers.
2. Counts multiplications and additions for sizes 2 ... 4,096, school against Strassen, and finds where switching
   to the school method for small blocks pays.
3. Multiplies two random 256 x 256 integer matrices both ways: identical results, multiplications counted.
4. Rounding: on 128 x 128 matrices of decimals, both methods against the exact product.
5. Inverting a matrix by blocks with the fast product, against Gauss-Jordan elimination.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Strassen.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [How fast can you multiply matrices?](https://www.johndcook.com/blog/2018/08/31/how-fast-can-you-multiply-matrices/) — John D. Cook (2018) | Eight products, then seven, in a short post |
| Start | [Volker Strassen](https://mathshistory.st-andrews.ac.uk/Biographies/Strassen.html) — MacTutor History of Mathematics | The mathematician, and his other fast algorithms |
| Deeper | [Computational complexity of matrix multiplication](https://en.wikipedia.org/wiki/Computational_complexity_of_matrix_multiplication) — Wikipedia | Every lowering of the exponent since 1969, with references |
| Deeper | [Schnelle Matrixmultiplikation und Kombinatorik](https://www.mat.univie.ac.at/~slc/wpapers/s36buerg.pdf) — Peter Bürgisser, Séminaire Lotharingien de Combinatoire (in German) | How the exponent came down, from someone in Strassen's school |
| Scholar | [Gaussian elimination is not optimal (bibliographic entry)](https://cr.yp.to/bib/1969/strassen.bibtex) — V. Strassen, *Numerische Mathematik* 13: 354–356 (1969) | The three-page paper; no openable copy of the text was found |
| Scholar | [Improving the matrix multiplication exponent with modern optimization and AlphaEvolve](https://arxiv.org/pdf/2608.16884) — E. Dupont et al. (2026), arXiv | The latest bound, found with the help of an AI system |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
