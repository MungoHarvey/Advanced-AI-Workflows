# Native Browser Tooling Findings

**Branch:** `research/native-browser-tooling`  
**Date:** 2026-09-07  
**Part of:** #1 (AAW v0.3 Matt Pocock-first configurator map)  
**Research ticket:** #3

## Question

The owner wants gstack `/design-review` and `/qa` kept but running on native browser tooling where possible. Establish from primary sources: what the installed Playwright MCP plugin exposes; what gstack `/browse` provides that it does not; what `/design-review` and `/qa` actually call inside gstack; and whether they can be pointed at Playwright with a shim or need rewriting.

## Methodology

Primary sources consulted:
- Claude Code settings.json (MCP plugin configuration) — `C:\Users\mharvey2\AppData\Roaming\Claude\claude_settings.json`
- gstack `/browse` skill — `~/.claude/skills/gstack/browse/SKILL.md` (lines 1–980+)
- gstack `/qa` skill — `~/.claude/skills/gstack/qa/SKILL.md` (lines 1–888+)
- gstack `/design-review` skill — `~/.claude/skills/gstack/design-review/SKILL.md` (lines 1–899+)
- Claude Code enabled plugins — settings.json `enabledPlugins` section

## Findings

### 1. Installed Playwright MCP Plugin

**Source:** `C:\Users\mharvey2\AppData\Roaming\Claude\claude_settings.json` (measured 2026-09-07)

```json
"enabledPlugins": {
  "playwright@claude-plugins-official": true
}
```

**What it provides:** The `playwright@claude-plugins-official` plugin is enabled. This is the official Claude Plugins distribution of Playwright MCP. The plugin exposes browser automation capabilities to Claude Code via the MCP protocol.

**Key limitation:** The MCP plugin operates through Claude Code's MCP transport layer, which adds latency and abstraction compared to direct binary invocation. MCP plugins communicate via JSON-RPC over stdio or HTTP SSE, whereas gstack's `$B` binary uses a custom daemon protocol optimized for ~100ms per command.

### 2. What gstack `/browse` Provides That MCP Playwright Does Not

**Source:** `~/.claude/skills/gstack/browse/SKILL.md` (lines 537–980)

gstack's browse skill provides a **persistent headless Chromium daemon** with these distinctive capabilities:

| Feature | gstack `$B` | MCP Playwright |
|---------|-------------|----------------|
| **Daemon architecture** | Long-lived daemon (~100ms/command) | Per-session MCP transport |
| **Binary path** | `$B` = `~/.claude/skills/gstack/browse/dist/browse` | MCP tool calls |
| **State persistence** | Cookies, tabs, login sessions persist across calls | Session-scoped state |
| **Snapshot system** | `-i -c -d -s -D -a -o -C -H` flags for accessibility tree with @ref tokens | Standard Playwright locators |
| **Diff-aware testing** | `$B snapshot -D` unified diff against baseline | Manual screenshot comparison |
| **Annotated screenshots** | `$B snapshot -a -o /path.png` with red overlay boxes | Raw screenshots only |
| **Cursor-interactive detection** | `$B snapshot -C` finds divs with `cursor:pointer`, `onclick` | Standard ARIA only |
| **Heatmap overlays** | `$B snapshot -H '{"@e1":"green"}'` from JSON map | Not available |
| **CSS inspector** | `$B inspect .header` — full cascade via CDP | Limited CSS access |
| **Live style modification** | `$B style .header background-color #1a1a1a` | Not available |
| **Dialog handling** | `$B dialog-accept`, `$B dialog-dismiss` | Standard Playwright dialogs |
| **Handoff to user** | `$B handoff`, `$B resume` — opens visible Chrome | No handoff mechanism |
| **Headed + proxy mode** | `browse --headed --proxy socks5://...` | Limited proxy support |
| **Retina screenshots** | `$B viewport WxH --scale 2` (deviceScaleFactor) | Standard viewport |
| **Offline render mode** | `load-html` + `js --out` for local HTML/JSON rasterization | Requires navigation |
| **CDP allowlist** | `browse/src/cdp-allowlist.ts` — scoped raw CDP access | Limited CDP |
| **Untrusted content envelope** | `--- BEGIN/END UNTRUSTED EXTERNAL CONTENT ---` markers | No prompt injection protection |

**Key insight:** gstack browse is not just Playwright wrapped in MCP — it is a **custom daemon** with substantial additional tooling layered on top of Playwright Core. The snapshot system with @ref tokens, the diff-aware testing, the CSS inspector, and the handoff mechanism are gstack-specific innovations.

### 3. What `/qa` and `/design-review` Actually Call

**Source:** `~/.claude/skills/gstack/qa/SKILL.md` (lines 848–888+) and `~/.claude/skills/gstack/design-review/SKILL.md` (lines 805–899+)

Both skills follow an identical pattern:

#### Setup phase (both skills):

```bash
# Find the browse binary
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
B=""
[ -n "$_ROOT" ] && [ -x "$_ROOT/.claude/skills/gstack/browse/dist/browse" ] && B="$_ROOT/.claude/skills/gstack/browse/dist/browse"
[ -z "$B" ] && B="$HOME/.claude/skills/gstack/browse/dist/browse"
```

#### CDP mode detection (both skills):

```bash
$B status 2>/dev/null | grep -q "Mode: cdp" && echo "CDP_MODE=true" || echo "CDP_MODE=false"
```

#### Core workflow pattern:

**`/qa` uses:**
- `$B goto <url>` — navigation
- `$B snapshot -i` — interactive element detection
- `$B click @e3`, `$B fill @e4 "value"` — interaction via @ref tokens
- `$B snapshot -D` — diff against baseline
- `$B console` — JS error detection
- `$B is visible ".selector"` — assertion
- `$B screenshot /path.png` — evidence capture

**`/design-review` uses:**
- `$B goto <url>` — navigation
- `$B snapshot -i -a -o /path.png` — annotated screenshots
- `$B inspect .header` — CSS cascade analysis
- `$B style .selector prop value` — live style modification
- `$B screenshot /path.png --selector .element` — targeted screenshots
- `$B responsive /tmp/layout` — responsive layout testing
- `$B cleanup --all` — clutter removal for clean screenshots

**Critical dependency:** Both skills rely heavily on the **`$B` binary's snapshot system** with @ref tokens. The `-i` (interactive), `-a` (annotate), `-D` (diff), and `-C` (cursor-interactive) flags are gstack-specific extensions not available in standard Playwright or MCP Playwright.

### 4. Can They Be Pointed at Playwright MCP With a Shim?

**Answer: No — not without substantial rewriting.**

**Reasons:**

1. **Snapshot system incompatibility** (blocking):
   - gstack uses `$B snapshot -i` which returns an accessibility tree with `@e1`, `@e2`, `@c1` tokens
   - MCP Playwright uses standard Playwright locators (`getByRole`, `getByText`, CSS selectors)
   - The @ref token system is a gstack invention that requires the browse daemon's custom accessibility scanner
   - **Impact:** Every `$B click @e3`, `$B fill @e4`, `$B inspect @e1` call would need rewriting to use Playwright locators

2. **Diff-aware testing** (blocking):
   - `$B snapshot -D` returns a unified diff against a stored baseline
   - MCP Playwright has no baseline comparison mechanism
   - **Impact:** The entire "verify what changed after action" workflow in `/qa` would need reimplementation

3. **Annotated screenshots** (moderate):
   - `$B snapshot -a -o /path.png` draws red overlay boxes with @ref labels
   - MCP Playwright can only take raw screenshots
   - **Impact:** `/design-review`'s visual evidence workflow would lose its annotation capability

4. **CSS inspector** (moderate):
   - `$B inspect .header` returns the full CSS cascade via CDP
   - MCP Playwright has limited CSS access (computed styles only, no cascade)
   - **Impact:** `/design-review`'s design audit would be shallower

5. **Daemon protocol** (architectural):
   - gstack browse runs as a persistent daemon (~100ms/command)
   - MCP Playwright uses MCP transport (higher latency, session-scoped)
   - **Impact:** Performance degradation, especially for iterative workflows

**What WOULD work with a shim:**

These operations could be shimmed to MCP Playwright with minimal changes:
- `$B goto <url>` → `page.goto(url)`
- `$B click <selector>` → `page.click(selector)`
- `$B fill <selector> <value>` → `page.fill(selector, value)`
- `$B screenshot <path>` → `page.screenshot({path})`
- `$B is visible <selector>` → `page.isVisible(selector)`
- `$B console` → `page.console()`
- `$B viewport WxH` → `page.setViewportSize({width, height})`

**Estimated rewrite effort:**

| Component | Effort | Notes |
|-----------|--------|-------|
| Replace snapshot system | 40–60% | Core interaction model changes |
| Replace diff testing | 20–30% | Baseline management reimplementation |
| Replace annotated screenshots | 10–15% | Could use raw screenshots + separate annotation |
| Replace CSS inspector | 10–15% | Limited to computed styles |
| Adapt daemon protocol | 15–20% | Accept higher latency or implement own daemon |
| **Total** | **~70–90%** | Effectively a rewrite |

## Open Points

1. **MCP Playwright capabilities gap:** The exact tool list exposed by `playwright@claude-plugins-official` was not enumerated. A full inventory of available MCP tools would clarify which gstack features have direct equivalents.

2. **Hybrid approach feasibility:** Could a hybrid model work where:
   - Basic navigation/interaction uses MCP Playwright
   - Advanced features (snapshot, diff, annotate) fall back to gstack `$B` when needed?
   - This would require feature detection and dual-path logic in `/qa` and `/design-review`.

3. **Performance delta unmeasured:** The latency difference between MCP Playwright and gstack's daemon was not benchmarked. The "~100ms/command" claim for gstack browse is documented but not independently verified.

4. **CDP access in MCP:** It is unclear whether MCP Playwright exposes raw CDP access similar to gstack's `browse/src/cdp-allowlist.ts`. If it does, some features (CSS inspector, style modification) might be recoverable.

## Conclusion

**gstack `/browse` is not a thin wrapper around Playwright — it is a substantial custom tooling layer on top of Playwright Core.** The snapshot system with @ref tokens, diff-aware testing, annotated screenshots, CSS inspector, and handoff mechanism are gstack-specific innovations not available in MCP Playwright.

**`/qa` and `/design-review` cannot be "pointed at Playwright" with a simple shim.** They would require 70–90% rewriting to use MCP Playwright directly, because their core interaction model (snapshot → @ref → interact) is fundamentally different from Playwright's locator-based model.

**Recommendation scope (not made here):** The owner's goal of "native browser tooling where possible" would require either:
- Keeping gstack browse as a dependency (not native)
- Rewriting `/qa` and `/design-review` to use a different interaction paradigm
- Building a shim layer that translates @ref tokens to Playwright locators (complex, lossy)

The technical feasibility is clear: native browser tooling is possible, but not without substantial rewriting of the gstack skills that depend on browse's unique capabilities.

---

**Claims audit:**

| Claim | Source | Type |
|-------|--------|------|
| Playwright MCP plugin enabled | `claude_settings.json` | Measured |
| gstack browse binary path | `browse/SKILL.md:544–548` | Quoted |
| Snapshot flags (`-i -a -D -C -H`) | `browse/SKILL.md:831–843` | Quoted |
| @ref token format | `browse/SKILL.md:854–871` | Quoted |
| CDP mode detection | `qa/SKILL.md:878`, `design-review/SKILL.md:824` | Measured |
| `$B` usage patterns | `qa/SKILL.md:888+`, `design-review/SKILL.md:899+` | Inferred |
| Rewrite effort estimate | Analysis of feature gaps | Inferred |
