Select a word, click **Rhymes**, and a submenu opens listing words that rhyme
with it. Click one and it replaces the word in your line. Hold **⇧ Shift** when
clicking to copy it instead.

Everything is bundled in the extension. It works offline, it never touches the
network, and **nothing you select is sent anywhere** — the extension has no
network access at all.

## Ranked for poetry, not for the web

The ordering is the whole point. A general rhyming dictionary ranks by how
common a word is on the internet, which for *fire* gives you:

> higher, prior, entire, require, buyer, supplier, identifier, amplifier

These lists are ranked instead by **how often poets actually end a line on a
word**, measured across 3.1 million lines of verse:

> desire, sire, higher, retire, require, choir, tire, attire, dire, mire, pyre

Function words are pushed to the back — you don't need *that* offered as the
best rhyme for *cat* — and brand names, dialect spellings and web-corpus noise
are filtered out.

| | ranked by web frequency | ranked for poetry |
| --- | --- | --- |
| **night** | site, copyright, right, website, white | light, sight, bright, right, white, might, delight |
| **time** | crime, prime, anytime, maritime, enzyme | crime, rhyme, sublime, prime, climb, chime, thyme |
| **sea** | see, free, tree, company, key, de, re | see, free, tree, three, knee, bee, glee, flee |

## Near rhymes

Some words have no perfect rhyme at all: *orange*, *autumn*, *month*, *silver*,
*music*. Below a divider, the submenu offers slant rhymes instead — *orange*
gives *fringe, tinge, hinge, cringe, twinge, lozenge*.

By default these appear only when perfect rhymes are scarce. Set **Near rhymes**
to *Always* if you want slant rhymes offered every time.

## Settings

| Option | Default | What it does |
| --- | --- | --- |
| Rhymes to list | 24 | How many entries the submenu holds. |
| Near rhymes | When there are few perfect rhymes | Or *Always*, or *Never*. |

When there are more rhymes than fit, a **Show all…** item at the bottom shows
the complete list in Large Type.

The button appears only when you select a single word, which keeps it out of the
way the rest of the time.

## How it works

Two words rhyme when their pronunciations match from the last **primary**
stressed vowel onward, so *understand* rhymes with *hand* and *happy* with
*snappy*. Near rhymes match from the last vowel, widened by one more phoneme
when that ending is too short to mean anything — otherwise every `-le` word
would "rhyme" with *purple*.

Primary stress matters: CMUdict marks the same word shape inconsistently
(`shadow SH AE1 D OW2` but `follow F AA1 L OW0`), and anchoring on secondary
stress drops *shadow*, *willow* and *meadow* into the `-ow` group, where they
wrongly rhyme with *know* and *below*.

The result is ~28,000 words in 3,525 perfect-rhyme groups and 2,036 near-rhyme
groups, stored as plain text: one group per line, one word per token. A lookup
is just finding the line the word sits on, which takes about a millisecond.

The index is built by a script in this repository, from the sources credited
below, and the build is reproducible.

## Credits

The rhyme data is derived from:

- [CMU Pronouncing Dictionary](https://github.com/cmusphinx/cmudict) —
  pronunciations. BSD-style licence.
- [A Gutenberg Poetry Corpus](https://github.com/aparrish/gutenberg-poetry-corpus)
  by Allison Parrish — 3.1M lines of public-domain verse from Project Gutenberg,
  used for the line-end ranking.
- Webster's Second, via `/usr/share/dict/words` on macOS — vocabulary. Public
  domain.
- [Peter Norvig's `count_1w.txt`](https://norvig.com/ngrams/) — modern word
  frequency.

## Changelog

- 2026-09-18: Initial release.
