# Genome Assembly with de Bruijn Graphs: the program

*Era 8 · topic 9 · 1995–2001* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/09-genome-assembly/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/09-genome-assembly/genome-assembly.html) · [All era 8 programs](../README.md)

## How it works

```text
A sequencer reads only short pieces ("reads") of a long genome, from many copies cut at random places. Cut every
read into all its words of k letters (k-mers). Make a graph whose points are the words of k - 1 letters and draw
one arrow for each k-mer, from its first k - 1 letters to its last k - 1 letters. Walking the genome from end to
end crosses every arrow once, so the genome is a path that uses every arrow exactly once: an Eulerian path.
Euler (Era 3) showed when such a path exists (every point has as many arrows in as out, except the two ends),
and Hierholzer's method finds one in time proportional to the number of arrows. The older approach, one point per
read and a link for each overlap, needs a path that visits every point once, a Hamiltonian path, for which no
fast method is known.
What goes wrong: a stretch the reads missed breaks the path into pieces ("contigs"); a repeat longer than k makes
points where the path can go more than one way, so several genomes fit the reads; a misread letter adds k false
words, but each false word is seen only once or twice while true words are seen many times, so rare words can be
thrown away first.
```

## What the program does

```text
1. A random genome of 20,000 letters, 6,000 error-free reads of 100 letters (two of them at the genome's two ends,
   the rest at random places): the graph for k = 31, Euler's degree rule, and the genome rebuilt exactly by
   Hierholzer's method.
2. Lower coverage: how many contigs when the reads leave gaps.
3. A repeat: the same 300 letters at three places; how many different genomes fit, and which.
4. Reads with 1% misread letters: the k-mer counts, the threshold, and the contigs before and after it.
5. A 32-letter genome for the book's widget, for k = 3 to 8: how many genomes fit its words.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java GenomeAssembly.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Sequence assembly](https://en.wikipedia.org/wiki/Sequence_assembly) — Wikipedia | Shotgun reads, the two approaches, and the repeat limit |
| Start | [Constructing a De Bruijn Graph](https://rosalind.info/problems/dbru) — Rosalind | Build one yourself |
| Scholar | [A New Algorithm for DNA Sequence Assembly](https://cs.brown.edu/courses/csci1820/spring-2022/resources/Idury_Waterman_1995.pdf) — R. Idury, M. Waterman, *J. Comput. Biol.* (1995), on a Brown course page | The k-tuple graph and its walk |
| Scholar | [An Eulerian path approach to DNA fragment assembly](https://pmc.ncbi.nlm.nih.gov/articles/PMC55524) — P. Pevzner, H. Tang, M. Waterman, *PNAS* (2001) | Hamiltonian against Eulerian, and EULER's results |
| Scholar | [Velvet: Algorithms for de novo short read assembly using de Bruijn graphs](https://genome.cshlp.org/content/18/5/821) — D. Zerbino, E. Birney, *Genome Research* (2008) | The de Bruijn method for short reads |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
