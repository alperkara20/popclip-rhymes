"""Extract poetry-specific word statistics from the Gutenberg Poetry Corpus.

Three signals matter for a rhyming dictionary aimed at poets:
  line_end : how often a word ends a line -- i.e. how often poets actually
             rhyme on it. This is the ranking signal.
  total    : how often it appears at all, as a register check.
  cap      : how often it appears capitalised *away from the start of a line*
             (poetry capitalises line openings, so line-initial words tell us
             nothing). A high ratio means a proper noun.
"""
import gzip, json, re, collections

WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

line_end = collections.Counter()
total    = collections.Counter()
cap      = collections.Counter()
lines = 0

with gzip.open("build/poetry.ndjson.gz", "rt", errors="replace") as f:
    for raw in f:
        try:
            s = json.loads(raw)["s"]
        except Exception:
            continue
        lines += 1
        toks = WORD.findall(s)
        if not toks:
            continue
        for i, t in enumerate(toks):
            low = t.lower()
            total[low] += 1
            if i > 0 and t[0].isupper():
                cap[low] += 1
        line_end[toks[-1].lower()] += 1

print(f"lines parsed      : {lines}")
print(f"distinct words    : {len(total)}")
print(f"distinct line-ends: {len(line_end)}")

json.dump({"line_end": line_end, "total": total, "cap": cap},
          open("build/poetry_stats.json", "w"))

print("\ntop line-end words:", ", ".join(w for w, _ in line_end.most_common(25)))
print("\nlikely proper nouns (cap ratio > .9, >=20 uses):")
pn = [w for w, c in total.items() if c >= 20 and cap[w] / c > 0.9]
print(len(pn), "e.g.", ", ".join(sorted(pn)[:25]))
