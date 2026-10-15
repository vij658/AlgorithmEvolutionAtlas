import java.util.*;

/**
 * Era 7, topic 10: TCP congestion control (Van Jacobson and Michael Karels, 1988; Chiu and Jain, 1989).
 *
 * HOW IT WORKS
 *   Many senders share one link through a router with a small buffer. A sender that keeps a fixed number of packets
 *   in flight, and resends everything when an acknowledgement is late, can fill the buffer, lose packets, time out,
 *   and resend copies that are still on their way: the link stays busy carrying duplicates while useful throughput
 *   falls. Jacobson's rules make each sender adjust: start with one packet and double each round trip ("slow start");
 *   once past a threshold, add about one packet per round trip ("additive increase"); on a loss, take it as a sign of
 *   congestion, halve the threshold and start again from one packet. Retransmission timers use the measured round-trip
 *   time plus four times its measured variation, doubling after each timeout. Chiu and Jain showed why "increase by
 *   adding, decrease by multiplying" is the right shape: it is the combination that drives senders sharing a link
 *   towards both full use and equal shares, from any start.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A packet-level simulation: 1 to 64 senders through one bottleneck link with a 120-packet buffer. Senders with a
 *      fixed window and a fixed resend-everything rule, against senders following Jacobson's rules (slow start,
 *      congestion avoidance, fast retransmit, timers based on the round trip's variation, with backoff).
 *   2. Chiu and Jain's model: two users adjusting their rates after each signal of over- or under-use, with the four
 *      combinations of additive and multiplicative increase and decrease.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java TcpCongestion.java
 *   Expected output: expected-output.txt in this folder.
 */
public class TcpCongestion {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- the network: sender -> (D1) -> bottleneck queue, 1 packet per tick -> (D2) -> receiver -> (D3) -> ack ------
    static final int D1 = 10, D2 = 10, D3 = 20, BUFFER = 120;
    static final int BASE_RTT = D1 + 1 + D2 + D3;               // 41 ticks

    static class Sender {
        boolean tahoe;
        int base, next, maxSent;                // lowest unacknowledged, next to send, highest ever sent + 1
        double cwnd = 1, ssthresh = 64;
        int fixedWindow;
        double srtt = -1, rttvar, rto = 3 * BASE_RTT;
        long timer = -1;                        // deadline for the oldest unacknowledged packet
        int timedSeq = -1;
        long timedAt;
        int dupacks;
        // receiver: keeps packets that arrive out of order, and acknowledges everything it has in order
        int expected;
        BitSet held = new BitSet();
        long useful, duplicates, sent, timeouts;
    }

    // events: kind 0 = data reaches the queue, 1 = data reaches the receiver, 2 = ack reaches the sender
    static long[] evTime;
    static int[] evKind, evFlow, evSeq;
    static PriorityQueue<Integer> events;
    static int evCount;

    static void schedule(long time, int kind, int flow, int seq) {
        if (evCount == evTime.length) {
            int cap = evTime.length * 2;
            evTime = Arrays.copyOf(evTime, cap); evKind = Arrays.copyOf(evKind, cap);
            evFlow = Arrays.copyOf(evFlow, cap); evSeq = Arrays.copyOf(evSeq, cap);
        }
        evTime[evCount] = time; evKind[evCount] = kind; evFlow[evCount] = flow; evSeq[evCount] = seq;
        events.add(evCount++);
    }

    static double[] simulate(int flows, boolean tahoe, long ticks, long warmup) {
        evTime = new long[1 << 16]; evKind = new int[1 << 16]; evFlow = new int[1 << 16]; evSeq = new int[1 << 16];
        evCount = 0;
        events = new PriorityQueue<>((a, b) -> evTime[a] != evTime[b] ? Long.compare(evTime[a], evTime[b]) : Integer.compare(a, b));
        Sender[] s = new Sender[flows];
        for (int f = 0; f < flows; f++) { s[f] = new Sender(); s[f].tahoe = tahoe; s[f].fixedWindow = 32; }
        ArrayDeque<int[]> queue = new ArrayDeque<>();
        long busy = 0, drops = 0, arrivals = 0;
        long[] usefulAtWarmup = new long[flows];
        for (long t = 0; t < ticks; t++) {
            if (t == warmup) for (int f = 0; f < flows; f++) { usefulAtWarmup[f] = s[f].useful; s[f].duplicates = 0; }
            // deliver events due now (events are handled before senders act, so the order is fixed)
            while (!events.isEmpty() && evTime[events.peek()] <= t) {
                int e = events.poll();
                int f = evFlow[e], seq = evSeq[e];
                Sender x = s[f];
                if (evKind[e] == 0) {
                    if (t >= warmup) arrivals++;
                    if (queue.size() < BUFFER) queue.add(new int[]{f, seq}); else if (t >= warmup) drops++;
                } else if (evKind[e] == 1) {
                    if (seq < x.expected || x.held.get(seq)) x.duplicates++;   // a copy of something already received
                    else {
                        x.held.set(seq);
                        x.useful++;                                // a packet the receiver did not have
                        while (x.held.get(x.expected)) { x.held.clear(x.expected); x.expected++; }
                    }
                    schedule(t + D3, 2, f, x.expected);           // the acknowledgement: everything before this arrived
                } else {
                    onAck(x, seq, t);
                }
            }
            // the bottleneck sends one packet per tick
            if (!queue.isEmpty()) { int[] p = queue.poll(); schedule(t + D2, 1, p[0], p[1]); if (t >= warmup) busy++; }
            // timers
            for (Sender x : s) if (x.timer >= 0 && t >= x.timer && x.base < x.next) onTimeout(x, t);
            // senders fill their windows
            for (int f = 0; f < flows; f++) {
                Sender x = s[f];
                int window = x.tahoe ? (int) Math.min(Math.floor(x.cwnd), 64) : x.fixedWindow;
                while (x.next < x.base + window) {
                    if (x.next >= x.maxSent && x.timedSeq < 0) { x.timedSeq = x.next; x.timedAt = t; }   // Karn: time only new packets
                    schedule(t + D1, 0, f, x.next);
                    x.next++;
                    x.maxSent = Math.max(x.maxSent, x.next);
                    if (t >= warmup) x.sent++;
                    if (x.timer < 0) x.timer = t + (long) x.rto;
                }
            }
        }
        double span = ticks - warmup;
        double useful = 0, sumSq = 0, sentAll = 0, dup = 0;
        double[] per = new double[flows];
        for (int f = 0; f < flows; f++) {
            per[f] = (s[f].useful - usefulAtWarmup[f]) / span;
            useful += per[f];
            sumSq += per[f] * per[f];
            sentAll += s[f].sent;
            dup += s[f].duplicates;
        }
        double fairness = useful * useful / (flows * sumSq);
        return new double[]{useful, busy / span, drops / Math.max(1.0, arrivals), fairness, dup / span};
    }

    static void onAck(Sender x, int ack, long t) {
        if (ack > x.base) {
            int newly = ack - x.base;
            x.base = ack;
            if (x.next < x.base) x.next = x.base;
            if (x.timedSeq >= 0 && ack > x.timedSeq) {           // a round-trip sample
                double r = t - x.timedAt;
                if (x.srtt < 0) { x.srtt = r; x.rttvar = r / 2; }
                else { x.rttvar += 0.25 * (Math.abs(r - x.srtt) - x.rttvar); x.srtt += 0.125 * (r - x.srtt); }
                x.rto = x.tahoe ? x.srtt + 4 * x.rttvar : 2 * x.srtt;
                x.timedSeq = -1;
            }
            if (x.tahoe) for (int k = 0; k < newly; k++) x.cwnd += x.cwnd < x.ssthresh ? 1 : 1 / x.cwnd;
            x.dupacks = 0;
            x.timer = x.base < x.next ? t + (long) x.rto : -1;
        } else if (ack == x.base && x.base < x.next && x.tahoe) {
            if (++x.dupacks == 3) {                              // fast retransmit
                x.ssthresh = Math.max(Math.min(x.cwnd, 64) / 2, 2);
                x.cwnd = 1;
                x.next = x.base;
                x.timedSeq = -1;
                x.timer = t + (long) x.rto;
            }
        }
    }

    static void onTimeout(Sender x, long t) {
        x.timeouts++;
        x.next = x.base;                                         // go back and resend from the oldest lost packet
        x.timedSeq = -1;
        if (x.tahoe) {
            x.ssthresh = Math.max(Math.min(x.cwnd, 64) / 2, 2);
            x.cwnd = 1;
            x.rto = Math.min(x.rto * 2, 64.0 * BASE_RTT);        // exponential backoff
        }
        x.timer = t + (long) x.rto;
        x.dupacks = 0;
    }

    // ---- Chiu and Jain's model --------------------------------------------------------------------------------------
    /** Two users, capacity 1: each step, if the total exceeds 1 both decrease, otherwise both increase. */
    static double[] chiuJain(String policy, double x1, double x2, int steps) {
        double sumF = 0, sumE = 0;
        int count = 0;
        for (int k = 0; k < steps; k++) {
            boolean over = x1 + x2 > 1;
            switch (policy) {
                case "AIMD": if (over) { x1 *= 0.5; x2 *= 0.5; } else { x1 += 0.01; x2 += 0.01; } break;
                case "AIAD": if (over) { x1 = Math.max(0, x1 - 0.02); x2 = Math.max(0, x2 - 0.02); } else { x1 += 0.01; x2 += 0.01; } break;
                case "MIMD": if (over) { x1 *= 0.5; x2 *= 0.5; } else { x1 *= 1.05; x2 *= 1.05; } break;
                default:     if (over) { x1 = Math.max(0, x1 - 0.02); x2 = Math.max(0, x2 - 0.02); } else { x1 *= 1.05; x2 *= 1.05; } break;  // MIAD
            }
            if (k >= steps - 200) { sumF += (x1 + x2) * (x1 + x2) / (2 * (x1 * x1 + x2 * x2)); sumE += x1 + x2; count++; }
        }
        return new double[]{sumF / count, sumE / count, x1, x2};
    }

    public static void main(String[] args) {
        // ---- 1. the packet simulation --------------------------------------------------------------------------------
        StringJoiner nj = new StringJoiner(" ; "), tj = new StringJoiner(" ; ");
        long ticks = 60_000, warmup = 10_000;
        double oldWorstDup = 0, tahoeMinUseful = 1, tahoeMaxDup = 0, tahoeMinFair = 1, oldMinFair = 1;
        for (int flows : new int[]{1, 2, 4, 8, 16, 32, 64}) {
            double[] o = simulate(flows, false, ticks, warmup);
            double[] j = simulate(flows, true, ticks, warmup);
            check(o[0] <= 1 + 1e-9 && j[0] <= 1 + 1e-9, "no more than one useful packet per tick");
            check(o[1] <= 1 && j[1] <= 1, "the link carries at most one packet per tick");
            nj.add(String.format("%d sender%s: useful %.3f, link busy %.3f, duplicates %.3f, dropped %.1f%%, fairness %.2f", flows, flows == 1 ? "" : "s", o[0], o[1], o[4], 100 * o[2], o[3]));
            tj.add(String.format("%d sender%s: useful %.3f, link busy %.3f, duplicates %.3f, dropped %.1f%%, fairness %.2f", flows, flows == 1 ? "" : "s", j[0], j[1], j[4], 100 * j[2], j[3]));
            check(o[0] <= o[1] + 1e-9 && j[0] <= j[1] + 1e-9, "useful packets are a part of what the link carries");
            oldWorstDup = Math.max(oldWorstDup, o[4]);
            oldMinFair = Math.min(oldMinFair, o[3]);
            tahoeMinUseful = Math.min(tahoeMinUseful, j[0]);
            tahoeMaxDup = Math.max(tahoeMaxDup, j[4]);
            tahoeMinFair = Math.min(tahoeMinFair, j[3]);
        }
        check(oldWorstDup > 0.2, "without congestion control, a fifth or more of the link carries duplicates");
        check(tahoeMaxDup < 0.02, "with Jacobson's rules, almost none");
        check(tahoeMinUseful > 0.95 && tahoeMinFair > 0.95, "and the link is used fully and fairly");
        check(oldMinFair < 0.5, "while uncontrolled senders get very unequal shares");
        System.out.printf("network: one bottleneck link sending 1 packet per tick, a %d-packet buffer, a round trip of %d ticks without queueing ; %,d ticks measured after %,d to settle ; useful = new packets delivered in order per tick, duplicates = copies of packets already delivered, per tick%n",
                BUFFER, BASE_RTT, ticks - warmup, warmup);
        System.out.printf("fixed: senders without congestion control: a window of 32 packets, a timer of 2 x the smoothed round trip, resend everything from the oldest unacknowledged packet on a timeout ; %s%n", nj);
        System.out.printf("jacobson: senders with Jacobson's rules: slow start, congestion avoidance, fast retransmit after 3 duplicate acknowledgements, timer = smoothed round trip + 4 x its variation, doubled after each timeout ; %s%n", tj);

        // ---- 2. Chiu and Jain --------------------------------------------------------------------------------------
        StringJoiner cj = new StringJoiner(" ; ");
        double[] r = null;
        for (String pol : new String[]{"AIMD", "AIAD", "MIMD", "MIAD"}) {
            double[] res = chiuJain(pol, 0.1, 0.6, 2000);
            if (pol.equals("AIMD")) r = res;
            cj.add(String.format("%s: fairness %.3f, total use %.3f, ending at (%.3f, %.3f)", pol, res[0], res[1], res[2], res[3]));
        }
        double[] aiad = chiuJain("AIAD", 0.1, 0.6, 2000), mimd = chiuJain("MIMD", 0.1, 0.6, 2000);
        check(r[0] > 0.999, "AIMD reaches equal shares");
        check(aiad[0] < 0.9 && mimd[0] < 0.9, "AIAD and MIMD keep the unfairness they started with");
        System.out.printf("chiujain: two users share a capacity of 1, starting at rates 0.1 and 0.6 ; after each step both learn only whether the total was over 1 ; additive steps +0.01 or -0.02, multiplicative x1.05 or x0.5 ; averages over the last 200 of 2,000 steps, fairness = (x1 + x2)^2 / (2 (x1^2 + x2^2)), 1 when equal ; %s%n", cj);

        System.out.println("TcpCongestion: " + passed + " checks passed");
    }
}
