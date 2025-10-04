# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains a **BMad Method** installation - an AI-driven agile development framework that uses specialized agents to manage the complete software development lifecycle from planning through implementation. It includes:

- **BMad Core**: Main framework with development workflow agents
- **BMad Creative Writing Expansion Pack**: Additional agents for fiction/screenwriting workflows

## Architecture

### Framework Structure

The BMad Method operates through specialized AI agents that handle different roles in the development process:

**Core Agents** (in `.bmad-core/agents/`):
- **Product Manager (pm)**: Creates PRDs from project briefs
- **Architect**: Designs system architecture from requirements
- **Product Owner (po)**: Validates alignment, shards documents into epics/stories
- **Scrum Master (sm)**: Drafts user stories from sharded epics
- **Developer (dev)**: Implements stories with tests
- **Test Architect (qa)**: Risk assessment, test design, quality gates
- **Analyst**: Market research, project brief creation
- **UX Expert**: Front-end specifications and UI prompts

**Special Agents**:
- **BMad-Master**: Can execute any task except story implementation
- **BMad-Orchestrator**: Heavy-weight agent for web-based team coordination (not for IDE use)

### Workflow Types

BMad supports two primary workflows:

1. **Greenfield**: New projects starting from scratch
2. **Brownfield**: Existing projects requiring enhancement/refactoring

### Document Organization

```
docs/
├── prd.md                    # Product Requirements Document
├── architecture.md           # System Architecture Document
├── prd/                      # Sharded PRD epics
├── architecture/             # Sharded architecture components
│   ├── coding-standards.md
│   ├── tech-stack.md
│   └── source-tree.md
├── stories/                  # User stories for implementation
└── qa/
    ├── assessments/          # Risk, test design, NFR, trace reports
    └── gates/                # Quality gate decisions
```

## Configuration

### Core Configuration (`.bmad-core/core-config.yaml`)

Key settings that control BMad behavior:

- **Document Locations**: Configures where PRD, architecture, QA artifacts are stored
- **Versioning**: Tracks PRD/architecture document versions (currently v4)
- **Dev Context Files**: Files the dev agent always loads:
  - `docs/architecture/coding-standards.md`
  - `docs/architecture/tech-stack.md`
  - `docs/architecture/source-tree.md`
- **Sharding**: Enables breaking large documents into manageable pieces
- **Slash Prefix**: `BMad` - used for Claude Code slash commands

### Expansion Packs

**Creative Writing Pack** (`.bmad-creative-writing/`):
- 10 specialized writing agents (plot architect, character psychologist, etc.)
- 8 workflows (novel writing, screenplay development, series planning)
- 27 quality checklists for different genres
- Slash prefix: `bmad-cw`

## Development Workflow

### Planning Phase (Typically Web UI)

1. **Analyst** (optional): Brainstorming → Market research → Create project brief
2. **PM**: Create PRD from brief with FRs, NFRs, epics & stories
3. **UX Expert** (optional): Create front-end spec and UI prompts
4. **Architect**: Create architecture from PRD/UX spec
5. **QA** (optional): Early test architecture input on high-risk areas
6. **PO**: Run master checklist to validate alignment
7. **PO**: Shard PRD and Architecture into epics/stories

### Development Cycle (IDE)

1. **SM**: Reviews previous notes → Drafts next story from sharded epic
2. **QA** (optional): `*risk` and `*design` assessment for high-risk stories
3. **PO** (optional): Validates story draft against artifacts
4. **Dev**: Sequential task execution → Implement with tests
5. **QA** (optional): Mid-dev checks with `*trace` or `*nfr`
6. **Dev**: Run validations → Mark ready for review
7. **QA** (required): Test architecture review + quality gate
8. **Commit changes** (critical: commit before proceeding to next story)
9. **QA** (if needed): Update gate status
10. Mark story as done → Continue to next story

### Test Architect (QA) Commands

The QA agent provides quality assurance throughout the lifecycle:

| Command | When | Purpose | Output |
|---------|------|---------|--------|
| `*risk` | After story draft | Identify risks (1-9 scoring) | `docs/qa/assessments/{epic}.{story}-risk-{YYYYMMDD}.md` |
| `*design` | After risk assessment | Create test strategy | `docs/qa/assessments/{epic}.{story}-test-design-{YYYYMMDD}.md` |
| `*trace` | During development | Verify test coverage | `docs/qa/assessments/{epic}.{story}-trace-{YYYYMMDD}.md` |
| `*nfr` | During development | Validate quality attributes | `docs/qa/assessments/{epic}.{story}-nfr-{YYYYMMDD}.md` |
| `*review` | After development | Full quality assessment | QA Results section + gate file |
| `*gate` | Post-review | Update quality decision | Updated gate file |

**Gate Statuses**:
- **PASS**: All critical requirements met
- **CONCERNS**: Non-critical issues, team should review
- **FAIL**: Critical issues must be addressed
- **WAIVED**: Issues acknowledged and accepted

### Risk Scoring System

| Risk Score | Testing Priority | Gate Impact |
|------------|------------------|-------------|
| 9 | P0 - Must test thoroughly | FAIL if untested |
| 6 | P1 - Should test well | CONCERNS if gaps |
| 4 | P1 - Should test | CONCERNS if notable gaps |
| 2-3 | P2 - Nice to have | Note in review |
| 1 | P2 - Minimal | Note in review |

## Agent Interaction in Claude Code

Agents are invoked via slash commands with the `BMad` prefix:

```
/BMad:pm          # Product Manager tasks
/BMad:architect   # Architect tasks
/BMad:sm          # Scrum Master - draft next story
/BMad:dev         # Developer - implement story
/BMad:qa          # Test Architect - quality gates
/BMad:po          # Product Owner - validation/sharding
```

For creative writing expansion:
```
/bmad-cw:plot-architect
/bmad-cw:character-psychologist
# etc.
```

## Key Principles

### Test Quality Standards

- No flaky tests (proper async handling)
- No hard waits (dynamic strategies only)
- Stateless and parallel-safe tests
- Self-cleaning (tests manage their own data)
- Appropriate test levels (unit/integration/E2E)
- Explicit assertions (keep in tests, not helpers)

### Context Management

- Keep files lean and focused
- Load only relevant files into context
- Dev agent auto-loads coding standards, tech stack, and project structure
- Reduce coding standards over time as patterns become consistent
- Agent infers standards from surrounding code

### Document Sharding

Large documents (PRD, Architecture) are broken down into:
- **Epics**: Higher-level feature groupings
- **Stories**: Implementable units of work
- **Components**: Architectural modules/services

### Commit Discipline

**CRITICAL**: Always commit changes before moving to the next story to prevent work loss and maintain clear history.

## Dependencies System

Each agent declares dependencies in YAML:

```yaml
dependencies:
  templates:
    - prd-template.md
  tasks:
    - create-doc.md
  data:
    - bmad-kb.md
```

This ensures agents load only needed resources for lean context usage.

## Technical Preferences

The file `.bmad-core/data/technical-preferences.md` can be customized to bias PM and Architect recommendations toward your preferred:
- Design patterns
- Technology choices
- Architecture styles
- Development practices

## Special Situations

### Brownfield Projects

For existing codebases:
- Review `.bmad-core/working-in-the-brownfield.md`
- Always run `*risk` and `*design` before changes
- Focus on regression test coverage
- Pay extra attention to backward compatibility

### High-Risk Stories

- **Required**: `*risk` and `*design` before development
- **Recommended**: Mid-dev `*trace` and `*nfr` checkpoints
- **Required**: Comprehensive `*review` before completion

### Performance-Critical Features

- Run `*nfr` early and often (not just at review)
- Establish performance baselines before changes
- Document acceptable performance degradation
