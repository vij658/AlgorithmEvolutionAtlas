import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;

/**
 * Era 1, topic 8: Archimedes squeezes pi (Measurement of a Circle, Syracuse, probably about 250 BCE).
 *
 * HOW IT WORKS
 *   Pi cannot be written down exactly, so Archimedes trapped it. A regular polygon drawn inside a circle has a perimeter
 *   shorter than the circle; one drawn outside has a longer perimeter. Starting from hexagons and doubling the number
 *   of sides four times (6, 12, 24, 48, 96), the two perimeters close in on the circumference from both sides. With
 *   diameter 1, if a is the outside perimeter and b the inside one, doubling the sides gives
 *       a' = 2ab / (a + b)        (the harmonic mean)
 *       b' = sqrt(a' b)           (the geometric mean)
 *   Every square root has to be approximated, so Archimedes rounded each bound the safe way: lower bounds down, upper
 *   bounds up. His result, Proposition 3: 3 10/71 < pi < 3 1/7, that is 223/71 < pi < 22/7.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Runs the doubling from hexagons to 96 sides at high precision and prints both bounds and the gap at each step.
 *   2. Checks Archimedes' result against the 96-gon (his fractions lie safely outside the exact polygon values) and his
 *      bounds for the square root of 3, 265/153 < sqrt(3) < 1351/780, which are continued-fraction convergents.
 *   3. Redoes the whole computation rounding every intermediate value outward to 4 significant digits, as a hand
 *      computer must: the bounds stay valid. This is interval arithmetic.
 *   4. Measures how the gap shrinks (about 4 times per doubling), how many doublings 35 digits need (van Ceulen's
 *      record, c. 1600), and what Huygens-style extrapolation gets from the 48- and 96-gons.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ArchimedesPi.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ArchimedesPi {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final MathContext MC = new MathContext(120);
    static final BigDecimal TWO = BigDecimal.valueOf(2), THREE = BigDecimal.valueOf(3);
    // pi to 110 digits, for measuring errors only (the bounds themselves never use it)
    static final BigDecimal PI = new BigDecimal("3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651");

    /** One doubling step: from the outside and inside perimeters of an n-gon (diameter 1) to those of the 2n-gon. */
    static BigDecimal[] doubleSides(BigDecimal a, BigDecimal b, MathContext mc) {
        BigDecimal a2 = TWO.multiply(a).multiply(b).divide(a.add(b), mc);   // harmonic mean
        BigDecimal b2 = a2.multiply(b).sqrt(mc);                             // geometric mean
        return new BigDecimal[]{a2, b2};
    }

    static String d(BigDecimal x, int digits) { return x.round(new MathContext(digits)).toPlainString(); }

    /** Correct decimal places: how many digits after the point the value shares with pi. */
    static int places(BigDecimal x) {
        BigDecimal err = x.subtract(PI).abs();
        int k = 0;
        BigDecimal t = BigDecimal.ONE;
        while (err.compareTo(t) < 0 && k < 105) { k++; t = t.movePointLeft(1); }
        return k - 1;
    }

    public static void main(String[] args) {
        // 1. hexagons to 96-gons
        BigDecimal a = TWO.multiply(THREE.sqrt(MC)), b = THREE;             // outside hexagon 2 sqrt 3, inside hexagon 3
        int n = 6;
        BigDecimal prevGap = null;
        List<BigDecimal[]> bounds = new ArrayList<>();
        Map<Integer, BigDecimal[]> byN = new LinkedHashMap<>();
        while (true) {
            check(b.compareTo(PI) < 0 && a.compareTo(PI) > 0, "pi lies between the polygons");
            BigDecimal gap = a.subtract(b);
            System.out.printf("polygon %d: inside %s outside %s gap %s%s%n", n, d(b, 10), d(a, 10), d(gap, 4),
                    prevGap == null ? "" : String.format(" (gap shrank %.3f times)", prevGap.divide(gap, MC).doubleValue()));
            byN.put(n, new BigDecimal[]{a, b});
            prevGap = gap;
            if (n == 96) break;
            BigDecimal[] next = doubleSides(a, b, MC);
            a = next[0];
            b = next[1];
            n *= 2;
        }

        // 2. Archimedes' fractions
        BigDecimal lo = new BigDecimal(223).divide(new BigDecimal(71), MC), hi = new BigDecimal(22).divide(new BigDecimal(7), MC);
        BigDecimal[] p96 = byN.get(96);
        check(lo.compareTo(p96[1]) < 0 && hi.compareTo(p96[0]) > 0, "223/71 and 22/7 lie outside the 96-gon values");
        System.out.printf("archimedes: 223/71 = %s < inside 96-gon %s ; outside 96-gon %s < 22/7 = %s ; pi = %s%n",
                d(lo, 8), d(p96[1], 8), d(p96[0], 8), d(hi, 8), d(PI, 8));
        // his bounds for sqrt 3, and where they come from
        BigInteger l1 = BigInteger.valueOf(265), l2 = BigInteger.valueOf(153), u1 = BigInteger.valueOf(1351), u2 = BigInteger.valueOf(780);
        check(l1.pow(2).compareTo(BigInteger.valueOf(3).multiply(l2.pow(2))) < 0, "265/153 < sqrt 3");
        check(u1.pow(2).compareTo(BigInteger.valueOf(3).multiply(u2.pow(2))) > 0, "1351/780 > sqrt 3");
        List<String> conv = new ArrayList<>();
        BigInteger p0 = BigInteger.ONE, q0 = BigInteger.ONE, p1 = BigInteger.TWO, q1 = BigInteger.ONE;   // sqrt 3 = [1; 1, 2, 1, 2, ...]
        conv.add("1/1");
        conv.add("2/1");
        for (int i = 2; i < 14; i++) {
            BigInteger k = BigInteger.valueOf(i % 2 == 0 ? 2 : 1);
            BigInteger p2 = k.multiply(p1).add(p0), q2 = k.multiply(q1).add(q0);
            conv.add(p2 + "/" + q2);
            p0 = p1; q0 = q1; p1 = p2; q1 = q2;
        }
        int iL = conv.indexOf("265/153"), iU = conv.indexOf("1351/780");
        check(iL > 0 && iU > 0, "both are convergents of sqrt 3");
        System.out.printf("sqrt3: 265/153 = %s < sqrt(3) = %s < 1351/780 = %s ; convergents %d and %d of [1; 1, 2, 1, 2, ...]: %s%n",
                d(new BigDecimal(265).divide(new BigDecimal(153), MC), 9), d(THREE.sqrt(MC), 9), d(new BigDecimal(1351).divide(new BigDecimal(780), MC), 9),
                iL, iU, String.join(", ", conv.subList(0, iU + 1)));
        System.out.printf("archimedes-margin: his lower bound gives up %s, his upper bound %s, against the exact 96-gon values%n",
                d(p96[1].subtract(lo), 3), d(hi.subtract(p96[0]), 3));

        // 3. interval arithmetic: carry a lower and an upper value for each perimeter, rounding outward to 4 digits.
        // Both steps are increasing in both inputs, so lower inputs give a lower result and upper inputs an upper one.
        for (int digits = 4; digits <= 7; digits++) {
            MathContext down = new MathContext(digits, RoundingMode.FLOOR), up = new MathContext(digits, RoundingMode.CEILING);
            BigDecimal aL = TWO.multiply(new BigDecimal(265)).divide(new BigDecimal(153), down);  // 2 x 265/153 < 2 sqrt 3
            BigDecimal aU = TWO.multiply(new BigDecimal(1351)).divide(new BigDecimal(780), up);   // 2 x 1351/780 > 2 sqrt 3
            BigDecimal bL = THREE, bU = THREE;
            for (int m = 6; m < 96; m *= 2) {
                BigDecimal naL = TWO.multiply(aL).multiply(bL).divide(aL.add(bL), down);
                BigDecimal naU = TWO.multiply(aU).multiply(bU).divide(aU.add(bU), up);
                BigDecimal nbL = naL.multiply(bL).sqrt(down);
                BigDecimal nbU = naU.multiply(bU).sqrt(up);
                aL = naL; aU = naU; bL = nbL; bU = nbU;
                check(bL.compareTo(PI) < 0 && aU.compareTo(PI) > 0, "the rounded bounds still trap pi at " + (2 * m) + " sides");
                check(aL.compareTo(aU) <= 0 && bL.compareTo(bU) <= 0, "intervals stay ordered");
            }
            boolean asGood = bL.compareTo(lo) >= 0 && aU.compareTo(hi) <= 0;
            System.out.printf("rounded %d digits: every value rounded outward: %s < pi < %s at 96 sides, still valid; %s Archimedes' 223/71 and 22/7%n",
                    digits, bL.toPlainString(), aU.toPlainString(), asGood ? "at least as tight as" : "looser than");
        }

        // 4a. how many doublings for more digits
        a = TWO.multiply(THREE.sqrt(MC));
        b = THREE;
        n = 6;
        int doublings = 0;
        int[] want = {2, 3, 10, 35};
        int w = 0;
        StringJoiner sj = new StringJoiner("; ");
        while (w < want.length) {
            BigDecimal gap = a.subtract(b);
            if (gap.compareTo(BigDecimal.ONE.movePointLeft(want[w])) < 0) {
                sj.add(String.format("%d places: %d doublings (a polygon of 6 x 2^%d sides)", want[w], doublings, doublings));
                w++;
                continue;
            }
            BigDecimal[] next = doubleSides(a, b, MC);
            a = next[0];
            b = next[1];
            doublings++;
        }
        System.out.printf("doublings: gap below 10^-d needs %s%n", sj);

        // 4b. Huygens-style extrapolation from the 48- and 96-gons
        BigDecimal[] p48 = byN.get(48);
        BigDecimal combo = TWO.multiply(p96[1]).add(p96[0]).divide(THREE, MC);                      // (2 inside + outside) / 3
        BigDecimal rich = BigDecimal.valueOf(4).multiply(p96[1]).subtract(p48[1]).divide(THREE, MC); // (4 inside96 - inside48) / 3
        System.out.printf("extrapolate: inside 96-gon %d correct places; (2 x inside + outside)/3 = %s, %d places; (4 x inside96 - inside48)/3 = %s, %d places%n",
                places(p96[1]), d(combo, 12), places(combo), d(rich, 12), places(rich));
        check(places(combo) > places(p96[1]) && places(rich) > places(p96[1]), "combining bounds gains digits");

        System.out.printf("ArchimedesPi: %d checks passed%n", passed);
    }

}
