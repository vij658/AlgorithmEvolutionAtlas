# Diffusion Models: the program

*Era 9 · topic 11 · 2015–2020* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/11-diffusion-models/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/11-diffusion-models/diffusion-models.html) · [All era 9 programs](../README.md)

## How it works

```text
The forward process destroys data a little at a time: x_t = sqrt(1 - beta_t) x_(t-1) + sqrt(beta_t) * noise, for
t = 1 to T = 1000, with beta rising from 0.0001 to 0.02. After all the steps, x_T is indistinguishable from
pure Gaussian noise. Any step can be reached at once: x_t = sqrt(abar_t) x_0 + sqrt(1 - abar_t) eps, where
abar_t is the product of (1 - beta_s) for s up to t and eps is standard Gaussian noise.
Training: take a data point x_0, a random t and fresh noise eps, form x_t, and teach a network eps_theta(x_t, t)
to guess eps (squared error). Sampling: start from pure noise x_T and for t = T down to 1 remove the predicted
noise, x_(t-1) = (x_t - beta_t / sqrt(1 - abar_t) * eps_theta(x_t, t)) / sqrt(1 - beta_t) + sqrt(beta_t) z,
with fresh Gaussian z (none at the last step). Points the network never saw appear, shaped like the data.
```

## What the program does

```text
1. The forward process on a two-armed spiral of points: running 1,000 small steps agrees with the closed form,
   and at the end the points have the mean and spread of pure noise.
2. Trains a small network (time-embedded, two hidden layers, gradients written by hand and checked) to predict
   the noise, with Adam (topic 5).
3. Samples new points from pure noise by the reverse process, and measures how close they lie to the spiral,
   against fresh spiral points and against plain Gaussian points; also with the network replaced by zero.
4. Prints the trained weights and a few sample paths for the book's widget.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Diffusion.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [But how do AI images and videos actually work? \| Guest video by Welch Labs](https://www.youtube.com/watch?v=iv-5mZ_9CPY) — 3Blue1Brown | Diffusion from the ground up, a guest video on 3Blue1Brown's channel |
| Deeper | [Diffusion Models \| Paper Explanation \| Math Explained](https://www.youtube.com/watch?v=HoKDTa5jHvg) — Outlier | The mathematics of the 2020 paper |
| Scholar | [Deep Unsupervised Learning using Nonequilibrium Thermodynamics](https://arxiv.org/abs/1503.03585v1) — J. Sohl-Dickstein, E. A. Weiss, N. Maheswaranathan, S. Ganguli (2015) | The idea |
| Scholar | [Denoising Diffusion Probabilistic Models](https://arxiv.org/pdf/2006.11239v2) — J. Ho, A. Jain, P. Abbeel (2020) | The simplified training and sampling |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
