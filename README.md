[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/1987566643/news-images-0123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/1987566643/news-images-0123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# The World in One Day — 23 November 2026

An entry for the [make.fun](https://make.fun/bounty/news-image-20261123)
competition **news-image-20261123** — *"Sum up 23 November's world news in
one image"* ($100 in USDC).

## The image

A vintage broadsheet front page for Monday, 23 November 2026: a large
serif masthead with ornamental rules, black ink on cream newsprint, a
price line and a weather line, dense justified columns, and a "latest
wires" strip. It carries **40 dated stories across 7 regions**, with
**3 lead stories** (Ukraine sinks the Russian corvette Merkury off Libya,
COP31 ends with no deal, Nvidia reinstates Jensen Huang as CEO).

Every story was checked against real reporting (BBC, Reuters, AP,
Al Jazeera, CNN, Ukrinform and others) on 24 November 2026; the full list
with sources is in [NEWS.md](NEWS.md).

## How it works

`main.py` is a pure Python 3 standard-library program: a hand-written PNG
encoder, an embedded 5x7 bitmap font, and a small drawing library. It
draws the whole front page at run time — no network, no assets, no
dependencies — and writes the image to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output`). Two runs write byte-identical output.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The output is a 1024x1024 PNG, well under the 1 MiB limit.

## Referral

Built with make.fun — sign up with my referral link:
https://make.fun/r/grk0r34z

## License

MIT — see [LICENSE](LICENSE).
