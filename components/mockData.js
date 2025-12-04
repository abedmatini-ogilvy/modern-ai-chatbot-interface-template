// Mock data removed - conversations start empty
export const INITIAL_CONVERSATIONS = []

export const INITIAL_TEMPLATES = [
  {
    id: "t1",
    name: "Bug Report",
    content: `**Bug Report**

**Description:**
Brief description of the issue

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- Browser/OS:
- Version:
- Additional context:`,
    snippet: "Structured bug report template with steps to reproduce...",
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "t2",
    name: "Daily Standup",
    content: `**Daily Standup Update**

**Yesterday:**
- Completed task A
- Made progress on task B

**Today:**
- Plan to work on task C
- Continue with task B

**Blockers:**
- None / List any blockers here

**Notes:**
Any additional context or updates`,
    snippet: "Daily standup format with yesterday, today, and blockers...",
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "t3",
    name: "Code Review",
    content: `**Code Review Checklist**

**Scope:**
What changes are being reviewed

**Key Areas to Focus:**
- Logic correctness
- Performance implications
- Security considerations
- Test coverage

**Questions:**
- Any specific concerns?
- Performance impact?
- Breaking changes?

**Testing:**
- Unit tests added/updated?
- Manual testing completed?`,
    snippet: "Comprehensive code review checklist and questions...",
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "t4",
    name: "Meeting Notes",
    content: `**Meeting Notes - [Meeting Title]**

**Date:** [Date]
**Attendees:** [List attendees]

**Agenda:**
1. Topic 1
2. Topic 2
3. Topic 3

**Key Decisions:**
- Decision 1
- Decision 2

**Action Items:**
- [ ] Task 1 - @person - Due: [date]
- [ ] Task 2 - @person - Due: [date]

**Next Steps:**
What happens next

**Notes:**
Additional context and discussion points`,
    snippet: "Meeting notes template with agenda, decisions, and action items...",
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
]

// Folders removed - start empty
export const INITIAL_FOLDERS = []
