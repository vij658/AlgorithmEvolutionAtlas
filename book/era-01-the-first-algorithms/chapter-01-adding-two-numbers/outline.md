# Chapter 1 outline: "Two numbers, one answer"

**This is the plan, not the chapter.** The text is not written yet. Every historical claim below is backed by the [history fact sheet](history-fact-sheet.md); every number is from the output of [AddingTwoNumbers.java](../../../code/chapter-01-adding-two-numbers/AddingTwoNumbers.java) (see [its output](../../../code/chapter-01-adding-two-numbers/expected-output.txt)). Design background: [design decisions](../../00-about-the-book/design-decisions.md).

**Subtitle:** Why adding has a carry, why the carry became the most fought-over wire in a computer, and where the word "algorithm" came from.

## The chain of needs (shown at the top of the page)

| # | What hurt | The fix | Where in history |
|---|---|---|---|
| 1 | A stick with a thousand notches: too many marks to read or check | One new mark for a full bunch | Notched bones; Egyptian numerals |
| 2 | How many make a bunch? Every trade has its own | The carry as an exchange rate (it is always one bunch) | Uruk bookkeeping; pounds, shillings and pence until 1971 |
| 3 | Piles of identical pebbles don't remember which column they belong to | A board whose position remembers: push, then settle | Salamis tablet; the English Exchequer |
| 4 | The board forgets how it got there, and can't be mailed | Written place value, zero, the pen; the word *algorism* is born | Babylon to India to al-Khwarizmi to Fibonacci to Adam Ries |
| 5 | In the machine, the carry is the slow part | Wait only as long as needed, or look ahead | Pascal, Babbage, von Neumann, Kogge and Stone |

## Opening (draft wording, not final)

> You have been adding numbers since before you could ride a bicycle. It feels like the least interesting thing a computer does.
>
> So here is a test of how well you know it. Take 478 + 359. You write 837, and on the way you write a small 1 above the next column, twice. **Why does the 1 go there?** Not how: you know how. Why that, and not something else? Who decided?
>
> Nobody decided. Every part of the method you were taught, the columns, the tiny 1 above the next column, the zero that holds a place open, was forced on people by something that hurt. The last of those pains is still being fought over today, in the circuits of every processor. This chapter walks that road, one pain at a time, from the first notched bones to the word *algorithm* itself.
>
> The whole book asks one question of every algorithm: **what hurt?** If you can name the pain, you can usually rebuild the fix on your own. That is the test I'll keep setting you.

Then a short "how to read this book" legend: the devices (Pause and try, Wrong turn, Time travel, ⊕, Full circle, Key idea, Prove it) and the four source labels.

## Section 1. Stuck 1: A stick with a thousand notches

- **Evidence.** Bones with rows of notches: Lebombo (29 notches, 44,200–43,000 years old), the Dolní Věstonice wolf bone (about 30,000 years, 55 marks), Ishango. Labelled **conjecture**: nobody knows what they counted. What *is* sure is that a row of marks is what a tally is.
- **The first algorithm in the book:** Tally. For each thing, make one mark. To add two tallies, put the marks together. No carry, no digits. The answer is as long as the question; you need no number words (compare by pairing marks off).
- **Pause and try.** Two herders with sticks of 29 and 31 notches and no word for "twenty-nine": who has more, and what do both flocks look like added together? (Answer: pair the marks; join the sticks.)
- **The pain.** A thousand notches. The eye cannot see "how many" in a long row of identical marks, so it counts, and counting is where mistakes happen. A small figure shows 13 and 14 strokes ungrouped, then grouped in fives. (Source for the legibility claim: tally marks are typically clustered in fives; it does not say when that began, so the chapter will not date it.)
- **Pause and try.** Your stick has a thousand notches and you may invent one new kind of mark. What do you carve? (Answer: a mark for ten notches; then a mark for ten of those; you have reinvented the Egyptian numerals.)
- **Documented payoff.** MacTutor on Egyptian numerals: adding is putting symbols together "but replacing ten copies of a symbol by a single symbol of the next higher value." That sentence is the carry's first appearance in print. Also: 276 needs fifteen symbols (2 + 7 + 6).
- **Wrong turn (the obvious one, not a documented episode):** give every number its own sign. No rule connects the signs, so every pair of numbers needs its own table.
- **⊕** putting heaps together ⊕ one new mark for a full bunch = additive numerals, the carry in embryo.
- **Key idea.** When a row of identical marks gets too long to read, trade a full bunch for one mark of a new kind.
- **Bridge.** That sentence quietly assumed a number: ten. Who said how many make a bunch?

## Section 2. Stuck 2: How many make a bunch?

- **Evidence.** Uruk, about 3350–3000 BC: roughly 85% of the proto-cuneiform tablets are bookkeeping; thirteen numerical systems; different products used different systems (grain rations, barley and emmer wheat on one tablet). Pounds, shillings and pence: librae, solidi and denarii imposed across Western Europe by Charlemagne, adopted in Britain by King Offa in the late 8th century, kept until Decimal Day, Monday 15 February 1971. 12 pence to a shilling, 20 shillings to a pound, 240 pence to the pound.
- **The worked sum.** £3 17s 9d + £2 5s 8d. Pence: 9 + 8 = 17, one bunch of 12 leaves, 5 stay. Shillings: 17 + 5 + 1 = 23, one bunch of 20 leaves, 3 stay. Pounds: 3 + 2 + 1 = 6. Answer: **£6 3s 5d** (printed by the program).
- **The reveal.** The "carry the 1" is a bunch leaving one column and arriving in the next as one unit. It is an *exchange*; the rate can be anything.
- **The rule for any ladder.** For each column from the smallest: total = both digits + what arrived from below; what stays = total mod rate; what moves up = total div rate.
- **Prove it (Java):** `value`, `addColumns`. Checked against `BigInteger` with 100,000 random sums each on rate 2, rate 10, rate 60 and random mixed ladders (up to 40 columns).
- **Pause and try.** 7 yd 2 ft 11 in + 4 yd 1 ft 5 in. (Answer: **12 yd 1 ft 4 in**, program-checked.) A second exercise on the clock: 1 h 45 min 50 s + 2 h 20 min 25 s = **4 h 6 min 15 s**.
- **Pause and try.** Why can't a column ever need to send up a 2? (Answer: the most a column can hold is (rate − 1) + (rate − 1) + 1 = 2·rate − 1, which is less than 2·rate. The program checked every digit pair and incoming carry for every rate from 2 to 100: 676,698 cases, the carry was never more than 1.)
- **Why it matters later.** What one column tells the next is a single yes-or-no. That is what will make the carry possible to hurry up in a machine.
- **⊕** grouping ⊕ a different bunch size in each column = the carry as an exchange rate. **Key idea:** a carry is an exchange, and it is always one bunch.
- **Bridge.** The rule works for any ladder, but doing it means remembering which column each pebble belongs to.

## Section 3. Stuck 3: Piles don't remember their column (the counting board)

- **Evidence.** The Salamis tablet (marble counting board, around 300 BC): pebbles (Latin *calculi*) placed and moved, each counter standing for one unit of a magnitude set by its position. *Calculus* meant "pebble used as a reckoning counter", the root of *calculate*. The English Exchequer: a table covered by a black cloth with hand-wide chequered stripes (hence the name, from *échiquier*), counters for various values, spaces for pounds, shillings and pence, and a person called the "calculator" who placed the counters. The *Dialogus de Scaccario* dates from the late 12th century (author Richard FitzNeal; the exact date is disputed).
- **The board's algorithm: push, then settle.** Push both numbers' counters onto the same columns; nothing is exchanged yet, so every column could be done at the same moment. Then settle: sweep up, trading each full bunch for one counter on the next column. For the worked sum: after pushing, 17 pence, 22 shillings, 5 pounds; after settling, 5 pence, 3 shillings, 6 pounds.
- **Figure:** two panels of the board (after push, after settle) with the bunches of 12 and 20 highlighted and the exchanged counters ringed.
- **The logic.** An exchange never changes what the board is worth, so any order of exchanges that ends with no full bunch left ends at the same board. (Planned test: random-order settling on 20,000 random boards.)
- **Prove it (Java):** `columnSums`, `settle` (and the planned `settleInAnyOrder`).
- **Time-travel scene (reconstructed):** the Exchequer table, a sheriff disputing a total, a calculator who has just swept the counters away. The pain: the board shows an answer and nothing else. The Exchequer issued wooden tally sticks as receipts; they were in use from about 1100 until 1826, and in 1834 the old ones were ordered burned, and the fire spread until most of the building was destroyed. The board is for reckoning, the stick for remembering.
- **Wrong turn (documented):** doing arithmetic in the written Roman numerals. The system was "cumbersome and posed a serious obstacle to calculations"; the Romans reckoned on an abacus of pebble counters instead.
- **⊕** exchange rate ⊕ a board whose lines are the rungs = push, then settle. **Key idea:** make the position remember.
- **Thread planted for section 5:** the push is parallel; the settle is sequential.

## Section 4. Stuck 4: The board forgets (written place value, zero, and the word)

- **Why the board loses.** Working state is destroyed as you go; you cannot mail it; the tally and the roll did the remembering.
- **Derivation.** On the board a column at rest holds at most (rate − 1) counters. So instead of drawing up to nine counters, write one symbol saying how many (a digit) and let the *position* say which column. Small table: 276 written as Egyptian signs (15), Roman CCLXXVI (7 letters), place value (3 digits).
- **The empty column.** On a board an empty line is visibly empty; on paper it leaves nothing to see. Babylon had base-60 place value, but "there was no zero to put into an empty position": 1 and 60 had exactly the same representation (MacTutor). By 300 BC a pair of slanted wedges was repurposed as a placeholder; rules for zero as a number appear in Brahmagupta (7th century); the Maya wrote their own zero (a shell shape), assumed not to have influenced Old World systems. Zero is first a placeholder, the thing that lets one rule work on every column.
- **Pause and try.** You are a Babylonian scribe with place value and no zero. Write "one" and "sixty". (Answer: the same.)
- **The word.** al-Khwarizmi (c. 780–850) wrote about 825 on arithmetic with Hindu numerals; the Arabic original is lost; a Latin version begins *Dixit Algorizmi* ("Thus spake Al-Khwarizmi"), known by its 1857 title *Algoritmi de Numero Indorum*, and its texts "described algorithms on decimal numbers … that could be carried out on a dust board." *Algorism* = "the technique of performing basic arithmetic by writing numbers in place value form and applying a set of memorized rules". The written method is the board with the counters replaced by digits and the settle folded into one pass: that is `addColumns`.
- **Time-travel scene (reconstructed):** Bugia, a boy at a dust board, a teacher. Documented background: Fibonacci's father; "a marvelous instruction in the art of the nine Indian figures"; *Liber Abaci* (1202) teaches the numerals, conversions of currency and measures, profit and interest.
- **Wrong turn (in the telling) and myth check.** Florence, 1299: a guild statute barred bankers from writing credits or debits "in the letter of the abacus", requiring words; the reasons are "a matter of speculation" (fraud is a popular guess). The popular story that numerals or zero were feared as devilish and outlawed by church or state is, per Nothaft, a modern myth: **myth**.
- **The long fight.** In European mathematics from the 12th century, common use only from the 15th. Reisch's 1503 woodcut (Pythagoras at a counting board looking despondent, Boethius with Hindu–Arabic numerals looking happy; one commentator's reading, and the sums are wrong). Adam Ries: a 1518 book on reckoning on the lines of the board, a 1522 book adding the digits and pen; "nach Adam Riese" still means "by correct arithmetic". Chaucer writes of a student's "augrym stones", meaning counting stones for an abacus: the word for the written method had been attached to the pebbles.
- **The word becomes algorithm.** By 1596 Thomas Hood used *algorithm* in English; the 17th-century French form was altered after *logarithm*; "it wasn't until the late 19th century that 'algorithm' took on the meaning that it has in modern English." For centuries the word meant exactly this chapter's procedure.
- **⊕** the board's positions ⊕ a mark for the empty column = written place value with zero (algorism). **Key idea:** on paper the carry is written above the next column; the board's two phases fold into one pass.

## Section 5. Stuck 5: The carry is slow (the machine)

- **Pascal, 1642, aged 18,** building for his father's tax work in Rouen. Carries are where information has to cross columns. An account of an earlier machine (Schickard's): the cumulative friction and inertia could "potentially damage the machine if a carry needed to be propagated through the digits, for example like adding 1 to a number like 9,999." Pascal's *sautoir* is armed by gravity and thrown at the next wheel "like an acrobat jumping from one trapeze to the next"; with it "a machine with 10,000 wheels would work as well as a machine with two wheels." Leibniz's stepped reckoner left the operator to check for errors after multiple carries.
- **Babbage.** Recognized the performance penalty of ripple-carry in the difference engine and designed anticipating carriage for the Analytical Engine. The 1843 English translation of Menabrea's *Sketch* lists "Plan of mechanism for carrying the tens (by anticipation), connected with long pinions"; the Science Museum holds Babbage's drawing "Hoarding and anticipating carriages" (7 November – 23 December 1863).
- **1946.** Burks, Goldstine and von Neumann: "the first step in an addition is to add each digit of the addend to the corresponding digit of the augend. The second step is to perform the carries, and this must be done in sequence since a carry may produce a carry." That is the Exchequer's two phases again: a parallel step and a sequential step. "It is inefficient to allow 39 times as much time for the second step … Hence either the carries must be accelerated, or use must be made of the average number of carries or both."
- **Measured.** Average longest carry chain on random numbers, 1,000,000 pairs each: 8 bits 2.16 (log₂ n = 3.00; longest seen 8), 16 bits 3.24 (4.00; 16), 32 bits 4.29 (5.00; 21), 40 bits 4.62 (5.32; 23), 64 bits 5.31 (6.00; 23). The 1946 report estimated about log₂ 40 ≈ 5.3, "about 5". Intuition: each extra column a carry must pass is a coin flip.
- **Way out 1: wait only as long as needed.** `addByRippling` hands every carry one column up per round and stops when none is left; it needs exactly (longest chain + 1) rounds (verified on 1,000,000 pairs at 40 and 62 bits). Average: 5.62 rounds for random 40-bit numbers, 6.29 for 64-bit; more than 6 rounds for 37.6% of random 64-bit pairs; all ones + 1 needs 64 rounds. On average an asynchronous adder finishes in O(log n) time, but a clocked machine must budget for the worst case.
- **Way out 2: look ahead.** A column *generates* a carry if a + b ≥ rate, and *propagates* one if a + b = rate − 1. Blocks of columns combine: (g, p) = (`g_u` ∨ (`p_u` ∧ `g_l`), `p_u` ∧ `p_l`), where `u` is the upper block and `l` the lower one. After ⌈log₂ n⌉ doubling rounds every column knows its carry: 6 rounds for 64 columns, at the cost of 321 combine operations instead of 63 hand-offs. No free lunch: less time, more hardware. Kogge and Stone (1973): log₂ n stages, with significant wiring congestion; Zuse's Z1 is thought to have implemented the first carry-lookahead adder in the 1930s.
- **Figures:** the ripple of 99999 + 1 with step numbers; the doubling reach of lookahead (what column 7 knows after rounds 0, 1, 2, 3).
- **Pause and try.** Add 1 to 999,999,999: how many carries in a row, and could you start the last before the first finishes? Also: for random 40-bit numbers, is the longest carry chain about 20, 10 or 5? (Answer: about 4.6 measured; the bound is 5.3.)
- **Prove it (Java):** `generates`, `propagates`, `lookaheadCarries`, `addLookahead`; `longestChain`; and on a real 64-bit word `addByRippling` and `addByLookahead`, both agreeing with Java's own `+` on 1,000,000 random pairs and 81 edge cases.
- **Binary.** Leibniz, *Explication de l'Arithmétique Binaire* (1703); Stibitz's relay adder, the "Model K", November 1937. In radix 2 the column rule is a three-input, two-output circuit.
- **Full circle (machine learning).** (a) The carry bound is why accumulators are wider than the numbers they add: 2^k numbers of w bits need at most w + k bits. The Google TPU paper (Jouppi et al., ISCA 2017) has 8-bit multiply-adds with 16-bit products collected in 32-bit accumulators; the paper does not say why 32, the arithmetic does: 65,536 products of two unsigned 8-bit numbers add up to at most 4,261,478,400, below 2³². (b) Lookahead works because its combine rule is associative, so work can be regrouped. Floating-point addition is not associative ((0.1 + 0.2) + 0.3 = 0.6000000000000001, 0.1 + (0.2 + 0.3) = 0.6), so a parallel sum that regroups additions can return slightly different totals. (Both checks are planned for the program.)
- **⊕** ripple ⊕ generate/propagate and regrouping = carry-lookahead; ripple ⊕ wait only as long as needed = early completion.

## Epilogue and bridge

- **What "algorithm" means now.** The word began as the name of this procedure. In the last section the question changed from "how do I add?" to "how many steps does adding take, and can I do fewer?" That is where an algorithm stops being a recipe and becomes an object with a cost. That question is the book from here on.
- **Summary bullets** (the chain again, one line each).
- **Bridge to chapter 2.** Adding is solved for two numbers. Multiply 1,000 by 1,000 with the method above and you do a thousand additions. The Rhind papyrus (around 1550 BC; the scribe Ahmose copying an older text) does it by doubling: "although in ancient Egypt the concept of base 2 did not exist, the algorithm is essentially the same algorithm as long multiplication after the multiplier and multiplicand are converted to binary."

## Back matter

- **Timeline with how sure we are:** about twenty rows (date, event, label, source).
- **Sources:** every citation numbered in order of first use, each with a link.
- **Full program:** `AddingTwoNumbers.java` and the output it printed, downloadable.

## Planned additions to the program (not yet in `AddingTwoNumbers.java`)

- Push/settle board counts printed for the worked sum.
- Random-order exchanges: the final board is always the same (20,000 random boards), and a single exchange never changes the board's worth.
- The lookahead combine rule is associative (all 64 triples).
- Floating-point regrouping example.
- Accumulator width: 2^k numbers of w bits fit in w + k bits; 65,536 products of two 8-bit numbers fit in 32 bits.
- Digit-sum check that 276 needs 15 additive signs; Roman numeral length 7.
- Tidy the long comments so displayed code stays under about 100 columns (the longest displayed line is currently 193).
