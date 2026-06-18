# RABBIT Memory And Chat Conversation Strategy

## Purpose

This document is dedicated only to memory, chat sessions, conversation continuity, summarization, and future chat-widget behavior for RABBIT.

It does not describe the full project build progression. The goal is to explain how RABBIT should remember, summarize, reset, and manage conversations across the dashboard and future website chat widget.



## General Applicability

This document is written for RABBIT, but the concepts are intentionally general. It can be used as a guide for designing memory and conversation strategy in any conversational application, including:

- website chat widgets
- customer-support bots
- recruiter assistants
- enterprise knowledge assistants
- personal AI assistants
- RAG applications
- mobile chat apps
- agentic assistants
- voice assistants

The same core design questions apply to almost every chat app:

- What is a session?
- How many messages should be stored?
- How many messages should be rendered?
- What counts as one conversational turn?
- When should old messages be summarized?
- Where should memory live: browser, backend, database, vector store, or all of them?
- What information should be visible to public users?
- What should be reserved for debug/observability/admin modes?
- What should happen when the user starts a new chat?
- What privacy guardrails are required?
- What happens when retrieval fails or the API fails?
- How do we trace an answer back to its sources?

RABBIT is the applied example in this document, but the vocabulary, phases, and platform choices can be reused for other chat systems.

## Core Principle

RABBIT should not keep unlimited chat messages in the UI or prompt.

Instead, it should use a layered memory strategy:

```text
Recent messages stay visible.
Older messages become a summary.
The RAG corpus remains the source of truth for facts.
Debug/Observability keep traceability.
```

This keeps the assistant fast, clean, and safer for public website use.

## Phase 1: Current Lightweight Session Memory

### Objective

Maintain a basic anonymous chat session without adding database complexity.

### Current Status

The current UI already uses a browser-generated session ID.

```js
const SESSION_KEY = 'bti_session_id';
const MAX_STORED_MESSAGES = 40;
const MAX_RENDERED_MESSAGES = 24;
```

### What This Means

- Each browser gets an anonymous session ID.
- The session ID is sent to `/api/chat`.
- Backend logs can connect requests using session ID, request ID, and turn ID.
- The browser stores the latest 40 messages.
- The UI renders only the latest 24 messages.
- Older messages are trimmed after the limit.

### Why This Exists

This improves:

- UI speed
- mobile performance
- basic traceability
- debugging
- observability
- retry behavior

### Limitation

Phase 1 trims older messages. That is fast, but it can lose conversation context.

## Phase 2: Rolling Conversation Summary

### Objective

Replace simple deletion with summarization.

Instead of deleting old chat turns, RABBIT should compress older turns into a short rolling summary.

### Proposed Behavior

When message count crosses a threshold:

```text
Keep latest 12-16 messages.
Summarize older messages.
Store the summary separately.
Use summary + recent messages for context.
```

### Example

Old chat turns:

```text
User asked about Rajesh's AI experience.
User asked about BPCL.
User asked about R-Cafe.
User asked about education.
User asked about role fit.
```

Rolling summary:

```text
The user has asked about Rajesh's AI/MLOps experience, BPCL industrial background, R-Cafe entrepreneurship, education, and suitability for business-tech hybrid roles. The assistant has positioned Rajesh as a Mechanical Engineering and business-trained operator with entrepreneurship through RedRybbons and R-Cafe, plus AI/MLOps project experience.
```

### Recommended Settings For Dashboard

```text
Visible/rendered messages: latest 24
Stored messages: latest 40
Summary trigger: after 30-40 messages
Summary location: browser localStorage first
```

### Recommended Settings For Website Widget

```text
Visible/rendered messages: latest 12-16
Stored messages: latest 20
Summary trigger: after 16-20 messages
Summary location: browser localStorage first
```

### Why This Is Better Than Deletion

- Keeps UI fast.
- Preserves conversational continuity.
- Reduces future token cost.
- Avoids bloated prompts.
- Makes mobile/widget behavior smoother.
- Gives a clear memory architecture story.

## Phase 3: Summary-Aware API Requests

### Objective

Send conversation memory to the backend in a structured way.

The API request should eventually include:

```json
{
  "session_id": "BTI-20260618-ABCDE",
  "question": "What roles is he suitable for?",
  "conversation_summary": "User has asked about Rajesh's AI, BPCL, R-Cafe, education, and role fit.",
  "recent_messages": [
    {"role": "user", "content": "Tell me about his AI experience"},
    {"role": "assistant", "content": "Rajesh has AI/MLOps experience..."}
  ]
}
```

### Important Rule

The conversation summary should help with continuity, but it should not become the factual source of truth.

Facts should still come from:

```text
RAG documents + Azure AI Search + approved source links
```

The summary should only help interpret follow-up questions like:

- “Tell me more.”
- “What about his education?”
- “Can he do this role?”
- “Show evidence.”

## Phase 4: Memory Visibility In Debug / Observability

### Objective

Expose memory behavior for owner/demo users without showing it in public User Mode.

### User Mode

Do not show:

- session internals
- summaries
- message counts
- request IDs
- memory state

User Mode should stay clean.

### Debug Mode

Can show:

- current question
- recent messages sent
- conversation summary
- whether summary was used
- summary age/version

### Observability Mode

Can show:

- session ID
- rendered message count
- stored message count
- summary token/character length
- summary update count
- API retry count
- last request ID

### Tech Mode

Can later show:

- raw memory payload
- summary generation prompt
- summary storage location
- memory reset events
- backend memory contract

## Phase 5: New Chat And Reset Strategy

### Objective

Allow clean session reset.

Current UI has `Clear` for messages. Future UI should distinguish:

### Clear Chat

Clears visible messages but may keep the same session ID.

Useful when:

- user wants a clean screen
- demo needs to reset visible history

### New Chat

Creates a new session ID and clears:

- visible messages
- stored messages
- conversation summary
- retry state
- local conversation state

Useful when:

- a new recruiter starts a conversation
- public widget user wants a fresh chat
- debugging one session versus another

Recommended final widget controls:

```text
New chat
Clear chat
```

For the public widget, `New chat` is more important than showing a technical session ID.

## Phase 6: Website Chat Widget Memory

### Objective

Make the final RABBIT website widget lightweight and responsive.

The website widget should not behave like the full dashboard.

### Widget Memory Rules

```text
User Mode only
Anonymous session ID
Latest 12-16 visible messages
Rolling summary for older turns
No Debug/Observability/Tech in public widget
No raw sources or scores
One or two relevant webpage links only
Guardrails always active
```

### Widget Experience

The user should experience:

- quick load
- clean chat window
- short answers
- relevant links
- session continuity during the visit
- easy new chat/reset

The owner/demo dashboard should continue to provide the deeper modes.

## Phase 7: Optional Persistent Memory

### Objective

Consider whether memory should persist beyond the browser session.

This is not needed immediately.

Possible future options:

### Browser-Only Memory

Best for current phase.

Pros:

- simple
- private
- no database
- easy to reset

Cons:

- lost if user clears browser storage
- not shared across devices

### Server-Side Session Memory

Possible future phase.

Pros:

- better analytics
- persistent session logs
- easier debugging

Cons:

- privacy responsibilities
- storage/security design needed
- needs cleanup/retention policy

### Recommended Direction

For now:

```text
Browser-only memory + backend logs
```

Later:

```text
Optional server-side anonymous session store with retention limits
```

## Privacy Guardrails For Memory

Memory should not retain unnecessary private information.

Guardrails:

- Do not store or summarize private relationship questions as factual user memory.
- Do not speculate on personal life.
- Do not store sensitive personal details unless explicitly needed for a professional context.
- Keep public assistant focused on professional profile, projects, business experience, education, role fit, and public evidence.
- Private/off-scope questions should be summarized only as “user asked an off-scope/private question; assistant redirected professionally.”

## Interview Talking Points

This memory strategy shows that RABBIT is designed with product thinking, not just prompt engineering.

Key points:

- We separate short-term UI memory from long-term RAG knowledge.
- We avoid infinite chat history for performance reasons.
- We use session IDs for traceability without requiring login.
- We plan rolling summarization instead of deleting conversation context.
- We keep public User Mode clean while exposing memory diagnostics in Debug/Observability/Tech.
- We prepare the same backend for both dashboard and future website widget.
- We design privacy guardrails into memory, not as an afterthought.

## Recommended Implementation Roadmap

### Phase 1: Done / Current

- Anonymous session ID.
- Stored message cap.
- Rendered message cap.
- API logs include session/request IDs.
- Retry available after failed requests.

### Phase 2: Next

- Add `conversation_summary` in localStorage.
- Add summary trigger after message threshold.
- Add summary display in Debug or Observability Mode.

### Phase 3: After That

- Send summary plus latest messages to `/api/chat`.
- Teach backend prompt to use summary only for conversational continuity.
- Keep facts grounded in RAG retrieval.

### Phase 4: Widget Preparation

- Use smaller message caps.
- Add `New chat` button.
- Hide all memory internals from User Mode.
- Keep guardrails active.

### Phase 5: Future

- Optional server-side session memory.
- Retention policy.
- Analytics dashboard.
- Memory evaluation tests.

---

# Appendix: Conversational App Glossary, Memory Strategy, And Infrastructure Plan

## 1. Conversational App Glossary

This section defines common vocabulary used across modern conversational applications, chatbots, AI assistants, RAG systems, and website chat widgets.

### Session

A session is one continuous chat experience for one visitor, browser, or user interaction window.

In RABBIT, a session is anonymous and browser-based.

Example:

```text
BTI-20260618-ABCDE
```

A session helps group multiple turns together for traceability, observability, and future memory.

### Message

A message is one individual chat item.

Examples:

```text
User message: Who is Rajesh?
Assistant message: Rajesh is a business-tech leader...
```

A message has a role:

- user
- assistant
- system
- tool, later if agents/tools are added

### Conversational Turn

A conversational turn is one user message plus one assistant response.

```text
1 turn = 1 user message + 1 assistant response
```

This matters because many memory limits are easier to understand by turns.

Example:

```text
12 turns = about 24 messages
20 turns = about 40 messages
```

### Conversation

A conversation is the full set of turns inside a session.

A conversation may include:

- visible messages
- stored messages
- summarized older turns
- API trace data
- retrieval evidence
- guardrail events

### Chat History

Chat history is the ordered list of previous messages in a conversation.

In RABBIT, chat history exists in two ways:

- rendered history: what is visible on screen
- stored history: what is saved in browser storage

### Rendered History

Rendered history is the set of messages currently drawn on the UI.

Purpose:

- keep the page fast
- avoid loading too many old message cards
- improve mobile performance

Current RABBIT setting:

```js
MAX_RENDERED_MESSAGES = 24;
```

### Stored History

Stored history is the set of messages saved in local browser storage.

Purpose:

- preserve conversation after refresh
- allow retry/context
- support short-term memory

Current RABBIT setting:

```js
MAX_STORED_MESSAGES = 40;
```

### Short-Term Memory

Short-term memory is the recent conversation context available during the current session.

In RABBIT, this includes:

- latest stored messages
- current question
- future conversation summary

### Long-Term Memory

Long-term memory is durable knowledge that exists outside the chat session.

For RABBIT, long-term memory is not personal chat memory. It is the RAG corpus:

- approved website pages
- chunks
- embeddings
- Azure AI Search index
- metadata
- source URLs

### Conversation Summary

Conversation summary is a compressed version of older chat turns.

Purpose:

- avoid keeping unlimited history
- preserve continuity
- reduce token/prompt load
- support mobile and widget performance

Example:

```text
The user asked about Rajesh's AI experience, BPCL background, R-Cafe, education, and role fit. The assistant explained his Mechanical Engineering background, IIM Calcutta marketing/strategy focus, ISB Product Management, IISc Bangalore Advanced Business Analytics, RedRybbons, R-Cafe, and AI/MLOps positioning.
```

### Context Window

The context window is the amount of text the model can consider in one request.

It can include:

- system prompt
- current user question
- retrieved chunks
- recent messages
- conversation summary

A good memory strategy avoids wasting context window on unnecessary old chat.

### System Prompt

The system prompt defines assistant behavior, rules, tone, guardrails, output style, and constraints.

For RABBIT, it controls:

- recruiter-facing tone
- privacy guardrails
- source behavior
- GenAI project caveats
- salary answer policy
- education precision
- business-tech positioning

### User Prompt

The user prompt is the current user question.

Example:

```text
Why should we hire Rajesh?
```

### Assistant Response

The assistant response is the generated answer shown to the user.

For User Mode, it should be:

- clean
- concise
- professional
- grounded
- readable
- supported by one or two relevant links

### Retrieval

Retrieval is the process of finding relevant knowledge from the indexed corpus.

In RABBIT:

```text
User question -> embedding/search -> Azure AI Search -> relevant chunks
```

### RAG

RAG means Retrieval-Augmented Generation.

The answer is generated using:

- retrieved evidence
- model reasoning
- prompt rules
- source metadata

### Chunk

A chunk is a smaller searchable unit created from a source document or webpage.

RABBIT has approved chunks uploaded to Azure AI Search.

### Source

A source is the original webpage/document from which a chunk came.

Example:

```text
R-Cafe by Red Rybbons — Built from Ground Zero
https://rajesharigala.com/buiss skills/r-cafe
```

### Citation / Relevant Link

A citation or relevant link is the user-facing evidence link.

In User Mode, RABBIT should show:

- one or two relevant links
- title/header
- URL below it
- clickable blue link

### Metadata

Metadata is structured information attached to documents/chunks.

Examples:

- page_id
- section_id
- source_url
- title
- depth
- approval status
- chunk index
- related pages

Metadata supports filtering, tracing, dashboards, and source quality.

### Guardrail

A guardrail is a rule that prevents unsafe, irrelevant, private, or misleading behavior.

RABBIT guardrails include:

- do not speculate about private relationships
- do not invent salary numbers
- do not claim GenAI projects exist before they are indexed
- do not show irrelevant links for private/off-scope answers
- do not expose debug internals in User Mode

### Fallback

A fallback is the response when the system cannot answer well.

Examples:

- no relevant source found
- private/off-scope question
- API failure
- retrieval failure

A good fallback is honest, brief, and redirects usefully.

### Retry

Retry allows the same failed request to be sent again.

RABBIT supports retry after failed requests.

### Traceability

Traceability means the ability to follow an answer back to:

- session ID
- request ID
- question
- retrieved chunks
- source URLs
- model call
- logs

### Observability

Observability means system-level visibility into behavior and health.

RABBIT Observability Mode includes:

- API health
- status code
- latency
- total calls
- failed calls
- retry count
- last request ID
- errors

### Conversation State

Conversation state is structured state about the current chat session.

Examples:

- current session ID
- recent messages
- summary
- last question
- retry state
- selected mode

### New Chat

New Chat starts a new conversation/session.

It should reset:

- session ID
- messages
- summary
- retry state

### Clear Chat

Clear Chat removes visible/stored messages but may keep the same session ID.

### Memory Reset

Memory Reset clears conversation memory, including summary and recent messages.

### User Mode

Public polished mode for recruiters, HR teams, hiring managers, consultants, peers, and website visitors.

### Debug Mode

Evidence mode for retrieval, chunks, source lineage, scores, prompt preview, and answer confidence.

### Observability Mode

Metrics mode for API health, latency, call counts, errors, retries, and request IDs.

### Tech Mode

Future backend-internals mode for raw payloads, schemas, deployment diagnostics, and tool traces.

## 2. Chat Conversation Strategy

RABBIT's conversation strategy should change depending on the platform surface.

### Web Dashboard

Purpose:

- demo
- testing
- interview walkthrough
- debugging
- observability

Conversation behavior:

- keep more messages visible
- allow Debug/Observability/Tech modes
- show session IDs and request IDs in non-user modes
- support retry
- support copy payload
- show source lineage and retrieval details

Recommended settings:

```text
Rendered messages: 24
Stored messages: 40
Summary trigger: 30-40 messages
Modes: User, Debug, Observability, Tech
```

### Mobile Responsive Web

Purpose:

- same URL adapts to phone screen
- bridge between dashboard and final widget
- test mobile reading quality

Conversation behavior:

- chat-first layout
- compact header
- compact sample questions
- keyword chips
- sticky composer
- fewer visible messages
- User Mode should feel close to final widget

Recommended settings:

```text
Rendered messages: 12-16
Stored messages: 20-30
Summary trigger: 16-24 messages
Modes: available, but stacked/compact
```

### Website Chat Widget

Purpose:

- final public assistant on Rajesh's website
- recruiter/hiring-manager visitor experience

Conversation behavior:

- floating chat button
- User Mode only
- no Debug/Observability/Tech visible publicly
- anonymous session ID
- lightweight history
- rolling summary
- clean relevant links
- strict guardrails

Recommended settings:

```text
Rendered messages: 12
Stored messages: 20
Summary trigger: 16-20 messages
Modes: User only
New Chat: available
Clear Chat: optional
```

## 3. Memory Strategy

### Current Implemented Memory

Currently implemented:

```text
Anonymous session ID
Stored message cap: 40
Rendered message cap: 24
Retry state
API observability
Privacy guardrails
Backend logs with session/request IDs
```

This is Phase 1 memory.

It is enough for the current dashboard and early mobile testing.

### Next Memory Layer: Rolling Summary

Next implementation should add:

```js
const SUMMARY_KEY = 'bti_conversation_summary';
```

The summary object can look like:

```json
{
  "summary": "User asked about AI, BPCL, R-Cafe, education, and role fit.",
  "updated_at": "2026-06-18T00:00:00Z",
  "turn_count_summarized": 12,
  "version": 1
}
```

### Summary Trigger

Possible trigger:

```text
If stored messages exceed threshold:
  summarize older messages
  keep latest messages
  update summary
```

### Important Rule

Conversation summary should not become the factual authority.

```text
Summary = conversation continuity
RAG corpus = factual grounding
```

### Where Memory Is Shown

User Mode:

```text
No memory internals shown.
```

Debug Mode:

```text
Show conversation summary and recent-message payload.
```

Observability Mode:

```text
Show summary length, message counts, update counts.
```

Tech Mode:

```text
Show raw memory payload and backend contract.
```

## 4. Infrastructure Across Platforms And Clouds

RABBIT's memory and conversation infrastructure should remain portable.

### Browser / Frontend Layer

Responsibilities:

- session ID
- recent messages
- rendered history
- stored history
- local summary
- retry UI
- new chat / clear chat
- mobile/widget behavior

Storage:

```text
localStorage for current phase
```

### Flask Backend Layer

Responsibilities:

- `/api/chat`
- `/health`
- request IDs
- logs
- mode enforcement
- shaping User/Debug/Observability/Tech payloads
- future summary-aware prompt input

### Azure Layer

Current Azure role:

- Azure AI Search for chunks/index
- Azure OpenAI for embeddings/chat completions
- vector/hybrid retrieval

Memory role:

- not primary chat memory
- source of grounded knowledge
- retrieval and citations

### AWS / S3 / Lambda / API Gateway Option

Possible future role:

- host static widget assets
- store approved documents
- store logs or anonymous session summaries
- expose API Gateway endpoint
- Lambda as lightweight backend proxy

Memory role:

- optional server-side session summary store
- optional log archive
- optional document upload lifecycle

### Website Hosting Layer

Possible website integration:

- JavaScript embed snippet
- floating RABBIT chat button
- iframe or script widget
- calls same backend API

Memory role:

- anonymous session in browser
- local rolling summary
- optional backend sync later

### Cross-Cloud Principle

Keep memory contracts platform-neutral.

Example memory payload should work whether backend is:

- Flask local
- Azure App Service
- AWS Lambda/API Gateway
- containerized service
- future agent backend

Core payload:

```json
{
  "session_id": "...",
  "question": "...",
  "conversation_summary": "...",
  "recent_messages": [],
  "mode": "user"
}
```

## 5. Three Progression Options

### Option 1: Browser-Only Memory

Best for immediate website widget v1.

Includes:

- session ID
- stored messages
- rendered messages
- local rolling summary
- no database

Pros:

- simple
- fast
- privacy-friendly
- easy to reset

Cons:

- browser-specific
- not persistent across devices

### Option 2: Browser Memory + Backend Logs

Best for recruiter/demo-ready deployment.

Includes:

- Option 1
- backend request logs
- session/request traceability
- API health and latency
- retry metrics
- anonymous usage visibility

Pros:

- practical
- traceable
- good for interviews
- no user accounts required

Cons:

- not full persistent memory
- log retention must be managed

### Option 3: Persistent Anonymous Memory Service

Best for mature product phase.

Includes:

- server-side anonymous session store
- rolling summaries stored server-side
- retention policy
- analytics dashboard
- export/delete controls

Pros:

- production-grade
- better analytics
- stronger continuity

Cons:

- more engineering
- privacy/security requirements
- database/storage layer needed

Recommended path:

```text
Option 1 now
Option 2 for public demo / early deployment
Option 3 only if RABBIT becomes a larger production assistant
```

## 6. Recommended Next Implementation

Next practical implementation:

1. Add `SUMMARY_KEY` to frontend.
2. Add `conversationSummary` object.
3. Add summary trigger after message threshold.
4. Keep latest messages as full text.
5. Store older-message summary locally.
6. Show summary in Debug/Observability only.
7. Later send summary to backend `/api/chat`.
8. Add New Chat to reset session + messages + summary.

## 7. Interview Explanation

A concise explanation:

```text
RABBIT uses anonymous chat sessions and short-term browser memory. It caps stored and rendered messages so the UI stays fast, especially on mobile and the future website widget. The next layer is rolling summarization: older turns are compressed into a conversation summary while the latest turns remain available as full messages. This preserves continuity without overloading the UI or model context. Facts remain grounded in the RAG corpus and Azure AI Search, while conversation summary is only used for dialogue continuity. Debug and Observability modes expose memory and API behavior for technical review, while User Mode remains clean for recruiters and website visitors.
```

---

# Strategic Layers For Conversational Applications

This section generalizes the memory and conversation plan into short-term, mid-term, long-term, and cloud strategy layers. These layers can guide RABBIT and any other conversational app.

## 1. Short-Term Strategy

### Goal

Build a fast, safe, usable chat experience without over-engineering infrastructure.

### Recommended Approach

Use browser/session-based memory first.

Typical short-term design:

```text
Session ID: browser-generated anonymous ID
Stored messages: limited
Rendered messages: limited
Conversation summary: optional or planned
Backend: simple API
Storage: localStorage + backend logs
Public UI: clean
Debug UI: available only to owner/admin
```

### What To Prioritize

- One working chat flow.
- Fast UI loading.
- Clear session ID.
- Basic retry.
- API health check.
- Guardrails for private/off-scope questions.
- Relevant links/citations.
- Basic logging.

### What To Avoid Initially

- User accounts.
- Permanent personal memory.
- Complex database-backed chat history.
- Multi-cloud complexity.
- Overexposing debug data to public users.

### RABBIT Short-Term Application

RABBIT short-term strategy:

```text
Browser session ID
40 stored messages
24 rendered messages
User/Debug/Observability/Tech modes in dashboard
User Mode clean for public use
API metrics in Observability Mode
Retry available after failed request
Rolling summary planned next
```

This is suitable for:

- local testing
- recruiter demo
- mobile responsive testing
- first website widget planning

## 2. Mid-Term Strategy

### Goal

Improve continuity, observability, and deployment readiness without adding unnecessary identity complexity.

### Recommended Approach

Add rolling conversation summaries and stronger backend traceability.

Typical mid-term design:

```text
Session ID: browser-generated anonymous ID
Recent messages: stored locally
Older turns: summarized
Summary: sent to backend with recent messages
Backend logs: structured
Observability: request/session metrics
Public widget: User Mode only
Admin dashboard: Debug/Observability/Tech
```

### What To Prioritize

- Rolling summary memory.
- New Chat versus Clear Chat separation.
- Summary-aware API payload.
- Better fallback behavior.
- Better source quality routing.
- Widget-ready public UI.
- Deployment packaging.
- Anonymous analytics.

### RABBIT Mid-Term Application

RABBIT mid-term strategy:

```text
Add SUMMARY_KEY in localStorage
Summarize older turns after threshold
Show summary only in Debug/Observability
Send summary + recent messages to backend
Keep facts grounded in Azure AI Search
Build website chat widget using User Mode only
Keep dashboard as admin/demo console
```

This is suitable for:

- public website widget v1
- recruiter-facing demo
- stronger technical interview story
- lightweight production deployment

## 3. Long-Term Strategy

### Goal

Move toward a production-grade assistant with durable memory, governance, analytics, and optional personalization.

### Recommended Approach

Only add persistent memory if the app requires it.

Typical long-term design:

```text
Session store: backend/database
Conversation summaries: server-side with retention
Message history: optional and limited
User identity: optional, only if needed
Admin dashboard: logs, analytics, source quality, feedback
Governance: privacy, retention, deletion controls
```

### What To Prioritize

- Data retention policy.
- Privacy/security review.
- Export/delete controls.
- Role-based admin access.
- Session analytics.
- Feedback loop for bad answers.
- Source quality scoring.
- Automated re-indexing.
- Monitoring and alerting.

### What To Avoid

- Storing sensitive chat data without a reason.
- Treating conversation memory as factual truth.
- Mixing private memory with public RAG evidence.
- Keeping unlimited message history.

### RABBIT Long-Term Application

RABBIT long-term strategy:

```text
Optional anonymous server-side session store
Retention-limited conversation summaries
Admin dashboard for document/chunk lifecycle
Azure index sync controls
Feedback and answer-quality review
Optional voice/MCP/agent integration
```

This is suitable only if RABBIT evolves into a mature public product.

## 4. Cloud Strategy

### Goal

Keep the chat architecture portable while using the right cloud service for the right layer.

A conversational app usually has these cloud layers:

```text
Frontend hosting
Backend API
Model provider
Search/retrieval
Document storage
Logs/observability
Session/memory store
Security/secrets
Deployment/CI-CD
```

## 5. Cloud Layer Options

### Frontend Hosting

Options:

- Static website hosting
- Vercel/Netlify
- Azure Static Web Apps
- AWS S3 + CloudFront
- Existing personal website hosting

RABBIT direction:

```text
Final chat widget can be served as a lightweight JS/CSS embed from website hosting or S3/CloudFront.
```

### Backend API

Options:

- Flask app
- FastAPI app
- Azure App Service
- Azure Container Apps
- AWS Lambda + API Gateway
- containerized backend

RABBIT current state:

```text
Flask backend locally
/api/chat
/health
```

RABBIT possible direction:

```text
Keep Flask/FastAPI for dashboard.
Use AWS Lambda/API Gateway or Azure App Service for public widget backend.
```

### Model Provider

Options:

- Azure OpenAI
- OpenAI API
- AWS Bedrock
- Google Vertex AI
- local/open-source models

RABBIT current state:

```text
Azure OpenAI for chat and embeddings.
```

### Search / Retrieval

Options:

- Azure AI Search
- OpenSearch
- Pinecone
- Weaviate
- FAISS
- pgvector
- Vertex AI Search

RABBIT current state:

```text
Azure AI Search with hybrid/vector retrieval.
```

### Document Storage

Options:

- local files
- Azure Blob Storage
- AWS S3
- database-backed document store
- CMS/webpage source

RABBIT current state:

```text
Local approved RAG documents and Azure AI Search index.
```

RABBIT possible direction:

```text
S3 bucket can store approved documents, exports, logs, or widget assets.
Azure AI Search remains retrieval/index layer.
```

### Logs And Observability

Options:

- local JSONL logs
- Azure Monitor / Application Insights
- AWS CloudWatch
- OpenTelemetry
- custom dashboard

RABBIT current state:

```text
Local JSONL logs + Observability Mode.
```

RABBIT future direction:

```text
Cloud logs for deployed backend.
Dashboard reads summarized health/call metrics.
```

### Session / Memory Store

Options:

- browser localStorage
- Redis
- DynamoDB
- Cosmos DB
- PostgreSQL
- S3/Blob JSON storage

Recommended progression:

```text
Short term: localStorage
Mid term: localStorage + backend logs
Long term: optional anonymous server-side memory store
```

### Secrets Management

Options:

- local `.env`
- Azure Key Vault
- AWS Secrets Manager
- environment variables in deployment platform

RABBIT current state:

```text
.env for local development.
```

RABBIT future direction:

```text
Use cloud secrets manager or deployment environment variables.
Never expose keys in frontend widget.
```

## 6. Cloud Strategy By Phase

### Short-Term Cloud Strategy

```text
Local Flask app
Azure OpenAI
Azure AI Search
local files
local logs
browser localStorage
.env secrets
```

Best for:

- development
- testing
- demo

### Mid-Term Cloud Strategy

```text
Hosted backend API
Azure AI Search
Azure OpenAI
static hosted widget assets
browser localStorage summary
cloud logs
secrets manager/env vars
```

Best for:

- public website widget v1
- recruiter demo
- controlled production-like setup

### Long-Term Cloud Strategy

```text
containerized or serverless backend
managed search/index lifecycle
document storage in S3 or Blob
anonymous session memory store
cloud observability
CI/CD deployment
retention and deletion policies
optional agent/voice services
```

Best for:

- mature production assistant
- multi-user analytics
- stronger governance

## 7. Recommended Cloud Direction For RABBIT

Recommended path:

### Now

```text
Keep current Flask dashboard local.
Keep Azure AI Search and Azure OpenAI.
Finalize responsive one-link UI.
Document memory and chat strategy.
```

### Next

```text
Add rolling summary in frontend.
Prepare public chat widget UI.
Deploy backend to one cloud target.
Keep keys server-side only.
```

### Later

```text
Choose between Azure App Service/Container Apps or AWS Lambda/API Gateway.
Optionally use S3 for widget assets/doc exports.
Add cloud logs and anonymous session analytics.
```

## 8. General Rule For Any Chat App

A good conversational app should separate these layers:

```text
UI memory = what the user sees
Session memory = recent conversation
Summary memory = compressed older turns
Knowledge memory = trusted factual corpus
Observability memory = system metrics/logs
Persistent memory = optional, governed, retention-limited
```

This separation keeps the app fast, explainable, safe, and scalable.

---

# Cloud Options Matrix For Conversational Apps

This section lists common cloud and open-source options for each layer of a conversational AI application. It is not limited to RABBIT. It can guide architecture decisions for any chat app, RAG app, AI assistant, website widget, or agentic system.

## 1. Frontend / Web App Hosting

Purpose:

- host dashboard UI
- host website chat widget assets
- serve static JS/CSS
- provide public web entry point

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Static hosting | S3 + CloudFront | Azure Static Web Apps, Azure Blob Static Website | Cloud Storage + Cloud CDN, Firebase Hosting | Nginx, Apache, Caddy |
| Web app hosting | Elastic Beanstalk, ECS, App Runner | Azure App Service, Container Apps | Cloud Run, App Engine | Docker on VM/VPS |
| Frontend frameworks | Amplify Hosting | Static Web Apps | Firebase Hosting | Vercel, Netlify, self-hosted Next.js/Vite |

RABBIT direction:

```text
Dashboard can remain Flask-hosted.
Final widget can be served as static JS/CSS from website hosting, S3/CloudFront, Azure Static Web Apps, or similar.
```

## 2. Backend API Layer

Purpose:

- receive chat requests
- apply guardrails
- call retrieval
- call model
- shape User/Debug/Observability payloads
- keep API keys server-side

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Serverless API | Lambda + API Gateway | Azure Functions | Cloud Functions | OpenFaaS, Knative |
| Container API | ECS/Fargate, App Runner, EKS | Azure Container Apps, AKS, App Service | Cloud Run, GKE | Docker, Kubernetes, Nomad |
| VM API | EC2 | Azure VM | Compute Engine | VPS + Nginx/Gunicorn/Uvicorn |
| Python backend | Lambda Python, ECS Python | Azure Functions Python, App Service | Cloud Run Python | Flask, FastAPI, Django |

RABBIT direction:

```text
Current: Flask backend.
Near-term deployment options: Azure App Service/Container Apps or AWS Lambda/API Gateway.
```

## 3. LLM / Chat Model Layer

Purpose:

- generate assistant responses
- follow prompt rules
- synthesize retrieved evidence
- produce user-facing answers

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Managed LLM | Amazon Bedrock | Azure OpenAI | Vertex AI Gemini | OpenAI API, Anthropic API, Cohere |
| Open model hosting | Bedrock marketplace, SageMaker | Azure AI Foundry, AKS | Vertex AI Model Garden, GKE | vLLM, Ollama, llama.cpp, TGI |
| Prompt orchestration | Bedrock Agents | Azure AI Foundry Agents | Vertex AI Agent Builder | LangChain, LlamaIndex, Haystack, Semantic Kernel |

RABBIT current direction:

```text
Azure OpenAI for chat generation.
```

## 4. Embedding Model Layer

Purpose:

- convert text into vectors
- support semantic search
- power vector/hybrid retrieval

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Managed embeddings | Bedrock Titan Embeddings, Cohere on Bedrock | Azure OpenAI embeddings | Vertex AI text embeddings | OpenAI embeddings, Cohere, Voyage AI |
| Open embeddings | SageMaker hosted models | Azure ML hosted models | Vertex AI hosted models | sentence-transformers, BGE, E5, Instructor |

RABBIT current direction:

```text
Azure OpenAI text-embedding-3-small.
```

## 5. Search / Vector Database / Retrieval Layer

Purpose:

- store chunks
- run keyword search
- run vector search
- run hybrid search
- return source metadata

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Managed search | Amazon OpenSearch Service, Kendra | Azure AI Search | Vertex AI Search, AlloyDB vector, Matching Engine | Elasticsearch/OpenSearch self-hosted |
| Vector DB | OpenSearch vector, Aurora pgvector | Azure AI Search, Cosmos DB vector, PostgreSQL pgvector | AlloyDB/Cloud SQL pgvector, Vertex Matching Engine | Qdrant, Weaviate, Milvus, Chroma, FAISS, pgvector |
| Hybrid search | OpenSearch hybrid | Azure AI Search hybrid | Vertex AI Search hybrid options | OpenSearch, Elasticsearch, Vespa |

RABBIT current direction:

```text
Azure AI Search for vector/hybrid retrieval.
```

## 6. Document Storage Layer

Purpose:

- store raw documents
- store approved RAG documents
- store exports
- store crawl outputs
- store versioned files

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Object storage | S3 | Azure Blob Storage | Cloud Storage | MinIO, local filesystem |
| File storage | EFS, FSx | Azure Files | Filestore | NFS, mounted disk |
| Versioned docs | S3 versioning | Blob versioning | Cloud Storage versioning | Git, DVC, lakeFS |

RABBIT possible direction:

```text
S3 can store approved documents, exports, widget assets, or logs.
Azure AI Search can remain the retrieval index.
```

## 7. Metadata / Relational Store

Purpose:

- document registry
- chunk registry
- approval status
- source metadata
- dashboard state
- lifecycle state

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Relational DB | RDS PostgreSQL/MySQL, Aurora | Azure Database for PostgreSQL/MySQL, SQL Database | Cloud SQL, AlloyDB | PostgreSQL, MySQL, SQLite |
| NoSQL DB | DynamoDB | Cosmos DB, Table Storage | Firestore, Bigtable | MongoDB, CouchDB |
| Lightweight local | SQLite on EFS/EC2 | SQLite on App Service/VM | SQLite on VM | SQLite, DuckDB |

RABBIT future direction:

```text
Document/chunk lifecycle dashboard may eventually need SQLite/PostgreSQL or DynamoDB/Cosmos depending on deployment path.
```

## 8. Session Memory / Conversation Store

Purpose:

- session ID
- recent messages
- rolling summary
- retry state
- memory reset
- anonymous usage tracking

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Browser memory | localStorage/sessionStorage | localStorage/sessionStorage | localStorage/sessionStorage | localStorage/sessionStorage |
| Cache/session store | ElastiCache Redis | Azure Cache for Redis | Memorystore Redis | Redis, KeyDB |
| NoSQL session store | DynamoDB | Cosmos DB | Firestore | MongoDB |
| SQL session store | RDS/Aurora | Azure PostgreSQL/SQL DB | Cloud SQL/AlloyDB | PostgreSQL, SQLite |
| Object session logs | S3 | Blob Storage | Cloud Storage | MinIO/local files |

Recommended progression:

```text
Short term: browser localStorage
Mid term: browser memory + backend logs
Long term: optional Redis/DynamoDB/Cosmos/PostgreSQL anonymous session store
```

## 9. Logs / Observability / Monitoring

Purpose:

- API health
- latency
- error tracking
- request IDs
- traceability
- usage analytics

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Logs | CloudWatch Logs | Azure Monitor Logs, Log Analytics | Cloud Logging | ELK/OpenSearch, Loki |
| Metrics | CloudWatch Metrics | Azure Monitor Metrics | Cloud Monitoring | Prometheus, Grafana |
| Tracing | X-Ray | Application Insights | Cloud Trace | OpenTelemetry, Jaeger, Tempo |
| Dashboards | CloudWatch Dashboard | Azure Dashboard, App Insights | Cloud Monitoring Dashboards | Grafana, Metabase |

RABBIT current direction:

```text
Local JSONL logs + Observability Mode.
Future: cloud logs depending on backend deployment target.
```

## 10. Secrets Management

Purpose:

- store API keys safely
- avoid exposing secrets in frontend
- manage environment config

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Secrets | AWS Secrets Manager, SSM Parameter Store | Azure Key Vault | Secret Manager | Doppler, Vault, SOPS, .env for local only |
| App env vars | Lambda/ECS/App Runner env | App Service/Functions env | Cloud Run/Functions env | Docker/Kubernetes env/secrets |

Rule:

```text
Never expose LLM/Search API keys in the website widget frontend.
```

## 11. Authentication / Access Control

Purpose:

- protect admin/debug modes
- secure APIs
- separate public widget from owner dashboard

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Identity | Cognito | Microsoft Entra ID / B2C | Identity Platform / Firebase Auth | Auth0, Clerk, Keycloak, custom auth |
| API auth | IAM, API Gateway authorizers | Managed Identity, Easy Auth | IAM, IAP | JWT, OAuth2, API keys |
| Admin access | Cognito groups/IAM | Entra roles | IAM roles | RBAC in app |

RABBIT current direction:

```text
Simple owner/demo password for non-user modes.
Future: real admin auth if deployed publicly.
```

## 12. CI/CD And Deployment

Purpose:

- build
- test
- deploy
- rollback
- manage versions

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| CI/CD | CodePipeline, CodeBuild | Azure DevOps, GitHub Actions | Cloud Build, Cloud Deploy | GitHub Actions, GitLab CI, Jenkins |
| Containers | ECR + ECS/EKS | ACR + Container Apps/AKS | Artifact Registry + Cloud Run/GKE | Docker Registry + Kubernetes |
| IaC | CloudFormation, CDK, Terraform | Bicep, ARM, Terraform | Deployment Manager, Terraform | Terraform, Pulumi |

RABBIT future direction:

```text
GitHub Actions or Azure DevOps can deploy dashboard/backend/widget assets.
```

## 13. Feedback And Evaluation Layer

Purpose:

- capture bad answers
- improve prompts
- improve retrieval
- measure answer quality

| Layer | AWS | Azure | GCP | Open Source / Platform Neutral |
|---|---|---|---|---|
| Feedback store | DynamoDB, S3 | Cosmos DB, Blob | Firestore, Cloud Storage | PostgreSQL, SQLite, Supabase |
| Evaluation | Bedrock evals, custom Lambda | Azure AI evaluation, Prompt Flow | Vertex AI evals | Ragas, DeepEval, TruLens, custom evals |
| Analytics | QuickSight | Power BI | Looker Studio | Metabase, Superset |

RABBIT future direction:

```text
Add thumbs up/down or feedback capture after widget is stable.
```

## 14. Recommended Cloud Choices By Maturity

### Prototype / Local Demo

```text
Frontend: Flask templates
Backend: Flask
Model: Azure OpenAI
Search: Azure AI Search
Memory: browser localStorage
Logs: local JSONL
Secrets: .env
```

### Public Widget V1

```text
Frontend: website embed JS/CSS
Backend: Azure App Service / Container Apps OR AWS Lambda/API Gateway
Model: Azure OpenAI
Search: Azure AI Search
Memory: browser localStorage + rolling summary
Logs: cloud logs
Secrets: Key Vault / Secrets Manager / env vars
```

### Production Assistant

```text
Frontend: CDN-hosted widget
Backend: container/serverless API
Model: managed LLM provider
Search: managed search/vector DB
Memory: anonymous session store + retention
Logs: cloud observability
Secrets: managed secrets
CI/CD: automated deployment
Governance: retention/delete/export controls
```

## Stakeholder Context Capture

In the RABBIT Assistant flow, the assistant may ask for a visitor's name, profession, and company position as part of a polite professional introduction. If provided, these details should be treated as session-level conversation context. They help later review in Debug/Observability modes and can help Rajesh prepare for formal follow-up conversations.

The assistant should not make User Mode feel like data collection. It should ask politely, continue naturally, and avoid over-personalizing the answer. Conversation review can happen later through logs, session metadata, and observability screens.

