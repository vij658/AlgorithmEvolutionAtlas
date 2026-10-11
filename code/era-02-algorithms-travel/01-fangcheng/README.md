# Elimination on the Counting Board: the program

*Era 2 · topic 1 · c. 200 BCE – 263 CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/01-fangcheng/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/01-fangcheng/fangcheng.html) · [All era 2 programs](../README.md)

## How it works

```text
Each condition of the problem is laid out as one column of rods: the counts of each unknown from top to bottom,
and the total at the foot. The first condition goes on the right. To clear the top place of another column,
multiply that whole column by the top number of the right-hand column, then subtract the right-hand column from it
again and again until the top place is empty. Repeat with the next place down, until the board is a triangle and
the last column holds one unknown alone. Then work back up. Because every column is multiplied before it is
subtracted, nothing is ever divided until the end, and every number on the board stays a whole number.
Subtraction can leave less than nothing, so the board needs negative numbers and rules for them: subtract like
signs, add unlike signs, and a number taken from an empty place changes its sign.
Turned a quarter turn, the board is the matrix of modern "Gaussian" elimination.
```

## What the program does

```text
1. Solves Problem 1 of chapter 8 (three grades of grain) step by step on the board, checks each step against the
   intermediate columns published for it, and finishes with the Nine Chapters' common divisor.
2. Solves the cattle, sheep and pigs problem of the same chapter, where conditions and working are negative, and
   counts how often each part of the sign rule is used.
3. Measures how big the numbers get: plain cross-multiplication (digits double at each step), the same with common
   factors cancelled, and Bareiss's 1968 fraction-free method, against exact rational answers.
4. Counts the multiplications of cross-multiplying against modern elimination by division.
5. Shows what machines added: a tiny pivot that wrecks elimination in floating point, partial pivoting that fixes
   it, and the textbook worst case, where partial pivoting itself lets the numbers grow as 2^(n-1).
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java FangCheng.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Illustrating The Nine Chapters on the Mathematical Art: Their Use in a College Mathematics History Classroom](https://www.maa.org/book/export/html/863323) — Joel K. Haack (University of Northern Iowa), MAA; from a 2008 Joint Mathematics Meetings talk | How a college course teaches the book; chapter 8 as "Gaussian elimination" |
| Start | [The Nine Chapters on the Mathematical Procedures](https://britannica.com/topic/The-Nine-Chapters-on-the-Mathematical-Procedures) — Encyclopaedia Britannica | Short overview: dates, rods, the chapter on simultaneous equations, negative numbers |
| Start | [Fangcheng Procedure in the Nine Chapters on the Mathematical Arts Revisited](https://retrospectjournal.com/?p=2906) — Kat Jivkova, *Retrospect Journal* (Edinburgh University student history magazine), 2021 | Walks through Problem 1 on the board, red and black rods, back substitution |
| Start | [The Linpack Benchmark](https://top500.org/project/linpack/) — TOP500 | The benchmark behind the TOP500 list: a dense linear system by LU factorization with partial pivoting, 2/3 n³ + O(n²) operations |
| Start | [Fangcheng (mathematics)](https://en.wikipedia.org/wiki/Fangcheng_(mathematics)) — Wikipedia | Problem 1's answer, the procedure for positive and negative numbers, and references |
| Start | [Counting rods](https://en.wikipedia.org/wiki/Counting_rods) — Wikipedia | How rod numerals are formed; red for positive, black for negative |
| Deeper | [Histories of Numbers](https://www.gresham.ac.uk/watch-now/numbers-cultures) — Gresham College, Karine Chemla (CNRS), 20 October 2021 | Video and transcript. How Chinese rod numerals existed only as rods laid out on a calculating surface. Background on the board, not on chapter 8 itself |
| Deeper | [The method of fang cheng, an ancient Chinese algorithm to solve simultaneous equations](https://courses.maths.ox.ac.uk/mod/resource/view.php?id=2763) — Zhuo Zhang (Exeter College), Oxford Mathematical Institute course resource, 2020 | Sets the rod array beside first-year linear-algebra row reduction and pins down the one difference: cross-multiplying instead of dividing |
| Deeper | [Nine Chapters on the Mathematical Art](https://mathshistory.st-andrews.ac.uk/HistTopics/Nine_chapters/) — MacTutor (O'Connor and Robertson) | All nine chapters, dating, and the column-reduction method of chapter 8 |
| Deeper | [The Chinese Roots of Linear Algebra](https://press.jhu.edu/books/title/10232/chinese-roots-linear-algebra) — Roger Hart, Johns Hopkins University Press, 2011 (publisher's page) | The book-length case that *fangcheng* was a rod-board practice that also yields determinant-style solutions |
| Deeper | [Use of the History of Negative Numbers in Education](https://bibnum.publimath.fr/ACF/ACF11039.pdf) — Lenka Molitorisová, Comenius University, Bratislava | Quotes the cattle, sheep and pigs problem and Liu Hui's commentary on red and black rods from Shen, Crossley and Lun (1999), p. 405 |
| Deeper | [Bareiss algorithm](https://en.wikipedia.org/wiki/Bareiss_algorithm) — Wikipedia | Fraction-free elimination with exact divisions (Bareiss, Mathematics of Computation, 1968) |
| Deeper | [The Suan shu shu and the Nine Chapters on the Mathematical Art: A Comparison](https://old.maa.org/sites/default/files/images/upload_library/46/HOMSIGMAA/2021-Megan%20Ferguson.pdf) — Megan Ferguson, Adelphi University, 2021 (MAA HOMSIGMAA) | Quotes Martzloff: negative numbers are never found in the statements of problems |
| Scholar | [How Ordinary Elimination Became Gaussian Elimination](https://arxiv.org/pdf/0907.2397) — Joseph F. Grcar, arXiv preprint | How the method was done in chapter 8, and how it came to carry Gauss's name |
| Scholar | [The Chinese Roots of Linear Algebra (review)](https://arxiv.org/pdf/1104.2282) — Joseph F. Grcar, arXiv | A review of Hart's thesis by the author of the paper above; the counting board as an ancient "spreadsheet" |
| Scholar | [Rectangular Arrays](https://academic.oup.com/book/52966/chapter/421961670) — Shen Kangshen, J. N. Crossley and A. W.-C. Lun, *The Nine Chapters on the Mathematical Art: Companion and Commentary*, OUP 1999 (chapter page) | The standard English translation of chapter 8 with Liu Hui's commentary (paywalled; abstract free) |
| Scholar | [Nine Chapters on the Mathematical Art, Vols 7–9](https://sourcelibrary.org/book/nine-chapters-on-the-mathematical-art-vols-7-9) — Source Library: *Siku Quanshu* edition (1773), scanned by Zhejiang University Library | Chinese text of chapter 8, "Rectangular Arrays", from p. 43. The English shown alongside is a machine translation, so do not cite it |
| Scholar | [Alan Turing and the origins of modern Gaussian elimination](https://arbor.revistas.csic.es/index.php/arbor/article/download/1886/2073?inline=1) — Froilán M. Dopico, Arbor 189 (764), 2013 | Turing's 1948 paper, the name LU, the condition number, partial pivoting and the growth factor |
| Scholar | [John von Neumann's Analysis of Gaussian Elimination and the Origins of Modern Numerical Analysis](https://epubs.siam.org/doi/10.1137/080734716) — Joseph F. Grcar, SIAM Review 53(4), 2011, 607–682 | Why von Neumann and Goldstine's 1947 paper is called the first modern paper in numerical analysis |
| Scholar | [The Chinese Rod Numeral Legacy and its Impact on Mathematics](https://sms.math.nus.edu.sg/smsmedley/Vol-15-2/The%20Chinese%20rod%20numeral%20legacy%20and%20its%20impact%20on%20mathematics(Lam%20Lay%20Yong).pdf) — Lam Lay Yong, presidential address, Singapore Mathematical Society, 1987 | Two sets of rod notations, alternating by place; a horizontal rod for five |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
