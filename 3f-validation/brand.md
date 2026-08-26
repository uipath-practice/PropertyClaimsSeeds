# UiPath brand — the part an app needs

Everything below is transcribed from *UiPath Brand Identity Guidelines 2026 V3.1*, reduced to what a screen uses. **You do not need any brand tooling to apply it** — the values are here because the guidelines themselves are a slide-deck skill you are not expected to have.

`uipath-coded-apps` ships the design system this plugs into: copy its `index-template.css` to `src/index.css`, then **change only the token values below**. The skill's own rule is that brand, colour, font and radius requests are satisfied in `:root` / `body.dark` and nowhere else — component stylesheets stay untouched, which keeps the diff reviewable and the baseline stable.

## The palette

| Role | Name | Hex |
|---|---|---|
| **Hero** — impact, and used sparingly | Robotic Orange | `#FA4616` |
| **Structure** — brand-related content | Deep Blue | `#182126` |
| **Contrast** — agentic content | Agentic Teal | `#0BA2B3` |
| Canvas | Bright White | `#FFFFFF` |
| Secondary — light fill | Bright Blue | `#CCF2FF` |
| Secondary — mid | Dark Blue | `#1E6482` |
| Secondary — deep orange | Offset Orange | `#A32200` |
| Secondary — platform content | Black | `#000000` |
| Reserved for **testing** content only | Testing Purple | `#8B288A` |

**Neutrals**, lightest to darkest: `#F6F6F6` · `#D9D9D9` · `#B9B9B9` · `#9D9D9D` · `#616161` · `#484848` · `#343434`.

## The three rules that decide whether it looks right

**Bright White is a canvas, not an emphasis colour.** It is what lets the other colours do their job. A screen that is mostly white with orange used at a few deliberate points reads as UiPath; a screen washed in orange does not.

**Robotic Orange is for impact; Deep Blue and Agentic Teal carry contrast and structure.** Orange is the hero and should be prominent — prominent is not the same as frequent.

**Secondary and tertiary colours support, they do not compete.** Use them to guide the eye, separate sections or emphasise one thing — intentionally, not decoratively.

**Where the brand splits orange and teal by meaning:** orange represents robots, teal represents agents. On a claims screen that mapping mostly does not apply, so do not force it.

## Typography

| Use | Brand typeface | What to actually ship |
|---|---|---|
| Headline | Urbane Rounded | **licensed — substitute Poppins SemiBold/Bold**, which the guidelines name as the alternative |
| Subheadline | Urbane Rounded Medium | Poppins SemiBold |
| Body and UI | **Inter Regular** | Inter — already the skill template's body face |
| Fallback anywhere | Arial | Arial, then `system-ui` |

## Tokens, ready to paste

Replace the corresponding lines in `:root`. Everything not listed here keeps the template's value.

```css
:root {
  --bg-canvas:      #F6F6F6;
  --bg-card:        #FFFFFF;
  --bg-secondary:   #CCF2FF;

  --text-primary:   #182126;   /* Deep Blue reads as near-black and is on-brand */
  --text-secondary: #616161;
  --text-muted:     #9D9D9D;

  --border-color:   #D9D9D9;
  --border-strong:  #B9B9B9;
  --border-focus:   #0BA2B3;

  --accent-color:   #FA4616;   /* Robotic Orange — the hero, used sparingly */
  --accent-hover:   #A32200;
  --accent-soft:    #0BA2B3;
  --accent-text:    #FFFFFF;
  --accent-bg:      rgba(250, 70, 22, 0.10);
  --accent-grad:    linear-gradient(135deg, #FA4616 0%, #A32200 100%);
  --accent-grad-vivid: linear-gradient(120deg, #0BA2B3 0%, #1E6482 50%, #182126 100%);

  --sans:    'Inter', Arial, system-ui, sans-serif;
  --heading: 'Poppins', 'Inter', Arial, system-ui, sans-serif;
}

body.dark, .dark {
  --bg-canvas:  #182126;
  --bg-card:    #343434;
  --bg-hover:   #484848;
  --text-primary:   #FFFFFF;
  --text-secondary: #B9B9B9;
  --border-color:   #484848;
}
```

**Delete the template's `@import` from `fonts.googleapis.com`.** It is an external request the Action Center host may refuse — the same sandbox already blocks `<embed>`, `<object>` and `<iframe>` for PDFs (`cookbook.md`). Either self-host the two families or let the Arial and `system-ui` fallbacks carry it. **The screen has to look deliberate with no webfont at all**, so check it that way once.

## Two things the brand does not give you

**There is no status palette** — no approved green/amber/red trio. Do not invent one and call it brand. Keep status semantics functional and legible, use the brand colours for chrome and emphasis, and **never carry meaning by colour alone**: a flagged finding needs a word or an icon as well, which is also what makes the screen readable to a reviewer who cannot distinguish them.

**Testing Purple is reserved.** It means testing-related content and nothing else. It has no place on a claims screen.
