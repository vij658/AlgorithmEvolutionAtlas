import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/**
 * Era 8, topic 13: Bitcoin's proof-of-work ledger (Satoshi Nakamoto, "Bitcoin: A Peer-to-Peer Electronic Cash
 * System", 31 October 2008; the network started on 3 January 2009).
 *
 * HOW IT WORKS
 *   A ledger of payments is kept by everyone, as a chain of blocks. Each block holds a batch of transactions (as the
 *   root of a Merkle tree of their hashes, Era 7), the hash of the block before it, and a number called the nonce.
 *   A block counts only if the SHA-256 hash of its header, read as a number, is below a target: in other words it
 *   starts with enough zero bits. No one knows how to find such a nonce except by trying: with d zero bits needed,
 *   about 2^d tries. Checking it takes one hash. That is the proof of work.
 *   Changing an old transaction changes its block's Merkle root, so its hash, so the next block's "previous hash" no
 *   longer matches: to rewrite history an attacker must redo the work of that block and of every block after it,
 *   while honest computers keep extending the chain. Everyone follows the chain with the most work.
 *   Nakamoto's Section 11 computes the chance that an attacker with a share q of the computing power, starting z
 *   blocks behind, ever catches up: while the honest side makes z blocks the attacker makes about z q / p (a Poisson
 *   count), and from k blocks behind a gambler with odds q / p catches up with probability (q / p)^k.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The real genesis block of 3 January 2009: its 80-byte header, hashed twice with SHA-256, against its published
 *      hash, and against the target encoded in the header.
 *   2. A toy chain: Merkle roots, and blocks mined at 4 to 16 zero bits; tries against 2^d.
 *   3. Tampering: one transaction changed in block 3 of 10, what breaks, and the work to repair it.
 *   4. Nakamoto's Section 11 tables, recomputed from his formula, against the numbers printed in the paper; and the
 *      race simulated directly.
 *   5. A block mined with plain SHA-256 at 4 to 16 zero bits, for the book's widget to repeat.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Bitcoin.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Bitcoin {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long hashes = 0;

    static byte[] sha256(byte[] b) {
        hashes++;
        try { return MessageDigest.getInstance("SHA-256").digest(b); } catch (Exception e) { throw new RuntimeException(e); }
    }

    static byte[] dsha(byte[] b) { return sha256(sha256(b)); }

    static String hex(byte[] b) { StringBuilder s = new StringBuilder(); for (byte x : b) s.append(String.format("%02x", x)); return s.toString(); }

    static byte[] unhex(String h) { byte[] b = new byte[h.length() / 2]; for (int i = 0; i < b.length; i++) b[i] = (byte) Integer.parseInt(h.substring(2 * i, 2 * i + 2), 16); return b; }

    static byte[] reverse(byte[] b) { byte[] r = new byte[b.length]; for (int i = 0; i < b.length; i++) r[i] = b[b.length - 1 - i]; return r; }

    static int leadingZeroBits(byte[] h) {
        int n = 0;
        for (byte x : h) { if (x == 0) { n += 8; continue; } n += Integer.numberOfLeadingZeros(x & 0xff) - 24; break; }
        return n;
    }

    static byte[] concat(byte[]... parts) {
        int len = 0;
        for (byte[] p : parts) len += p.length;
        byte[] r = new byte[len];
        int o = 0;
        for (byte[] p : parts) { System.arraycopy(p, 0, r, o, p.length); o += p.length; }
        return r;
    }

    /** Bitcoin's Merkle root: hash pairs with double SHA-256, repeating the last hash when a level has an odd count. */
    static byte[] merkleRoot(List<byte[]> leaves) {
        List<byte[]> level = new ArrayList<>(leaves);
        while (level.size() > 1) {
            List<byte[]> up = new ArrayList<>();
            for (int i = 0; i < level.size(); i += 2) up.add(dsha(concat(level.get(i), level.get(Math.min(i + 1, level.size() - 1)))));
            level = up;
        }
        return level.get(0);
    }

    static byte[] header(byte[] prev, byte[] root, long nonce) {
        byte[] n = new byte[8];
        for (int i = 0; i < 8; i++) n[i] = (byte) (nonce >>> (8 * i));
        return concat(prev, root, n);
    }

    static long mine(byte[] prev, byte[] root, int bits) {
        for (long nonce = 0; ; nonce++) if (leadingZeroBits(dsha(header(prev, root, nonce))) >= bits) return nonce;
    }

    /** Nakamoto's Section 11 formula. */
    static double attackerSuccess(double q, int z) {
        double p = 1 - q, lambda = z * (q / p), sum = 1;
        for (int k = 0; k <= z; k++) {
            double poisson = Math.exp(-lambda);
            for (int i = 1; i <= k; i++) poisson *= lambda / i;
            sum -= poisson * (1 - Math.pow(q / p, z - k));
        }
        return sum;
    }

    public static void main(String[] args) {
        // ---- 1. the genesis block -----------------------------------------------------------------------------------
        String genesisHeader = "01000000" + "0".repeat(64) + "3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a" + "29ab5f49" + "ffff001d" + "1dac2b7c";
        byte[] gh = unhex(genesisHeader);
        check(gh.length == 80, "a block header is 80 bytes");
        String shown = hex(reverse(dsha(gh)));
        check(shown.equals("000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"), "the header hashes to the genesis block's published hash");
        int zeros = leadingZeroBits(reverse(dsha(gh)));
        // the target from bits 0x1d00ffff: 0x00ffff * 256^(0x1d - 3)
        java.math.BigInteger target = java.math.BigInteger.valueOf(0x00ffff).shiftLeft(8 * (0x1d - 3));
        java.math.BigInteger value = new java.math.BigInteger(1, reverse(dsha(gh)));
        check(value.compareTo(target) < 0, "the hash is below the target");
        long time = 0x495fab29L, nonce = 0x7c2bac1dL;
        System.out.printf("genesis: header %s (80 bytes: version 1, previous hash zero, Merkle root, time %d, bits 0x1d00ffff, nonce %d) ; SHA-256 twice, bytes reversed: %s, the published hash ; %d leading zero bits ; target 0x00ffff x 256^26 = 2^%d x %.6f, so about 2^32 = %,d tries were expected%n",
                genesisHeader, time, nonce, shown, zeros, target.bitLength() - 1, target.doubleValue() / Math.pow(2, target.bitLength() - 1), 1L << 32);

        // ---- 2. a toy chain ------------------------------------------------------------------------------------------
        StringJoiner mj = new StringJoiner(" ; ");
        byte[] prevHash = new byte[32];
        for (int bits : new int[]{4, 8, 12, 16}) {
            int blocks = bits <= 12 ? 200 : 60;
            long tries = 0;
            for (int b = 0; b < blocks; b++) {
                List<byte[]> txs = new ArrayList<>();
                for (int t = 0; t < 4; t++) txs.add(dsha(("block " + bits + "." + b + " payment " + t).getBytes(StandardCharsets.UTF_8)));
                byte[] root = merkleRoot(txs);
                long n = mine(prevHash, root, bits);
                tries += n + 1;
                byte[] h = dsha(header(prevHash, root, n));
                check(leadingZeroBits(h) >= bits, "a mined block has the zeros it needs");
                prevHash = h;
            }
            double triesPer = (double) tries / blocks;
            check(triesPer > 0.7 * Math.pow(2, bits) && triesPer < 1.3 * Math.pow(2, bits), "tries per block are about 2^d");
            mj.add(String.format("%d zero bits: %d blocks, %,.0f tries per block on average (2^%d = %,d)", bits, blocks, triesPer, bits, 1 << bits));
        }
        System.out.printf("mining: blocks of 4 transactions, header = previous hash + Merkle root + nonce, double SHA-256 ; %s%n", mj);

        // ---- 3. tampering ------------------------------------------------------------------------------------------------
        int bits = 14, len = 10;
        List<List<byte[]>> blockTx = new ArrayList<>();
        byte[][] prev = new byte[len][], root = new byte[len][], hash = new byte[len][];
        long[] nonces = new long[len];
        byte[] p0 = new byte[32];
        for (int b = 0; b < len; b++) {
            List<byte[]> txs = new ArrayList<>();
            for (int t = 0; t < 4; t++) txs.add(dsha(("alice pays bob " + (b * 4 + t)).getBytes(StandardCharsets.UTF_8)));
            blockTx.add(txs);
            prev[b] = p0; root[b] = merkleRoot(txs); nonces[b] = mine(p0, root[b], bits);
            hash[b] = dsha(header(p0, root[b], nonces[b]));
            p0 = hash[b];
        }
        blockTx.get(3).set(2, dsha("alice pays mallory 14".getBytes(StandardCharsets.UTF_8)));
        byte[] newRoot = merkleRoot(blockTx.get(3));
        byte[] newHash3 = dsha(header(prev[3], newRoot, nonces[3]));
        boolean stillValid = leadingZeroBits(newHash3) >= bits;
        check(!Arrays.equals(newRoot, root[3]), "the Merkle root changes");
        check(!Arrays.equals(newHash3, hash[3]), "so block 3's hash changes, and block 4's 'previous hash' no longer matches");
        long redo = 0;
        byte[] pp = prev[3];
        for (int b = 3; b < len; b++) {
            byte[] r = b == 3 ? newRoot : root[b];
            long n = mine(pp, r, bits);
            redo += n + 1;
            pp = dsha(header(pp, r, n));
        }
        System.out.printf("tamper: a chain of %d blocks at %d zero bits ; one payment in block 3 changed ; block 3's Merkle root and hash change ; the old nonce %s %d zero bits ; block 4's link to block 3 breaks ; re-mining blocks 3 to 9 took %,d tries (about 7 x 2^%d = %,d)%n",
                len, bits, stillValid ? "still gives (by luck)" : "no longer gives", bits, redo, bits, 7L << bits);

        // ---- 4. Section 11 -------------------------------------------------------------------------------------------
        double[] paper01 = {1.0000000, 0.2045873, 0.0509779, 0.0131722, 0.0034552, 0.0009137, 0.0002428, 0.0000647, 0.0000173, 0.0000046, 0.0000012};
        double[] paper03 = {1.0000000, 0.1773523, 0.0416605, 0.0101008, 0.0024804, 0.0006132, 0.0001522, 0.0000379, 0.0000095, 0.0000024, 0.0000006};
        StringJoiner aj = new StringJoiner(" "), bj = new StringJoiner(" ");
        for (int z = 0; z <= 10; z++) {
            double v = attackerSuccess(0.1, z);
            check(Math.abs(v - paper01[z]) < 5e-8, "q = 0.1 matches the paper's table to 7 decimals");
            aj.add(String.format("%d:%.7f", z, v));
        }
        for (int i = 0; i <= 10; i++) {
            double v = attackerSuccess(0.3, 5 * i);
            check(Math.abs(v - paper03[i]) < 5e-8, "q = 0.3 matches the paper's table to 7 decimals");
            bj.add(String.format("%d:%.7f", 5 * i, v));
        }
        double[] qs = {0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45};
        int[] paperZ = {5, 8, 11, 15, 24, 41, 89, 340};
        StringJoiner zj = new StringJoiner(" ");
        for (int i = 0; i < qs.length; i++) {
            int z = 0;
            while (attackerSuccess(qs[i], z) >= 0.001) z++;
            check(z == paperZ[i], "the smallest z for P < 0.1% matches the paper");
            zj.add(String.format("%.2f:%d", qs[i], z));
        }
        System.out.printf("section11: Nakamoto's formula, recomputed ; q = 0.1, z:P %s ; q = 0.3, z:P %s ; every value equals the paper's to 7 decimals ; smallest z with P < 0.1%%, q:z %s, as in the paper%n", aj, bj, zj);

        // the race simulated directly: while honest miners find z blocks the attacker finds some; then a random walk
        SplittableRandom rnd = new SplittableRandom(2009);
        StringJoiner sj = new StringJoiner(" ; ");
        int trials = 1_000_000;
        for (int z : new int[]{1, 2, 3, 5}) {
            int wins = 0;
            for (int t = 0; t < trials; t++) {
                int honest = 0, attacker = 0;
                while (honest < z) { if (rnd.nextDouble() < 0.1) attacker++; else honest++; }
                int behind = z - attacker; // the attacker wins on drawing level, as in the formula
                int steps = 0;
                while (behind > 0 && steps < 2000) { if (rnd.nextDouble() < 0.1) behind--; else behind++; steps++; if (behind > 60) break; }
                if (behind <= 0) wins++;
            }
            double sim = (double) wins / trials, formula = attackerSuccess(0.1, z);
            sj.add(String.format("z = %d: simulated %.5f, formula %.5f", z, sim, formula));
        }
        System.out.printf("race: q = 0.1, %,d simulated races for each z, block by block (the attacker's blocks while the honest side finds z, then the race until it draws level) ; %s%n", trials, sj);

        // ---- 5. the widget ------------------------------------------------------------------------------------------------
        String msg = "alice pays bob 10";
        StringJoiner wj = new StringJoiner(" ; ");
        for (int b = 4; b <= 16; b += 4) {
            long n = 0;
            byte[] h;
            while (true) { h = sha256((msg + "|nonce:" + n).getBytes(StandardCharsets.UTF_8)); if (leadingZeroBits(h) >= b) break; n++; }
            wj.add(String.format("%d bits: nonce %d, hash %s", b, n, hex(h)));
        }
        System.out.printf("widget: one SHA-256 of the text \"%s|nonce:N\" for N = 0, 1, 2, ... until the hash starts with enough zero bits ; %s%n", msg, wj);

        System.out.println("Bitcoin: " + passed + " checks passed");
    }
}
