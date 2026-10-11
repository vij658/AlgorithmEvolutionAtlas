# Algorism and Al-Jabr: the program

*Era 2 · topic 6 · c. 820–830 CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/06-algorism-and-al-jabr/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/06-algorism-and-al-jabr/algorism-and-al-jabr.html) · [All era 2 programs](../README.md)

## How it works

```text
Al-Khwarizmi's algebra has no symbols, only words, and still it is an algorithm that works for any numbers.
1. Al-jabr ("restoring"): a subtracted term is moved to the other side, where it is added.
2. Al-muqabala ("balancing"): like terms on both sides cancel, leaving each kind on one side only.
3. Divide by the number of squares, so that one square remains.
4. The equation is now one of six types, each with a fixed recipe:
     squares equal roots; squares equal numbers; roots equal numbers;
     squares and roots equal numbers (x^2 + 10x = 39: halve the roots, 5; square, 25; add, 64; root, 8;
     take away half the roots: x = 3);
     squares and numbers equal roots (x^2 + 21 = 10x: half the roots plus or minus the root of
     25 - 21: x = 7 or 3);
     roots and numbers equal squares (3x + 4 = x^2: half the roots plus the root of 2 1/4 + 4: x = 4).
Only positive answers count; a type with no positive answer is "impossible".
His other book taught the Indian numerals and written, step-by-step arithmetic with them, including square roots.
Latin copies began "Dixit Algorizmi", and his name became the word "algorithm".
```

## What the program does

```text
1. Solves the three worked examples of the mixed types by the recipes, step by step.
2. Reduces 100,000 random equations, with subtracted terms on both sides, by al-jabr and al-muqabala, sorts them
   into the six types, solves them by the recipes, and checks every answer against the quadratic formula.
3. Takes a square root digit by digit, as written arithmetic does, against the Babylonian averaging of Era 1.
4. Shows what the recipe meets in floating point: Forsythe's example, where one root loses every digit, and the
   rearranged formula that keeps them.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java AlKhwarizmi.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Who invented algebra?](https://www.gresham.ac.uk/node/11558) — Gresham College, Robin Wilson, 5 October 2005 (video and transcript) | Islamic mathematics from 750 to 1400. Covers al-Khwarizmi at the House of Wisdom, the origin of "algebra", and x² + 10x = 39 solved by a geometric "completing the square" |
| Start | [Al-Khwarizmi's Completing the Square Activity](https://bulldog2.redlands.edu/fac/Beery/math115/m115_activ_complsq.htm) — Math 115 course page on the University of Redlands site. Activity by J. Beery, C. Dolezal, A. Sauk and L. Shuey, from *Historical Modules* (MAA, 2003) | Classroom worksheet: translate one of his problems into an equation, then complete the square by drawing it |
| Start | [Completing the Square](https://old.maa.org/node/116292) — Barnabas Hughes, MAA *Convergence* | The geometric method for x² + 10x = 39, with practice equations |
| Start | [Urgench](https://en.wikipedia.org/wiki/Urgench) — Wikipedia | Capital of the Xorazm region, with a large statue of al-Khwarizmi |
| Deeper | [Al-Khwarizmi](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Khwarizmi/) — MacTutor | Life, the six equation types, completing the square, and the debate over his sources |
| Deeper | [Pitfalls in Computation, or Why a Math Book Isn't Enough](https://apps.dtic.mil/sti/pdfs/AD0699897.pdf) — George E. Forsythe, Stanford CS Technical Report 147, January 1970 (DTIC) | The quadratic formula gives one root "100 percent wrong" by catastrophic cancellation; alternative formulas avoid it |
| Scholar | [Al-Khwārizmī](https://mathshistory.st-andrews.ac.uk/DSB/Al-Khwarizmi.pdf) — G. J. Toomer, *Dictionary of Scientific Biography* (reprint hosted by MacTutor) | Dating of each work, the arithmetic's content, and the Greek–Hindu–Hebrew sources question. The OCR is garbled in places |
| Scholar | [Al-Khwarizmi resource page](https://www.jphogendijk.nl/khwarizmi.html) — Jan Hogendijk (Utrecht University address), 2022 | Editions, translations and manuscripts of every work, with links to digitized copies |
| Scholar | [The Toledan *Regule* (*Liber Alchorismi*, part II): A Twelfth-century Arithmetical Miscellany](https://sciamvs.org/files/SCIAMVS_08_141-231_Burnett_Zhao_Lampey.pdf) — Charles Burnett, Ji-Wei Zhao, Kurt Lampe, *SCIAMVS* 8 (2007), 141–231 | How the Latin algorisms grew out of his lost arithmetic. Treats *Dixit Algorizmi* as one Latin version among several |
| Scholar | [The Algebra of Mohammed ben Musa](https://archive.org/details/algebraofmohamme00khuwuoft/algebraofmohamme00khuwuoft) — Frederic Rosen (ed. and trans.), London: Oriental Translation Fund, 1831. Internet Archive (University of Toronto copy) | Rosen's edition and English translation of the algebra |
| Scholar | [Algorithms in modern mathematics and computer science: proceedings, Urgench, Uzbek SSR, September 16–22, 1979](https://ci.nii.ac.jp/ncid/BA02973768) — A. P. Ershov and D. E. Knuth (eds.), LNCS 122, Springer, 1981 (CiNii record) | The symposium on algorithms held in Urgench |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
