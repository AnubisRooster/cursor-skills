---
name: writing-voice
description: >-
  Rewrite and draft outbound prose in Mike Fink's voice so it reads human, not
  AI. Use when writing or editing emails, Slack/Teams messages, Confluence page
  bodies, meeting notes, status updates, leadership asks, or when the user says
  humanize, less robotic, sound like me, draft an email, or write a wiki page.
  Do not use for code, JSON, HTML dashboards, commit messages, or Jira field
  contracts (AC/DoR/DoD/BV).
---

# Writing voice (Mike Fink)

Apply this whenever the output is meant to be sent or published as Mike, not as chat back to him.

Mike's own rules, verbatim:

- My sentence length is usually about as long as the previous sentence, if not shorter.
- I am always cordial and friendly, but also frame things in terms of problem/ask(s)/risks if we don't do something.
- Formal in Confluence but less formal sounding in emails and Slack.

## Default shape

Lead with the situation. Then the ask. Then what happens if we wait.

```
Problem:  what is broken or blocked, in plain language
Ask(s):   what you need from the reader, named, with a by-when if you have one
Risk:     the concrete cost of inaction (velocity, spend, date, access, people idle)
```

Do not label those words unless the channel wants headings (Confluence does). In email and Slack, the shape is the same but the labels stay off the page.

## Cadence

- Start in the middle. No warmup paragraph.
- Sentences stay medium. The next one should match or get shorter. Never stack a longer sentence after a long one.
- Fragments are fine when they land the point. "It is a cross pillar effort."
- Collaborative: we / let's / can we. Direct, not bossy.
- Cordial: please, thanks, Good day. Not groveling.
- Concrete nouns. Credits, dates, teams, dollars, regions. Not "stakeholders" and "alignment across the organization" unless those are the actual words needed.
- One idea per sentence. If you need a list of asks, use short questions or short bullets, not a polished triad.

Openers that sound like him:

- "Let's clarify the ask."
- "Take a look at this please."
- "Following up here."
- "Good day!" after names, in email.
- "The problem:" then one plain sentence.

## Channel

**Email** — less formal. Names, then Good day or Hi. Short paragraphs. Asks as questions. One risk sentence. Close with thanks. Sign off Best / Thanks, Mike.

**Slack / Teams** — even less formal. Skip Good day. Two to six sentences. Can open with the problem. @people only when they own the ask. No sign-off essay.

**Confluence** — formal. Complete sentences. Capitalize. Headings. No chat openers (no Good day, no ok, no let's just). Still his cadence: short, problem / ask / risk, no brochure language. Preferred headings: Problem, Ask, Risk if we don't. Add context sections only if the page needs them (Background, Scope, Out of scope).

## Ban list (usual AI tells)

Do not use these, even once:

- Hope this finds you well / I wanted to take a moment / I hope you're doing well
- Here's a comprehensive overview / In today's fast-paced / It's important to note
- Leverage, synergy, delve, landscape, robust, seamless, holistic, utilize (say use)
- Additionally / Furthermore / Moreover / That said / With that in mind
- Key takeaways / In conclusion / To summarize / Going forward
- Please don't hesitate to reach out / Let me know if you have any questions as a closer
- Happy to help / Happy to dive deeper / I'll go ahead and
- As an AI / As a language model
- Emoji, em-dash chains, Title Case blog headings
- Bold on every other phrase. One bold run is plenty, and usually none.
- Three parallel bullets that all start with the same verb and the same rhythm
- Restating the whole situation before the ask
- Fake warmth: "Thanks so much for your incredible partnership"

## What this skill is not

- Chat replies to Mike in Cursor. Those stay terse per session rules.
- Jira custom-field contracts. `jira-create-issues` still owns AC/DoR/DoD/BV. If you write a Jira *narrative* (summary of a problem for humans), use this voice inside that narrative only.
- HTML dashboards, code, JSON, YAML, commit messages.

## Before you send the draft

Read it out loud once. Cut any sentence that only restates the last one. Cut any word he would not say in a meeting. If two asks exist, keep both; don't merge them into a vague "alignment."

If the user pasted source material, keep the facts. Change only the voice and the shape.

For before/after samples, see [examples.md](examples.md).
