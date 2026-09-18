# popclip-rhymes

A [PopClip](https://www.popclip.app) extension: select a word, click **Rhymes**,
and pick from a submenu of words that rhyme with it — ranked for writing poetry
rather than by how common the word is on the web.

The extension itself is in [`source/Rhymes.popclipext`](source/Rhymes.popclipext);
see [its readme](source/Rhymes.popclipext/readme.md) for what it does and how it
works.

## Rebuilding the rhyme index

`source/Rhymes.popclipext/data/*.js` are generated. The corpora they are built
from are about 60 MB and are not committed:

```sh
./build/fetch-sources.sh          # download the corpora into build/
python3 build/poetry_stats.py     # extract line-end and frequency signals
python3 build/build_index.py      # write source/Rhymes.popclipext/data/*.js
```

The build is deterministic: the same inputs produce byte-identical output.

## Licence

MIT — see [LICENSE](LICENSE). The bundled rhyme data is derived from third-party
corpora that are credited in the
[extension readme](source/Rhymes.popclipext/readme.md#credits).
