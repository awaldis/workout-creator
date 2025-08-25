# Goal
Extract workout data from a single-page Remarkable 2 image containing printed exercise lines and handwritten results.

# Output
Return TWO blocks only, in this order:
1) A **CSV** code block (label `csv`) with the header:
   date_completed,exercise_name,laterality,sets,weight_left,weight_right,reps_left,reps_right
2) A **JSON** code block (label `json`) named `warnings`.

# CSV shape (one row per EXERCISE)
- **date_completed**: YYYY-MM-DD, from the printed date at the top.
- **exercise_name**: printed text BEFORE the **last** hyphen-like char (one of `- – —`) on that exercise line; trim; preserve interior hyphens.
- **laterality**: "unilateral" or "bilateral".
- **sets**: integer count of sets per side (see padding rule below).
- **weight_left, weight_right, reps_left, reps_right**:
  - Values for **all sets** encoded in a single cell, joined by **semicolons** with **no spaces**, e.g., `115;115` or `30;25`.
  - Units: pounds for weights (strip `#`), reps are integers.
  - For **unilateral** exercises: write actual values in `*_left`; set `*_right` to **zeros repeated `sets` times** (e.g., `0;0`), as requested.
  - If the handwriting omits repeated weights, **expand** by repeating the most recent weight for later sets.
  - If **no weight** is present anywhere in the box, weights are `0` for all sets.

# Parsing rules (handwriting inside each box)
- Normalize: treat `×` as `x`; treat `- – —` as `-`; ignore extra unicode spacing.
- Tokens
  - WEIGHT := 1–3 digits + `#`  (e.g., `190#`)
  - REPS   := 1–3 digits         (e.g., `20`)
  - PAIR   := (WEIGHT)? SP* `x` SP* REPS  (e.g., `115# x 20`, `190#x15`)
- **Unilateral pattern**
  - Sequence of PAIRs separated by commas. If later PAIRs omit WEIGHT, reuse the most recent WEIGHT.
- **Bilateral pattern**
  - Box contains two labeled segments starting with `L` or `R` followed by `:` or `-` (e.g., `L - ... R - ...`) in any order.
  - Parse each side independently using the Unilateral rules.
  - **sets** = the **maximum** of left/right set counts. Pad the **shorter side** with `NA` for the missing trailing entries. Emit a warning about the mismatch.
- Limits & sanity
  - All numeric tokens must be < 1000. Skip 4+ digit tokens, pad with `NA`, and warn.
  - Preserve any non-parsed scribbles by listing them in `warnings` (do **not** place them in CSV cells).
- Ambiguity
  - If a token cannot be confidently parsed, write `NA` for that position and add a warning. Do **not** invent values.

# Warnings JSON (second block)
Output a JSON object:
{
  "page_level": [ "...free-text messages..." ],
  "exercise_level": [
    { "exercise": "<exercise_name>", "issues": ["<message>", "..."] },
    ...
  ]
}

# Response formatting
- First: CSV in a fenced block labeled `csv`.
- Second: JSON in a fenced block labeled `json`.
- No extra prose before/after the two blocks.

# Examples (format illustration only)
- Unilateral:
  - Handwriting: `Chin-ups` box: `8, 6`
  - CSV cells: laterality=`unilateral`, sets=`2`, weight_left=`0;0`, reps_left=`8;6`, weight_right=`0;0`, reps_right=`0;0`
- Bilateral with equal sets:
  - Handwriting: `L - 5# x 30, 12# x 25   R - 5# x 30, 12# x 25`
  - weights_left=`5;12`, reps_left=`30;25`, weights_right=`5;12`, reps_right=`30;25`, sets=`2`
- Bilateral with mismatch (pad with NA and warn):
  - Left has 3 sets, Right has 2 → sets=`3`; right-side lists end with `NA` (e.g., `weights_right=50;50;NA`, `reps_right=12;10;NA`)
