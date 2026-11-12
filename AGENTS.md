# Agent notes

## Worktrees and disk space

The disk on this machine is small, and each full worktree of this project is about 5 GB. Most of that is source art.

- **New worktrees are slim by default.** A local git hook leaves out `Art Source/Apartment Redesign` (2.4 GB of Blender, FBX and texture sources). Everything else is checked out: `Content`, `Source`, `Tools`, `docs`, and the rest of `Art Source` (Audio, Portraits, Character Art and so on).
- **Art work gets the full checkout.** Branches named `art/*` or `environment/*` keep everything.
- **If a slim worktree needs the art**, for example to run a `Tools/Editor/import_redesign_*` script, an Apartment Design handoff script, or anything that reads `Art Source/Apartment Redesign`, run this inside the worktree:

  ```sh
  git sparse-checkout disable
  ```

  To create a worktree with the art already included, prefix the command: `ART_SOURCE=full git worktree add ...`.
- **To make a worktree slim again** after finishing art work:

  ```sh
  git sparse-checkout set --no-cone '/*' '!/Art Source/Apartment Redesign/'
  ```

- `git status` in a slim worktree shows nothing for the missing folder, and commits leave those files untouched. Don't recreate or delete files under that path by hand.
- Remove a worktree with `git worktree remove` once its branch is merged. Each one you leave behind holds 2–5 GB.
