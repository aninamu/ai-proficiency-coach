# AI Proficiency Coach

A Cursor plugin with one coaching skill. It places an engineer, eng leader or PM on a four-level AI proficiency framework (PL1-PL4, eight Steps), then gives one or two concrete Cursor next steps for the week and one thing to avoid.

It's a conversation, not a report. There's no data to gather, no score and nothing to install beyond the plugin: the skill works from what you tell it and what's visible in the chat, using the recognition cues in the framework to place you.

**You invoke it, it doesn't invoke itself** (`disable-model-invocation: true`). Agent never applies it on its own, never assesses you in the background, and never brings up your level while you're working on something else. Reach for it when you want a read — before a 1:1, at the start of a quarter, or when you're not sure what to try next. In Agent chat, type `/ai-proficiency-coach` followed by your question:

```text
/ai-proficiency-coach What PL am I?
/ai-proficiency-coach How do I get to PL3?
/ai-proficiency-coach What should I try next in Cursor?
/ai-proficiency-coach How do I move my team up a level?
```

Two reference files do the work: `references/framework.md` for what each level and Step means, and `references/cursor-playbook.md` for the recommendations. Every suggestion comes from the playbook, so the advice is the same whoever asks.

## Framework at a glance

| | PL1 | PL2 | PL3 (org target) | PL4 |
|---|---|---|---|---|
| Name | AI-Assisted | Reusable Agents | Delegational Orchestration | Governed Autonomy |
| Steps | 1 Explore · 2 Cursor-first | 3 Codify · 4 Standardize & verify | 5 Delegate & parallelize · 6 Agents act as you | 7 Governed pipelines · 8 Multiply |
| In practice | Cursor desktop (editor and Agents Window) is your daily default; Agent handles anything beyond a small edit. | Rules, `AGENTS.md` and skills carry your standards; Plan Mode for big changes; hooks, plugins and MCP extend the agent. | Scoped work goes to Cloud Agents and parallel agents; MCP lets agents act as you; you review. | Event-driven Automations behind approval gates, hooks and an audit trail; others adopt what you build. |

- **Four pillars**: Adoption, Reuse, Orchestration and Outcomes. Outcomes depends on your role: AI and cloud commits on the primary branch for a Developer IC, the group's spread for Eng Leadership, accepted agent diffs and Automations for a PM / Specialist.
- **Levels are cumulative**, so you're roughly where your four pillars agree. Being uneven across them is normal, and the uneven pillar is usually the useful thing to talk about.
- **It's a placement, not a measurement.** No score, no percentage, and "between Steps 3 and 4" is a perfectly good answer. `framework.md` section 2 lists what each pillar looks like from the outside at each level.

## Repository layout

```text
.cursor-plugin/
  plugin.json            # Cursor plugin manifest (name: ai-proficiency-coach)
  marketplace.json       # single-plugin marketplace manifest, source "./"
assets/logo.svg
skills/ai-proficiency-coach/
  SKILL.md               # the coaching procedure
  references/
    framework.md         # what each level and Step means; section 2 is what each looks like
    cursor-playbook.md   # Step -> recognition cue, features, exercise, avoid, org unblock
```

## Install

### As a local plugin

```bash
git clone <this-repo-url> ~/.cursor/plugins/local/ai-proficiency-coach
```

Then restart Cursor, or run **Developer: Reload Window**. Open **Customize** and check that the `ai-proficiency-coach` skill appears under Skills. Invoke it by typing `/ai-proficiency-coach` in Agent chat. Because the skill is manual-only, asking "what PL am I?" without the slash command won't load it.

Notes:

- Clone or copy the repo into the folder. Cursor skips symlinks in `~/.cursor/plugins/local` that point outside that folder.
- On Teams and Enterprise, local plugins load only if an admin has turned on **Allow Local Plugin Imports**. It's under Dashboard → Settings → Security & Identity → Marketplace and Plugins, and it's off by default on Enterprise.

### Through a team marketplace (Teams and Enterprise)

1. A team admin opens **Dashboard → Plugins & MCPs → Team Marketplaces → Add Marketplace**.
2. Choose **Import from Repo** and paste this repository's URL (or your fork's). The repo includes `.cursor-plugin/marketplace.json`, so the plugin is discovered automatically.
3. Under **Marketplace Settings**, set Marketplace Access and optionally turn on Auto Refresh. Choose an installation mode: Default Off, Default On or Required.
4. Developers then install it from **Customize**.

To add it to an existing team marketplace repo instead, add an entry to that repo's `marketplace.json` that points at a copy of this plugin folder.

## How it places you

There's nothing to feed it. The skill reads the "You'll recognize this stage when…" cue for each Step against what's already visible — how you're working with it, what you're asking for, and what your repo has in it — then asks one or two short questions to confirm before naming a Step.

The questions are about how you work, never for counts:

- "When something will take more than an hour, do you start in Plan Mode or go straight in?"
- "Is there a workflow you've turned into a rule or skill, or do you re-explain it each time?"
- "Have you handed a whole ticket to a Cloud Agent and reviewed the PR?"
- "Does anything run without you starting it?"

Then it names the Step, gives one or two actions from that Step's playbook entry, and one thing to avoid.

If you want this measured across an org rather than coached one person at a time, that's a different exercise, built on the Cursor Admin, Analytics and AI Code Tracking APIs (Enterprise). This plugin deliberately doesn't do it: a number invites comparison, and the next step is the part that actually helps.

## Privacy

- **Nothing is collected.** The skill reads no usage data, no local databases and no telemetry. It makes no network call and writes no files.
- **It won't go looking.** It doesn't ask for usage exports or dashboards, and it doesn't read your history, prompts, code or diffs to assess you.
- **No score to pass around.** The output is a Step and a couple of suggestions, not a number that can end up in a spreadsheet.
- **For coaching, not appraisal.** Say the word and it'll tell you the same.

## Limitations

- The placement is as good as the conversation. Someone having an unusual week, or being terse, will be placed roughly — which is why it says "around Step 3" rather than claiming precision.
- It only knows what you tell it. If you undersell what you're already doing, the next step will be one you've outgrown; say so and it'll move up.
- Nobody is "at" one Step. Pillars move at different speeds, and the uneven one is usually the interesting conversation.
- Leaders get coached on their own work plus one or two org unblocks. For a real picture of how a group is spread, you need data this plugin doesn't collect.

## Development

Three markdown files, no code and nothing to run. Keep the actions, exercises, what to avoid and org unblocks in `cursor-playbook.md` only, and what each level means in `framework.md` only, so there's one place to change each.

## License

[MIT](LICENSE)
