// Rhymes -- offline rhyming dictionary for PopClip, ranked for writing poetry.
//
// The two data files are newline-separated rhyme groups, each group a
// space-separated list of words, best first. Words that rhyme share a group,
// so a lookup is just "find the line this word sits on". Ordering comes from
// how often poets end a line on a word, not from raw web frequency -- see
// build/build_index.py.

const PERFECT = require("./data/perfect.js");
const NEAR = require("./data/near.js");

const NEAR_CAP = 10; // when near rhymes ride along with a full list of perfect ones

// Spellings to look up, best first: the last word of the selection, so a stray
// space or trailing punctuation doesn't break it. A contraction gives two
// candidates -- "cat's" is listed as "cats", while "don't" is only "don".
function candidates(text) {
  const tokens = String(text).toLowerCase().match(/[a-z]+(?:['’][a-z]+)*/g);
  if (!tokens) return [];
  const raw = tokens[tokens.length - 1];
  const joined = raw.replace(/['’]/g, "");
  const stem = raw.split(/['’]/)[0];
  return joined === stem ? [joined] : [joined, stem];
}

// Every word sharing a group with `word`. A word with more than one
// pronunciation ("live", "again") sits in more than one group, so keep
// scanning after the first hit.
function lookup(packed, word) {
  const out = [];
  const seen = new Set([word]);
  let i = 0;
  while ((i = packed.indexOf(word, i)) !== -1) {
    const end = i + word.length;
    const before = i === 0 ? "\n" : packed.charAt(i - 1);
    const after = end >= packed.length ? "\n" : packed.charAt(end);
    // Only a whole-word match counts -- "cat" must not match "catalog".
    if ((before === " " || before === "\n") && (after === " " || after === "\n")) {
      const start = packed.lastIndexOf("\n", i) + 1;
      let stop = packed.indexOf("\n", end);
      if (stop === -1) stop = packed.length;
      for (const w of packed.slice(start, stop).split(" ")) {
        if (!seen.has(w)) {
          seen.add(w);
          out.push(w);
        }
      }
    }
    i = end;
  }
  return out;
}

// First candidate spelling that is actually in the data.
function resolve(found, packed) {
  for (const w of found) {
    if (lookup(packed, w).length > 0) return w;
  }
  return found[0];
}

// Clicking a rhyme drops it straight into the line, replacing the word you
// selected. Hold shift to put it on the clipboard instead.
function wordAction(word) {
  return {
    title: word,
    icon: null,
    code: () => {
      if (popclip.modifiers.shift) popclip.copyText(word);
      else popclip.pasteText(word);
    },
  };
}

function message(text) {
  return [{ title: text, icon: null, code: () => popclip.showText(text) }];
}

module.exports = {
  options: [
    {
      identifier: "count",
      type: "multiple",
      label: "Rhymes to list",
      values: ["12", "24", "48", "100"],
      valueLabels: ["12", "24", "48", "100"],
      defaultValue: "24",
    },
    {
      identifier: "near",
      type: "multiple",
      label: "Near rhymes",
      description:
        "Slant rhymes, listed below a divider. Some words (orange, autumn, month) have no perfect rhyme at all.",
      values: ["auto", "always", "never"],
      valueLabels: ["When there are few perfect rhymes", "Always", "Never"],
      defaultValue: "auto",
    },
  ],

  action: {
    title: "Rhymes",
    // The population function belongs on an action, not on the extension:
    // PopClip only accepts a static array for a top-level `submenu`. It runs
    // when the submenu opens, so the lookup is only paid for on demand.
    submenu: (input, options) => {
      const found = candidates(input.text);
      if (found.length === 0) return message("Select a word first");

      const word = resolve(found, PERFECT);
      const limit = Number(options.count) || 24;
      const perfect = lookup(PERFECT, word);

      let near = [];
      const wantNear =
        options.near === "always" ||
        (options.near !== "never" && perfect.length < 3);
      if (wantNear) {
        const exclude = new Set(perfect);
        near = lookup(NEAR, resolve(found, NEAR)).filter((w) => !exclude.has(w));
      }

      if (perfect.length === 0 && near.length === 0) {
        return message(`No rhymes for “${word}”`);
      }

      // A full list of perfect rhymes shouldn't be buried under slant ones.
      const shownPerfect = perfect.slice(0, limit);
      const shownNear = near.slice(0, shownPerfect.length > 0 ? NEAR_CAP : limit);

      const items = shownPerfect.map(wordAction);
      if (shownNear.length > 0) {
        if (items.length > 0) items.push({ separator: true });
        items.push(...shownNear.map(wordAction));
      }

      // Everything, when the submenu only had room for the best few.
      if (perfect.length + near.length > shownPerfect.length + shownNear.length) {
        const all = [];
        if (perfect.length > 0) all.push(perfect.join(", "));
        if (near.length > 0) all.push(`Near rhymes: ${near.join(", ")}`);
        items.push({ separator: true });
        items.push({
          title: `Show all ${perfect.length + near.length}\u2026`,
          icon: null,
          code: () =>
            popclip.showText(`${word}\n\n${all.join("\n\n")}`, { style: "large" }),
        });
      }
      return items;
    },
  },
};
