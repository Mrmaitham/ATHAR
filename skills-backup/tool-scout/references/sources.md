# Where to search

Use these when the user describes a need ("أبي أداة تسوي ثمبنيل يوتيوب") instead of sending a link. Run several searches in parallel and merge the results.

## Search order

1. **Web search scoped to GitHub.** Phrase it a few ways, in English (most repos are English) plus the user's language when the topic is local:
   - `"claude skill" <task> site:github.com`
   - `"claude code plugin" <task> site:github.com`
   - `"SKILL.md" <task> github`
   - `MCP server <service name> github`
2. **Skill and plugin directories.** Search them by name; they move often, so treat this list as a starting point:
   - claudemarketplaces.com (skills and plugins)
   - skills.sh / agentskills.io (Agent Skills standard; `npx skills add owner/repo`)
   - Anthropic's official skills and plugins repos (search "anthropics skills github")
   - "awesome-claude-skills", "awesome-claude-code", "awesome-mcp-servers" lists
3. **Launch galleries for brand-new tools:** whatships.com (launch videos from X), Product Hunt, Hacker News "Show HN".
4. **Plugin marketplaces inside repos:** a repo with `.claude-plugin/marketplace.json` lists several plugins. Read it; there may be a better-fitting sibling plugin.

## Access notes

- **Public GitHub repos need no special access:** search the web, then `git clone --depth 1`. A session's own GitHub integration may be scoped to the user's repos; that scope is for acting on their account, and you don't need it to read public code.
- **Search engines lag.** A repo published this week may not show up yet. Say so when coverage matters, and invite the user to forward links they see.
- **X, Instagram and TikTok posts** are hard to fetch directly. Ask the user for the link inside the post, or a screenshot.
- **YouTube:** metadata is often reachable from cloud sessions, but video downloads are usually blocked (403).

## Quick filter before deep vetting

Drop a candidate early if any of these is true:
- It isn't actually a Claude tool, or one that works with Claude (check for SKILL.md, plugin.json, an MCP server, or a CLI an agent can drive)
- No commits in over a year and open issues pile up unanswered
- Archived, or the README says it moved (follow the move instead)
- No license, and the user would use it commercially

Then deep-vet the best 2–3 and mention the rest in one line each.
