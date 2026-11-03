# MapReduce: the program

*Era 8 · topic 11 · 2004* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/11-mapreduce/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/11-mapreduce/mapreduce.html) · [All era 8 programs](../README.md)

## How it works

```text
The programmer writes two functions. map(record) emits (key, value) pairs; reduce(key, all values for that key)
combines them. For counting words: map emits (word, 1) for each word of its piece of text; reduce adds up the 1s.
The library does the rest. It cuts the input into M pieces and runs a map task on each, on whichever machine is
free; each map task sorts its output into R parts by hash(key) mod R and keeps them on its own disk. Then R reduce
tasks each fetch their part from every map task, group by key, and write the results to a shared file system.
Because map and reduce are deterministic and change nothing else, any task can be run again with the same
result. So when a machine dies, the master simply runs its tasks again elsewhere, including finished map tasks,
whose output was on the dead machine's disk. And when the job is nearly done, the master starts backup copies of
the tasks still running; whichever copy finishes first counts, so one slow machine cannot hold up the whole job.
```

## What the program does

```text
1. Counts the words of this book's field notes (corpus.txt) with 40 map tasks and 8 reduce tasks on a simulated
   cluster of 10 machines, and checks the result against a plain count.
2. The same job when a machine dies halfway through the map phase; when one machine runs 5 times slower; and the
   slow machine again with backup tasks. Time is simulated: a task's duration is its amount of data divided by
   its machine's speed. The counts are checked to be identical every time.
3. PageRank (topic 7) written as a map and a reduce, run for 10 rounds on topic 7's 8-page web.
4. A smaller job (12 map tasks, 3 reduce tasks, 6 machines) whose schedules are printed for the book's widget.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java MapReduce.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [MIT 6.5840, Lecture 1: Introduction](https://pdos.csail.mit.edu/6.824/notes/l01.txt) — F. Kaashoek, R. Morris (2026), lecture notes | MapReduce as the first example of a distributed system |
| Deeper | [MapReduce](https://en.wikipedia.org/wiki/MapReduce) — Wikipedia | Origins, Hadoop, criticism and decline |
| Scholar | [MapReduce: Simplified Data Processing on Large Clusters](https://courses.cs.cornell.edu/cs5410/2008fa/Readings/mapreduce-osdi04.pdf) — J. Dean, S. Ghemawat, OSDI (2004), on a Cornell course page | The model, the implementation and the measurements |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
