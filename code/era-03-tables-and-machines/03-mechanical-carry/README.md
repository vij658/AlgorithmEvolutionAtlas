# The Carry, Mechanized: the program

*Era 3 · topic 3 · 1623–1694* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/03-mechanical-carry/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/03-mechanical-carry/mechanical-carry.html) · [All era 3 programs](../README.md)

## How it works

```text
A wheel with ten positions holds one digit. Turning it past 9 back to 0 must turn the next wheel by one: the carry.
In Schickard's design a single tooth on each wheel pushes the next one, so a long chain of carries (999,999 + 1)
makes every wheel turn at once, driven by the hand on the first. Pascal's sautoir is a weighted lever lifted as a
wheel turns and dropped when it passes 9, so each carry is delivered by gravity, one wheel after another. Pascal's
wheels turn only one way, so the machine adds; to subtract, enter the nines' complement of the first number,
add the second, and read the complement of the result: C(C(a) + b) = a - b, where C(x) = 999...9 - x.
Leibniz's stepped drum has nine teeth of increasing length; setting a digit d engages d teeth, so one turn of the
crank adds d. A carriage shifts the setting one place for each digit of the multiplier, so multiplying by 8,912
takes 8 + 9 + 1 + 2 = 20 turns and 3 shifts, not 8,912 additions.
```

## What the program does

```text
1. Simulates a six-wheel adding machine: counts carries and the longest chain of carries for counting up and for
   adding columns of figures.
2. Checks subtraction by nines' complements on 100,000 random pairs.
3. Simulates Leibniz's stepped drum: crank turns and shifts for multiplication and division, against repeated
   addition.
4. Full circle: the longest carry chain in random 64-bit binary additions, as in a processor's adder.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java MechanicalCarry.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Early Mechanical Computers](https://cspages.ucalgary.ca/~tam/2025/409F/notes/early_mechanical/early_mechanical_part1_6_per_page.pdf) — James Tam, CPSC 409 (history of computing), University of Calgary | Schickard's single-tooth carry, Pascal's falling weights, Leibniz's stepped drum and its manual carries |
| Start | [Pascal's calculator](https://en.wikipedia.org/wiki/Pascaline) — Wikipedia | The sautoir, nines' complement subtraction, the 50 prototypes and the nine survivors |
| Start | [Blaise Pascal Invents a Calculator: The Pascaline](https://historyofinformation.com/detail.php?id=382) — Jeremy Norman, History of Information | The 1645 pamphlet and the 1652 machine in Paris |
| Start | [Wilhelm Schickard](https://mathshistory.st-andrews.ac.uk/SH/schickard_sh.pdf) — MacTutor (illustrated poster, unsigned) | The letter to Kepler, the fire and the reconstruction |
| Deeper | [Stepped reckoner](https://en.wikipedia.org/wiki/Stepped_reckoner) — Wikipedia | The Leibniz wheel, the shifting carriage and the carry flaw |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
