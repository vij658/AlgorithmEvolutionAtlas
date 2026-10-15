# The Relational Model of Data: the program

*Era 6 · topic 6 · 1970* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/06-relational-model/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/06-relational-model/relational-model.html) · [All era 6 programs](../README.md)

## How it works

```text
The databases of the 1960s stored records in trees and chains, and a program found its data by walking them:
to the supplier, then down to the parts that supplier sends. A question that ran against the grain of the tree
("who sends part 42?") meant walking all of it, and reorganizing the tree broke the programs that walked it.
Codd proposed that a program should see only relations: tables of rows, each row a tuple of values, with no order
and no pointers. Questions are asked with a few operations on whole tables:
    restriction  keep the rows that satisfy a condition
    projection   keep some columns, drop duplicate rows
    join         combine rows of two tables that agree on a column
How the rows are stored, sorted or indexed is the system's business, and may change without changing a question.
Nested records are put in "normal form" by copying each parent's key into its children, giving flat tables.
```

## What the program does

```text
1. A supplier-and-part database stored as a tree, and two questions: one with the grain, one against it.
2. The same data as relations: the same two questions, written once, with and without an index.
3. A join of three tables by three methods (nested loops, hashing, sorting): the same answer, different work.
4. Normal form: nested employee records flattened into four tables, and rebuilt from them exactly.
5. One fact in one place: a supplier's city stored in every shipment row against stored once.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Relational.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The relational database](https://www.ibm.com/history/relational-database) — IBM History | The idea, System R, SQL and DB2, from the company where it began |
| Start | [The History of SQL](https://learnsql.com/blog/history-of-sql/) — Agnieszka Kozubek-Krycuń, LearnSQL (2020) | From SEQUEL to SQL |
| Deeper | [Edgar F. Codd](https://www.ibm.com/es-es/history/edgar-codd) — IBM History | The life of the man behind the model |
| Scholar | [A Relational Model of Data for Large Shared Data Banks](https://cs-people.bu.edu/mathan/reading-groups/papers-classics/codd.pdf) — E. F. Codd, *Communications of the ACM* 13(6): 377–387 (1970), on a Boston University page | The eleven-page paper |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
