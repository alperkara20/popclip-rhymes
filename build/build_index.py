"""Build packed rhyme indexes for the PopClip Rhymes extension.

Tuned for writing poetry, so the ordering is not general word frequency but
how often poets actually end a line on a word (the Gutenberg Poetry Corpus,
3.1M lines), tempered by modern frequency so the archaisms that dominate a
pre-1920s corpus don't crowd out live words. Function words are pushed to the
back: nobody needs "that" offered as the best rhyme for "cat".
"""
import re, json, math, collections, pathlib

BUILD = pathlib.Path("build")
OUT   = pathlib.Path("source/Rhymes.popclipext/data")

# Closed-class words. Kept in the data (you may want them) but ranked last.
FUNCTION = set("""
a an the and but or nor of in on at to from by with as if than that this these
those it its i me my mine you your yours he him his she her hers we us our they
them their who whom whose which what is are was were am be been being have has
had do does did done shall should would could thee thou thy thine ye unto o oh
ah for upon into onto thereof whereof herein therein
""".split())

# --- signals ----------------------------------------------------------------
stats     = json.load(open(BUILD / "poetry_stats.json"))
line_end  = collections.Counter(stats["line_end"])
poem_tot  = collections.Counter(stats["total"])
poem_cap  = collections.Counter(stats["cap"])

google, order = {}, []
for line in (BUILD / "count_1w.txt").read_text(errors="replace").splitlines():
    p = line.split("\t")
    if len(p) == 2 and p[0].isalpha() and p[0].lower() not in google:
        google[p[0].lower()] = int(p[1]); order.append(p[0].lower())
top_google = set(order[:20000])

web2 = {w.strip().lower() for w in
        pathlib.Path("/usr/share/dict/words").read_text(errors="replace").splitlines() if w.strip()}
poetry_words = {w for w, c in poem_tot.items() if c >= 3}

names = {w.strip().lower() for w in
         pathlib.Path("/usr/share/dict/propernames").read_text(errors="replace").splitlines() if w.strip()}

# Proper nouns: nearly always capitalised away from the start of a line. Poets
# capitalise personifications too (God, Nature, Muse, Death), so a word that is
# still common in modern English is rescued -- that keeps April and June while
# dropping Aegean and Adonis.
proper = {w for w, c in poem_tot.items()
          if c >= 10 and poem_cap[w] / c > 0.85 and google.get(w, 0) < 50_000_000}

def usable(w):
    if len(w) < 3 or w in proper:          # "de", "re", "Aegean"
        return False
    # Some evidence the word is real: used in poetry at all, or current in
    # modern English. Kept deliberately loose -- a word missing from the index
    # can't be looked up at all, whereas a weak word just ranks last.
    if not (poem_tot[w] >= 1 or google.get(w, 0) >= 1_000_000):
        return False
    # Webster's is the vocabulary of record; anything outside it needs to be
    # solidly current, which drops dialect spellings and brand names.
    if w not in web2 and google.get(w, 0) < 20_000_000:
        return False
    return True

vocab = {w for w in (web2 | poetry_words | top_google) if usable(w)}

def score(w):
    """Higher is better. Line-end use in poetry leads; modern frequency keeps
    archaisms in check; function words go to the back."""
    # Line-end use dominates: it is the only signal that measures "do poets
    # actually rhyme on this word". Modern frequency is a light corrective so
    # that a pre-1920s corpus doesn't bury living words under archaisms.
    s = (math.log1p(line_end[w]) * 4.00
         + math.log1p(poem_tot[w]) * 0.50
         + math.log1p(google.get(w, 0)) * 0.30)
    # Function words and first names are kept but ranked last: you don't need
    # "that" offered as the best rhyme for "cat", or "Beth" for "breath".
    if w in FUNCTION or (w in names and google.get(w, 0) < 10_000_000):
        return s - 100
    return s

# --- pronunciations ---------------------------------------------------------
VOWEL = re.compile(r"^(AA|AE|AH|AO|AW|AY|EH|ER|EY|IH|IY|OW|OY|UH|UW)\d?$")

def keys(phones):
    """Anchor the perfect-rhyme key on the last PRIMARY-stressed vowel.

    cmudict is inconsistent about secondary stress on a final vowel -- it
    writes "shadow SH AE1 D OW2" but "follow F AA1 L OW0" for the same word
    shape. Anchoring on secondary stress therefore drops shadow, willow and
    meadow into the "-ow" group, where they wrongly rhyme with know and below.
    Primary stress is marked consistently, so use that, and let the near index
    pick up compounds ("sunshine"/"shine") that a secondary anchor would catch.
    """
    primary = secondary = last = None
    for i, p in enumerate(phones):
        if VOWEL.match(p):
            last = i
            if p[-1] == "1":
                primary = i
            elif p[-1] == "2":
                secondary = i
    if last is None:
        return None, None
    stressed = primary if primary is not None else secondary
    strip = lambda s: " ".join(p.rstrip("012") for p in phones[s:])
    # A near key of only 1-2 phonemes (a bare "-er", "-le") matches far too
    # broadly, so widen it by one preceding phoneme.
    n = last if len(phones) - last >= 3 or last == 0 else last - 1
    return strip(stressed if stressed is not None else last), strip(n)

perfect, near = collections.defaultdict(list), collections.defaultdict(list)
seen_p, seen_n, kept = set(), set(), set()

for line in (BUILD / "cmudict.dict").read_text(errors="replace").splitlines():
    line = line.split("#", 1)[0].strip()
    if not line:
        continue
    head, _, rest = line.partition(" ")
    word = re.sub(r"\(\d+\)$", "", head).lower()
    if not word.isalpha() or len(word) < 2 or word not in vocab:
        continue
    phones = rest.split()
    if not phones:
        continue
    pk, nk = keys(phones)
    if not pk:
        continue
    if (pk, word) not in seen_p:
        seen_p.add((pk, word)); perfect[pk].append(word); kept.add(word)
    if (nk, word) not in seen_n:
        seen_n.add((nk, word)); near[nk].append(word)

# --- pack -------------------------------------------------------------------
OUT.mkdir(parents=True, exist_ok=True)

def pack(groups, name):
    lines = []
    for words in groups.values():
        if len(words) < 2:
            continue
        words.sort(key=lambda w: -score(w))
        lines.append(" ".join(words))
    lines.sort()
    text = "\n".join(lines)
    (OUT / f"{name}.js").write_text(
        f"// Generated by build/build_index.py -- do not edit.\nmodule.exports = `{text}`;\n")
    print(f"{name:8} groups={len(lines):6}  data={len(text)/1024:6.0f} KB")

print(f"proper nouns dropped : {len(proper)}")
print(f"words in index       : {len(kept)}")
pack(perfect, "perfect")
pack(near, "near")
