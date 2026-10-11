# Era 3 — Tables and Machines (plan)

*1545 to 1890 CE. Topic list in strict order of time. Dates were checked in the reference catalog; the catalog's certainty labels win where they differ.*

> **Field note from the visiting historian.** In the second era, procedures travelled. In this one they are made to run without a thinking person: printed as tables so that nobody has to compute, built into wheels so that nobody has to carry, turned into rules that correct themselves, and at last written as instructions for a machine. Along the way, logic becomes arithmetic and arithmetic becomes binary.

| # | Topic | Working date | Where | What hurt | The step forward | Builds on |
|---|---|---|---|---|---|---|
| 1 | Cardano's cubic | del Ferro c. 1515; Tartaglia 1535; *Ars Magna* 1545; Bombelli 1572 | Bologna, Venice, Milan | Cubic equations had no general method | A substitution that reduces the cubic to a quadratic; rules for square roots of negatives when the formula needs them | al-jabr (Era 2, 6), roots digit by digit (Era 2, 9) |
| 2 | Logarithms | Napier 1614; Briggs 1617, 1624 | Edinburgh, London | Long multiplications for astronomy and navigation | A table that turns multiplication into addition; base 10 built from repeated square roots | Doubling (Era 1, 5), decimal fractions (Era 2, 11) |
| 3 | The carry, mechanized | Schickard 1623; Pascal 1642–1645; Leibniz 1673–1694 | Tübingen, Rouen, Paris, Hanover | Columns of addition and every carry by hand | Wheels of ten with an automatic carry; complements for subtraction; a stepped drum for multiplication | Counting boards (Era 1, 6) |
| 4 | The problem of points | Pascal and Fermat, 1654 | Paris, Toulouse | No fair rule for a game stopped early | Value a position by what can still happen: enumerate, or work backward round by round | Tally and counting (Era 1, 1) |
| 5 | Newton's method | Newton 1669 (printed 1685, 1711); Raphson 1690; Simpson 1740 | Cambridge, London | Formulas stop at degree four; digit-by-digit roots are slow | Follow the tangent line and repeat; the correct digits roughly double | Babylonian square roots (Era 1, 4), Qin's root method (Era 2, 9) |
| 6 | Binary arithmetic | Harriot c. 1601–1605 (unpublished); Caramuel 1670; Leibniz 1679, 1703 | England, Paris, Hanover | Base-ten arithmetic needs memorised tables | Two digits; every operation reduces to "one and one make ten" | Egyptian doubling (Era 1, 5) |
| 7 | The bridges of Königsberg | Euler 1735–1736 (printed 1741); Hierholzer 1873 | St Petersburg | A route question with too many cases to try | Keep only what connects to what, and count: zero or two odd places | — |
| 8 | Least squares, and the lost planet | Ceres 1801; Legendre 1805; Gauss 1809 | Palermo, Paris, Göttingen | More observations than unknowns, and they disagree | Minimize the sum of squared errors; solve the normal equations by elimination | Elimination (Era 2, 1) |
| 9 | Gauss's fast Fourier transform | Gauss 1805 (printed 1866); Cooley and Tukey 1965 | Göttingen | A periodic fit from N observations costs N² products | Split N = N₁ × N₂ and combine small fits: about N log N | Chords and sines (Era 2, 2) |
| 10 | Babbage's difference engine | 1821–1822; No. 2 designed 1847–1849, built 1991 | London | Printed tables full of errors | Constant differences: every entry by additions only, printed by the machine | Logarithm tables (2), the carry (3) |
| 11 | Lovelace's Note G | Menabrea 1842; Lovelace's notes 1843 | London | A machine needs to be told what to do | A calculation as a sequence of operations on numbered stores, with repetition, read from cards | Difference engine (10) |
| 12 | Boole's algebra of logic | 1847, 1854; Shannon 1937 | Lincoln, Cork | Logic as a catalogue of syllogisms | Classes and propositions as symbols, with x² = x: an algebra of 0 and 1 | Binary (6) |
| 13 | Hollerith's tabulator | Patent 1889; the 1890 United States census | New York, Washington | Census tallies took years | One punched card per person, counted by electric circuits and sorted into drawers | Tally marks (Era 1, 1), counting wheels (3) |

## Decisions after the reference catalog

- The era runs from 1545 to 1890, not from 1600 as first proposed: Cardano's cubic sets up why Newton's method is needed, and Hollerith closes the century with machines counting data.
- Logarithms and Napier's bones share topic 2. Stevin's decimal fractions (1585) are left to topic 2's notes; Era 2, topic 11 already covers decimal fractions.
- Binary is dated by Leibniz's publication (1703); Harriot's earlier, unpublished work (1601–1605) is in the topic and labelled as such.
- Least squares (8) comes before Gauss's FFT (9): Ceres was found in 1801, while Gauss's FFT manuscript is from late 1805.
- Topic 9 is named "160 years early": 1805 to Cooley and Tukey's 1965 paper.
- Note G's table could not be read in an opened copy; topic 11's program rebuilds Lovelace's recurrence rather than her exact table.

The [reference catalog](reference-catalog.md) holds the links (every one opened before it was listed) and the evidence for each topic.
