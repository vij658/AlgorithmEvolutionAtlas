import java.util.*;

/**
 * Era 6, topic 3: objects, classes and subclasses (Dahl and Nygaard, Simula 67).
 *
 * HOW IT WORKS
 *   Simula was built for simulation: a post office, a harbour, a factory, each made of many things that act on their
 *   own and meet now and then. Dahl and Nygaard let the programmer write a class (data together with the procedures
 *   that act on it), make as many objects of it as needed, each living as long as anything refers to it, and declare
 *   subclasses that inherit everything and change only what differs. A "virtual" procedure is looked up in the
 *   object's own class when it is called, so a program written for the general class works unchanged for every
 *   subclass. Java, the language of this book's programs, is one of Simula's descendants.
 *   A discrete-event simulation keeps a list of future events ordered by time, takes the earliest, lets the object
 *   concerned act (which may schedule more events), and repeats.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A small class hierarchy, Customer with subclasses Letter and Parcel, and which code each call reaches.
 *   2. A post office with one clerk, simulated for a million customers, against queueing theory's formula.
 *   3. The same with two clerks.
 *   4. Letters and parcels mixed: the simulator is not changed, only the subclasses; against the
 *      Pollaczek-Khinchine formula.
 *   5. The same simulation written without objects (arrays and a switch), with the same random numbers: identical
 *      results, and what each version must change to add a new kind of customer.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Objects.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Objects {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return ((seed >>> 11) + 0.5) / (double) (1L << 53);
    }

    static double exponential(double mean) { return -mean * Math.log(uniform()); }

    // ---- 1. the classes --------------------------------------------------------------------------------------------
    /** A customer of the post office. serviceTime() is virtual: each subclass may give its own. */
    static class Customer {
        final double arrived;
        Customer(double arrived) { this.arrived = arrived; }
        double serviceTime() { return exponential(1.0); }
        String kind() { return "customer"; }
    }

    static class Letter extends Customer {
        Letter(double t) { super(t); }
        @Override double serviceTime() { return exponential(0.5); }
        @Override String kind() { return "letter"; }
    }

    static class Parcel extends Customer {
        Parcel(double t) { super(t); }
        @Override double serviceTime() { return exponential(2.0); }
        @Override String kind() { return "parcel"; }
    }

    // ---- the simulator: an event list ordered by time ----------------------------------------------------------------
    record Event(double time, int type, Customer who, int order) {}          // type 0: arrival, 1: service ends

    interface Maker { Customer make(double t); }

    /** Simulate a post office with `clerks` clerks; return {mean wait in the queue, mean time in the office}. */
    static double[] simulate(int clerks, double arrivalRate, int customers, Maker maker) {
        PriorityQueue<Event> events = new PriorityQueue<>(Comparator.comparingDouble(Event::time).thenComparingInt(Event::order));
        Deque<Customer> queue = new ArrayDeque<>();
        int busy = 0, served = 0, arrivals = 0, order = 0;
        double waitSum = 0, systemSum = 0;
        events.add(new Event(exponential(1 / arrivalRate), 0, null, order++));
        while (served < customers) {
            Event e = events.poll();
            if (e.type() == 0) {
                Customer c = maker.make(e.time());
                arrivals++;
                if (arrivals < customers) events.add(new Event(e.time() + exponential(1 / arrivalRate), 0, null, order++));
                if (busy < clerks) { busy++; events.add(new Event(e.time() + c.serviceTime(), 1, c, order++)); }
                else queue.add(c);
            } else {
                served++;
                systemSum += e.time() - e.who().arrived;
                if (!queue.isEmpty()) {
                    Customer c = queue.poll();
                    waitSum += e.time() - c.arrived;
                    events.add(new Event(e.time() + c.serviceTime(), 1, c, order++));
                } else busy--;
            }
        }
        return new double[]{waitSum / customers, systemSum / customers};
    }

    /** The same post office without objects: customers are numbers in arrays, kinds are handled by a switch. */
    static double[] simulatePlain(int clerks, double arrivalRate, int customers, double letterShare) {
        int n = customers;
        double[] arrived = new double[n];
        int[] kind = new int[n];
        // events: time, type, customer index, order; kept in a priority queue of arrays
        PriorityQueue<double[]> events = new PriorityQueue<>((x, y) -> x[0] != y[0] ? Double.compare(x[0], y[0]) : Double.compare(x[3], y[3]));
        int[] queue = new int[n];
        int qh = 0, qt = 0, busy = 0, served = 0, arrivals = 0, order = 0;
        double waitSum = 0, systemSum = 0;
        events.add(new double[]{exponential(1 / arrivalRate), 0, -1, order++});
        while (served < customers) {
            double[] e = events.poll();
            if (e[1] == 0) {
                int c = arrivals;
                arrived[c] = e[0];
                kind[c] = uniform() < letterShare ? 1 : 2;
                arrivals++;
                if (arrivals < customers) events.add(new double[]{e[0] + exponential(1 / arrivalRate), 0, -1, order++});
                if (busy < clerks) { busy++; events.add(new double[]{e[0] + service(kind[c]), 1, c, order++}); }
                else queue[qt++] = c;
            } else {
                served++;
                systemSum += e[0] - arrived[(int) e[2]];
                if (qh < qt) {
                    int c = queue[qh++];
                    waitSum += e[0] - arrived[c];
                    events.add(new double[]{e[0] + service(kind[c]), 1, c, order++});
                } else busy--;
            }
        }
        return new double[]{waitSum / customers, systemSum / customers};
    }

    static double service(int kind) {
        switch (kind) {                                      // every new kind of customer means a new case here
            case 1: return exponential(0.5);
            case 2: return exponential(2.0);
            default: return exponential(1.0);
        }
    }

    public static void main(String[] args) {
        // ---- 1. dispatch ------------------------------------------------------------------------------------------------
        seed = 1967L;
        Customer[] sample = {new Customer(0), new Letter(0), new Parcel(0)};
        StringJoiner kinds = new StringJoiner(" ; ");
        for (Customer c : sample) {
            double sum = 0;
            int k = 100000;
            for (int i = 0; i < k; i++) sum += c.serviceTime();
            double want = c instanceof Letter ? 0.5 : c instanceof Parcel ? 2.0 : 1.0;
            check(Math.abs(sum / k - want) / want < 0.02, c.kind() + " reaches its own serviceTime");
            kinds.add(String.format("%s: declared as Customer, the call reaches %s.serviceTime, mean of %,d calls %.3f", c.kind(), c.getClass().getSimpleName(), k, sum / k));
        }
        check(sample[1] instanceof Customer && sample[2] instanceof Customer, "subclasses are customers");
        System.out.println("classes: Customer, with subclasses Letter and Parcel that change only serviceTime() ; " + kinds);

        // ---- 2. one clerk ------------------------------------------------------------------------------------------------
        int n = 1_000_000;
        double lambda = 0.8;
        seed = 1967L;
        double[] one = simulate(1, lambda, n, Customer::new);
        double wq1 = lambda / (1.0 * (1.0 - lambda)), w1 = 1 / (1.0 - lambda);
        check(Math.abs(one[0] - wq1) / wq1 < 0.05 && Math.abs(one[1] - w1) / w1 < 0.05, "M/M/1 within 5%");
        System.out.printf("oneclerk: customers arrive at random, 0.8 a minute on average ; one clerk, service 1 minute on average ; %,d customers simulated: average wait in the queue %.3f minutes (formula 0.8 / (1 - 0.8) = %.3f), average time in the office %.3f (formula %.3f)%n",
                n, one[0], wq1, one[1], w1);

        // ---- 3. two clerks ------------------------------------------------------------------------------------------------
        seed = 1967L;
        double lambda2 = 1.6;
        double[] two = simulate(2, lambda2, n, Customer::new);
        // Erlang C for c = 2, a = lambda/mu = 1.6, rho = 0.8
        double a = lambda2, rho = a / 2;
        double p0inv = 1 + a + a * a / (2 * (1 - rho));
        double pw = (a * a / (2 * (1 - rho))) / p0inv;
        double wq2 = pw / (2 * 1.0 - lambda2);
        check(Math.abs(two[0] - wq2) / wq2 < 0.05, "M/M/2 within 5%");
        check(two[0] < wq1 / 2, "one shared queue beats two separate ones");
        System.out.printf("twoclerks: twice as many customers (1.6 a minute) and two clerks ; average wait %.3f minutes (Erlang's formula %.3f) ; one queue shared by two clerks cuts the wait to %.0f%% of what two separate one-clerk offices give (%.3f)%n",
                two[0], wq2, 100 * two[0] / wq1, wq1);

        // ---- 4. letters and parcels -------------------------------------------------------------------------------------
        seed = 1967L;
        double share = 0.8, lambda3 = 0.6;
        double[] mix = simulate(1, lambda3, n, t -> uniform() < share ? new Letter(t) : new Parcel(t));
        double es = share * 0.5 + (1 - share) * 2.0, es2 = share * 2 * 0.25 + (1 - share) * 2 * 4.0, rho3 = lambda3 * es;
        double pk = lambda3 * es2 / (2 * (1 - rho3));
        check(Math.abs(mix[0] - pk) / pk < 0.05, "Pollaczek-Khinchine within 5%");
        System.out.printf("mixed: 80%% letters (0.5 minutes on average) and 20%% parcels (2 minutes), 0.6 customers a minute, one clerk ; the simulator is unchanged, only the subclasses differ ; average wait %.3f minutes (Pollaczek-Khinchine formula %.3f) ; the clerk is busy %.0f%% of the time, yet the parcels make the wait %.1f times what it would be if every service took exactly %.1f minutes%n",
                mix[0], pk, 100 * rho3, pk / (lambda3 * es * es / (2 * (1 - rho3))), es);

        // ---- 5. without objects ------------------------------------------------------------------------------------------
        seed = 1967L;
        double[] plain = simulatePlain(1, lambda3, n, share);
        check(plain[0] == mix[0] && plain[1] == mix[1], "the plain version gives identical results");
        System.out.printf("twin: the same post office written with arrays and a switch, fed the same random numbers ; average wait %.6f and %.6f, identical ; to add a third kind of customer the object version needs one new subclass, the plain version a new number, a new case in the switch, and a new branch where customers are made%n",
                mix[0], plain[0]);

        System.out.println("Objects: " + passed + " checks passed");
    }
}
