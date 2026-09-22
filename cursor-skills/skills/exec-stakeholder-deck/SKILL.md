---
name: exec-stakeholder-deck
description: Build PowerPoint presentations for executives, leadership, or other senior stakeholders. Use this whenever the user asks for a deck, slides, or presentation aimed at execs, leadership, a steering committee, a sponsor, or "the business" — including phrases like "exec review," "leadership update," "board deck," "steering committee," "stakeholder presentation," or "I need to present this to my VP/director/sponsor." Drives the work through a stakeholder-analysis framework (audience, goal, what matters to them, why they'd act, their objections, why they should listen) before writing a single slide, then builds the .pptx itself. Use even if the user doesn't explicitly ask for the framework — just says "make me a deck for leadership."
---

# Executive Stakeholder Deck

Most decks fail before anyone opens PowerPoint: the builder starts from the content they have, not from the person who has to read it. An executive skims for 90 seconds, decides whether to act, and moves on. A deck built around what the presenter knows reads as a data dump; a deck built around what the audience needs to decide reads as a recommendation. This skill exists to force the second kind.

The method is a six-question stakeholder analysis, done *before* any slide gets written, followed by a build that keeps every slide answerable back to those six answers.

## Step 1: Run the stakeholder analysis

Do not start drafting slides until you have real answers — not placeholders — to these six questions. If the user hasn't given you enough to answer one, ask. A vague answer here (e.g. "leadership" as the audience) produces a generic deck; push for specifics the same way you would push a colleague who said "just make it good."

1. **Who is my audience?** Names or roles if possible (e.g. "David and Chris, my two managers" or "the LATC steering committee"), not just "execs." What do they already know about this topic? What's their relationship to it — sponsor, approver, informed bystander?

2. **Goal — what do I want them to do as a result of this presentation?** Force a single answer into one of three buckets, because each implies a different deck shape:
   - *Information* — they need to understand something; no decision is being asked for today. Deck emphasizes clarity and context, ends with a summary, not an ask.
   - *Call to action* — they need to approve, fund, or greenlight something in this meeting. Deck builds to one explicit ask with a clear decision framed on one slide.
   - *Future call to action* — this is groundwork for a decision later. Deck plants the case and previews what's coming, without forcing a decision now.

3. **What is important to this audience?** Not what's important to the presenter. A technical audience cares about feasibility and risk; a finance-oriented sponsor cares about cost and ROI; an operations exec cares about timeline and disruption. This answer determines which facts make the cut and which get cut, no matter how interesting they are to the builder.

4. **Why would they act?** The motivation that gets this specific audience to say yes — cost savings, risk reduction, competitive pressure, alignment with a stated priority of theirs. This becomes the throughline of the narrative, not a bullet buried on slide 8.

5. **What could be their objections?** Name the real ones — cost, timing, "we tried this before," political risk, resourcing. Each real objection gets addressed somewhere in the deck (a slide, a callout, or a backup/appendix slide), so the exec doesn't have to ask and doesn't get to dismiss the deck on a gap.

6. **Why should they pay attention to me?** The presenter's credibility or standing on this topic — track record, ownership of the space, data no one else has. This shapes the tone of the opening (lead with authority/context) but isn't usually its own slide.

If the user gives you source material (a project doc, ticket, Confluence page, prior deck) instead of direct answers, extract answers to all six from it and confirm your read with the user in one short pass before building — e.g. "Sounds like: audience = David + Chris, goal = call to action (approve budget), main resistance is likely cost and 'why now.' Sound right?" Don't silently guess on the goal type or the audience — get those two confirmed, since they drive the whole structure; the other four can be stated as assumptions if the user is in a hurry.

## Step 2: Translate the analysis into a slide plan

Before opening the pptx skill, write a short slide-by-slide outline (title + one-line purpose per slide) and map each slide back to one of the six answers. This is the check that keeps the deck honest — if a slide doesn't serve the goal, the audience's priorities, the motivation, or an objection, cut it or move it to appendix.

A goal-driven shape to start from (adjust freely — this isn't a template to fill mechanically):

- **Title slide** — topic, presenter, date. Nothing else.
- **The headline / BLUF slide** — one sentence stating the point of the whole deck, framed around the audience's stated priorities (from Q3) and the goal (Q2). An exec who reads only this slide should get the message.
- **Context, briefly** — only the background this specific audience doesn't already have. Skip what they know.
- **The core content** — 2-5 slides max, each making one point, each traceable to what matters to this audience (Q3) or the motivation to act (Q4). Prefer one chart, one table, or one clear statement per slide over dense paragraphs.
- **Addressing resistance** — either woven into the relevant content slide or as a dedicated "here's what you might be thinking" slide, covering the real objections from Q5. Don't dodge the hard one; naming it first is more credible than hoping it doesn't come up.
- **The ask (if Q2 is Call to Action)** — one slide, one explicit ask, stated as a decision or approval, not a vague "thoughts?" Include what happens next if they say yes and the cost of saying no or waiting, if relevant.
- **Close / next steps** — what happens after this meeting regardless of the answer.
- **Appendix** — detailed data, backup for objections that came up in prep but don't need airtime unless asked, source links. Execs rarely read this in the room, but its presence signals rigor and gives you somewhere to put material that would otherwise bloat the core deck.

Share this outline with the user before building the full deck, unless they've explicitly said to just go. A wrong turn caught at the outline stage costs one message; caught after the deck is built, it costs a rebuild.

## Step 3: Build the deck

Once the outline is confirmed (or the user says to proceed), read the `pptx` skill's SKILL.md and build the actual `.pptx` file with it. A few things specific to executive decks, on top of whatever the pptx skill itself instructs:

- **Density**: executives are reading fast — cap most content slides at one core idea, a headline sentence, and supporting visual/bullets. If a slide needs more than ~6 bullets or a paragraph of prose to make its point, it's probably two slides or belongs in the appendix.
- **Headlines carry the argument**: title each content slide with the takeaway, not the topic — "Vendor consolidation cuts licensing cost 30%" beats "Vendor Analysis." An exec should be able to read just the titles top to bottom and get the argument.
- **No unexplained jargon or raw IDs**: write for someone who doesn't live in the project day to day, even if the requester does — this mirrors the same instinct that keeps Jira tickets and Confluence pages free of raw field dumps and unexplained shorthand.
- **Visuals over paragraphs**: where the content permits, prefer a simple chart, comparison table, or timeline to a block of text — see the `dataviz` skill if a chart is involved.
- **One ask, stated plainly**: if Q2 was Call to Action, the ask slide should be unambiguous about what a "yes" means and what happens next. Don't bury the ask in a summary bullet.

## Step 4: Sanity-check against the six answers before delivering

Before sending the deck, walk back through the six questions one more time as a checklist:

- Does the opening reflect what this audience (Q1) already knows, without over-explaining?
- Does the deck clearly serve the stated goal (Q2) — informs, asks, or plants a seed, and nothing more ambitious than that?
- Would this audience recognize their own priorities (Q3) in what got emphasized?
- Is the motivation to act (Q4) explicit somewhere, not just implied?
- Is every real objection (Q5) addressed somewhere, even briefly?
- Does the framing establish why this presenter/analysis should be trusted (Q6)?

If any answer is no, that's the fix to make before calling the deck done — not a note to leave for the user to catch.
