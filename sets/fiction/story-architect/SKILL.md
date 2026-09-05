---
name: story-architect
description: "Use when planning a new story, building a plot, writing a chapter or scene beat list, or reworking a story's structure, before any prose is drafted. Runs the planning half of sepia's fiction workflow (architecture sheet, 3 to 5 moves plus one rarity move, outline, echo test), adds a choice of structure, and stops at the plan for sign-off instead of drafting."
license: MIT
metadata:
  requires: sepia, placed alongside this skill as ../sepia
---

# Story architect

A thin skill over sepia. Sepia's fiction workflow A plans and drafts in one run. This skill runs the planning half, adds a structure choice, and stops so the author reviews the plan before any prose exists.

Read `../sepia/SKILL.md` first, in full. Its calibration rule and hard guardrails apply here unchanged.

## Workflow

Steps 1, 2, 3, and 5 are sepia workflow A steps 1 to 4. Step 4 and the stop are this skill's additions.

1. **Premise.** Promise to the reader in one sentence, then genre and length. Genre sets the calibration targets. If the premise is one sentence and nothing more, ask for material before going on.
2. **Architecture sheet.** Fill the sheet in `../sepia/references/narrative-pass.md`. Work through all seven groups. Write a choice for every row, including the ones left at their default.
3. **Moves.** Select 3 to 5 human-leaning moves and exactly one rarity move. Name them in the plan.
4. **Structure.** Choose one from [references/structures.md](references/structures.md) and say why. None is the default.
5. **Outline.** Write the beat list. Run the outline and QUD checks in `../sepia/references/discourse-pass.md` §1, the middle check in §2, and the echo test in narrative-pass §2 on every turning point.
6. **Stop.** Write the plan and wait for sign-off. Drafting, sepia workflow A step 5 onward, is a separate step the author starts.

## The plan

One document. Sections, in this order:

- Premise and promise. Genre, length, intended reader.
- Architecture sheet, with the chosen moves and the rarity move marked.
- Structure, and why it fits this premise.
- Beat list.
- Echo test, one line per turning point: what a generic regeneration would do here, and what this story does instead.
- One alternative plan that was considered and why it lost. A different structure or a different resolution driver, not a variation of the same plan.
- Open questions for the author.

Save it where the project keeps structure documents (for the novel template, `structure/architecture.md` and `structure/outline.md`).
