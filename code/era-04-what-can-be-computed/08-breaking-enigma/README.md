# Breaking Enigma: the program

*Era 4 · topic 8 · 1932–1940* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/08-breaking-enigma/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/08-breaking-enigma/breaking-enigma.html) · [All era 4 programs](../README.md)

## How it works

```text
An Enigma sends each key press through a plugboard (which swaps some pairs of letters), three wired rotors, a
reflector, and back through the rotors and plugboard. The rightmost rotor turns before every letter, and turns the
next one at its notch, so the scrambling changes with every letter. Because of the reflector, the machine's
letter swaps are their own inverse (typing the cipher text gives back the plain text) and no letter is ever
enciphered as itself.
Rejewski's attack (1932-1938): operators sent each message's three-letter key twice. If A, B, ..., F are the
machine's swaps at positions 1 to 6, the first and fourth cipher letters are linked by the product of A and D,
which every day's traffic reveals. The lengths of its cycles come in pairs and do not depend on the plugboard
(the "characteristic"), so a catalogue of characteristics for every rotor order and position points to the
day's setting.
Turing's Bombe (1940): guess a stretch of plain text (a "crib"). For each rotor position, assume a plug partner
for one letter and follow what the crib then forces; a contradiction (one letter plugged to two others) rules the
position out. Positions with no contradiction are "stops", checked by hand.
```

## What the program does

```text
1. Builds the Enigma I with the rotor wirings of 1930 and checks the published test (AAAAA gives BDZGO).
2. Checks that enciphering twice gives back the message, and that no letter goes to itself at any position.
3. Rejewski's characteristic: cycles in pairs for all 105,456 settings, the same with any plugboard; the
   catalogue; and a simulated day's traffic in which the catalogue finds the setting.
4. A Bombe run on a 23-letter crib over all 6 rotor orders and 17,576 positions: the stops, and the plugs deduced.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Enigma.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Cryptanalysis of the Enigma](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Enigma) — Wikipedia | The machine, the doubled indicators, Rejewski's characteristic, Zygalski's sheets and the Bombe |
| Start | [Marian Adam Rejewski](https://mathshistory.st-andrews.ac.uk/Biographies/Rejewski/) — MacTutor | Rejewski's life, from Poznań to the Cipher Bureau and after |
| Start | [Milestone: First Breaking of Enigma Code by the Team of Polish Cipher Bureau, 1932–1939](https://ethw.org/Milestones:First_Breaking_of_Enigma_Code_by_the_Team_of_Polish_Cipher_Bureau%2C_1932-1939) — IEEE History Center, Engineering and Technology History Wiki (dedicated 5 August 2014) | The citation for the bomba |
| Deeper | [Cyclometer](https://en.wikipedia.org/wiki/Cyclometer) — Wikipedia | The catalogue of 105,456 characteristics and why it failed in 1937–38 |
| Deeper | [Bombe](https://en.wikipedia.org/wiki/Bombe) — Wikipedia | Cribs, menus, logical contradictions and the diagonal board |
| Deeper | [The Polish recovery of the Enigma rotor wiring](https://www.cryptocellar.org/enigma/files/rejewski-paper.pdf) — F.L.C., Crypto Cellar (March 2005) | The permutation equations step by step |
| Deeper | [Enigma rotor details](https://en.wikipedia.org/wiki/Enigma_rotor_details) — Wikipedia | The wirings used by the program |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
