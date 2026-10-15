import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/**
 * Era 7, topic 2: Merkle's hash trees (Ralph Merkle, Stanford, 1979).
 *
 * HOW IT WORKS
 *   A hash function turns any data into a short fingerprint (here SHA-256, 32 bytes) that nobody can fake: finding
 *   other data with the same fingerprint is believed to be infeasible. To fingerprint a million blocks, hash each
 *   block, then hash the fingerprints together in pairs, then the pairs of pairs, up to a single root. Anyone who
 *   trusts the root can check one block with only the fingerprints beside the path from that block to the root:
 *   about log2 n of them, 20 for a million blocks, instead of all n. Two copies of the data can find where they
 *   differ by comparing roots and walking down only into the halves that disagree. Merkle's own use was signatures:
 *   a Lamport one-time key can sign one message; hash 2^h one-time public keys into a tree and the 32-byte root
 *   becomes a public key good for 2^h messages.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Builds trees the way Certificate Transparency does (RFC 6962): 0x00 before a leaf, 0x01 before a pair.
 *      Checks every inclusion proof for every tree of 1 to 200 leaves, and that a changed leaf, a wrong position or
 *      a wrong root is rejected. Counts the hashes a proof needs against the number of leaves.
 *   2. Two copies of 2^20 blocks with a few blocks changed: finds them by walking down the two trees.
 *   3. Shows why the 0x00 and 0x01 bytes matter: without them, a different list of leaves has the same root.
 *   4. Lamport one-time signatures and Merkle's tree of them: 64 messages signed under one 32-byte public key.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MerkleTrees.java
 *   Expected output: expected-output.txt in this folder.
 */
public class MerkleTrees {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long hashes = 0;   // SHA-256 calls, counted

    static byte[] sha(byte[]... parts) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (byte[] p : parts) md.update(p);
            hashes++;
            return md.digest();
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    static final byte[] LEAF = {0x00}, NODE = {0x01}, NONE = {};
    static boolean prefixes = true;

    static byte[] leafHash(byte[] d) { return prefixes ? sha(LEAF, d) : sha(NONE, d); }

    static byte[] nodeHash(byte[] l, byte[] r) { return prefixes ? sha(NODE, l, r) : sha(NONE, l, r); }

    /** The largest power of two smaller than n (RFC 6962's split point). */
    static int split(int n) {
        int k = 1;
        while (k * 2 < n) k *= 2;
        return k;
    }

    /** The Merkle tree hash of leaves lo..hi-1, given their leaf hashes. */
    static byte[] root(byte[][] leaf, int lo, int hi) {
        if (hi - lo == 1) return leaf[lo];
        int k = split(hi - lo);
        return nodeHash(root(leaf, lo, lo + k), root(leaf, lo + k, hi));
    }

    /** The inclusion proof (audit path) for leaf m among leaves lo..hi-1, bottom first. */
    static List<byte[]> proof(byte[][] leaf, int m, int lo, int hi) {
        if (hi - lo == 1) return new ArrayList<>();
        int k = split(hi - lo);
        List<byte[]> p;
        if (m < lo + k) { p = proof(leaf, m, lo, lo + k); p.add(root(leaf, lo + k, hi)); }
        else { p = proof(leaf, m, lo + k, hi); p.add(root(leaf, lo, lo + k)); }
        return p;
    }

    /** Recomputes the root from one leaf hash and its proof; the verifier needs only m and n. */
    static byte[] rootFromProof(byte[] h, int m, int n, List<byte[]> path, int top) {
        if (n == 1) return top == 0 ? h : null;               // proof too long
        if (top == 0) return null;                            // proof too short
        int k = split(n);
        byte[] sib = path.get(top - 1);
        if (m < k) { byte[] l = rootFromProof(h, m, k, path, top - 1); return l == null ? null : nodeHash(l, sib); }
        byte[] r = rootFromProof(h, m - k, n - k, path, top - 1);
        return r == null ? null : nodeHash(sib, r);
    }

    static boolean verify(byte[] data, int m, int n, List<byte[]> path, byte[] root) {
        byte[] r = rootFromProof(leafHash(data), m, n, path, path.size());
        return r != null && Arrays.equals(r, root);
    }

    static byte[] block(String tag, int i) { return (tag + " block " + i).getBytes(StandardCharsets.UTF_8); }

    static String hex(byte[] b, int bytes) {
        StringBuilder s = new StringBuilder();
        for (int i = 0; i < bytes; i++) s.append(String.format("%02x", b[i]));
        return s.toString();
    }

    static int ceilLog2(long n) { int k = 0; while ((1L << k) < n) k++; return k; }

    // ---- a full binary tree over 2^levels leaves, stored as an array: node 1 is the root, node i has children 2i, 2i+1
    static byte[][] fullTree(byte[][] blocks) {
        int n = blocks.length;
        byte[][] t = new byte[2 * n][];
        for (int i = 0; i < n; i++) t[n + i] = leafHash(blocks[i]);
        for (int i = n - 1; i >= 1; i--) t[i] = nodeHash(t[2 * i], t[2 * i + 1]);
        return t;
    }

    static long compared;

    static void differences(byte[][] a, byte[][] b, int node, int n, List<Integer> out) {
        compared++;
        if (Arrays.equals(a[node], b[node])) return;
        if (node >= n) { out.add(node - n); return; }
        differences(a, b, 2 * node, n, out);
        differences(a, b, 2 * node + 1, n, out);
    }

    // ---- deterministic "random" bytes for the demonstration keys (a real key needs a secure random generator) -------
    static long seed = 1979L;

    static byte[] randomBytes(int k) {
        byte[] r = new byte[k];
        for (int i = 0; i < k; i++) {
            seed = seed * 6364136223846793005L + 1442695040888963407L;
            r[i] = (byte) (seed >>> 56);
        }
        return r;
    }

    static boolean bit(byte[] h, int i) { return ((h[i / 8] >> (7 - i % 8)) & 1) == 1; }

    /** A Lamport one-time key: 256 pairs of secrets; the public key is their 512 hashes. */
    static byte[][][] lamportSecret() {
        byte[][][] s = new byte[256][2][];
        for (int i = 0; i < 256; i++) { s[i][0] = randomBytes(32); s[i][1] = randomBytes(32); }
        return s;
    }

    static byte[][][] lamportPublic(byte[][][] s) {
        byte[][][] p = new byte[256][2][];
        for (int i = 0; i < 256; i++) { p[i][0] = sha(s[i][0]); p[i][1] = sha(s[i][1]); }
        return p;
    }

    /** Signing reveals, for each bit of the message's hash, the secret for that bit's value. */
    static byte[][] lamportSign(byte[][][] s, byte[] msg) {
        byte[] h = sha(msg);
        byte[][] sig = new byte[256][];
        for (int i = 0; i < 256; i++) sig[i] = s[i][bit(h, i) ? 1 : 0];
        return sig;
    }

    static boolean lamportVerify(byte[][][] p, byte[] msg, byte[][] sig) {
        byte[] h = sha(msg);
        for (int i = 0; i < 256; i++) if (!Arrays.equals(sha(sig[i]), p[i][bit(h, i) ? 1 : 0])) return false;
        return true;
    }

    static byte[] flatten(byte[][][] p) {
        byte[] out = new byte[256 * 2 * 32];
        for (int i = 0; i < 256; i++) for (int j = 0; j < 2; j++) System.arraycopy(p[i][j], 0, out, (2 * i + j) * 32, 32);
        return out;
    }

    public static void main(String[] args) {
        // ---- 1. inclusion proofs -------------------------------------------------------------------------------------
        long proofs = 0, rejected = 0;
        for (int n = 1; n <= 200; n++) {
            byte[][] data = new byte[n][];
            byte[][] leaf = new byte[n][];
            for (int i = 0; i < n; i++) { data[i] = block("log", i); leaf[i] = leafHash(data[i]); }
            byte[] r = root(leaf, 0, n);
            int longest = 0;
            for (int m = 0; m < n; m++) {
                List<byte[]> p = proof(leaf, m, 0, n);
                longest = Math.max(longest, p.size());
                check(verify(data[m], m, n, p, r), "proof of leaf " + m + " of " + n);
                proofs++;
                check(!verify(block("forged", m), m, n, p, r), "a changed leaf is rejected"); rejected++;
                if (n > 1) { check(!verify(data[m], (m + 1) % n, n, p, r), "a wrong position is rejected"); rejected++; }
                check(!verify(data[m], m, n, p, sha(r)), "a wrong root is rejected"); rejected++;
            }
            check(longest == ceilLog2(n), "the longest proof has ceil(log2 n) hashes, n=" + n);
        }
        System.out.printf("proofs: trees of 1 to 200 leaves, hashed as in Certificate Transparency (RFC 6962) ; %,d inclusion proofs checked, every one accepted ; %,d forged ones (changed leaf, wrong position, wrong root) all rejected ; the longest proof in a tree of n leaves is always ceil(log2 n) hashes%n",
                proofs, rejected);

        // the eight-block tree the book's widget rebuilds: every node's hash, level by level (first 8 hex digits)
        byte[][] eight = new byte[8][];
        for (int i = 0; i < 8; i++) eight[i] = leafHash(block("log", i));
        StringJoiner lv = new StringJoiner(" | ");
        for (int size = 1; size <= 8; size *= 2) {
            StringJoiner row = new StringJoiner(" ");
            for (int lo = 0; lo < 8; lo += size) row.add(hex(root(eight, lo, lo + size), 4));
            lv.add(row.toString());
        }
        System.out.printf("eight: the blocks \"log block 0\" ... \"log block 7\" ; node hashes from the leaves up, first 8 hex digits, levels separated by | : %s ; root %s%n", lv, hex(root(eight, 0, 8), 32));

        StringJoiner pj = new StringJoiner(" ; ");
        for (long n : new long[]{8, 1_000, 1_000_000, 1_000_000_000L}) {
            pj.add(String.format("%,d blocks: a proof needs %d hashes plus the leaf's own, a plain list of fingerprints needs all %,d", n, ceilLog2(n), n));
        }
        System.out.printf("pathcost: hashes needed to check one block against a trusted root ; %s%n", pj);

        // ---- 2. finding differences between two copies --------------------------------------------------------------
        int levels = 20, n = 1 << levels;
        byte[][] a = new byte[n][], b = new byte[n][];
        for (int i = 0; i < n; i++) { a[i] = block("replica", i); b[i] = a[i]; }
        byte[][] ta = fullTree(a);
        StringJoiner dj = new StringJoiner(" ; ");
        for (int d : new int[]{0, 1, 10, 100, 1000}) {
            byte[][] bb = b.clone();
            TreeSet<Integer> changed = new TreeSet<>();
            seed = 7L * d + 1;
            while (changed.size() < d) {
                seed = seed * 6364136223846793005L + 1442695040888963407L;
                changed.add((int) ((seed >>> 33) % n));
            }
            for (int i : changed) bb[i] = block("changed", i);
            byte[][] tb = fullTree(bb);
            List<Integer> found = new ArrayList<>();
            compared = 0;
            differences(ta, tb, 1, n, found);
            check(new TreeSet<>(found).equals(changed) && found.size() == d, "every changed block found, d=" + d);
            check(compared <= 1 + 2L * d * levels, "at most 1 + 2 d log2 n comparisons");
            dj.add(String.format("%,d changed: %,d comparison%s", d, compared, compared == 1 ? "" : "s"));
        }
        System.out.printf("repair: two copies of %,d blocks, compare the roots, then walk down only into halves whose fingerprints differ ; %s ; comparing block by block takes %,d%n",
                n, dj, n);

        // ---- 3. why the 0x00 and 0x01 bytes matter ----------------------------------------------------------------
        byte[][] four = {block("doc", 0), block("doc", 1), block("doc", 2), block("doc", 3)};
        String[] lines = new String[2];
        for (int pass = 0; pass < 2; pass++) {
            prefixes = pass == 1;
            byte[][] lf = new byte[4][];
            for (int i = 0; i < 4; i++) lf[i] = leafHash(four[i]);
            byte[] honest = root(lf, 0, 4);
            // the forger submits two "blocks", each the concatenation of two leaf hashes from the honest tree
            byte[][] forgedData = {concat(lf[0], lf[1]), concat(lf[2], lf[3])};
            byte[][] lf2 = {leafHash(forgedData[0]), leafHash(forgedData[1])};
            byte[] forged = root(lf2, 0, 2);
            boolean same = Arrays.equals(honest, forged);
            if (pass == 0) check(same, "without prefixes, the forged two-leaf list has the same root");
            else check(!same, "with prefixes, it does not");
            lines[pass] = String.format("%s: four blocks give root %s..., two 64-byte forged blocks give root %s..., %s",
                    prefixes ? "with 0x00 and 0x01" : "without the bytes", hex(honest, 6), hex(forged, 6), same ? "the same" : "different");
        }
        prefixes = true;
        System.out.printf("preimage: a different list of leaves with the same root ; %s ; %s%n", lines[0], lines[1]);

        // ---- 4. Lamport one-time signatures and Merkle's tree of them -------------------------------------------------
        byte[][][] s0 = lamportSecret(), p0 = lamportPublic(s0);
        byte[] m1 = "pay Alice 10".getBytes(StandardCharsets.UTF_8), m2 = "pay Mallory 9000".getBytes(StandardCharsets.UTF_8);
        byte[][] sig1 = lamportSign(s0, m1);
        check(lamportVerify(p0, m1, sig1), "Lamport signature verifies");
        check(!lamportVerify(p0, m2, sig1), "and does not verify another message");
        byte[][] sig2 = lamportSign(s0, m2);
        int both = 0, revealed = 0;
        for (int i = 0; i < 256; i++) {
            boolean r0 = sig1[i] == s0[i][0] || sig2[i] == s0[i][0];
            boolean r1 = sig1[i] == s0[i][1] || sig2[i] == s0[i][1];
            revealed += (r0 ? 1 : 0) + (r1 ? 1 : 0);
            if (r0 && r1) both++;
        }
        check(revealed == 256 + both, "secrets revealed after two signatures");
        System.out.printf("lamport: one key is 512 secrets of 32 bytes; the public key is their 512 hashes (%,d bytes) ; a signature reveals one secret per bit of the message's 256-bit hash (%,d bytes) ; signing one message reveals 256 of the 512 secrets ; signing a second with the same key revealed %d, both secrets at %d positions, so the key must be used only once%n",
                512 * 32, 256 * 32, revealed, both);

        int h = 6, keys = 1 << h;
        byte[][][][] secrets = new byte[keys][][][], publics = new byte[keys][][][];
        byte[][] leaves = new byte[keys][];
        long before = hashes;
        for (int i = 0; i < keys; i++) { secrets[i] = lamportSecret(); publics[i] = lamportPublic(secrets[i]); leaves[i] = leafHash(flatten(publics[i])); }
        byte[] publicKey = root(leaves, 0, keys);
        long keygen = hashes - before;
        int sigBytes = 0, good = 0, bad = 0;
        for (int i = 0; i < keys; i++) {
            byte[] msg = ("message number " + i).getBytes(StandardCharsets.UTF_8);
            // signature: the index, the one-time signature, the one-time public key, and its path to the root
            byte[][] ots = lamportSign(secrets[i], msg);
            List<byte[]> path = proof(leaves, i, 0, keys);
            sigBytes = 4 + 256 * 32 + 512 * 32 + path.size() * 32;
            boolean ok = lamportVerify(publics[i], msg, ots) && verify(flatten(publics[i]), i, keys, path, publicKey);
            check(ok, "Merkle signature " + i + " verifies");
            good++;
            byte[] other = ("message number " + (i + 1)).getBytes(StandardCharsets.UTF_8);
            check(!lamportVerify(publics[i], other, ots), "a changed message is rejected"); bad++;
            byte[][][] wrongKey = publics[(i + 1) % keys];
            check(!(lamportVerify(wrongKey, msg, ots) && verify(flatten(wrongKey), i, keys, path, publicKey)), "another key is rejected"); bad++;
        }
        System.out.printf("mss: Merkle's signature scheme with %d one-time keys in a tree of height %d ; public key: the 32-byte root %s... ; making the keys took %,d hashes ; %d signatures verified, %d forgeries rejected ; each signature is %,d bytes: the one-time signature (8,192), the one-time public key (16,384), the index (4) and %d path hashes (%d)%n",
                keys, h, hex(publicKey, 6), keygen, good, bad, sigBytes, h, h * 32);

        System.out.println("MerkleTrees: " + passed + " checks passed");
    }

    static byte[] concat(byte[] x, byte[] y) {
        byte[] r = Arrays.copyOf(x, x.length + y.length);
        System.arraycopy(y, 0, r, x.length, y.length);
        return r;
    }
}
