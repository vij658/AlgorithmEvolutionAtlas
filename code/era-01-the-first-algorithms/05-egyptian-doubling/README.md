# Egyptian Doubling: the program

*Era 1 · topic 5 · c. 1550 BCE* · Book page: [GitHub edition](../../../book/era-01-the-first-algorithms/05-egyptian-doubling/README.md) · [interactive edition](../../../book/era-01-the-first-algorithms/05-egyptian-doubling/egyptian-doubling.html) · [All era 1 programs](../README.md)

## How it works

```text
To multiply a by b with no times table, write two columns: 1 and b, then keep doubling both (2 and 2b, 4 and 4b,
...) while the left column stays at most a. Tick the rows whose left numbers add up to a, and add their right
numbers. For 41 x 59: rows 1, 8 and 32 make 41, so the answer is 59 + 472 + 1888 = 2419. Only two skills are
needed, doubling and adding, and about log2(a) rows. The ticked rows are the binary digits of a, though the
scribes had no idea of base 2. Replace "add" by "multiply" and "double" by "square", and the same table computes
powers: square-and-multiply, the method behind RSA.
```

## What the program does

```text
1. Multiplies by doubling, printing the table for the papyrus-style example 41 x 59, and checks the method against
   ordinary multiplication on 500,000 random pairs, counting doublings and additions.
2. Divides by doubling the divisor, as the scribes did.
3. Runs the same algorithm on other operations (Stepanov's generic power): multiplication from addition,
   powers from multiplication, Fibonacci numbers from 2 x 2 matrices, and RSA decryption with modular powers.
4. Finds the shortest addition chains for every number up to 128 and counts where doubling-and-adding is not the
   shortest way (the first is 15).
Every printed line starts with a tag that the book's page builder reads. Random inputs use fixed seeds.
```

## Run it

```
java EgyptianDoubling.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Russian Multiplication](https://www.youtube.com/watch?v=HJ_PP5rqLg0) — Numberphile (Johnny Ball) | Halving and doubling, and why it is binary |
| Start | [How Ancient Egyptians Multiplied Numbers Quickly](https://www.youtube.com/watch?v=qHXsKyVSPOU) — MindYourDecisions (Presh Talwalkar) | The Egyptian method, its "Russian peasant" form, and why it works |
| Start | [Early Mathematics: A Short Introduction](https://www.youtube.com/watch?v=ojvdPjMhnKI) — Gresham College, Robin Wilson | The Rhind papyrus, doubling and halving, unit fractions |
| Start | [Mathematics in Egyptian Papyri](https://mathshistory.st-andrews.ac.uk/HistTopics/Egyptian_papyri/) — MacTutor | 41 × 59 worked by doubling, plus the Rhind and Moscow problems |
| Deeper | [Four Algorithmic Journeys Part 1: Spoils of the Egyptians](https://www.youtube.com/playlist?list=PLHxtyCq_WDLV5N5zUCBCDC2WqF1VBDGg1) — Alexander Stepanov (A9), lecture playlist | From Ahmes's 41 × 59 to the generic power algorithm. Lecture notes (PDF) |
| Deeper | [From Mathematics to Generic Programming: The First Algorithm](https://www.informit.com/articles/article.aspx?p=2264460) — Stepanov and Rose (book excerpt) | Ahmes's algorithm and why it relies on associativity |
| Deeper | [Fast multiplication / exponentiation](https://www.cs.uaf.edu/2013/spring/cs463/lecture/02_13_multiplication.html) — University of Alaska Fairbanks, CS 463 notes | "Replacing + with * gives the fast exponentiation by squaring trick", and why RSA needs it |
| Scholar | [Rhind Mathematical Papyrus, EA10057](https://www.britishmuseum.org/collection/object/Y_EA10057) — British Museum | Catalogue records of both sections |
| Scholar | [Learn maths like an Egyptian](https://www.britishmuseum.org/blog/learn-maths-egyptian-secrets-rhind-mathematical-papyrus) — British Museum blog (curator, 2025) | The papyrus as Ahmose's copy of an older original |
| Scholar | [Egyptian multiplication and some of its ramifications](https://arxiv.org/html/1901.10961) — M. H. van Emden, arXiv | From the binary expansion to exponentiation, division and logarithms |
| Scholar | [On the history of the square-and-multiply algorithm](https://arxiv.org/html/2606.00958) — Aydin et al., arXiv (2026 preprint) | From Pingala (c. 200 BCE) to al-Kashi (1427). It does not cover Egypt |

Every link was opened before it was listed. More, with certainty labels: [Era 1 reference catalog](../../../book/era-01-the-first-algorithms/reference-catalog.md).
