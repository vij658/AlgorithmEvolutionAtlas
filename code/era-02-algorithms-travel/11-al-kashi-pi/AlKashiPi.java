import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;

/**
 * Era 2, topic 11: al-Kashi's pi (Ghiyath al-Din Jamshid al-Kashi, Treatise on the Circumference, Samarkand, July 1424).
 *
 * HOW IT WORKS
 *   Archimedes' method, with an accountant's discipline. First the target: for a circle 600,000 times as wide as the
 *   Earth, the computed circumference must be off by less than the breadth of a horse's hair; the Dictionary of
 *   Scientific Biography converts this to an error in pi of at most 0.5 x 10^-17. Then the plan: start from a hexagon in
 *   a circle of radius 60 and double the sides until the polygons are close enough, which happens at 3 x 2^28 =
 *   805,306,368 sides. Each doubling is one square root, done in base 60:
 *     the chord of 180 degrees minus half the arc, squared, is 60 x (120 + the chord of 180 minus the arc),
 *   starting from the chord of 60 degrees, which is the radius. The side of the polygon follows by Pythagoras, and the
 *   circumscribed side by proportion. Roots were checked by squaring and by casting out 59 (base 60's casting out nines).
 *
 * WHAT THIS PROGRAM DOES
 *   1. Finds how many doublings the target needs, for inscribed, circumscribed and combined polygons.
 *   2. Runs al-Kashi's 28 square roots in base 60 with exact whole numbers, checking each root by casting out 59, and
 *      gives 2 pi in sexagesimal and in decimal, against the true value and the DSB's 6.2831853071795865. The DSB says
 *      he took the arithmetic mean of the inscribed and circumscribed perimeters; the program does the same.
 *   3. Computes sin 1 degree by his iteration for the cubic of the trisection, from sin 3 degrees (Ptolemy's 6-degree
 *      chord, topic 2), and tests his sexagesimal value 1;2,49,43,11,14,44,16,26,17 (radius 60, as the DSB gives it)
 *      and the decimal 0.017452406437283571 printed beside it.
 *   4. Full circle: compares his 2 pi with the 2 pi of a computer's 64-bit floating point.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AlKashiPi.java
 *   Expected output: expected-output.txt in this folder.
 */
public class AlKashiPi {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final MathContext MC = new MathContext(80);
    static BigDecimal PI;

    static BigDecimal arctanInv(int x) {
        BigDecimal xx = BigDecimal.valueOf((long) x * x), term = BigDecimal.ONE.divide(BigDecimal.valueOf(x), MC), sum = term;
        for (int k = 1; term.abs().compareTo(new BigDecimal("1e-85")) > 0; k++) {
            term = term.divide(xx, MC).negate();
            sum = sum.add(term.divide(BigDecimal.valueOf(2L * k + 1), MC), MC);
        }
        return sum;
    }

    /** Base-60 digits after the semicolon, to a number of places. */
    static String sexa(BigDecimal v, int places) {
        BigInteger whole = v.toBigInteger();
        BigDecimal frac = v.subtract(new BigDecimal(whole));
        StringJoiner s = new StringJoiner(",");
        for (int i = 0; i < places; i++) {
            frac = frac.multiply(BigDecimal.valueOf(60));
            BigInteger d = frac.toBigInteger();
            s.add(d.toString());
            frac = frac.subtract(new BigDecimal(d));
        }
        return whole + ";" + s;
    }

    /** Base-60 digits, rounded in the last place. */
    static String sexaRound(BigDecimal v, int places) {
        BigInteger units = v.multiply(BigDecimal.valueOf(60).pow(places)).setScale(0, RoundingMode.HALF_EVEN).toBigInteger();
        LinkedList<String> digs = new LinkedList<>();
        BigInteger sixty = BigInteger.valueOf(60);
        for (int i = 0; i < places; i++) { BigInteger[] qr = units.divideAndRemainder(sixty); digs.addFirst(qr[1].toString()); units = qr[0]; }
        return units + ";" + String.join(",", digs);
    }

    /** The sum of the base-60 digits of n, modulo 59: casting out 59. */
    static int castOut59(BigInteger n) {
        BigInteger s = BigInteger.ZERO, sixty = BigInteger.valueOf(60);
        while (n.signum() > 0) { BigInteger[] qr = n.divideAndRemainder(sixty); s = s.add(qr[1]); n = qr[0]; }
        return s.mod(BigInteger.valueOf(59)).intValue();
    }

    static int casts;
    static List<String> bounds = new ArrayList<>();

    /** Square root of a whole number in base 60, checked as al-Kashi checked his: square it back, and cast out 59. */
    static BigInteger root(BigInteger radicand) {
        BigInteger r = radicand.sqrt(), rem = radicand.subtract(r.multiply(r));
        check(castOut59(r.multiply(r).add(rem)) == castOut59(radicand), "casting out 59 confirms the root");
        check(rem.signum() >= 0 && rem.compareTo(r.shiftLeft(1)) <= 0, "the remainder is less than twice the root plus one");
        casts++;
        return r;
    }

    static int correctDecimals(BigDecimal approx, BigDecimal truth) {
        BigDecimal err = approx.subtract(truth).abs();
        int d = 0;
        while (d < 40 && err.compareTo(new BigDecimal("0.5").movePointLeft(d + 1)) < 0) d++;
        return d;
    }

    /** Al-Kashi's 28 roots with every number carried to `places` sexagesimal places. Returns {inscribed, circumscribed, side}. */
    static BigDecimal[] polygons(int places, List<String> table) {
        BigInteger S = BigInteger.valueOf(60).pow(places);  // one part = S units
        BigInteger r = BigInteger.valueOf(60).multiply(S);  // the radius, 60 parts
        BigInteger d = r;                                   // the chord of 60 degrees = the radius ; then 120, 150, 165, ...
        for (int k = 0; k < 28; k++) {
            d = root(r.multiply(r.shiftLeft(1).add(d)));    // chord(180 - a/2)^2 = r (2r + chord(180 - a))
            if (table != null && (k < 3 || k == 27)) {
                String arc = k < 3 ? (180 - (60 >> k)) + " degrees" : "180 - 60/2^" + k + " degrees";
                table.add(arc + ": " + sexa(new BigDecimal(d).divide(new BigDecimal(S), MC), 4));
            }
            if (table != null && k < 4) {                   // the first few polygons, for the picture (not counted as his roots)
                BigInteger dm = r.shiftLeft(1), sd = dm.subtract(d).multiply(dm.add(d)).sqrt();
                BigDecimal nk = BigDecimal.valueOf(6L << k), sdD = new BigDecimal(sd);
                BigDecimal lo = nk.multiply(sdD).divide(new BigDecimal(dm), MC), hi = nk.multiply(sdD).divide(new BigDecimal(d), MC);
                check(lo.compareTo(PI) < 0 && hi.compareTo(PI) > 0, "each polygon pair traps pi");
                bounds.add(String.format("%d sides %s < pi < %s", 6L << k, lo.setScale(6, RoundingMode.DOWN).toPlainString(), hi.setScale(6, RoundingMode.UP).toPlainString()));
            }
        }
        // the side of the 3 x 2^28-gon by Pythagoras in the semicircle: side^2 = (D - d)(D + d)
        BigInteger diam = r.shiftLeft(1);
        BigInteger side = root(diam.subtract(d).multiply(diam.add(d)));
        BigDecimal n = BigDecimal.valueOf(3L << 28), Sd = new BigDecimal(S);
        BigDecimal sideD = new BigDecimal(side).divide(Sd, MC), apothem = new BigDecimal(d).divide(Sd, MC).divide(BigDecimal.valueOf(2), MC);
        BigDecimal inscribed = n.multiply(sideD).divide(BigDecimal.valueOf(60), MC);    // perimeter over the radius: 2 pi from below
        BigDecimal circumscribed = n.multiply(sideD).divide(apothem, MC);               // the circumscribed side is side x r / apothem
        return new BigDecimal[]{inscribed, circumscribed, sideD};
    }

    public static void main(String[] args) {
        PI = arctanInv(5).multiply(BigDecimal.valueOf(16)).subtract(arctanInv(239).multiply(BigDecimal.valueOf(4))).round(MC);
        BigDecimal twoPi = PI.multiply(BigDecimal.valueOf(2));

        // ---- the target, and how many doublings it needs --------------------------------------------------------
        BigDecimal target = new BigDecimal("0.5e-17");
        int needIn = -1, needOut = -1, needAvg = -1;
        for (int k = 0; k <= 40; k++) {
            BigDecimal n = BigDecimal.valueOf(6).multiply(BigDecimal.valueOf(2).pow(k));
            double ang = Math.PI / (6 * Math.pow(2, k));
            // errors from the series: pi - n sin(pi/n) ~ pi^3/(6 n^2) ; n tan(pi/n) - pi ~ pi^3/(3 n^2)
            BigDecimal n2 = n.pow(2), pi3 = PI.pow(3);
            BigDecimal eIn = pi3.divide(n2.multiply(BigDecimal.valueOf(6)), MC), eOut = pi3.divide(n2.multiply(BigDecimal.valueOf(3)), MC);
            BigDecimal eAvg = pi3.divide(n2.multiply(BigDecimal.valueOf(12)), MC);                // the average of the two polygons
            if (needIn < 0 && eIn.compareTo(target) <= 0) needIn = k;
            if (needOut < 0 && eOut.compareTo(target) <= 0) needOut = k;
            if (needAvg < 0 && eAvg.compareTo(target) <= 0) needAvg = k;
        }
        System.out.printf("target: error in pi at most 0.5e-17 ; doublings from the hexagon needed: inscribed alone %d, circumscribed alone %d, the average of the two %d ; al-Kashi's 3 x 2^28 = %d sides is %d doublings%n",
                needIn, needOut, needAvg, 3L << 28, 27);
        check(needAvg == 27, "the average of the two polygons meets the target at 3 x 2^28 sides, al-Kashi's polygon");

        // ---- the computation in base 60 ------------------------------------------------------------------------------
        // how many sexagesimal places must every number carry? try a few, then run with enough
        StringJoiner byPlaces = new StringJoiner(" ; ");
        int enough = -1;
        for (int places = 10; places <= 26; places += 2) {
            BigDecimal[] res = polygons(places, null);
            BigDecimal avg = res[0].add(res[1]).divide(BigDecimal.valueOf(2), MC);
            int dec = correctDecimals(avg, twoPi);
            byPlaces.add(places + " places: " + dec + " decimals");
            if (enough < 0 && dec >= 16) enough = places;
        }
        System.out.printf("precision: sexagesimal places carried in each chord, and the correct decimals of 2 pi from the average: %s%n", byPlaces);
        int P = enough + 2;
        List<String> table = new ArrayList<>();
        casts = 0;
        BigDecimal[] res = polygons(P, table);
        BigDecimal inscribed = res[0], circumscribed = res[1], sideD = res[2];
        check(inscribed.compareTo(twoPi) < 0 && circumscribed.compareTo(twoPi) > 0, "the two polygons trap 2 pi");
        System.out.printf("bounds: %s%n", String.join(" ; ", bounds));
        for (String t : table) System.out.printf("chord %s%n", t);
        System.out.printf("roots: %d square roots in base 60, each carried to %d sexagesimal places and checked by casting out 59 ; the polygon's side %s parts%n",
                casts, P, sexa(sideD, 8));
        BigDecimal average = inscribed.add(circumscribed).divide(BigDecimal.valueOf(2), MC);
        int inDec = correctDecimals(inscribed, twoPi), outDec = correctDecimals(circumscribed, twoPi), avgDec = correctDecimals(average, twoPi);
        System.out.printf("two pi: inscribed %s (%s) ; circumscribed %s (%s) ; true %s (%s)%n",
                sexa(inscribed, 10), inscribed.round(new MathContext(20)).toPlainString(), sexa(circumscribed, 10), circumscribed.round(new MathContext(20)).toPlainString(),
                sexa(twoPi, 10), twoPi.round(new MathContext(20)).toPlainString());
        BigDecimal dsb = new BigDecimal("6.2831853071795865");
        check(twoPi.setScale(16, RoundingMode.HALF_EVEN).compareTo(dsb) == 0, "the DSB's 6.2831853071795865 is 2 pi rounded to 16 decimals");
        check(inscribed.add(circumscribed).divide(BigDecimal.valueOf(2), MC).setScale(16, RoundingMode.HALF_EVEN).compareTo(dsb) == 0, "the average of the polygons rounds to the same 16 decimals");
        String mean9 = sexaRound(average, 9), true9 = sexaRound(twoPi, 9);
        check(mean9.equals("6;16,59,28,1,34,51,46,14,50") && mean9.equals(true9), "the mean, rounded to nine sexagesimal places, is 6;16,59,28,1,34,51,46,14,50, the true value so rounded");
        System.out.printf("mean: the arithmetic mean of the two perimeters, rounded to nine sexagesimal places, is %s ; 2 pi rounded the same way is %s%n", mean9, true9);
        System.out.printf("places: inscribed correct to %d decimals, circumscribed to %d, their average %s to %d ; the DSB's 6.2831853071795865 is 2 pi rounded to 16 decimals (error %s)%n",
                inDec, outDec, average.round(new MathContext(20)).toPlainString(), avgDec, dsb.subtract(twoPi).round(new MathContext(2)).toString());

        // ---- sin 1 degree by iteration ---------------------------------------------------------------------------------
        // sin 3 degrees from the chord of 6 degrees: 72 - 60 = 12, halved to 6 (Ptolemy's route, topic 2); radius 1
        // chord of 72 degrees on a unit circle: 2 sin 36 = sqrt(10 - 2 sqrt 5) / 2 ; chord 60 = 1
        BigDecimal crd72 = BigDecimal.valueOf(10).subtract(BigDecimal.valueOf(2).multiply(BigDecimal.valueOf(5).sqrt(MC))).sqrt(MC).divide(BigDecimal.valueOf(2), MC);
        BigDecimal crd60 = BigDecimal.ONE, D2 = BigDecimal.valueOf(4);                           // diameter squared
        BigDecimal sup72 = D2.subtract(crd72.pow(2)).sqrt(MC), sup60 = D2.subtract(crd60.pow(2)).sqrt(MC);
        BigDecimal crd12 = crd72.multiply(sup60).subtract(crd60.multiply(sup72)).divide(BigDecimal.valueOf(2), MC);   // Ptolemy's difference rule, diameter 2
        BigDecimal crd6 = BigDecimal.valueOf(2).subtract(D2.subtract(crd12.pow(2)).sqrt(MC)).sqrt(MC);                 // halving: crd(a/2)^2 = r (2r - crd(180 - a)), r = 1
        BigDecimal sin3 = crd6.divide(BigDecimal.valueOf(2), MC);
        BigDecimal x = sin3.divide(BigDecimal.valueOf(3), MC);
        int iters = 0;
        BigDecimal trueSin1;                                                                   // sin 1 degree by its series
        BigDecimal rad = PI.divide(BigDecimal.valueOf(180), MC), term = rad, sum = rad;
        for (int k = 1; k < 20; k++) { term = term.multiply(rad.pow(2)).divide(BigDecimal.valueOf((2L * k) * (2L * k + 1)), MC).negate(); sum = sum.add(term, MC); }
        trueSin1 = sum;
        StringJoiner progress = new StringJoiner(" ; ");
        while (x.subtract(trueSin1).abs().compareTo(new BigDecimal("1e-30")) > 0 && iters < 40) {
            x = sin3.add(BigDecimal.valueOf(4).multiply(x.pow(3))).divide(BigDecimal.valueOf(3), MC);   // sin 3t = 3 sin t - 4 sin^3 t
            iters++;
            if (iters <= 4) progress.add(iters + ": " + correctDecimals(x, trueSin1) + " decimals");
        }
        check(correctDecimals(x, trueSin1) >= 29, "the iteration converges");
        System.out.printf("sin1: from sin 3 degrees = %s, iterating x = (sin 3 + 4x^3)/3 ; correct decimals after %s ; true sin 1 = %s%n",
                sin3.round(new MathContext(18)).toPlainString(), progress, trueSin1.round(new MathContext(20)).toPlainString());
        // his value, radius 60, as the DSB gives it: 1;2,49,43,11,14,44,16,26,17
        int[] his = {1, 2, 49, 43, 11, 14, 44, 16, 26, 17};
        BigDecimal kashi = BigDecimal.ZERO;
        for (int i = 0; i < his.length; i++) kashi = kashi.add(BigDecimal.valueOf(his[i]).divide(BigDecimal.valueOf(60).pow(i), MC));
        BigDecimal kashiUnit = kashi.divide(BigDecimal.valueOf(60), MC);
        String trueSexa = sexa(trueSin1.multiply(BigDecimal.valueOf(60)), 9);
        int sameDigits = 0;
        String[] ts = trueSexa.substring(trueSexa.indexOf(';') + 1).split(",");
        while (sameDigits < 9 && Integer.parseInt(ts[sameDigits]) == his[sameDigits + 1]) sameDigits++;
        int kashiOk = correctDecimals(kashiUnit, trueSin1);
        BigDecimal dsbSin = new BigDecimal("0.017452406437283571");
        int dsbOk = correctDecimals(dsbSin, trueSin1);
        String tDig = trueSin1.toPlainString().substring(2), dDig = dsbSin.toPlainString().substring(2);
        int sameDec = 0;
        while (sameDec < dDig.length() && tDig.charAt(sameDec) == dDig.charAt(sameDec)) sameDec++;
        check(kashiOk >= 17, "al-Kashi's sexagesimal sin 1 degree is correct to 17 decimals");
        check(sameDigits >= 8, "his first eight sexagesimal places agree with the true value");
        check(dsbOk == 15, "the decimal printed beside it, 0.017452406437283571, is correct to 15 decimals only");
        System.out.printf("sin1 his: 1;2,49,43,11,14,44,16,26,17 (radius 60) ; true %s ; first %d places agree ; as a decimal %s, correct to %d decimals (error %s) ; the printed decimal 0.017452406437283571 shares its first %d digits with the true value but is correct to %d (error %s), so it is not an exact conversion of his digits%n",
                trueSexa, sameDigits, kashiUnit.round(new MathContext(20)).toPlainString(), kashiOk, kashiUnit.subtract(trueSin1).round(new MathContext(2)).toString(),
                sameDec, dsbOk, dsbSin.subtract(trueSin1).round(new MathContext(2)).toString());

        // ---- full circle: a computer's 2 pi ----------------------------------------------------------------------------
        BigDecimal dbl = new BigDecimal(2 * Math.PI);        // the exact value of the double
        BigDecimal errDouble = dbl.subtract(twoPi), errKashi = dsb.subtract(twoPi);
        check(errKashi.abs().compareTo(errDouble.abs()) < 0, "al-Kashi's 2 pi is closer than the double");
        System.out.printf("double: 2 * Math.PI prints %s and is exactly %s ; error %s ; al-Kashi's error %s, %.0f times smaller%n",
                2 * Math.PI, dbl.round(new MathContext(20)).toPlainString(), errDouble.round(new MathContext(2)).toString(), errKashi.round(new MathContext(2)).toString(),
                errDouble.abs().divide(errKashi.abs(), MC).doubleValue());

        System.out.printf("AlKashiPi: %d checks passed%n", passed);
    }
}
