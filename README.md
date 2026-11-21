# Daily Orbit — 21 November 2026

[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/DLiiMaGaming/daily-orbit-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/DLiiMaGaming/daily-orbit-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

A one-page newspaper front page summing up the world's news of Saturday
21 November 2026: Russian missiles hit Poland and NATO's chief heads to
Warsaw, Wall Street slides into correction, Cyclone Akvan makes landfall in
Odisha, banks report a vendor cyberattack, the Palisades fire arsonist is
convicted, and COP31 enters its endgame — plus a ticker of five more stories
from the same day.

## How it works

`main.py` (Python 3.13, standard library only) draws the whole front page
from scratch — a small raster canvas, a hand-drawn 5x7 bitmap font, shape
helpers for the six story pictograms, and a hand-rolled PNG encoder — and
writes it as `entry.png`. No network, no assets, no randomness, no clock:
two runs produce byte-identical output.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The result is a 1024x1024 PNG, well under the 1 MiB limit.

## Entry

Built for the [make.fun](https://make.fun/bounty/news-image-20261121)
competition `news-image-20261121` — "Sum up 21 November's world news in
one image".
