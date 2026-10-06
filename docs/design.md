# ForensiWeb — UI/UX Design System

**File:** `design.md`  
**Status:** Source of Truth  
**Version:** 1.0  
**Design Direction:** Futuristic / AI-Inspired Cybersecurity  
**Primary Experience:** Dark Analyst Command Center  
**Product:** ForensiWeb

---

# 1. Design UI Principles

## 1.1 Design Vision

ForensiWeb should feel like a:

> **Modern cybersecurity command center combined with a forensic investigation workspace.**

The interface must communicate:

- intelligence;
- security;
- technical sophistication;
- evidence;
- investigation;
- trust;
- precision;
- control.

The UI should feel futuristic without becoming visually noisy or looking like a generic AI chatbot.

---

## 1.2 Primary Design Direction

The selected visual direction is:

```text
Futuristic
    +
Dark Cinematic
    +
Technical
    +
Professional
    +
Data-Driven
    +
AI-Inspired
```

The interface should use dark surfaces, cool blue/cyan accents, subtle gradients, restrained glow effects, data visualizations, and structured information layouts.

---

## 1.3 Design Principles

| Principle | Requirement |
|---|---|
| Clarity | Important information must be immediately understandable |
| Hierarchy | Critical security information must receive visual priority |
| Consistency | Similar interactions must look and behave consistently |
| Precision | Forensic information must be displayed accurately |
| Explainability | Findings should clearly communicate why they exist |
| Density | Analyst dashboards may contain high information density without clutter |
| Focus | Avoid unnecessary decorative elements |
| Responsiveness | Interface should adapt to different screen sizes |
| Accessibility | Important information must not depend only on color |
| Feedback | User actions must produce visible feedback |
| Trust | Evidence and findings must look authoritative and traceable |
| Performance | Animations and visual effects must not harm usability |

---

# 1.4 Analyst-First Design

ForensiWeb is primarily an analyst/investigator platform.

Therefore:

```text
User
 ↓
Question
 ↓
Evidence
 ↓
Event
 ↓
Finding
 ↓
Investigation
```

The interface should help the analyst answer:

- What happened?
- When did it happen?
- What evidence supports it?
- Which attack stage occurred?
- What triggered the detection?
- What happened before and after the event?
- How confident is the conclusion?
- What should be investigated next?

---

# 1.5 Visual Hierarchy

The interface must visually prioritize information in this order:

```text
Critical Security Information
        ↓
Investigation Findings
        ↓
Attack Timeline
        ↓
Evidence / Events
        ↓
Supporting Analytics
        ↓
Secondary Metadata
```

Critical alerts should never be visually buried beneath decorative elements.

---

# 1.6 Dark-First Experience

Dark mode is the primary visual mode.

The default application environment should use:

- dark navy background;
- slightly lighter navigation surfaces;
- layered dark cards;
- blue/cyan accents;
- controlled glow;
- high-contrast text.

A future light mode may be introduced, but it must not be implemented at the expense of the primary dark experience.

---

# 1.7 Layered Interface

The UI should use multiple visual layers.

```text
Application Background
        ↓
Navigation Layer
        ↓
Content Layer
        ↓
Card Layer
        ↓
Interactive Layer
        ↓
Modal / Detail Layer
```

Each layer should have a subtle difference in:

- background;
- border;
- elevation;
- shadow;
- contrast.

Avoid excessive glassmorphism.

---

# 1.8 Controlled Glow

Glow effects are allowed only for:

- active navigation;
- selected elements;
- critical data;
- attack-chain nodes;
- interactive focus;
- important alerts;
- AI/analysis states.

Do not apply glow to every component.

> **Glow should communicate state, not decoration.**

---

# 1.9 Information Density

Forensic analysis requires substantial information.

Therefore, ForensiWeb should support:

- compact tables;
- expandable rows;
- filtering;
- sorting;
- search;
- pagination;
- side panels;
- drill-down views;
- contextual details.

However:

> **High information density must never become visual clutter.**

---

# 1.10 Interaction Philosophy

Interactions should feel:

- fast;
- predictable;
- responsive;
- deliberate.

Use:

```text
Hover
 ↓
Visual feedback
 ↓
Click
 ↓
State transition
 ↓
Result feedback
```

Important interactions should never appear unresponsive.

---

# 1.11 Progressive Disclosure

Do not show every technical detail immediately.

Use:

```text
Summary
   ↓
Detailed View
   ↓
Technical Evidence
   ↓
Raw Evidence
```

Example:

```text
Suspicious Event
      ↓
Why was this detected?
      ↓
Related Events
      ↓
Evidence Artifact
      ↓
Raw Log Entry
```

This keeps the main interface understandable while preserving forensic depth.

---

# 1.12 Visual Language

The visual language should combine:

### Primary

- dark navy;
- electric blue;
- cyan;
- cool white.

### Supporting

- violet;
- indigo;
- slate;
- muted blue-gray.

### Security States

- red;
- amber;
- green.

Security colors must be used semantically rather than decoratively.

---

# 2. Required Colour Palette

## 2.1 Core Palette

| Token | Hex | Purpose |
|---|---|---|
| `bg-primary` | `#050B14` | Main application background |
| `bg-secondary` | `#08111F` | Secondary background |
| `bg-tertiary` | `#0C1728` | Navigation / elevated sections |
| `surface-primary` | `#0F1B2D` | Main cards |
| `surface-secondary` | `#132238` | Secondary cards |
| `surface-hover` | `#172A43` | Hover state |
| `border-default` | `#1E3552` | Standard borders |
| `border-active` | `#2B6FFF` | Active/selected border |

---

## 2.2 Primary Accent Palette

| Token | Hex | Purpose |
|---|---|---|
| `accent-blue` | `#2F80FF` | Primary interaction |
| `accent-blue-light` | `#4DA3FF` | Hover/highlight |
| `accent-cyan` | `#22D3EE` | Data/forensic accent |
| `accent-cyan-light` | `#67E8F9` | Highlight |
| `accent-indigo` | `#6366F1` | Secondary accent |
| `accent-violet` | `#8B5CF6` | AI/analysis accent |

---

## 2.3 Text Palette

| Token | Hex | Purpose |
|---|---|---|
| `text-primary` | `#F8FAFC` | Main text |
| `text-secondary` | `#CBD5E1` | Secondary text |
| `text-muted` | `#94A3B8` | Supporting text |
| `text-disabled` | `#64748B` | Disabled text |
| `text-inverse` | `#020617` | Text on bright surfaces |

---

## 2.4 Security State Palette

| State | Token | Hex | Usage |
|---|---|---|---|
| Critical | `status-critical` | `#EF4444` | Critical security finding |
| High | `status-high` | `#F97316` | High severity |
| Medium | `status-medium` | `#F59E0B` | Medium severity |
| Low | `status-low` | `#EAB308` | Low severity |
| Informational | `status-info` | `#38BDF8` | Informational |
| Success | `status-success` | `#22C55E` | Successful operation |
| Neutral | `status-neutral` | `#64748B` | Unknown/neutral |

---

# 2.5 Colour Usage Rules

### Rule 1

Blue/cyan are the primary product colors.

### Rule 2

Red/orange/yellow/green must communicate meaningful states.

### Rule 3

Never use red simply because it looks attractive.

### Rule 4

Do not communicate critical information through color alone.

Example:

```text
🔴 CRITICAL
```

instead of relying only on a red background.

---

# 2.6 Gradient System

Gradients should be subtle.

Recommended conceptual gradients:

```text
Primary:
Blue → Cyan

AI:
Indigo → Violet → Blue

Background:
Dark Navy → Deep Blue

Critical:
Red → Orange
```

Gradients should primarily appear in:

- hero areas;
- selected states;
- charts;
- attack-chain visualization;
- AI analysis areas;
- important CTA elements.

Avoid gradients on every card.

---

# 2.7 Glow System

Recommended glow usage:

```text
Blue Glow
→ active / interactive

Cyan Glow
→ forensic / analytical

Violet Glow
→ AI / intelligence

Red Glow
→ critical threat

Green Glow
→ successful operation
```

Glow must remain subtle and should not reduce text readability.

---

# 3. Typography

## 3.1 Typography Direction

Typography should feel:

- modern;
- technical;
- highly readable;
- professional;
- compact enough for analyst dashboards.

Recommended primary font:

> **Inter**

Recommended technical/monospace font:

> **JetBrains Mono**

---

# 3.2 Font Families

### Primary UI Font

```text
Inter
```

Used for:

- headings;
- navigation;
- buttons;
- cards;
- tables;
- forms;
- dashboard content.

### Monospace Font

```text
JetBrains Mono
```

Used for:

- IP addresses;
- hashes;
- command output;
- log entries;
- file paths;
- process IDs;
- timestamps where technical precision is important;
- code;
- raw evidence.

---

# 3.3 Typography Scale

| Token | Size | Weight | Usage |
|---|---:|---:|---|
| `display-xl` | 32px | 700 | Major dashboard title |
| `display-lg` | 28px | 700 | Page heading |
| `heading-xl` | 24px | 700 | Section heading |
| `heading-lg` | 20px | 600 | Card/section heading |
| `heading-md` | 18px | 600 | Subsection |
| `body-lg` | 16px | 400 | Important content |
| `body-md` | 14px | 400 | Standard UI |
| `body-sm` | 13px | 400 | Secondary content |
| `caption` | 12px | 400 | Metadata |
| `micro` | 11px | 500 | Compact labels |

---

# 3.4 Font Weight

Use a limited weight system:

```text
400 — Regular
500 — Medium
600 — Semibold
700 — Bold
```

Avoid unnecessary font-weight variation.

---

# 3.5 Monospace Data

Technical information should visually distinguish itself.

Example:

```text
2026-10-06T10:31:22Z
10.0.0.25
SHA256: 8f4a...91cd
PID: 4821
/usr/local/bin/app
```

Use JetBrains Mono for this information.

---

# 4. UI Components

# 4.1 Application Shell

The primary application layout should follow:

```text
┌───────────────────────────────────────────────────────────┐
│ Top Bar                                                   │
├───────────────┬───────────────────────────────────────────┤
│               │                                           │
│ Sidebar       │              Main Content                 │
│               │                                           │
│ Navigation    │                                           │
│               │                                           │
│               │                                           │
└───────────────┴───────────────────────────────────────────┘
```

---

# 4.2 Sidebar

The sidebar is the primary navigation mechanism.

Recommended navigation:

```text
ForensiWeb
──────────────────
◉ Overview

INVESTIGATION
□ Cases
□ Evidence
□ Events
□ Detections
□ Timeline
□ Findings

ANALYSIS
□ Attack Chains
□ Analytics
□ Reports

LAB
□ Scenarios
□ Lab Status
□ Reset Lab

SYSTEM
□ Settings
□ Audit Logs
```

### Sidebar Behavior

- collapsible;
- persistent on desktop;
- icon + label;
- active state;
- tooltip when collapsed;
- smooth transition;
- keyboard accessible.

---

# 4.3 Top Navigation Bar

The top bar should contain:

```text
[Page Title]       [Global Search]    [Alerts] [Help] [Avatar]
```

Optional:

- current case;
- system status;
- lab status.

---

# 4.4 Global Search

Global search should allow users to search across:

- cases;
- evidence;
- events;
- detections;
- findings;
- reports.

Example:

```text
⌕ Search cases, events, evidence...
```

Search results should be categorized.

---

# 4.5 Cards

Cards are the primary content container.

### Card characteristics

- dark layered surface;
- subtle border;
- small shadow;
- moderate corner radius;
- clear heading;
- optional action area.

Recommended radius:

```text
12px
```

Cards should not appear excessively rounded.

---

# 4.6 Metric Cards

Used for high-level statistics.

Example:

```text
┌────────────────────────┐
│ ACTIVE CASES            │
│                         │
│ 12                      │
│ ↑ 8.4%                  │
│                         │
│ ────╱╲────╱╲───        │
└────────────────────────┘
```

Possible metrics:

- Active Cases
- Evidence Items
- Security Alerts
- Critical Findings
- Events Processed
- Detection Rate
- Risk Score

---

# 4.7 Status Badge

Used for:

- severity;
- processing state;
- case state;
- lab state;
- evidence state.

Examples:

```text
● CRITICAL
● HIGH
● MEDIUM
● LOW

● ACTIVE
● PROCESSING
● COMPLETED
● FAILED
```

---

# 4.8 Buttons

Button hierarchy:

### Primary

Used for the most important action.

Example:

```text
+ Create Case
```

### Secondary

Used for supporting actions.

```text
View Evidence
```

### Ghost

Used for low-priority actions.

```text
View Details
```

### Destructive

Used for dangerous operations.

```text
Reset Lab
Delete Case
```

Destructive operations require confirmation.

---

# 4.9 Inputs

Inputs should use:

- dark surface;
- subtle border;
- clear label;
- visible focus state;
- validation feedback.

Example:

```text
Case Name
┌──────────────────────────────────┐
│ Investigation - Scenario 001     │
└──────────────────────────────────┘
```

---

# 4.10 Tables

Tables are critical for forensic analysis.

Required capabilities:

- sorting;
- filtering;
- pagination;
- column visibility;
- row selection;
- expandable rows;
- search.

Example columns:

```text
Timestamp | Event | Source | Severity | Stage | Evidence | Status
```

Technical values should use monospace typography.

---

# 4.11 Event Row

Event rows should visually communicate:

```text
Timestamp
   +
Event Type
   +
Severity
   +
Attack Stage
   +
Evidence Reference
```

Example:

```text
10:31:22Z   Suspicious File Access
            HIGH   LFI
            evidence-00482
```

---

# 4.12 Evidence Card

Evidence cards should show:

```text
Evidence ID
Source
Filename
Acquisition Time
SHA-256
Size
Status
```

Example:

```text
┌─────────────────────────────────────────┐
│ evidence-00482                 VERIFIED │
│                                         │
│ Source: Web Server Access Log           │
│ File: access.log                        │
│ Size: 2.4 MB                            │
│ SHA-256: 8f4a...91cd                    │
│                                         │
│ [View] [Analyze]                        │
└─────────────────────────────────────────┘
```

---

# 4.13 Timeline Component

The timeline is one of the most important components.

Concept:

```text
LFI
 ●────────●────────●────────●────────●
          │        │        │
       Poison     RCE      Shell   PrivEsc
```

Timeline must support:

- zoom;
- filtering;
- stage selection;
- event selection;
- evidence drill-down;
- time range selection.

---

# 4.14 Attack Chain Visualization

Attack chains should be represented visually.

Example:

```text
┌────────┐
│  LFI   │
└───┬────┘
    ↓
┌──────────────┐
│ Log Poisoning│
└──────┬───────┘
       ↓
┌────────┐
│  RCE   │
└───┬────┘
    ↓
┌─────────────┐
│ Web Shell   │
└──────┬──────┘
       ↓
┌───────────────┐
│ Privilege Esc │
└───────────────┘
```

Nodes should support:

- hover;
- click;
- status;
- severity;
- evidence count;
- related events.

---

# 4.15 Alert Panel

Alerts should be visually prominent but controlled.

Example:

```text
┌─────────────────────────────────────────┐
│ ⚠ HIGH SEVERITY DETECTION               │
│                                         │
│ Suspicious command execution detected   │
│                                         │
│ Stage: RCE                              │
│ Evidence: evidence-0081                 │
│ Confidence: High                        │
│                                         │
│ [Investigate]                           │
└─────────────────────────────────────────┘
```

---

# 4.16 Notification System

Notifications should communicate:

- success;
- warning;
- failure;
- system status.

Use temporary notifications only for non-critical information.

Critical security findings should remain visible in the alert/investigation system.

---

# 4.17 Modal

Use modals for:

- confirmation;
- focused investigation;
- destructive actions;
- small forms.

Do not place large forensic investigations inside tiny modals.

For complex investigation, use a dedicated page or side panel.

---

# 4.18 Side Detail Panel

Recommended for event/evidence investigation.

```text
┌──────────────────────────────┐
│ Event Details            ×   │
├──────────────────────────────┤
│ Timestamp                    │
│ Event Type                   │
│ Severity                     │
│ Attack Stage                 │
│                              │
│ Related Evidence             │
│ ───────────────────────────  │
│ evidence-00482               │
│                              │
│ Related Events               │
│                              │
│ [Open Full Investigation]    │
└──────────────────────────────┘
```

This supports progressive disclosure without forcing the analyst away from the current context.

---

# 4.19 Charts

Charts should be functional rather than decorative.

Recommended visualizations:

- event volume;
- severity distribution;
- attack-stage distribution;
- timeline activity;
- detection trends;
- evidence processing status;
- risk score;
- correlation graph.

Charts should support:

- hover;
- filtering;
- date range;
- legends;
- accessible labels.

---

# 4.20 AI / Intelligence Panel

AI-inspired elements should represent **analysis assistance**, not replace forensic evidence.

Example:

```text
┌──────────────────────────────────────┐
│ ✦ Intelligence Summary               │
│                                      │
│ 5 events appear related to the same  │
│ attack sequence.                     │
│                                      │
│ Possible chain:                      │
│ LFI → Log Poisoning → RCE            │
│                                      │
│ [Review Evidence]                    │
└──────────────────────────────────────┘
```

AI-generated conclusions must always be clearly distinguished from verified evidence.

---

# 4.21 Raw Evidence Viewer

Raw evidence should use a technical viewer.

Features:

- monospace font;
- line numbers;
- search;
- highlighted matches;
- timestamp highlighting;
- evidence metadata;
- read-only mode.

Original evidence must never become editable through the viewer.

---

# 4.22 Command / Terminal Style Component

A terminal-style component may be used for:

- lab status;
- controlled scenario execution;
- command output;
- technical diagnostics.

It must visually distinguish simulated laboratory operations from arbitrary system access.

---

# 4.23 Loading States

Never leave users staring at a blank screen.

Use:

- skeleton loaders;
- progress indicators;
- contextual loading messages.

Example:

```text
Analyzing evidence...
██████████████░░░░ 72%
```

---

# 4.24 Empty States

Empty states should explain what the user can do next.

Example:

```text
No investigations yet

Create a case to begin forensic analysis.

[Create Case]
```

Avoid empty screens containing only:

```text
No data
```

---

# 4.25 Error States

Errors must clearly communicate:

1. what failed;
2. whether data was preserved;
3. what the user can do next.

Example:

```text
Evidence analysis failed

The original evidence was preserved successfully.

Reason:
Parser could not recognize the source format.

[View Details] [Retry]
```

---

# 4.26 Confirmation States

Dangerous actions must require confirmation.

Examples:

- delete case;
- reset laboratory;
- delete derived data;
- revoke access.

Confirmation should explain consequences.

---

# 4.27 Responsive Design

Primary experience:

```text
Desktop / Large Analyst Screen
```

Secondary:

```text
Tablet
Mobile
```

Desktop should provide the richest forensic experience.

On smaller screens:

- collapse sidebar;
- stack cards;
- simplify tables;
- use horizontal scrolling where required;
- preserve critical information;
- avoid hiding security severity.

---

# 4.28 Animation Rules

Animations should be subtle and purposeful.

Recommended:

- 150–250ms UI transitions;
- hover transitions;
- panel expansion;
- timeline movement;
- graph interaction;
- loading states.

Avoid:

- excessive bouncing;
- continuous decorative animation;
- distracting particle effects;
- animations that interfere with investigation.

---

# 4.29 Accessibility

The interface must support:

- keyboard navigation;
- visible focus;
- sufficient contrast;
- readable typography;
- semantic labels;
- screen-reader-friendly controls;
- non-color indicators for severity.

Example:

```text
🔴 Critical
🟠 High
🟡 Medium
🔵 Informational
```

Do not rely only on color.

---

# 4.30 Design Consistency Rules

Every new UI feature must answer:

- Does it follow the dark theme?
- Does it use the defined typography?
- Does it use existing spacing?
- Does it reuse existing components?
- Does it follow severity conventions?
- Does it include loading/error/empty states?
- Is it responsive?
- Is it accessible?

If an existing component can solve the requirement, reuse it.

---

# 4.31 Design Anti-Patterns

Avoid:

- excessive gradients;
- excessive glassmorphism;
- excessive neon;
- inconsistent border radii;
- random colors;
- oversized headings;
- unnecessary animations;
- cluttered dashboards;
- inconsistent buttons;
- inconsistent spacing;
- decorative charts with no analytical purpose;
- AI elements that make unsupported forensic claims.

---

# 4.32 Final Visual Identity

ForensiWeb should ultimately feel like:

```text
                    FORENSIWEB

       Cybersecurity Command Center
                    +
          Digital Forensics Lab
                    +
           Investigation Workspace
                    +
             Intelligent Analysis
```

The visual identity should communicate:

**Dark • Futuristic • Technical • Precise • Trustworthy • Interactive**

while maintaining the fundamental principle:

> **The interface exists to help analysts understand evidence, reconstruct events, and make defensible security conclusions—not merely to look futuristic.**