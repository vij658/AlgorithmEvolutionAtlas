# Simulated Annealing: the program

*Era 7 · topic 4 · 1983–1985* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/04-simulated-annealing/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/04-simulated-annealing/simulated-annealing.html) · [All era 7 programs](../README.md)

## How it works

```text
To shorten a travelling salesman's tour, try a small change: reverse one stretch of the tour. Iterative
improvement keeps a change only if the tour gets shorter, and soon stops at a tour that no single change can
improve, often far from the best. Annealing borrows the Metropolis rule from the physics of cooling metal: a change
that lengthens the tour by d is still accepted, with probability exp(-d / T). At a high "temperature" T nearly
every change is accepted and the tour wanders; as T is lowered slowly, worse changes are accepted more and more
rarely, and the tour settles into a deep valley rather than the first hollow it finds. Cooling fast is
"quenching" and gives worse tours; cooling slowly takes longer and gives better ones.
```

## What the program does

```text
1. Tours of 12 cities, where the best tour can be found exactly (Held and Karp's method, a dynamic programme; Era 5):
   how often iterative improvement and annealing find it.
2. Tours of 200 cities: a random tour, iterative improvement, and annealing.
3. The cooling rate: tour length and work for slower and slower cooling.
4. One annealing run, temperature by temperature: the share of changes accepted.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java SimulatedAnnealing.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Simulated Annealing: The Most Metal Algorithm Ever](https://rubyevents.org/talks/simulated-annealing-the-most-metal-algorithm-ever) — Chris Bloom, RubyConf 2022 (28 minutes) | The metallurgy analogy, a travelling-salesperson example and a real scheduling use |
| Start | [Simulated annealing](https://en.wikipedia.org/wiki/Simulated_annealing) — Wikipedia | The acceptance rule, the schedule, and who invented it when |
| Deeper | [Lecture 10: simulated annealing](https://ocw.mit.edu/courses/ids-338j-multidisciplinary-system-design-optimization-spring-2010/resources/mitesd_77s10_lec10/) — MIT OpenCourseWare, O. de Weck and K. Willcox (2010) | Lecture notes on annealing as an engineering design tool |
| Scholar | [Optimization by Simulated Annealing](https://zhanggroup.org/teaching/literature/Kirkpatrick_Annealing_Science_1983.pdf) — S. Kirkpatrick, C. D. Gelatt, M. P. Vecchi, *Science* (1983), on a research group's teaching page | The analogy, the schedule and the chip-design results |
| Scholar | [Thermodynamical Approach to the Traveling Salesman Problem](https://mk.bcgsc.ca/papers/cerny-travelingsalesman.pdf) — V. Černý, *JOTA* (1985), on a BC Cancer Genome Sciences Centre page | The independent discovery, with worked examples |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
