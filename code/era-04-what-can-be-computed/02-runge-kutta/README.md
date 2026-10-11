# Runge–Kutta: the program

*Era 4 · topic 2 · 1895–1901* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/02-runge-kutta/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/02-runge-kutta/runge-kutta.html) · [All era 4 programs](../README.md)

## How it works

```text
A differential equation y' = f(t, y) says how fast y changes at every moment. Euler's method (1768) walks forward
in steps of size h, each step following the slope at its start: y(t + h) ~ y(t) + h f(t, y). Its error is
proportional to h, so ten times the accuracy costs ten times the steps. Runge's idea (1895) was to sample the
slope more than once inside each step and combine the samples, as the midpoint and trapezoidal rules do for
areas. The classical method of Kutta (1901) samples four slopes:
    k1 = f(t, y)                  k2 = f(t + h/2, y + h k1/2)
    k3 = f(t + h/2, y + h k2/2)   k4 = f(t + h, y + h k3)
    y(t + h) ~ y + h (k1 + 2 k2 + 2 k3 + k4) / 6
The weights are chosen so that the step agrees with the Taylor series of the true solution up to h^4. That means
eight equations in the weights ("order conditions"); then halving h divides the error by about 2^4 = 16.
```

## What the program does

```text
1. Writes five methods as tables of weights (Euler; Runge's midpoint; Heun's third order; Kutta's classical
   method and his 3/8 rule) and tests the eight order conditions in exact fractions.
2. Measures each method's order on y' = y, whose answer at t = 1 is e: the error ratio when h is halved.
3. Runs each on the oscillator x'' = -x for 20 periods: Euler's circle spirals out by exactly (1 + h^2) per step.
4. Counts the slope evaluations each method needs for an error below 10^-6.
5. A pendulum swinging through 90 degrees, which no elementary formula describes: the period found by the
   classical method agrees with Gauss's arithmetic-geometric mean to 12 digits.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java RungeKutta.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Runge–Kutta methods](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods) — Wikipedia | The family of methods, RK4, and adaptive steps |
| Start | [Euler method](https://en.wikipedia.org/wiki/Euler_method) — Wikipedia | The first-order method that Runge improved |
| Start | [Martin Wilhelm Kutta](https://mathshistory.st-andrews.ac.uk/Biographies/Kutta/) — MacTutor | Kutta's thesis of 1901 and his aerofoil theorem |
| Start | [Carl Runge](https://mathshistory.st-andrews.ac.uk/Biographies/Runge/) — MacTutor | Runge's applied mathematics at Göttingen |
| Deeper | [A history of Runge–Kutta methods](https://tlakoba.w3.uvm.edu/math337/paper_1996_Butcher_RKhistory.pdf) — J. C. Butcher, *Applied Numerical Mathematics* 20:247–260 (1996), on a University of Vermont course page | From Euler and Runge to Heun, Kutta and Nyström |
| Scholar | [Ueber die numerische Auflösung von Differentialgleichungen (1895)](https://zenodo.org/record/2178704) — Carl Runge, open-access scan on Zenodo (CC0) | Runge's paper that started the family |
| Scholar | [Ueber die numerische Auflösung totaler Differentialgleichungen (1905)](https://eudml.org/doc/58614) — Carl Runge, *Nachrichten ... Göttingen* (1905), 252–257, EuDML record | Runge's later paper on systems of equations |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
