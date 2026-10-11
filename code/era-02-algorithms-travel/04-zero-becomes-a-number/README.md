# Zero Becomes a Number: the program

*Era 2 · topic 4 · 628 CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/04-zero-becomes-a-number/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/04-zero-becomes-a-number/zero-becomes-a-number.html) · [All era 2 programs](../README.md)

## How it works

```text
Place value writes a number as digits whose worth depends on their position. Without a mark for an empty place,
2, 7 could mean 27, 207, 270 or 2700: the reader has to guess. A placeholder fixes the reading; making zero a number
lets it take part in arithmetic. Brahmagupta's rules treat zero alongside "fortunes" and "debts" (positive and
negative numbers): a fortune minus zero is a fortune, zero minus a debt is a fortune, zero times anything is zero,
and so on. One rule, zero divided by zero is zero, was later rejected.
```

## What the program does

```text
1. Measures how ambiguous place value is without zero: in base 10 up to a million, and in base 60 (the
   Babylonian system) up to 60^3, with no mark at all and with a placeholder that is never written at the end.
2. Writes the Gwalior numbers (933, 187, 270, 50) and shows what each would collide with without a zero.
3. Implements Brahmagupta's rules for fortunes, debts and zero, and compares them with modern integer arithmetic
   on every pair from -60 to 60.
4. Shows what Java does with division by zero today: an exception for whole numbers; infinity, minus infinity
   and "not a number" for floating point, with a zero that has a sign.
5. Defines x / 0 = 0, the convention of the Lean and Isabelle proof assistants (and Brahmagupta's answer for 0 / 0),
   and checks which laws of fractions survive it, on every pair of fractions in a grid.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ZeroAsANumber.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Much ado about zero](https://www.gresham.ac.uk/watch-now/much-ado-about-zero) — Gresham College, Robin Wilson, 17 November 2004 (embedded video) | Mathematics of China, India and Central America over a thousand years, ending with "the elusive origins of zero" |
| Start | [Where do mathematical symbols come from?](https://www.gresham.ac.uk/sites/default/files/2021-04-27-1300_HART_Symbols-T.pdf) — Gresham College, Sarah Hart, 27 April 2021 (transcript) | Babylonian placeholder versus zero as a number in Brahmagupta (dated "around 630AD" in the talk) |
| Start | [You Can Visit the World's Oldest Zero at a Temple in India](https://www.smithsonianmag.com/smart-news/you-can-visit-the-worlds-oldest-zero-at-a-temple-in-india-2120286/) — Colin Schultz, *Smithsonian Magazine*, 16 October 2013 | Photo of the Gwalior "270" and the popular "oldest zero" story |
| Start | [The Elusive Origin of Zero](https://www.scientificamerican.com/article/the-elusive-origin-of-zero1/) — Swetz and Zain, *Scientific American* (opinion; undated on the page) | The Southeast Asian challenge to Gwalior: Sambor and the Sumatran stones |
| Deeper | [A history of Zero](https://mathshistory.st-andrews.ac.uk/HistTopics/Zero/) — MacTutor (O'Connor and Robertson) | From Babylonian wedges to Brahmagupta's rules and Gwalior |
| Deeper | [Brahmagupta](https://mathshistory.st-andrews.ac.uk/Biographies/Brahmagupta/) — MacTutor (O'Connor and Robertson) | The rules for fortunes, debts and zero, quoted in translation |
| Deeper | [All for Nought](https://www.ams.org/publicoutreach/feature-column/fcarc-india-zero) — Bill Casselman (UBC), AMS Feature Column, February 2007 | A translation of the Gwalior inscription with its numbers 933, 187, 270 and 50, and why it fixes a date for the zero |
| Deeper | [Mathematical Treasure: The Cambodian Zero](https://old.maa.org/press/periodicals/convergence/mathematical-treasure-the-cambodian-zero) — Frank J. Swetz (Penn State), MAA *Convergence*, 2015 (updated 2024) | Stele K-127, the zero two centuries older than Gwalior |
| Deeper | [1/0 = 0](https://hillelwayne.com/post/divide-by-zero/) — Hillel Wayne (2018, disclaimer added 2024) | Why Lean, Isabelle and Coq can define x/0 = 0 without contradiction |
| Scholar | [The Bakhshālī Manuscript: A Response to the Bodleian Library's Radiocarbon Dating](https://journals.library.ualberta.ca/hssa/index.php/hssa/article/view/22) — Plofker, Keller, Hayashi, Montelle and Wujastyk, *History of Science in South Asia* 5(1) (2017) 134–150 | The specialists' case against reading the earliest folio date as the date of the text |
| Scholar | [Algebra, with Arithmetic and Mensuration, from the Sanscrit of Brahmegupta and Bháscara](https://archive.org/details/algebrawitharith00brahuoft/page/n5/mode/2up) — H. T. Colebrooke (trans.), London: J. Murray, 1817, Internet Archive | The classic English translation of Brahmagupta's arithmetic and algebra, the source of his rules for zero |
| Scholar | [Carbon dating finds Bakhshali manuscript contains oldest recorded origins of the symbol 'zero'](https://www.glam.ox.ac.uk/node/218481) — University of Oxford, Gardens, Libraries and Museums, 14 September 2017 | The original announcement that started the dispute |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
