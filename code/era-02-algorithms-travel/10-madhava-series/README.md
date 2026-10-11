# Madhava's Series for Pi: the program

*Era 2 · topic 10 · c. 1400 CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/10-madhava-series/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/10-madhava-series/madhava-series.html) · [All era 2 programs](../README.md)

## How it works

```text
pi/4 = 1 - 1/3 + 1/5 - 1/7 + ...  An infinite sum, with no square roots at all. By itself it is hopeless: the
error after n terms is about 1/(4n), so each new digit costs ten times as many terms. Madhava's improvement: stop
after n terms and add one correction that estimates everything left out. The Kerala texts give three, each better:
  R = 1/(4n),   R = n/(4n^2 + 1),   R = (n^2 + 1)/(4n^3 + 5n),
added with the sign of the first term left out. A second series converges fast on its own:
  pi = sqrt(12) (1 - 1/(3 x 3) + 1/(5 x 3^2) - 1/(7 x 3^3) + ...).
```

## What the program does

```text
1. Counts how many terms of the plain series give 1 to 7 correct decimals.
2. Applies the three end corrections after 5, 10, 20 and 50 terms, in exact decimal arithmetic.
3. Sums 21 terms of the sqrt(12) series, against MacTutor's 3.14159265359.
4. Doubles Archimedes' polygons (Era 1, topic 8) until they agree to 11 decimals, counting the square roots.
5. Full circle: the Chudnovsky series (1988), the series behind modern record computations, to 1,000 digits,
   checked against an arctangent formula.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java MadhavaSeries.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Madhava of Sangamagrama](https://mathshistory.st-andrews.ac.uk/Biographies/Madhava/) — MacTutor | The series, the √12 form, the correction terms, and how his lost work is known |
| Start | [Indians predated Newton 'discovery' by 250 years](https://www.manchester.ac.uk/about/news/indians-predated-newton-discovery-by-250-years/) — University of Manchester press release (13 Aug 2007) | The transmission claim in its strongest public form, including the "circumstantial evidence" wording |
| Start | [Madhava and the Uninfluential Discovery](https://3quarksdaily.com/?p=143638) — Thomas Manuel, 3 Quarks Daily (2018) | The skeptical side, quoting Plofker's review |
| Start | [Chudnovsky algorithm](https://en.wikipedia.org/wiki/Chudnovsky_algorithm) — Wikipedia | Published by the Chudnovsky brothers in 1988; about 14 digits per term; record computations up to 314 trillion digits (18 November 2025, with y-cruncher) |
| Deeper | [Mathematics in India: From Vedic Period to Modern Times](https://nptel.ac.in/courses/111101080) — NPTEL video course, IIT Bombay (K. Ramasubramanian, M. D. Srinivas, M. S. Sriram) | Lectures 30–31, "Kerala School of Astronomy and Development of Calculus", and proofs from the *Yuktibhasa* (syllabus) |
| Deeper | [The History and Historiography of the Discovery of Calculus in India](https://mathunion.org/fileadmin/IMU/ICM2022/Presentation-slides/218-Krishnamurthi%20Ramasubramanian.pdf) — K. Ramasubramanian, invited talk, ICM 2022 (slides) | The series, the end-correction, and the Kerala lineage, Madhava to Jyesthadeva |
| Deeper | [Mathematics in India (review)](https://www.dam.brown.edu/people/mumford/beyond/papers/2010a--PlofkerReview-AMS.pdf) — David Mumford, *Notices of the AMS* 57(3) (2010) | A mathematician's account of the Kerala power series and the *Yuktibhasa* proofs |
| Deeper | [Ideas of Calculus in Islam and India](https://maa.org/node/95254) — Victor J. Katz, *Mathematics Magazine* 68(3):163–174 (1995), MAA | The classic survey of the Indian power series for sine, cosine and arctangent |
| Scholar | [On Mādhava and his correction terms for the Mādhava–Leibniz series for π](https://arxiv.org/abs/2405.11134) — V. N. Krishnachandran, arXiv (2024) | The three correction terms examined critically, and reconstructions of how they were found |
| Scholar | [Ganita-Yukti-Bhāṣā (Rationales in Mathematical Astronomy) of Jyeṣṭhadeva](https://link.springer.com/book/9781848820722) — K. V. Sarma (trans.), K. Ramasubramanian, M. D. Srinivas, M. S. Sriram; Springer / Hindustan Book Agency (2008), 2 vols. | The Malayalam text (c. 1530) that gives the derivations, in English translation with notes |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
