#!/bin/sh
# Fetch the corpora the rhyme index is built from. They are not committed:
# together they are about 60 MB, and they never change.
set -e
cd "$(dirname "$0")"

echo "CMU Pronouncing Dictionary..."
curl -fsSL https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict -o cmudict.dict

echo "Word frequency list (Norvig, from the Google Web Trillion Word Corpus)..."
curl -fsSL https://norvig.com/ngrams/count_1w.txt -o count_1w.txt

echo "Gutenberg Poetry Corpus (~52 MB)..."
curl -fsSL https://static.decontextualize.com/gutenberg-poetry-v001.ndjson.gz -o poetry.ndjson.gz

echo
echo "Done. Now run:"
echo "  python3 build/poetry_stats.py   # extract line-end / frequency signals"
echo "  python3 build/build_index.py    # write source/Rhymes.popclipext/data/*.js"
