# AI Cognitive Apprenticeship — Learn From AI's Reasoning Process

**When to use:** You're asking AI to solve a problem and want to learn *how* it gets there — observations, hypotheses, debugging steps, analysis — not just the solution. Use in Orient phase to set the mode, and in Execute phase to extract reasoning alongside code.

## The 6 Methods (Cognitive Apprenticeship Framework)

| Method | What AI does | Your prompt pattern |
|---|---|---|
| **1. Modelling** | Solves the problem while narrating full reasoning aloud — observations, dead ends, decisions | `"Solve this. Show your full reasoning: what you notice first, hypotheses you form, what you test, what you eliminate, why you choose the final approach. Then give the solution."` |
| **2. Coaching** | Watches you try to solve, then critiques your *process* | `"I'll try to solve it. Watch my approach and tell me where my reasoning goes wrong, not just the final answer."` |
| **3. Scaffolding** | Provides partial solution / hints, you fill gaps | `"Give me the first 30% of the solution — enough to get oriented — then let me take over."` |
| **4. Articulation** | Asks *you* to explain your reasoning, then critiques | `"Ask me how I'd approach this before you answer. Then correct my reasoning step by step."` |
| **5. Reflection** | After solving, shows how it *would have* solved it differently | `"Now reflect: what would you have done differently with more context? What were the tradeoffs you considered and rejected?"` |
| **6. Exploration** | Points direction, you explore independently | `"Don't solve it. Tell me what I should investigate first and what tools/techniques to use."` |

## The Two-Pass Learning Protocol

From Anthropic's RCT (Jan 2026): developers who asked follow-ups and requested explanations retained 17% more than passive AI users.

### Pass 1 — Process
```
Debug this bug. Before you give me any code, walk me through:
1. What do you observe first about the code/error?
2. What hypotheses do you form?
3. What would you test to confirm/eliminate each?
4. How do you narrow to the root cause?
5. What fix options do you consider? Why this one?
THEN give me the fix.
```

### Pass 2 — Reflection
```
Now reflect on what you just did:
- What other approaches did you consider and reject?
- What in the codebase misled you or was confusing?
- What would you do differently with more context?
- What pattern from this should I remember for next time?
```

## Debugging-with-Reasoning Protocol

When asking AI to debug, use this structure to extract the thinking:

```
The bug: [describe]
The error: [error message]
What I tried: [optional]

Please:
1. List what you observe looking at this code — don't jump to conclusions
2. Rank hypotheses by likelihood with your reasoning for each
3. For your top hypothesis: what specific evidence supports it?
4. Show the fix AND explain why it fixes the root cause, not just the symptom
5. What would have been the best way to catch this bug earlier?
```

## Git Safety Net (Required Companion)

Always pair cognitive apprenticeship with git checkpoints so you can learn freely without fear:

```
# Before any AI reasoning session
git checkout -b learn/<topic-date>
git add -A && git commit -m "init: state before AI reasoning session"

# After each interesting learning insight / AI code generation
# (even if incomplete — commit the learning checkpoint)
git add -A && git commit -m "learn: [what the AI discovered/taught]"

# If AI goes down a bad path — revert to last good checkpoint
git reset --hard HEAD

# If AI goes completely off — nuke the whole branch experiment
git checkout main && git branch -D learn/<topic>
```

Commit message format for learning sessions:
```
learn: <concept learned>
learn: debugging pattern — <pattern>
learn: design decision — <tradeoff>
learn: rejected approach — <why not>
```

## Integration with Feynman Workflow Phases

### Orient phase
> "Learning goal: understand how [framework/tool] handles [concept]. I'll use cognitive apprenticeship Modelling to extract the AI's reasoning."

### Execute phase — BEFORE→AFTER with reasoning annotations
```
BEFORE: [code before] — AI's observation: "I noticed X which suggests Y"
AFTER:  [code after]  — AI's reasoning: "Changed to Z because..."
```

### Verify phase
> "Now reflect: what was the key insight I should take away from this session?"

## Reference

- arXiv 2601.19053 — "From Answer Givers to Design Mentors: Guiding LLMs with the Cognitive Apprenticeship Model"
- arXiv 2601.16720 — "Watching AI Think: User Perceptions of Visible Thinking in Chatbots"
- Anthropic (Jan 2026) — "How AI assistance impacts the formation of coding skills" (RCT showing follow-up questions improve retention)
- bswen.com — "What Git Workflow Should You Use With AI Coding Tools?"
- understandingdata.com — "Checkpoint Commit Patterns: Git Strategies for AI-Assisted Development"
