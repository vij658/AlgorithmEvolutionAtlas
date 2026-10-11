# Frequency Analysis: the program

*Era 2 · topic 7 · 9th century CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/07-frequency-analysis/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/07-frequency-analysis/frequency-analysis.html) · [All era 2 programs](../README.md)

## How it works

```text
A substitution cipher replaces each letter by another, always the same one. There are 26! ways to do it in
English, far too many to try. But the cipher cannot hide how often each sign appears. Al-Kindi's method: take a
fairly long plain text in the same language and count its letters; count the signs of the secret message; rank
both lists and pair them, most common with most common. For a message too short for the counts to settle, he says,
look at which letters keep company with which (his "qualitative" method). Done by machine, that becomes a search
that swaps pairs of letters while the decryption's letter pairs grow more like the language's.
```

## What the program does

```text
1. Counts the letters of a reference sample of English (written for this program) and ranks them.
2. Encrypts a different English message with random substitution keys, and breaks it two ways: ranking alone
   (al-Kindi's first method) and ranking followed by a search on letter pairs (his second method, mechanized),
   for messages from 50 letters to the whole message, averaged over 20 keys per length.
3. Counts the keys: 26! of them.
4. Measures Friedman's index of coincidence (1922) for the plain text, the substitution cipher, a polyalphabetic
   (Vigenere) cipher and a one-time pad, and finds the Vigenere key length from it.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java FrequencyAnalysis.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The Black Chamber: cracking the substitution cipher](https://simonsingh.net/The_Black_Chamber/crackingsubstitution.html) — Simon Singh | Plain explanation of frequency analysis and al-Kindi's role, with the 1987 rediscovery claim |
| Start | [Arab origins of cryptology](https://muslimheritage.com/arab-origins-of-cryptology/) — Muslim Heritage, summary of a talk by Mohammed I. Al-Suwaiyel (2018) | The treatise's title and date, the 1979 manuscript search, and the later Arab cryptologists |
| Start | [Frequency analysis](https://en.wikipedia.org/wiki/Frequency_analysis) — Wikipedia | The method, al-Kindi, the Qur'an hypothesis, and the European sequel |
| Deeper | [Classical Cryptography: Shift Cipher and Substitution Cipher](https://www.cs.purdue.edu/homes/ninghui/courses/Fall05/lectures/355_Fall05_lect02.pdf) — CS 355 Introduction to Cryptography, lecture 2, Fall 2005 (Purdue computer science site) | University slides that place al-Kindi's frequency analysis against the substitution cipher |
| Deeper | [Chapter 2 quotes](https://sites.wcsu.edu/mbxml/html/section-24.html) — Charles F. Rocca Jr., *Cryptology Through History and Inquiry*, Appendix D (WCSU site) | An English excerpt of al-Kindi's own instructions, cited to vol. 1, pp. 121–123 of the book's reference [12] |
| Deeper | [Al-Kindi](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Kindi/) — MacTutor | Life, the House of Wisdom, and his works on Indian numbers. Silent on cryptography |
| Deeper | [Index of coincidence](https://en.wikipedia.org/wiki/Index_of_coincidence) — Wikipedia | Invented by William F. Friedman (1922); about 0.067 for English, 1/26 for uniform text; finds the key length of a Vigenère cipher |
| Scholar | [Letter counting: A stem cell for cryptology, quantitative linguistics, and statistics](https://benjamins.com/catalog/hl.40.3.01yca) — Bernard Ycart, *Historiographia Linguistica* 40(3) (2013), 303–330 | The long history of letter counting, from cryptology to Markov. Cites the al-Kindi edition and Al-Kadi (1992) |
| Scholar | [New books: *Al-Kindi's Treatise on Cryptanalysis*](https://iacr.org/newsletter/v20n3/newbooks.html) — IACR Newsletter 20(3) | Describes the Arabic–English edition (Mrayati, Meer Alam, at-Tayyan; KFCRIS and KACST), whose Chapter 3 is the translation, with the Arabic alongside |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
