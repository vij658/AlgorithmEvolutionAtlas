# Al-Kashi's Pi: the program

*Era 2 · topic 11 · 1424 CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/11-al-kashi-pi/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/11-al-kashi-pi/al-kashi-pi.html) · [All era 2 programs](../README.md)

## How it works

```text
Archimedes' method, with an accountant's discipline. First the target: for a circle 600,000 times as wide as the
Earth, the computed circumference must be off by less than the breadth of a horse's hair; the Dictionary of
Scientific Biography converts this to an error in pi of at most 0.5 x 10^-17. Then the plan: start from a hexagon in
a circle of radius 60 and double the sides until the polygons are close enough, which happens at 3 x 2^28 =
805,306,368 sides. Each doubling is one square root, done in base 60:
  the chord of 180 degrees minus half the arc, squared, is 60 x (120 + the chord of 180 minus the arc),
starting from the chord of 60 degrees, which is the radius. The side of the polygon follows by Pythagoras, and the
circumscribed side by proportion. Roots were checked by squaring and by casting out 59 (base 60's casting out nines).
```

## What the program does

```text
1. Finds how many doublings the target needs, for inscribed, circumscribed and combined polygons.
2. Runs al-Kashi's 28 square roots in base 60 with exact whole numbers, checking each root by casting out 59, and
   gives 2 pi in sexagesimal and in decimal, against the true value and the DSB's 6.2831853071795865. The DSB says
   he took the arithmetic mean of the inscribed and circumscribed perimeters; the program does the same.
3. Computes sin 1 degree by his iteration for the cubic of the trisection, from sin 3 degrees (Ptolemy's 6-degree
   chord, topic 2), and tests his sexagesimal value 1;2,49,43,11,14,44,16,26,17 (radius 60, as the DSB gives it)
   and the decimal 0.017452406437283571 printed beside it.
4. Full circle: compares his 2 pi with the 2 pi of a computer's 64-bit floating point.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java AlKashiPi.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Ghiyath al-Din Jamshid Mas'ud al-Kashi](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Kashi/) — MacTutor | Life, Samarkand, the July 1424 treatise, and the *Key to Arithmetic* (completed 2 March 1427) |
| Start | [Al-Kashi](https://mathshistory.st-andrews.ac.uk/Strick/al-kashi.pdf) — H. K. Strick, trans. J. O'Connor, MacTutor | Short illustrated article: the 805,306,368-sided polygon, sin 1°, and Ulugh Beg |
| Start | [The Scholars of Samarkand](https://muslimheritage.com/the-scholars-of-samarkand/) — Muslim Heritage (2005) | Ulugh Beg's madrasa and observatory, and al-Kashi's place among the Samarkand astronomers |
| Deeper | [π and its computation through the ages](https://gauss.dartmouth.edu/~m56s13/Gourdan2010notes_computing_pi_through_ages.pdf) — Xavier Gourdon and Pascal Sebah (2010), reading on a Dartmouth course server (Math 56, per the URL) | Places al-Kashi (6·2^27 sides, 1424) in a table of polygon computations of π. Gives the more cautious "about 14 correct decimals" |
| Deeper | [Al-Kāshī](https://mathshistory.st-andrews.ac.uk/DSB/Al-Kashi.pdf) — A. P. Youschkevitch and B. A. Rosenfeld, *Dictionary of Scientific Biography* (via MacTutor) | The fullest account opened here: the error target, the polygon, the sexagesimal result, comparisons with earlier and later values |
| Deeper | [al-Kāshī (BEA entry)](https://mathshistory.st-andrews.ac.uk/BEA/al_kashi_bea.pdf) — *Biographical Encyclopedia of Astronomers* (via MacTutor) | Al-Kashi as astronomer: the observatory, the *Zij*, sin 1° to 18 places and π to 16 |
| Deeper | [Um estudo da primeira e segunda parte do tratado da circunferência de Al-Kāshī](https://revistas.uece.br/index.php/BOCEHM/article/download/4964/4374/21743) — K. F. C. Andrade, *Boletim Cearense de Educação e História da Matemática* 8(23):665–676 (2021) | In Portuguese. Works through the recursion from the hexagon (R = 60) and the 28 tables |
| Scholar | [The Introduction of Al-Risāla Al-Muhītīyya: An English Translation](https://webcf.waybackmachine.org/web/20220512123120/https://ijpam.eu/contents/2009-57-6/5/5.pdf) — M. K. Azarian, *Int. J. Pure and Applied Mathematics* 57(6):903–914 (2009), archived copy | Al-Kashi's own statement of purpose, his critique of earlier values and the horse-hair target, in English |
| Scholar | [The Samarkand school in astronomy and mathematics (ca. 1420 CE)](https://www.jphogendijk.nl/samarkand.html) — Jan P. Hogendijk (Utrecht) | Facsimiles of the Istanbul and Mashhad manuscripts of the treatise, plus a bibliography (Luckey 1953; Hogendijk 2009; Azarian) |
| Scholar | [al-Risālah al-Muḥīṭiyyah](https://ismi.mpiwg-berlin.mpg.de/text/499858) — Islamic Scientific Manuscripts Initiative (ISMI), Max Planck Institute for the History of Science | Catalogue of the 9 known manuscript witnesses, with a description of the method |
| Scholar | [Al-Risala al-Muhitiyya (The Treatise on the Circumference). Preliminary report](https://www.jointmathematicsmeetings.org/amsmtgs/2109_abstracts/1035-01-248.pdf) — M. K. Azarian, AMS meeting abstract (received August 2007) | Dating of the autograph to Sha'ban 827 AH (July 1424) |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
