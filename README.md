# The World in One Day — 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/cryptotainment/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/cryptotainment/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A newspaper-style front page summing up the world news of Sunday 22 November 2026, drawn entirely in code by `main.py` (Python 3.13, standard library only). It writes one image to `output/entry.png`.

## The day's news

- **Lead:** FBI most-wanted cartel boss 'El Chapo Isidro' arrested in a Mexican army shoot-out in Sinaloa.
- FBI probes an apparent hack of its national crime database (NCIC).
- Israel: Eisenkot invites Likud to coalition talks, beginning Sunday.
- Gaza: Australia, Canada, Italy and the UK urge Israel to let aid reach flooded Gaza.
- France: cost-of-living protests roll into a fourth weekend.
- Peru: 152 homes uninhabitable after a quake; Lima residents fled.
- Africa: Kenya discharges its last Ebola patient as the DRC death toll passes 5,300.

## How it works

`main.py` draws the whole page with its own PNG encoder and its own 5x7 bitmap font — no third-party packages, no network, no randomness. Running it twice writes byte-identical files:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
