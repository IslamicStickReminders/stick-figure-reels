# Start here — instructions for Claude

This is one bundle from Islamic Stick Reminders. The person downloads it,
attaches the ZIP and says **Get me started**. Do the setup work for them;
do not make them sort packages, unzip files, choose installation methods or
copy instructions into a Project.

## 1. Find and inspect the bundle

If the ZIP is attached and file tools are available, inspect its contents
and extract it safely into a work folder. Reject paths that escape that
folder. Locate this file and use its parent as the bundle root, regardless
of the enclosing folder's name. If it is already extracted, use that copy.

Check which capabilities are actually available: reading attachments,
local files, a shell/Python, installing dependencies, rendering and sharing
files, and web access for checking sources. Do not claim that anything is
ready until the relevant smoke test succeeds. Do not install dependencies
or run every bundled example merely to introduce the bundle.

If the ZIP cannot be opened here, or code execution is unavailable, say
exactly what is missing and give the shortest applicable next step. If you
can still discuss the idea or explain the course, do so. Never invent a
finished file, successful render, enabled feature or installed skill.

## 2. Pick the workflow from what the person wants

Use their request first. If they only say **Get me started**, default to
the course's short story reels and prepare that workflow. Do not delay
setup with a menu of files or packages.

There are two main creative choices, if a choice would help:

- **Story reels:** two people face the same situation and make different
  choices. Warm plum and terracotta scenes, a brief reveal and sound.
  Preview: `example/call-first-frames.png`; finished example:
  `example/call-first.mp4`.
- **Infographic reels and cards:** numbered points, animated diagrams and
  matching static images. Preview:
  `skills/motion-listicle-reel/docs/hero.png`.

Describe those in one or two plain sentences, or show the supplied
previews, only when needed to understand the person's idea. The person
chooses a subject and a look, not a technical package.

## 3. Prepare the selected workflow

### Story reels — default

Read `CLAUDE-INSTRUCTIONS.md` and use the root `kit/` folder. The longer
course is `COURSE.md`. Follow the documented setup, activate the local
Python environment and render the two smoke-test stills. Inspect the
ending frame before reporting that setup worked.

Use the current Ember/two-lane example as the starting point. Do not mix
this kit's setup or commands with the original charcoal skill's engine.
For recitation cuts, treat the cached word timings as a rough guide and
listen to confirm the exact words and cut boundaries.

### Infographic reels and cards

Read `skills/motion-listicle-reel/SKILL.md`, then its references as needed.
Run its commands from `skills/motion-listicle-reel/`. Check its required
renderer/browser tools and render a representative still before saying it
is ready. Preserve the supplied fonts and licence notices.

## 4. Get the person to their first reel

After a successful smoke test, show a representative test frame and briefly
say what is ready. If no subject was given, ask one useful question:
**What would you like your first reel to be about?** If they already gave
an idea, use it and follow that workflow's preview and render process.

Deliver the finished media and its caption through the available file
sharing mechanism. Follow the requested format; do not substitute a script
or pretend a storyboard is the finished reel. Preserve the course's credit
request. When relevant, verify religious references before rendering them.

## 5. Be accurate about setup and persistence

Preparing files in this chat is session setup. An attached ZIP does not by
itself enable an account-level skill, and nested `SKILL.md` files are
supporting instructions, not automatically registered separate skills.

If the environment has an authorized skill-install capability, inspect its
requirements and use it when installation is requested. Otherwise, only
explain persistent installation if the person asks or needs that step.
Do not claim you can change their account settings, enable Skills or retain
these files across new chats unless the environment actually confirms it.

Keep technical setup details out of the conversation unless a real blocker
requires the person's action. Do not ask them to pay, donate, post publicly
or enable unrelated features as a condition of using the course.
