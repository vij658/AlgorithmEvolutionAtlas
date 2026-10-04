import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 62 of the principles catalog (Part 3): Merkle trees
 *
 * HOW IT WORKS
 *   A tree of hashes: each leaf hashes a block, each parent hashes its children. Two replicas compare roots and
 *   descend only into subtrees whose hashes differ, finding differences in O(d log n) comparisons. Prefixing
 *   leaves and nodes differently (RFC 6962) blocks second-preimage tricks.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MerkleTrees.java
 *   Expected: the output in expected-output.txt, ending "MerkleTrees: 12520 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class MerkleTrees {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static byte[] sha256(byte[]... parts) {
        try {
            java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-256");
            for (byte[] p : parts) md.update(p);
            return md.digest();
        } catch (java.security.NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
    }

    static byte[] leafHash(byte[] data) { return sha256(new byte[]{0}, data); }                       // RFC 6962: leaves are hashed with a 0x00 prefix...

    static byte[] nodeHash(byte[] l, byte[] r) { return sha256(new byte[]{1}, l, r); }                // ...and inner nodes with a 0x01 prefix

    static int split(int n) { int k = Integer.highestOneBit(n); return k == n ? k / 2 : k; }          // largest power of two smaller than n

    static final class Node {
        final byte[] hash; final Node left, right; final int size;
        Node(byte[] hash, Node left, Node right, int size) { this.hash = hash; this.left = left; this.right = right; this.size = size; }
    }

    static Node build(byte[][] leaves, int lo, int hi) {         // leaves[lo, hi)
        int n = hi - lo;
        if (n == 1) return new Node(leafHash(leaves[lo]), null, null, 1);
        int k = split(n);
        Node l = build(leaves, lo, lo + k), r = build(leaves, lo + k, hi);
        return new Node(nodeHash(l.hash, r.hash), l, r, n);
    }

    static void auditPath(Node node, int m, List<byte[]> out) {     // PATH(m, D[n]) of RFC 6962 section 2.1.1
        if (node.size == 1) return;
        int k = split(node.size);
        if (m < k) { auditPath(node.left, m, out); out.add(node.right.hash); }
        else { auditPath(node.right, m - k, out); out.add(node.left.hash); }
    }

    static byte[] rootFromPath(byte[] leaf, int m, int n, List<byte[]> path, int end) {          // uses path[0, end)
        if (n == 1) return end == 0 ? leaf : null;
        if (end == 0) return null;
        int k = split(n);
        byte[] sibling = path.get(end - 1);
        if (m < k) { byte[] left = rootFromPath(leaf, m, k, path, end - 1); return left == null ? null : nodeHash(left, sibling); }
        byte[] right = rootFromPath(leaf, m - k, n - k, path, end - 1);
        return right == null ? null : nodeHash(sibling, right);
    }

    static boolean verify(byte[] data, int m, int n, List<byte[]> path, byte[] root) {
        byte[] r = rootFromPath(leafHash(data), m, n, path, path.size());
        return r != null && Arrays.equals(r, root);
    }

    /** Leaves that differ between two trees of the same shape, found by comparing hashes top-down. compared[0] counts the hash comparisons. */
    static void diff(Node a, Node b, int lo, List<Integer> out, int[] compared) {
        compared[0]++;
        if (Arrays.equals(a.hash, b.hash)) return;
        if (a.size == 1) { out.add(lo); return; }
        diff(a.left, b.left, lo, out, compared);
        diff(a.right, b.right, lo + a.left.size, out, compared);
    }

    static byte[] hex(String s) { byte[] b = new byte[s.length() / 2]; for (int i = 0; i < b.length; i++) b[i] = (byte) Integer.parseInt(s.substring(2 * i, 2 * i + 2), 16); return b; }

    static String hexOf(byte[] b) { StringBuilder sb = new StringBuilder(); for (byte x : b) sb.append(String.format("%02x", x)); return sb.toString(); }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java MerkleTrees.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        byte[][] vectors = {{}, {0x00}, {0x10}, {0x20, 0x21}, {0x30, 0x31}, {0x40, 0x41, 0x42, 0x43}, {0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57},
                {0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f}};
        String[] roots = {"6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d", "fac54203e7cc696cf0dfcb42c92a1d9dbaf70ad9e621f4bd8d98662f00e3c125",
                "aeb6bcfe274b70a14fb067a5e5578264db0fa9b51af5e0ba159158f329e06e77", "d37ee418976dd95753c1c73862b9398fa2a2cf9b4ff0fdfe8b30cd95209614b7",
                "4e3bbb1f7b478dcfe71fb631631519a3bca12c9aefca1612bfce4c13a86264d4", "76e67dadbcdf1e10e1b74ddc608abd2f98dfb16fbce75277b5232a127f2087ef",
                "ddb89be403809e325750d3d263cd78929c2942b7942a34b77e122c9594a74c8c", "5dc9da79a70659a9ad559cb701ded9a2ab9d823aad2f4960cfe370eff4604328"};
        for (int n = 1; n <= 8; n++) check(hexOf(build(Arrays.copyOf(vectors, n), 0, n).hash).equals(roots[n - 1]), "root of the first " + n + " leaves matches the Certificate Transparency test vector");
        check(hexOf(sha256()).equals("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"), "the root of an empty tree is the hash of the empty string");

        Random rnd = new Random(62);
        for (int n = 1; n <= 70; n++) {
            byte[][] leaves = new byte[n][];
            for (int i = 0; i < n; i++) { leaves[i] = new byte[1 + rnd.nextInt(20)]; rnd.nextBytes(leaves[i]); }
            Node tree = build(leaves, 0, n);
            int depth = 32 - Integer.numberOfLeadingZeros(n - 1);                                  // ceil(log2 n)
            for (int m = 0; m < n; m++) {
                ArrayList<byte[]> path = new ArrayList<>();
                auditPath(tree, m, path);
                check(path.size() <= depth, "an audit path has at most ceil(log2 n) hashes, n = " + n);
                check(verify(leaves[m], m, n, path, tree.hash), "an audit path proves membership, n = " + n + ", leaf " + m);
                byte[] other = leaves[m].clone(); other[0] ^= 1;
                check(!verify(other, m, n, path, tree.hash), "a changed leaf fails verification");
                if (n > 1) check(!verify(leaves[m], (m + 1) % n, n, path, tree.hash) || Arrays.equals(leaves[m], leaves[(m + 1) % n]), "the wrong position fails verification");
                if (!path.isEmpty()) { ArrayList<byte[]> bad = new ArrayList<>(path); byte[] h = bad.get(0).clone(); h[5] ^= 1; bad.set(0, h); check(!verify(leaves[m], m, n, bad, tree.hash), "a tampered path fails verification"); }
            }
            byte[][] changed = leaves.clone();
            byte[] replacement = new byte[23];                       // 23 bytes is longer than any leaf above (at most 20), so it always differs
            Arrays.fill(replacement, (byte) 0xee);
            changed[rnd.nextInt(n)] = replacement;
            check(!Arrays.equals(build(changed, 0, n).hash, tree.hash), "changing any leaf changes the root");
        }
        // anti-entropy: two replicas of 65,536 slots that differ in d of them
        int n = 1 << 16;
        byte[][] base = new byte[n][];
        for (int i = 0; i < n; i++) { base[i] = new byte[32]; rnd.nextBytes(base[i]); }
        Node mine = build(base, 0, n);
        StringBuilder sb = new StringBuilder();
        for (int d : new int[]{0, 1, 4, 16, 64, 256, 1024}) {
            byte[][] theirs = base.clone();
            TreeSet<Integer> changed = new TreeSet<>();
            while (changed.size() < d) changed.add(rnd.nextInt(n));
            for (int i : changed) { theirs[i] = new byte[32]; rnd.nextBytes(theirs[i]); }
            ArrayList<Integer> found = new ArrayList<>();
            int[] compared = {0};
            diff(mine, build(theirs, 0, n), 0, found, compared);
            check(new TreeSet<>(found).equals(changed) && found.size() == d, "the diff finds exactly the changed slots, d = " + d);
            check(compared[0] <= 1 + 2L * d * 16, "at most 1 + 2 d log2 n hash comparisons, d = " + d + ", got " + compared[0]);
            sb.append(String.format("%d differences: %,d comparisons (bound %,d); ", d, compared[0], 1 + 2L * d * 16));
        }
        System.out.println("two replicas with 65,536 slots (comparing everything would take 65,536 hashes): " + sb);
        // a proof does not pin down the tree size: the path of leaf 0 in a 5-leaf tree also "verifies" as a path in a 6-leaf tree against the 5-leaf root
        byte[][] five = Arrays.copyOf(base, 5);
        Node t5 = build(five, 0, 5);
        ArrayList<byte[]> p5 = new ArrayList<>();
        auditPath(t5, 0, p5);
        check(verify(five[0], 0, 5, p5, t5.hash) && verify(five[0], 0, 6, p5, t5.hash), "the proof for leaf 0 of 5 also verifies when the size is claimed to be 6");
        check(!verify(five[0], 0, 9, p5, t5.hash), "but a size that needs a longer path fails");
        // naive scheme (no prefixes): leaf = H(data), node = H(left || right). The tree over {x, y} and the one-leaf tree over H(x)||H(y) then share a root.
        byte[] x = new byte[]{1}, y = new byte[]{2};
        byte[] hx = sha256(x), hy = sha256(y), joined = new byte[64];
        System.arraycopy(hx, 0, joined, 0, 32); System.arraycopy(hy, 0, joined, 32, 32);
        byte[] naiveRootTwo = sha256(hx, hy), naiveRootOne = sha256(joined);
        check(Arrays.equals(naiveRootTwo, naiveRootOne), "without prefixes, a two-leaf tree and a one-leaf tree share a root");
        byte[] rfcTwo = build(new byte[][]{x, y}, 0, 2).hash, rfcOne = build(new byte[][]{joined}, 0, 1).hash;
        check(!Arrays.equals(rfcTwo, rfcOne), "with the 0x00 / 0x01 prefixes they do not");
        System.out.println("without prefixes the tree over {x, y} and the one-leaf tree over H(x)||H(y) share the root " + hexOf(naiveRootTwo).substring(0, 16) + "...; with RFC 6962 prefixes the roots are " + hexOf(rfcTwo).substring(0, 16) + "... and " + hexOf(rfcOne).substring(0, 16) + "...");
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("MerkleTrees: " + passed + " checks passed");
    }
}
