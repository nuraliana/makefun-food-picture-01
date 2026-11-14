# Steaming Tonkotsu Ramen — make.fun food-picture-01

A steaming bowl of tonkotsu ramen, painted entirely in code with PIL:
a black lacquer bowl with a red rim on a dark wooden table, glossy golden
broth with oil droplets and chilli oil, a dense bed of wavy noodles, two
slices of chashu, a halved ajitama egg with a jammy orange yolk, a sheet
of nori, scallion rings, menma, and a lift of noodles pinched between
chopsticks while soft steam rises. No text anywhere in the picture.

## Files

- `render.py` — draws `entry.png` (1024x1024, pure PIL, fully
  deterministic: no network, no timestamps, no unseeded randomness).
- `entry.png` — the finished picture the entrypoint copies.
- `main.py` — stdlib-only entrypoint: copies `entry.png` next to it to
  `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).
- `LICENSE` — MIT.

## Run locally

```sh
python3 render.py            # redraw entry.png
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py   # copy it to out/entry.png
```

Run `render.py` twice and compare the sha256 of `entry.png`: the bytes
are identical every time.

## Referral

Built for make.fun: https://make.fun/r/ctnjhg8e
