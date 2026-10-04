# 9. Haversine (great-circle) distance

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#9-haversine-great-circle-distance)

## How it works

Great-circle distance on a sphere from latitudes and longitudes, using the haversine formula, which stays numerically stable for small distances. Treating the Earth as a sphere costs about 0.5% error compared with the ellipsoid.

## In depth (from the catalog page)

Distance along the surface of a sphere between two latitude/longitude points.

```java
static double haversineKm(double lat1, double lon1, double lat2, double lon2) {
    final double R = 6371.0088;                  // mean Earth radius, km
    double p1 = Math.toRadians(lat1), p2 = Math.toRadians(lat2);
    double dPhi = p2 - p1, dLam = Math.toRadians(lon2 - lon1);
    double a = Math.sin(dPhi / 2) * Math.sin(dPhi / 2)
             + Math.cos(p1) * Math.cos(p2) * Math.sin(dLam / 2) * Math.sin(dLam / 2);
    return 2 * R * Math.asin(Math.sqrt(a));
}
```

> **Verified.** New York to Los Angeles comes out at 3,935.8 km. Identical points give 0 and antipodal points give π·R. One degree of longitude is 111.20 km at the equator and 55.60 km at 60° N, exactly half, because it shrinks with the cosine of the latitude.

That last result is why plain Euclid on latitude and longitude is wrong. A spherical Earth can be off by up to about half a percent against the real ellipsoid, so use Vincenty or Karney's geodesic algorithms when that matters. For "what is near me" queries, use a spatial index (geohash, S2, H3 or a database's spatial type) instead of computing the distance to every row.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/09-haversine-distance
java HaversineDistance.java
```

JDK 17 or newer, no build step. It prints 4 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
NYC-LA = 3935.8 km; 1 deg lon at equator = 111.20 km, at 60N = 55.60 km
HaversineDistance: 4 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
