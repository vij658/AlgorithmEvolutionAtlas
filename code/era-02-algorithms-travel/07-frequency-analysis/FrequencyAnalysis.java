import java.math.BigInteger;
import java.util.*;

/**
 * Era 2, topic 7: frequency analysis (al-Kindi, A Manuscript on Deciphering Cryptographic Messages, Baghdad,
 * 9th century, usually dated about 850 CE).
 *
 * HOW IT WORKS
 *   A substitution cipher replaces each letter by another, always the same one. There are 26! ways to do it in
 *   English, far too many to try. But the cipher cannot hide how often each sign appears. Al-Kindi's method: take a
 *   fairly long plain text in the same language and count its letters; count the signs of the secret message; rank
 *   both lists and pair them, most common with most common. For a message too short for the counts to settle, he says,
 *   look at which letters keep company with which (his "qualitative" method). Done by machine, that becomes a search
 *   that swaps pairs of letters while the decryption's letter pairs grow more like the language's.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Counts the letters of a reference sample of English (written for this program) and ranks them.
 *   2. Encrypts a different English message with random substitution keys, and breaks it two ways: ranking alone
 *      (al-Kindi's first method) and ranking followed by a search on letter pairs (his second method, mechanized),
 *      for messages from 50 letters to the whole message, averaged over 20 keys per length.
 *   3. Counts the keys: 26! of them.
 *   4. Measures Friedman's index of coincidence (1922) for the plain text, the substitution cipher, a polyalphabetic
 *      (Vigenere) cipher and a one-time pad, and finds the Vigenere key length from it.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java FrequencyAnalysis.java
 *   Expected output: expected-output.txt in this folder.
 */
public class FrequencyAnalysis {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** The reference sample: ordinary English prose, written for this program (about the book's own subject). */
    static final String SAMPLE = """
        Long before there were machines to carry out instructions, people wrote down ways of doing things that would
        work every time. A clerk in a temple counted grain with tokens of clay, a scribe in a palace kept tables of
        reciprocals so that division became multiplication, and a surveyor on the banks of a river measured fields
        that the flood had washed away. None of them called what they did an algorithm. The word came much later,
        from the name of a scholar who worked in Baghdad, and it reached the languages of Europe through Latin copies
        of his book on the Indian way of writing numbers. Yet the habit of writing a procedure so that anyone could
        follow it is very old, and the history of that habit is the story this book tries to tell.
        The first procedures were written for people, not for machines, and people make mistakes. A good procedure
        therefore had to be short, it had to be checked, and it had to tell the reader what to do when something went
        wrong. The scribes who copied tables of squares and square roots did not explain why the tables were right;
        they simply wrote the numbers down, row after row, and trusted the next scribe to copy them faithfully. When
        a copy was wrong, the error travelled with it for centuries. Some of the oldest mathematical documents we have
        are school exercises, full of corrections, and they show how hard it was to learn even the simplest steps.
        In China the counting board turned arithmetic into the movement of rods on a grid. A problem with several
        unknown quantities was laid out in columns, one column for each condition, and the clerks subtracted one
        column from another until the answer stood alone. When a subtraction left less than nothing, they used rods of
        a different colour and carried on. In India the empty place in a number became a number of its own, with
        rules for adding it, taking it away, and multiplying by it, and the same writers gave rules for debts and
        fortunes, which we now call negative and positive numbers. In Alexandria an astronomer built a table of chords
        from a handful of exact values, using rules that made new entries from old ones, and the table was copied and
        used for more than a thousand years.
        Procedures travel. They cross borders with merchants and with books, and they change as they go. A method for
        finding a number from its remainders appears in a Chinese primer, then in a treatise written eight centuries
        later by a man who said he had learned it from the calendar makers, and then again in Europe under another
        name. A method for solving whole number equations was found in India, lost to Europe, and found again by a
        French lawyer who set it as a challenge to his friends. Sometimes the same idea is discovered twice, far apart,
        by people who never heard of each other, and sometimes a borrowing is so complete that nobody remembers where
        the idea began. The historian has to be careful with both stories, and to say plainly when the evidence runs
        out.
        Secrets travel too. Kings and generals have always wanted to send messages that only the right reader could
        understand, and scribes invented many ways of hiding the meaning of a text. The simplest is to replace every
        letter by another letter, always the same one, so that the message looks like nonsense to anyone who does not
        know the rule. There are so many possible rules that nobody could try them all, and for a long time this kind
        of cipher was thought to be safe. It was not. A philosopher in Baghdad noticed that a cipher of this kind hides
        the letters but not their habits. Some letters are common and some are rare, some like to stand together and
        some never meet, and these habits survive the substitution untouched. Count the signs in the secret message,
        compare them with the letters of an ordinary text in the same language, and the rule begins to show itself.
        This is the first procedure in our story that needs facts about a whole language, gathered in advance, as well
        as the message in front of the reader.
        What follows is a history of such procedures, told in order of time, from the first marks cut into bone to the
        programs that run on the machines of today. Each step answered a difficulty that the step before it left
        behind, and each one is written here as a small program that can be run and checked. Where the evidence is
        firm, the book says so; where scholars disagree, it gives their positions; and where nothing is known, it
        leaves the gap open rather than filling it with a guess. The reader who wants to go deeper will find, for
        every step, the lectures, the articles and the original sources that were opened and read while the book was
        being written, so that every claim can be followed back to the place where it was found.
        A river town in the dry season is a quiet place. The boats lie on the mud, the ferrymen mend their nets, and
        the children run along the banks looking for things the water has left behind. Then the rains come in the
        hills, far away, and one morning the river begins to rise. Within a week it has covered the fields, and within
        a month the town itself stands like an island in a brown and moving sea. When the water goes down again, the
        boundary stones are gone, the ditches are full of silt, and nobody can say exactly where one family's land
        ended and the next began. That is why the surveyors were among the most important people in the kingdom. They
        carried ropes knotted at equal intervals, and with these ropes they could lay out a right angle, measure a
        field, and work out its area from a few simple rules. Their rules were not always exact, but they were good
        enough to settle a quarrel, and a rule that settles quarrels is worth more than a perfect one that nobody can
        use.
        Teachers in every age have complained that their students learn the steps without understanding them, and
        students in every age have answered that the steps are what the examination asks for. Both are right. A
        procedure that can be followed without understanding is a powerful thing, because it lets a person who has
        never seen the proof get the right answer, and it lets a machine do the same. But a procedure that is followed
        without any understanding cannot be repaired when it breaks, or adapted when the problem changes a little.
        The great teachers of the past gave their readers both: a recipe for the common case, and a picture or an
        argument that showed why the recipe worked, so that a careful reader could find the way back if the recipe
        failed. We still teach that way today, and the best programs are still written that way, with the steps for
        the machine and the reasons for the people who will have to read and change them later.
        Weather, trade and war decided which books survived. A library could burn in a single night, and a work that
        existed in only one copy would vanish with it. Other books survived because somebody thought them useful
        enough to copy again and again, even when the copyist did not understand them, and some of these copies have
        come down to us full of mistakes that tell us how the text was read. A modern editor compares the surviving
        copies, notes where they differ, and tries to work out which reading came first. It is slow work, and it rarely
        ends in certainty, but without it we would not know what most ancient writers actually wrote. Every claim in a
        history like this one rests, in the end, on the patience of such editors, and on the libraries and museums that
        keep the objects safe and let anyone look at them.
        """;

    /** The secret message: a different English text, also written for this program. */
    static final String MESSAGE = """
        The caravan will leave the city before dawn on the third day of the month, when the gates are opened for the
        water carriers. Tell the captain of the guard that the cargo is wool and copper, and that the real cargo is in
        the second wagon, under the sacks of grain. Do not speak of the books to anyone, not even to the merchants who
        travel with us, for there are men in the market who would pay well to know where the library is going. When we
        reach the river, we will wait for the boat that carries the green flag, and the boatman will ask you for the
        name of your father. Give him the name we agreed, and nothing more. If the boat does not come before sunset,
        return to the inn by the old bridge and wait there for my letter. I will write in the usual way, and you will
        read it with the usual key. Burn this message when you have read it, and do not keep a copy of the key in the
        same place as the letters. The scholars who sent the books trust us with work that took them many years, and
        we must not fail them. Some of these pages exist nowhere else in the world. If they are lost on the road, they
        are lost for ever, and nobody will know what was written in them or who wrote it. Keep the wagon covered in
        the rain and away from the fire at night, and count the boxes every morning before the animals are loaded.
        If anyone asks where we are going, say that we are taking wool to the coast to be sold, and that we will come
        back in the spring with salt. The road through the hills is longer but safer, and the soldiers there know my
        name. Travel slowly, rest the animals often, and do not let the drivers drink before the day's work is done.
        """;

    static String letters(String s) {
        StringBuilder b = new StringBuilder();
        for (char c : s.toLowerCase().toCharArray()) if (c >= 'a' && c <= 'z') b.append(c);
        return b.toString();
    }

    static int[] counts(String t) {
        int[] c = new int[26];
        for (char ch : t.toCharArray()) c[ch - 'a']++;
        return c;
    }

    /** Letters from most to least common (ties alphabetical). */
    static char[] ranking(int[] c) {
        Integer[] idx = new Integer[26];
        for (int i = 0; i < 26; i++) idx[i] = i;
        Arrays.sort(idx, (a, b) -> c[b] != c[a] ? c[b] - c[a] : a - b);
        char[] r = new char[26];
        for (int i = 0; i < 26; i++) r[i] = (char) ('a' + idx[i]);
        return r;
    }

    static String apply(String t, char[] key) {               // key[plain] = cipher, or key[cipher] = plain
        StringBuilder b = new StringBuilder();
        for (char ch : t.toCharArray()) b.append(key[ch - 'a']);
        return b.toString();
    }

    static char[] randomKey(Random r) {
        List<Character> l = new ArrayList<>();
        for (char c = 'a'; c <= 'z'; c++) l.add(c);
        Collections.shuffle(l, r);
        char[] k = new char[26];
        for (int i = 0; i < 26; i++) k[i] = l.get(i);
        return k;
    }

    static double[][] pairLog;                                  // log probability of letter b after letter a

    static double score(String t) {
        double s = 0;
        for (int i = 1; i < t.length(); i++) s += pairLog[t.charAt(i - 1) - 'a'][t.charAt(i) - 'a'];
        return s;
    }

    /** Al-Kindi's first method: pair the cipher's ranking with the language's. Returns decrypt[cipher] = plain. */
    static char[] byRanking(String cipher, char[] languageRank) {
        char[] cr = ranking(counts(cipher));
        char[] dec = new char[26];
        for (int i = 0; i < 26; i++) dec[cr[i] - 'a'] = languageRank[i];
        return dec;
    }

    /** His second method, mechanized: swap two letters while the letter pairs look more like English; a few fresh starts. */
    static char[] byPairs(String cipher, char[] start) {
        Random r = new Random(cipher.hashCode());
        char[] best = climb(cipher, start);
        double bestScore = score(apply(cipher, best));
        for (int restart = 0; restart < 12; restart++) {
            char[] s = start.clone();
            for (int k = 0; k < 6; k++) { int i = r.nextInt(26), j = r.nextInt(26); char t = s[i]; s[i] = s[j]; s[j] = t; }
            char[] d = climb(cipher, s);
            double sc = score(apply(cipher, d));
            if (sc > bestScore) { bestScore = sc; best = d; }
        }
        return best;
    }

    static char[] climb(String cipher, char[] start) {
        char[] dec = start.clone();
        double best = score(apply(cipher, dec));
        boolean improved = true;
        while (improved) {
            improved = false;
            for (int i = 0; i < 26; i++) for (int j = i + 1; j < 26; j++) {
                char t = dec[i]; dec[i] = dec[j]; dec[j] = t;
                double s = score(apply(cipher, dec));
                if (s > best + 1e-9) { best = s; improved = true; }
                else { t = dec[i]; dec[i] = dec[j]; dec[j] = t; }
            }
        }
        return dec;
    }

    static double accuracy(String plain, String decoded) {
        int ok = 0;
        for (int i = 0; i < plain.length(); i++) if (plain.charAt(i) == decoded.charAt(i)) ok++;
        return (double) ok / plain.length();
    }

    static double ioc(String t) {
        int[] c = counts(t);
        long n = t.length(), s = 0;
        for (int x : c) s += (long) x * (x - 1);
        return (double) s / (n * (n - 1));
    }

    public static void main(String[] args) {
        String ref = letters(SAMPLE), msg = letters(MESSAGE);
        int[] rc = counts(ref);
        char[] rank = ranking(rc);
        StringBuilder top = new StringBuilder();
        for (int i = 0; i < 12; i++) top.append(rank[i]);
        StringJoiner pct = new StringJoiner(" ");
        for (int i = 0; i < 26; i++) pct.add(String.format("%c=%.1f", rank[i], 100.0 * rc[rank[i] - 'a'] / ref.length()));
        System.out.printf("sample: %d letters of English ; ranking %s ; the 12 most common: %s%n", ref.length(), new String(rank), top);
        System.out.printf("percent: %s%n", pct);
        check(rank[0] == 'e', "e is the most common letter of the sample");
        // letter pairs from the sample, with add-one smoothing
        pairLog = new double[26][26];
        int[][] pc = new int[26][26];
        for (int i = 1; i < ref.length(); i++) pc[ref.charAt(i - 1) - 'a'][ref.charAt(i) - 'a']++;
        for (int a = 0; a < 26; a++) {
            int row = 0;
            for (int b = 0; b < 26; b++) row += pc[a][b] + 1;
            for (int b = 0; b < 26; b++) pairLog[a][b] = Math.log((pc[a][b] + 1.0) / row);
        }

        BigInteger keys = BigInteger.ONE;
        for (int i = 2; i <= 26; i++) keys = keys.multiply(BigInteger.valueOf(i));
        System.out.printf("keys: 26! = %s substitution keys ; at a billion a second, trying them all takes %s years%n",
                keys, keys.divide(BigInteger.valueOf(1_000_000_000L * 3600L * 24 * 365)));

        // ---- break the message, by length -------------------------------------------------------------------------
        Random r = new Random(850);
        String example = null;
        for (int len : new int[]{50, 100, 200, 400, 800, msg.length()}) {
            String plain = msg.substring(0, len);
            double accRank = 0, accPairs = 0;
            int solvedRank = 0, solvedPairs = 0, trials = 20;
            for (int t = 0; t < trials; t++) {
                char[] key = randomKey(r);
                String cipher = apply(plain, key);
                check(ioc(cipher) == ioc(plain), "substitution does not change the index of coincidence");
                char[] inv = new char[26];
                for (int i = 0; i < 26; i++) inv[key[i] - 'a'] = (char) ('a' + i);
                check(apply(cipher, inv).equals(plain), "the true key reads the message");
                char[] d1 = byRanking(cipher, rank);
                char[] d2 = byPairs(cipher, d1);
                double a1 = accuracy(plain, apply(cipher, d1)), a2 = accuracy(plain, apply(cipher, d2));
                accRank += a1; accPairs += a2;
                if (a1 >= 0.95) solvedRank++;
                if (a2 >= 0.95) solvedPairs++;
                if (len == 400 && t == 0) {
                    example = String.format("cipher %s ; by ranking %s ; with letter pairs %s",
                            cipher.substring(0, 60), apply(cipher, d1).substring(0, 60), apply(cipher, d2).substring(0, 60));
                }
            }
            System.out.printf("break %d letters: ranking alone %.1f%% right (%d of %d keys read) ; ranking then letter pairs %.1f%% right (%d of %d keys read)%n",
                    len, 100 * accRank / trials, solvedRank, trials, 100 * accPairs / trials, solvedPairs, trials);
            if (len >= 800) check(accPairs / trials > 0.95, "long messages are read");
        }
        System.out.printf("example 400: %s%n", example);

        // ---- Friedman's index of coincidence ----------------------------------------------------------------------
        String kindi = "kindi";
        StringBuilder vig = new StringBuilder(), pad = new StringBuilder();
        Random pr = new Random(1922);
        for (int i = 0; i < msg.length(); i++) {
            int p = msg.charAt(i) - 'a';
            vig.append((char) ('a' + (p + kindi.charAt(i % kindi.length()) - 'a') % 26));
            pad.append((char) ('a' + (p + pr.nextInt(26)) % 26));
        }
        double iPlain = ioc(msg), iSub = ioc(apply(msg, randomKey(r))), iVig = ioc(vig.toString()), iPad = ioc(pad.toString());
        check(Math.abs(iPlain - iSub) < 1e-15, "substitution keeps the index");
        check(iVig < iPlain && iPad < iVig, "polyalphabetic ciphers flatten the counts");
        System.out.printf("ioc: plain %.4f ; substitution %.4f ; Vigenere with key \"%s\" %.4f ; one-time pad %.4f ; uniform 1/26 = %.4f%n",
                iPlain, iSub, kindi, iVig, iPad, 1.0 / 26);
        StringJoiner per = new StringJoiner(" ");
        int bestP = 0;
        for (int period = 1; period <= 10; period++) {
            double sum = 0;
            for (int c = 0; c < period; c++) {
                StringBuilder col = new StringBuilder();
                for (int i = c; i < vig.length(); i += period) col.append(vig.charAt(i));
                sum += ioc(col.toString());
            }
            double avg = sum / period;
            per.add(String.format("%d=%.4f", period, avg));
            if (bestP == 0 && avg > (iPlain + 1.0 / 26) / 2) bestP = period;   // the first guess that looks like plain English
        }
        check(bestP == kindi.length(), "the index finds the key length");
        System.out.printf("period: average index of the columns for each guessed key length: %s ; the key has %d letters%n", per, bestP);

        System.out.printf("FrequencyAnalysis: %d checks passed%n", passed);
    }
}
