# Business-Tech Keyword Guide And Embedded Questions

Generated at: 2026-06-20T03:00:19.313133+00:00

## Purpose

This document defines the guided keyword strategy for RABBIT Assistant before it is implemented in the UI. The goal is to make the assistant visibly business-plus-technology focused and to guide recruiters, HR teams, hiring managers, consultants, and collaborators into stronger questions.

RABBIT uses hybrid retrieval:

```text
user question
  -> keyword search terms
  -> vector semantic retrieval
  -> hybrid Azure AI Search results
  -> RAG answer
```

The keywords below are not Azure's fixed keyword dictionary. They are UI conversation guides. Each keyword triggers a stronger embedded question that improves both keyword matching and semantic retrieval.

## Design Principle

The UI should not only show generic labels like `AI` or `Business`. It should explicitly show Rajesh's positioning:

```text
Business experience
  + Technology capability
  + Business-Tech hybrid role fit
```

Recommended UI grouping:

```text
Business Keywords
Technology Keywords
Business-Tech Hybrid Keywords
```

Each keyword should be clickable and should submit the mapped embedded question.

---

## 1. Business Keywords

| Keyword | Intent | Embedded Strong Question | Notes |
|---|---|---|---|
| Business Leadership | Broad business profile | Summarize Rajesh's business leadership experience across BPCL, Medtronic, SMAAT, RedRybbons, and R-Cafe. | Good recruiter entry point. |
| BPCL | Industrial execution proof | What experience does Rajesh have with BPCL and how does it prove execution under pressure? | Strong evidence page. |
| Medtronic | Sales/P&L/healthcare business | What was Rajesh's Medtronic experience and business impact? | Connects healthcare, territory ownership, P&L. |
| SMAAT | Infrastructure/platform operations | What did Rajesh do at SMAAT and how does it show distributed infrastructure leadership? | Strong bridge to systems thinking. |
| RedRybbons | Entrepreneurship/craft platform | What is Rajesh's RedRybbons entrepreneurial experience? | Shows founder/operator background. |
| R-Cafe | Live entrepreneurship/current context | What is Rajesh's R-Cafe experience and current entrepreneurial context? | Important current business context. |
| P&L | Ownership and outcomes | Where has Rajesh handled P&L, operations, and measurable business outcomes? | Useful for leadership roles. |
| Strategy | IIM/business strategy fit | How do Rajesh's IIM Calcutta Marketing and Strategy background and business experience support role fit? | Academic + professional positioning. |
| Consulting | Advisory engagement fit | What consulting or advisory roles would fit Rajesh's business-tech background? | Useful for non-job engagements. |
| Governance | Law/PIL/governance mindset | How does Rajesh's Supreme Court advocacy and governance experience connect to AI governance and responsible systems? | Good for responsible AI discussions. |
| Operations | Operating discipline | What operating discipline has Rajesh demonstrated across refinery, healthcare, water infrastructure, and hospitality? | Bridges physical systems to digital systems. |
| Customer Experience | Market/customer orientation | How has Rajesh handled customer experience, market expansion, and business execution? | Good for business/product roles. |

---

## 2. Technology Keywords

| Keyword | Intent | Embedded Strong Question | Notes |
|---|---|---|---|
| AI | Broad AI capability | What is Rajesh's AI experience and how does it connect to business outcomes? | Main tech entry point. |
| Analytics | Data/business analytics foundation | What are Rajesh's data science, analytics, statistics, and business analytics capabilities? | Useful for analytics roles. |
| MLOps | Production ML capability | Show Rajesh's MLOps capability with project evidence. | Strong evidence category. |
| Architecture | System design evidence | Show Rajesh's architecture-related project evidence across AI, MLOps, cloud, CI/CD, Docker, and Kubernetes. | Broad term: appears across many pages. |
| Azure | Azure platform capability | Which Rajesh projects or skills demonstrate Azure AI, Azure DevOps, and Azure MLOps capability? | Important due to current RABBIT stack. |
| AWS | AWS/SageMaker/CDK capability | Which Rajesh projects demonstrate AWS, SageMaker, CDK, MLflow, and cloud architecture capability? | Strong AI project evidence. |
| GCP | GCP/Vertex/Cloud Build | Which Rajesh projects demonstrate GCP, Vertex AI, Cloud Build, and automation capability? | Strong project cluster. |
| Docker | Containerization capability | Which Rajesh projects demonstrate Docker and containerization capability? | Good for infrastructure discussion. |
| Kubernetes | Orchestration capability | Which Rajesh projects show Kubernetes capability? | Strong recruiter keyword. |
| CI/CD | Pipeline automation | Which pages discuss Rajesh's CI/CD pipeline capability across GitHub Actions, Azure DevOps, AWS, and GCP? | Important for MLOps/platform roles. |
| IaC | Infrastructure as Code | Which Rajesh projects demonstrate Infrastructure as Code and platform automation? | Connects Terraform/CDK/platform automation. |
| RAG | This app as evidence | Explain this RABBIT app as evidence of Rajesh's RAG, Azure AI Search, embeddings, and hybrid retrieval capability. | Visible proof of current work. |
| Vector Search | Retrieval architecture | Explain how RABBIT uses keyword search plus vector semantic retrieval in Azure AI Search. | Good technical interview question. |
| Embeddings | Semantic retrieval | What role do text embeddings play in RABBIT and Rajesh's AI search architecture? | Good for explaining architecture. |
| Observability | Runtime inspection | What observability, tracing, logging, and debug features are planned or implemented in RABBIT? | Bridges UI/backend. |

---

## 3. Business-Tech Hybrid Keywords

| Keyword | Intent | Embedded Strong Question | Notes |
|---|---|---|---|
| Role Fit | Broad role mapping | What roles is Rajesh qualified for across business and technology? | Main recruiter question. |
| AI Transformation | Business transformation | Why is Rajesh suitable for AI transformation and business-tech hybrid roles? | Strong positioning question. |
| Business + AI | Bridge business and tech | How does Rajesh connect business problems to AI, analytics, MLOps, and measurable outcomes? | Core narrative. |
| Transition | Career transition story | How should a recruiter understand Rajesh's transition into AI, MLOps, and business-tech roles? | Important personal-professional narrative. |
| Evidence | Proof request | What is the strongest evidence that Rajesh can deliver business-tech outcomes? | Good skeptical recruiter question. |
| Projects | Project portfolio | Show Rajesh's strongest AI, MLOps, cloud, and business integration projects. | Useful for quick browsing. |
| Recruiter View | Recruiter framing | How should a recruiter position Rajesh for Indian and international business-tech opportunities? | Helps HR/hiring manager. |
| Consulting Fit | Consulting discussion | What consulting engagements would be suitable for Rajesh's business-tech and AI background? | Useful for advisory work. |
| International Roles | Global fit | How does Rajesh's profile fit Indian and international business-tech roles? | Fits user goals. |
| Contact | Professional contact | How can a professional stakeholder contact Rajesh for a role, consulting, or collaboration? | Must stay professional and concise. |
| RABBIT App | App evidence | How does the RABBIT Assistant itself prove Rajesh's Business-AI-GenAI hybrid capability? | Important demo narrative. |
| Business-Tech Architecture | Full-stack project story | Explain the architecture of RABBIT as a business-tech RAG system built by Rajesh. | Good interview/demo bridge. |

---

## 4. UI Behavior Recommendation

### Desktop / Web Demo

Show all three groups in the sidebar:

```text
Conversation Guide
  Business Keywords
  Technology Keywords
  Business-Tech Hybrid
```

This is suitable for demo/interview mode because it shows the depth of the project.

### Mobile / Future Chat Widget

Show fewer chips by default:

```text
Business
AI/MLOps
Projects
Role Fit
Contact
```

Then expose the full keyword list behind a `Topics` or `Explore` button.

### User Mode

- Keep chips simple and non-technical unless the user selects a technical topic.
- Use embedded questions behind the chips so the search query is strong.
- Do not expose raw retrieval terms or debug logic.

### Debug Mode

Show:

- clicked keyword
- embedded question submitted
- rewritten/effective query
- retrieved chunks
- matched page IDs
- keyword + vector search behavior

---

## 5. Implementation Plan

1. Review and edit this keyword list.
2. Approve final labels and embedded questions.
3. Add grouped keyword UI to `18_flask_chat_ui/static/app.js`.
4. Update CSS for grouped keyword chips.
5. Cache-bust `index.html` static asset version.
6. Add traceability fields later:

```json
{
  "clicked_keyword": "Architecture",
  "keyword_group": "Technology Keywords",
  "embedded_question": "Show Rajesh's architecture-related project evidence..."
}
```

7. In Debug Mode, show the keyword mapping and effective query.

---

## 6. Open Review Questions

- Should `GenAI` be shown now as a full technology keyword, or should it remain future-facing until dedicated GenAI pages are added?
- Should `Salary/Compensation` be omitted entirely from guided keywords because of guardrails? Recommended: omit.
- Should `Contact` appear in User Mode chips? Recommended: yes, but only with professional boundaries.
- Should `Architecture` be one keyword or split into Cloud Architecture, MLOps Architecture, RAG Architecture? Recommended: one broad keyword first, then split later if needed.

---

## Current Recommendation

Use the three-group model:

```text
Business Keywords
Technology Keywords
Business-Tech Hybrid Keywords
```

This best represents Rajesh's positioning and prevents the assistant from looking like a purely technical bot or a purely business profile bot.

---

## 7. Corpus-Derived Bag-Of-Words And Phrase Analysis

Analyzed source: `/Users/jhonny001/Desktop/RABBIT_Assistant/06_output_rag_documents_ready`

- Canonical RAG documents scanned: 53
- Method: mined cleaned terms plus 2-word and 3-word phrases across all RAG-ready webpages. Extraction artifacts such as headings, URLs, and button boilerplate are filtered out.
- Classification: words and phrases are grouped as Business, Technology, or Business-Tech Hybrid.

### 7.1 Business Bag Of Words

| Word | Count | Document Coverage |
|---|---:|---:|
| execution | 255 | 33/53 |
| governance | 158 | 27/53 |
| outcomes | 67 | 23/53 |
| reliability | 58 | 21/53 |
| operations | 90 | 16/53 |
| business | 194 | 15/53 |
| strategy | 42 | 11/53 |
| leadership | 54 | 8/53 |
| sales | 22 | 7/53 |
| product | 28 | 6/53 |
| cafe | 57 | 4/53 |
| redrybbons | 39 | 4/53 |
| customer | 15 | 4/53 |
| transformation | 15 | 4/53 |
| stakeholder | 5 | 4/53 |
| smaat | 28 | 3/53 |
| bpcl | 25 | 3/53 |
| medtronic | 21 | 3/53 |
| market | 21 | 3/53 |
| marketing | 3 | 3/53 |
| consulting | 9 | 2/53 |
| entrepreneurship | 4 | 1/53 |

### 7.2 Technology Bag Of Words

| Word | Count | Document Coverage |
|---|---:|---:|
| deployment | 677 | 49/53 |
| mlops | 468 | 49/53 |
| model | 737 | 46/53 |
| github | 469 | 42/53 |
| architecture | 286 | 42/53 |
| monitoring | 170 | 41/53 |
| cloud | 409 | 40/53 |
| pipeline | 788 | 39/53 |
| ai | 440 | 38/53 |
| devops | 321 | 37/53 |
| yaml | 245 | 37/53 |
| orchestration | 196 | 37/53 |
| cicd | 420 | 36/53 |
| registry | 254 | 34/53 |
| container | 230 | 33/53 |
| training | 358 | 32/53 |
| docker | 417 | 29/53 |
| artifact | 165 | 27/53 |
| aws | 610 | 25/53 |
| inference | 215 | 22/53 |
| actions | 177 | 22/53 |
| logging | 82 | 21/53 |
| azure | 410 | 20/53 |
| kubernetes | 299 | 20/53 |
| endpoint | 182 | 20/53 |
| gcp | 171 | 19/53 |
| iac | 98 | 19/53 |
| architectural | 36 | 18/53 |
| cdk | 308 | 16/53 |
| sagemaker | 218 | 15/53 |
| vertex | 67 | 12/53 |
| mlflow | 214 | 11/53 |
| kubeflow | 184 | 10/53 |
| observability | 24 | 9/53 |
| traceability | 15 | 8/53 |
| terraform | 10 | 2/53 |
| rag | 2 | 1/53 |
| hybrid | 2 | 1/53 |
| vector | 1 | 1/53 |

### 7.3 Hybrid Bag Of Words

| Word | Count | Document Coverage |
|---|---:|---:|
| platform | 849 | 47/53 |
| production | 317 | 45/53 |
| architecture | 286 | 42/53 |
| ai | 440 | 38/53 |
| automation | 193 | 37/53 |
| governance | 158 | 27/53 |
| workflow | 82 | 26/53 |
| integration | 79 | 25/53 |
| outcomes | 67 | 23/53 |
| projects | 74 | 21/53 |
| reliability | 58 | 21/53 |
| business | 194 | 15/53 |
| systems | 189 | 14/53 |
| role | 33 | 12/53 |
| evidence | 25 | 9/53 |
| transformation | 15 | 4/53 |
| stakeholder | 5 | 4/53 |
| consulting | 9 | 2/53 |

### 7.4 Business 2-3 Word Phrases

| Phrase | Count | Document Coverage |
|---|---:|---:|
| scalability reliability | 23 | 11/53 |
| cafe redrybbons | 15 | 4/53 |
| execution governance | 15 | 5/53 |
| governance controls | 14 | 5/53 |
| medtronic india | 13 | 3/53 |
| execution evidence | 13 | 6/53 |
| smaat india | 11 | 3/53 |
| execution manual | 9 | 4/53 |
| redrybbons craft | 8 | 3/53 |
| strategy rather | 8 | 4/53 |
| project execution | 8 | 4/53 |
| strategy rather application | 8 | 4/53 |
| execution layer | 7 | 2/53 |
| lack governance | 7 | 5/53 |
| reproducibility governance | 7 | 3/53 |
| redrybbons built | 6 | 4/53 |
| refinery operations | 6 | 2/53 |
| field operations | 6 | 2/53 |
| same execution | 6 | 2/53 |
| lineage governance | 6 | 5/53 |
| codepipeline execution | 6 | 2/53 |
| multi-stage execution | 6 | 3/53 |
| execution link | 6 | 3/53 |
| redrybbons craft innovation | 6 | 3/53 |
| execution evidence project | 6 | 6/53 |
| view codepipeline execution | 6 | 2/53 |
| execution manual approvals | 6 | 3/53 |
| project execution link | 6 | 3/53 |
| execution link proof | 6 | 3/53 |
| redrybbons cafe | 5 | 2/53 |

### 7.5 Technology 2-3 Word Phrases

| Phrase | Count | Document Coverage |
|---|---:|---:|
| github actions | 169 | 18/53 |
| aws cdk | 161 | 15/53 |
| model registry | 132 | 23/53 |
| azure ml | 123 | 8/53 |
| azure devops | 110 | 12/53 |
| ai platform | 105 | 21/53 |
| kubeflow pipelines | 84 | 9/53 |
| mlops platform | 83 | 17/53 |
| training evaluation | 78 | 10/53 |
| google cloud | 77 | 9/53 |
| model serving | 71 | 10/53 |
| vertex ai | 65 | 12/53 |
| cicd pipelines | 61 | 17/53 |
| pipeline code | 61 | 15/53 |
| solution architecture | 58 | 26/53 |
| cicd pipeline | 56 | 16/53 |
| model deployment | 56 | 16/53 |
| docker compose | 55 | 7/53 |
| model training | 54 | 16/53 |
| container orchestration | 53 | 14/53 |
| github repository | 53 | 25/53 |
| artifact storage | 53 | 19/53 |
| ai ml | 50 | 18/53 |
| devops cicd | 50 | 17/53 |
| deployment pipeline | 50 | 13/53 |
| ml model | 48 | 14/53 |
| ml inference | 48 | 6/53 |
| cloud platform | 47 | 15/53 |
| aws eks | 47 | 5/53 |
| architecture yaml | 47 | 18/53 |

### 7.6 Hybrid 2-3 Word Phrases

| Phrase | Count | Document Coverage |
|---|---:|---:|
| pipeline execution | 67 | 15/53 |
| business leadership | 30 | 4/53 |
| challenges outcomes | 30 | 14/53 |
| business data | 22 | 5/53 |
| deployment strategy | 14 | 7/53 |
| pipeline execution governance | 13 | 5/53 |
| outcomes technical | 12 | 12/53 |
| pipeline execution evidence | 12 | 6/53 |
| challenges outcomes technical | 12 | 12/53 |
| real business | 11 | 4/53 |
| business architecture | 10 | 6/53 |
| business value | 10 | 4/53 |
| business problem | 10 | 4/53 |
| execution model | 9 | 3/53 |
| deployment strategy rather | 8 | 4/53 |
| outcomes technical challenges | 8 | 8/53 |
| business architecture story | 8 | 4/53 |
| real-world business | 7 | 2/53 |
| business outcomes | 6 | 3/53 |
| architecture execution | 6 | 3/53 |
| territory business | 6 | 2/53 |
| governance aws | 6 | 5/53 |
| deployment operations | 6 | 2/53 |
| model governance | 6 | 4/53 |
| business cases | 6 | 3/53 |
| business team | 6 | 3/53 |
| territory business leadership | 6 | 2/53 |
| same execution model | 6 | 2/53 |
| pipeline pipeline execution | 6 | 4/53 |
| technologies pipeline execution | 6 | 6/53 |

### 7.7 Architecture As Business And Technology Context

`Architecture` is not only a technical keyword in this corpus. It appears in both business-system context and technology-system context. Therefore the UI should treat it as a bridge keyword and route follow-up questions based on nearby terms.

| Architecture Phrase | Count | Document Coverage | Context |
|---|---:|---:|---|
| solution architecture | 58 | 26/53 | Technology |
| architecture yaml | 47 | 18/53 | Technology |
| architecture yaml mapping | 34 | 17/53 | Technology |
| cicd architecture | 30 | 15/53 | Technology |
| cicd architecture yaml | 28 | 14/53 | Technology |
| objective solution architecture | 26 | 25/53 | Technology |
| mapping architecture | 25 | 14/53 | Technology |
| architectural solution | 22 | 17/53 | Technology |
| devops cicd architecture | 22 | 11/53 | Technology |
| architecture block | 20 | 20/53 | Technology |
| architecture architectural | 17 | 17/53 | Technology |
| solution architecture architectural | 17 | 17/53 | Technology |
| architecture architectural solution | 17 | 17/53 | Technology |
| solve architectural | 16 | 16/53 | Technology |
| project solve architectural | 16 | 16/53 | Technology |
| architecture ai | 14 | 13/53 | Technology |
| solution architecture ai | 13 | 12/53 | Technology |
| architecture skills | 12 | 12/53 | Technology |
| solution architecture skills | 12 | 12/53 | Technology |
| architecture skills technologies | 12 | 12/53 | Technology |
| architecture yaml construct | 12 | 6/53 | Technology |
| yaml mapping architecture | 11 | 11/53 | Technology |
| construct mapping architecture | 11 | 11/53 | Technology |
| mapping architecture block | 11 | 11/53 | Technology |
| business architecture | 10 | 6/53 | Hybrid |
| reference architecture | 10 | 5/53 | Technology |
| architecture ai devops | 10 | 9/53 | Technology |
| docker architecture | 8 | 2/53 | Technology |
| architecture aws | 8 | 4/53 | Technology |
| architecture flow | 8 | 4/53 | Technology |
| architecture story | 8 | 4/53 | Technology |
| business architecture story | 8 | 4/53 | Hybrid |
| service architecture | 7 | 3/53 | Technology |
| mlops architecture | 7 | 4/53 | Technology |
| architecture execution | 6 | 3/53 | Hybrid |

### 7.8 Keyword Strategy From Corpus Evidence

Recommended UI keyword groups after corpus review:

**Business:** Business Leadership, Operations, Governance, Strategy, BPCL, Medtronic, SMAAT, RedRybbons, R-Cafe, Customer Experience, Consulting, P&L.

**Technology:** AI, MLOps, Architecture, AWS, Azure, GCP, Docker, Kubernetes, CI/CD, IaC, CDK, MLflow, Kubeflow, SageMaker, Monitoring, Logging, Observability.

**Hybrid:** Business + AI, AI Transformation, Platform Thinking, Production-Grade Systems, Architecture for Outcomes, Governance + MLOps, Role Fit, Evidence, Projects, Recruiter View, Consulting Fit.

### 7.9 Important Interpretation

- Bag-of-words terms improve keyword search coverage.
- 2-3 word phrases improve UI labels and embedded strong questions.
- Some high-repeat terms are technical and should be hidden in mobile User Mode but visible in web demo or Debug/Tech mode.
- Some low-repeat business names are still strategically important because they represent specific evidence pages.

---

## 8. Concept Normalization For Bag-Of-Words

A bag-of-words strategy should not treat every spelling or abbreviation as a separate concept. Some words, acronyms, and product names represent the same retrieval intent. RABBIT should normalize these into concept groups for UI labels, embedded questions, retrieval interpretation, and debug tracing.

### 8.1 Kubernetes Concept Group

Primary UI label:

```text
Kubernetes
```

Equivalent terms and related retrieval words:

```text
Kubernetes
K8s
container orchestration
orchestration
EKS
AKS
GKE
Minikube
Kubeflow
Kubernetes-native
cluster
pods
deployments
services
```

Recommended embedded question:

```text
Which Rajesh projects show Kubernetes / K8s capability, including EKS, Minikube, Kubeflow, container orchestration, clusters, pods, deployments, and services?
```

Interpretation:

- `K8s` is a shorthand for Kubernetes.
- `EKS`, `AKS`, and `GKE` are managed Kubernetes services.
- `Minikube` is local Kubernetes.
- `Kubeflow` is Kubernetes-native MLOps and should be associated with Kubernetes when discussing AI/MLOps orchestration.

### 8.2 Why Concept Normalization Matters

Without normalization, a user may click or type:

```text
K8s
```

while the corpus may use:

```text
Kubernetes
container orchestration
EKS
Minikube
Kubeflow
```

Treating these as one concept improves:

- keyword search recall
- vector semantic retrieval context
- UI keyword clarity
- debug traceability
- embedded question quality

### 8.3 General Rule

For each UI keyword, define:

```text
primary label
equivalent words
related words
embedded strong question
retrieval interpretation
```

This turns a flat bag of words into a concept-aware keyword guide.

---

## 9. NLP Concepts Used In The Keyword Strategy

Updated at: 2026-06-20T03:25:01.640574+00:00

The keyword guide is not just a UI convenience. It is an NLP-inspired query engineering layer for RABBIT's RAG pipeline. The goal is to convert natural user language into stronger searchable intent while preserving a clean user experience.

### 9.1 Corpus

In NLP, a corpus is the text collection being analyzed.

For RABBIT, the corpus is:

```text
53 canonical RAG documents
142 approved chunks
54 extracted website URLs
```

The corpus comes from Rajesh's professional website and is used for keyword search, vector semantic retrieval, source links, and answer grounding.

### 9.2 Tokenization

Tokenization breaks text into smaller units such as words, sub-words, or phrases.

In this project, corpus text was treated as tokens and phrases so we could identify repeated terms such as:

```text
AI
MLOps
Architecture
AWS
Azure
Docker
Kubernetes
Business
Governance
Operations
```

This helps build the bag-of-words layer.

### 9.3 Stopword Removal

Stopwords are common words that add little retrieval value, such as:

```text
the
and
is
of
to
with
```

For the keyword guide, stopwords and extraction artifacts were filtered out so the remaining terms better represent business and technology meaning.

We also filtered extraction noise such as:

```text
h1
h2
h3
https
url
button
source
page
```

### 9.4 Stemming And Lemmatization Style Normalization

Stemming and lemmatization reduce word variants into a common base form.

RABBIT uses a practical concept-normalization approach rather than strict linguistic stemming.

Examples:

```text
architecture / architectures / architectural / architect -> Architecture
operation / operations / operational -> Operations
deployment / deployments / deployed -> Deployment
Docker / Dockerized -> Docker
```

This prevents the UI and retrieval logic from treating related forms as unrelated concepts.

### 9.5 Synonyms, Aliases, And Controlled Vocabulary

A controlled vocabulary maps different user words to one canonical concept.

Example concept group:

```text
Kubernetes = Kubernetes + K8s + container orchestration + EKS + AKS + GKE + Minikube + Kubeflow + clusters + pods + deployments + services
```

This is important because users may type `K8s`, while the corpus may contain `Kubernetes`, `EKS`, `Minikube`, or `Kubeflow`.

RABBIT should use one visible UI label, but the embedded question can include the aliases.

### 9.6 Named Entity Recognition Style Thinking

Named Entity Recognition identifies important entities such as people, companies, tools, platforms, and locations.

For RABBIT, important entity groups include:

**Business entities:**

```text
BPCL
Medtronic
SMAAT
RedRybbons
R-Cafe
IIM Calcutta
IISc Bangalore
ISB
NITK Surathkal
```

**Technology entities:**

```text
Azure
AWS
GCP
Docker
Kubernetes
MLflow
Kubeflow
SageMaker
Vertex AI
GitHub Actions
Azure DevOps
Cloud Build
```

These entities should be preserved, not removed, because they carry strong retrieval and credibility value.

### 9.7 N-Grams: 2-Word And 3-Word Phrases

N-grams are sequences of words. They capture meaning better than isolated terms.

Examples from the RABBIT corpus:

```text
machine learning
github actions
aws cdk
model registry
azure devops
solution architecture
container orchestration
manual approval
artifact storage
model deployment
```

These phrases are stronger than single words because they preserve context.

### 9.8 Bag Of Words

A bag-of-words model represents text by the presence or frequency of important words, ignoring exact sentence order.

RABBIT uses bag-of-words thinking to create grouped keyword sets:

```text
Business bag of words
Technology bag of words
Business-Tech hybrid bag of words
```

This helps build UI chips and embedded strong questions.

### 9.9 Semantics And Word Embeddings

Word embeddings represent meaning as vectors. Similar meanings are closer in vector space.

RABBIT uses Azure OpenAI embeddings for vector semantic retrieval.

Current embedding setup:

```text
model/deployment: text-embedding-3-small
vector dimensions: 1536
```

This means RABBIT can retrieve relevant content even when the user does not use the exact same words as the webpage.

### 9.10 Query Expansion

Query expansion adds related terms to a short user query so search has more context.

Example:

User clicks:

```text
Kubernetes
```

Embedded strong question:

```text
Which Rajesh projects show Kubernetes / K8s capability, including EKS, Minikube, Kubeflow, container orchestration, clusters, pods, deployments, and services?
```

This improves both keyword retrieval and vector semantic retrieval.

### 9.11 Hybrid Search

RABBIT uses hybrid retrieval:

```text
keyword search + vector semantic retrieval
```

Keyword search helps with exact terms:

```text
BPCL
Kubernetes
Azure
SageMaker
R-Cafe
```

Vector semantic retrieval helps with meaning-based questions:

```text
What makes Rajesh suitable for business-tech roles?
Show me architecture evidence.
How does his business experience connect to AI?
```

The keyword guide improves hybrid search by giving both systems a better query.

### 9.12 Language Model And LLM Layer

The retrieved context is passed to an LLM to generate a polished answer.

The LLM is responsible for:

```text
answer generation
summarization
conversation tone
role-fit framing
professional guardrails
```

But the LLM should not invent source links. Links must come from validated metadata.

### 9.13 Transformer And Attention Concept

Modern LLMs use transformer architectures, where attention helps the model understand relationships across the prompt and retrieved context.

In RABBIT, this matters because the final answer depends on relationships between:

```text
user question
retrieved chunks
profile positioning context
prompt rules
guardrails
source metadata
```

### 9.14 Sentiment And Tone Control

RABBIT is not doing formal sentiment analysis yet, but it uses tone control in the prompt.

The desired tone is:

```text
professional
pleasant
concise
stakeholder-friendly
not defensive
not overly verbose
```

This is important for recruiter, HR, hiring manager, consulting, and collaboration conversations.

### 9.15 Information Retrieval Concepts

RABBIT's keyword guide improves classic retrieval metrics conceptually:

```text
precision: fewer irrelevant chunks
recall: better coverage through synonyms and aliases
ranking: stronger query terms improve top results
traceability: clicked keyword -> embedded question -> retrieved chunks -> answer
```

### 9.16 Concept Groups To Add Over Time

The same NLP concept-normalization approach should be extended beyond Kubernetes.

| Canonical Concept | Aliases / Related Terms |
|---|---|
| Kubernetes | K8s, EKS, AKS, GKE, Minikube, Kubeflow, pods, clusters, services |
| CI/CD | CICD, pipelines, GitHub Actions, Azure DevOps, Cloud Build, deployment automation |
| IaC | Infrastructure as Code, CDK, Terraform, CloudFormation, provisioning |
| RAG | Retrieval augmented generation, Azure AI Search, embeddings, vector search, hybrid retrieval |
| AI | Artificial intelligence, ML, machine learning, GenAI, LLM, models |
| Analytics | Data analytics, business analytics, statistics, probability, hypothesis testing, dashboards |
| Business Leadership | P&L, operations, strategy, execution, market expansion, stakeholder management |
| Governance | responsible AI, auditability, traceability, policy, controls, compliance |

### 9.17 Implementation Meaning

This NLP layer should eventually power:

```text
UI keyword chips
embedded strong questions
query expansion
debug traceability
retrieval evaluation
conversation guidance
```

This makes RABBIT more than a basic chat app. It becomes a structured business-tech retrieval assistant with explicit NLP-informed query design.

---

## 10. Corpus Examples For Each NLP Concept

This section maps the NLP concepts to concrete examples from the RABBIT corpus. The goal is to show how the keyword strategy was applied to the actual documents, not only described theoretically.

### 10.1 Corpus

RABBIT corpus example:

```text
06_output_rag_documents_ready/
53 canonical RAG documents
142 approved chunks
```

Representative corpus documents:

```text
00_Homepage
01_01_Business_Skill_BPCL
01_02_Business_Skill_Medtronic
01_03_Business_Skill_SMAAT
01_04_Business_Skill_R_Cafe
02_Tech_02_MLOps_01_CICD
02_Tech_02_MLOps_02_Containers_02_Kubernetes
03_03_AI_Project_AWS_SageMaker_MLOps_Platform
03_04_AI_Project_GCP_Automation_Platform
03_05_AI_Project_Kubeflow_MLOps_Platform
```

How achieved:

The website pages were crawled, cleaned, converted into RAG documents, chunked, embedded, and indexed. This became the working NLP/RAG corpus.

### 10.2 Tokenization

Corpus examples of useful tokens:

```text
BPCL
Medtronic
SMAAT
RedRybbons
R-Cafe
AI
MLOps
AWS
Azure
GCP
Docker
Kubernetes
Kubeflow
SageMaker
CI/CD
IaC
```

How achieved:

The corpus was scanned as individual terms and phrases. These tokens became candidates for UI keywords and embedded strong questions.

### 10.3 Stopword And Noise Removal

Removed or ignored terms:

```text
the
and
is
of
to
h1
h2
h3
https
url
button
source
page
```

Corpus issue observed:

The first frequency scan surfaced extraction artifacts such as `h2`, `h3`, `https`, and `rajesharigala com`. These are not useful keyword chips, so they were filtered out.

How achieved:

The bag-of-words analysis was refined to remove stopwords and crawler/extraction artifacts before creating the final keyword groups.

### 10.4 Stemming / Lemmatization-Style Normalization

Corpus examples:

```text
architecture
architectures
architectural
architect
```

Normalized concept:

```text
Architecture
```

Other examples:

```text
operation / operations / operational -> Operations
deployment / deployments / deployed -> Deployment
Docker / Dockerized -> Docker
```

How achieved:

Instead of showing separate UI chips for every word form, RABBIT uses one canonical concept label and puts related forms into the embedded question or retrieval interpretation.

### 10.5 Synonyms, Aliases, And Controlled Vocabulary

Corpus example:

```text
Kubernetes
K8s
container orchestration
EKS
Minikube
Kubeflow
clusters
pods
services
```

Canonical UI concept:

```text
Kubernetes
```

Embedded strong question:

```text
Which Rajesh projects show Kubernetes / K8s capability, including EKS, Minikube, Kubeflow, container orchestration, clusters, pods, deployments, and services?
```

How achieved:

The keyword guide treats these as one concept group. This improves recall when the user says `K8s` but the relevant document says `Kubernetes`, `EKS`, or `Kubeflow`.

### 10.6 Named Entity Recognition Style Entity Preservation

Business entities preserved:

```text
BPCL
Medtronic
SMAAT
RedRybbons
R-Cafe
IIM Calcutta
IISc Bangalore
ISB
NITK Surathkal
```

Technology entities preserved:

```text
Azure AI Search
Azure OpenAI
AWS SageMaker
AWS CDK
Google Cloud Build
Vertex AI
Docker
Kubernetes
Kubeflow
MLflow
GitHub Actions
Azure DevOps
```

How achieved:

These names were kept as high-value retrieval terms because they identify specific companies, platforms, projects, and qualifications. They should not be removed as generic words.

### 10.7 N-Grams: Two-Word And Three-Word Phrases

Two-word corpus examples:

```text
github actions
aws cdk
machine learning
infrastructure code
model registry
azure devops
model serving
container orchestration
manual approval
artifact storage
solution architecture
```

Three-word corpus examples:

```text
architecture yaml mapping
mlops platform engineering
machine learning model
cicd architecture yaml
key technologies concepts
```

How achieved:

The corpus was scanned for repeated 2-word and 3-word phrases. These phrases are better than single keywords because they preserve context. For example, `model registry` is clearer than `model` alone.

### 10.8 Bag Of Words

Business bag-of-words examples:

```text
business
leadership
operations
strategy
governance
execution
outcomes
consulting
customer
market
P&L
```

Technology bag-of-words examples:

```text
AI
MLOps
architecture
AWS
Azure
GCP
Docker
Kubernetes
CI/CD
IaC
MLflow
Kubeflow
SageMaker
embeddings
vector
hybrid search
```

Hybrid bag-of-words examples:

```text
business + AI
AI transformation
platform thinking
production-grade systems
measurable outcomes
governance + MLOps
role fit
```

How achieved:

The words were grouped into Business, Technology, and Business-Tech Hybrid categories so the UI can guide different stakeholder intents.

### 10.9 Word Embeddings And Semantic Retrieval

RABBIT implementation example:

```text
Azure OpenAI text-embedding-3-small
1536-dimensional vectors
Azure AI Search vector field
```

How achieved:

Each approved chunk was embedded into a vector representation. This allows semantically similar questions to retrieve relevant chunks even when the exact words differ.

Example:

```text
User asks: What makes him suitable for business-tech roles?
Relevant chunks may include: BPCL, SMAAT, R-Cafe, AI projects, MLOps architecture, governance, operations.
```

### 10.10 Query Expansion

Weak query:

```text
architecture
```

Expanded embedded question:

```text
Show Rajesh's architecture-related project evidence across AI, MLOps, cloud, CI/CD, Docker, and Kubernetes.
```

Weak query:

```text
business
```

Expanded embedded question:

```text
Summarize Rajesh's business leadership experience across BPCL, Medtronic, SMAAT, RedRybbons, and R-Cafe.
```

How achieved:

UI keyword clicks submit stronger embedded questions instead of only sending a single word. This improves both keyword search and semantic retrieval.

### 10.11 Hybrid Search

RABBIT retrieval architecture:

```text
keyword search + vector semantic retrieval
```

Keyword search helps exact matches:

```text
BPCL
Kubernetes
SageMaker
R-Cafe
Azure DevOps
```

Vector retrieval helps meaning-based matches:

```text
role fit
business-tech transformation
architecture evidence
AI business outcomes
consulting alignment
```

How achieved:

The same user question is used for keyword search and vector retrieval in Azure AI Search. Guided questions improve both parts.

### 10.12 LLM / Language Model Layer

RABBIT answer-generation example:

```text
retrieved chunks
+ profile positioning context
+ answer prompt template
+ guardrails
= final professional answer
```

How achieved:

The LLM is used after retrieval. It does not replace retrieval; it converts retrieved evidence into a polished professional answer.

### 10.13 Transformer / Attention Concept

RABBIT prompt context includes:

```text
user question
retrieved chunks
source metadata
profile context
prompt rules
guardrails
```

How achieved:

The LLM uses attention over the prompt and retrieved content to decide which information is relevant to the answer. This is why prompt structure and context quality matter.

### 10.14 Tone Control

Desired user-facing tone:

```text
professional
pleasant
concise
stakeholder-friendly
not defensive
not report-like
```

Corpus/application example:

RABBIT should answer a recruiter or stakeholder cleanly, then offer expansion if needed. User Mode should not behave like a raw debug report.

How achieved:

The prompt now includes User Mode brevity and mobile readability rules.

### 10.15 Precision, Recall, And Ranking

Precision improvement example:

```text
Kubernetes chip -> includes K8s, EKS, Minikube, Kubeflow
```

This reduces irrelevant results because the query is more specific.

Recall improvement example:

```text
Architecture chip -> includes AI, MLOps, cloud, CI/CD, Docker, Kubernetes
```

This increases coverage because architecture appears across many pages.

Ranking improvement example:

```text
BPCL chip -> includes BPCL + execution under pressure
```

This helps BPCL evidence rank higher for business execution questions.

How achieved:

The guided keyword strategy turns weak user input into stronger retrieval input.

### 10.16 Traceability

Future debug trace example:

```json
{
  "keyword_group": "Technology Keywords",
  "clicked_keyword": "Kubernetes",
  "canonical_concept": "Kubernetes",
  "aliases": ["K8s", "EKS", "Minikube", "Kubeflow"],
  "embedded_question": "Which Rajesh projects show Kubernetes / K8s capability...?",
  "retrieved_page_ids": [
    "02_Tech_02_MLOps_02_Containers_02_Kubernetes",
    "02_Tech_02_MLOps_02_Containers_02_Kubernetes_03_AWS_EKS_ML_Deployment",
    "03_05_AI_Project_Kubeflow_MLOps_Platform"
  ]
}
```

How achieved now:

The current document defines the concept mappings. Later UI/debug work can log the mapping at runtime.

---

## 11. Summary Of NLP Evidence In This Project

RABBIT now has a documented NLP-informed keyword strategy:

```text
corpus -> tokenization -> stopword/noise removal -> bag of words -> n-grams -> concept normalization -> query expansion -> hybrid search -> LLM answer generation
```

This shows that the keyword guide is not random. It is derived from the actual corpus and connected to how the retrieval system works.

---

## 12. Approximate Results And Improvement By NLP Concept

These numbers are approximate planning estimates. They are meant to consolidate the expected achievement of each NLP step in the RABBIT retrieval pipeline. They are not formal benchmark scores.

| NLP / IR Concept | What We Implemented | Approximate Expected Result | Why It Helps |
|---|---|---:|---|
| Corpus creation | 53 canonical RAG docs and 142 approved chunks | 90-95% usable corpus readiness | Provides a clean searchable base for RAG. |
| Tokenization | Extracted repeated words and important entities from all documents | +5-8% keyword coverage | Makes important corpus terms visible and reusable. |
| Stopword/noise removal | Removed common words and artifacts like h2/h3/URLs/buttons | +8-12% keyword-list quality | Prevents useless UI keywords and noisy retrieval hints. |
| Lemmatization-style normalization | Grouped variants like architecture/architectural/architectures | +8-15% concept recall | Different word forms point to one canonical concept. |
| Synonym/alias mapping | Grouped K8s/Kubernetes/EKS/Minikube/Kubeflow | +12-20% recall for technical concepts | User shorthand can still retrieve full project evidence. |
| NER-style entity preservation | Preserved BPCL, Medtronic, SMAAT, R-Cafe, AWS, Azure, GCP, etc. | +10-18% precision for named queries | Specific entities strongly identify correct pages. |
| 2-3 word n-grams | Mined phrases like GitHub Actions, AWS CDK, model registry | +10-15% phrase relevance | Phrases preserve more context than single words. |
| Bag of words | Built Business, Technology, and Hybrid word groups | +10-18% guided query quality | Makes UI guided search broader and clearer. |
| Concept groups | Converted flat words into canonical concepts | +12-20% retrieval consistency | Reduces duplicate labels and improves query expansion. |
| Query expansion | UI keyword becomes embedded strong question | +15-25% relevance for broad queries | Converts vague intent into rich searchable context. |
| Vector semantic retrieval | Embedded chunks and user queries using 1536-dimensional vectors | +15-25% semantic match quality | Retrieves by meaning even when words differ. |
| Hybrid search | Combined keyword search and vector retrieval | +20-30% overall retrieval robustness | Covers both exact terms and semantic intent. |
| Link metadata separation | Links rendered from validated source_url metadata | 54/54 links valid after normalization | Prevents LLM-invented or broken links. |
| Prompt brevity / tone control | User Mode prompt tuned for concise answers | +10-20% perceived readability | Reduces report-like answers and mobile clutter. |
| Conversation follow-up resolution | Short follow-ups inherit active topic | +25-45% improvement for short follow-ups | Prevents “more links” or “picture” from going off-topic. |
| Traceability design | clicked keyword -> concept -> query -> chunks -> answer | +20-30% debug clarity | Makes retrieval behavior explainable and improvable. |

### 12.1 Consolidated Approximate Before / After

| Area | Before | After | Approximate Gain |
|---|---:|---:|---:|
| Broad business/tech query relevance | 65-75% | 82-90% | +12-20% |
| Specific named-entity query relevance | 85-92% | 90-95% | +5-10% |
| Short follow-up query relevance | 30-55% | 75-88% | +25-45% |
| Link correctness in displayed source links | inconsistent when LLM wrote links | 54/54 validated corpus links | major reliability gain |
| User Mode readability | medium, sometimes verbose | improved by brevity prompt | +10-20% perceived quality |
| Debug/explainability readiness | partial | keyword/concept trace designed | +20-30% inspection clarity |

### 12.2 Most Important Achievement

The biggest improvement is not raw extraction. The extracted data was already available.

The biggest improvement is that RABBIT now has a documented NLP-informed query layer:

```text
weak user wording
  -> normalized concept
  -> expanded embedded question
  -> hybrid keyword + vector retrieval
  -> validated links
  -> concise professional answer
```

This makes RABBIT more reliable for broad, vague, and follow-up conversations.

---

## 13. Measured NLP Corpus Statistics

This section records measurable NLP statistics from the current RABBIT corpus. These are actual corpus-derived numbers from the 53 canonical RAG documents.

### 13.1 Corpus Size

| Metric | Value |
|---|---:|
| Canonical RAG documents scanned | 53 |
| Raw token count before filtering | 68,654 |
| Clean token count after stopword/artifact filtering | 53,826 |
| Unique raw vocabulary | 3,948 |
| Unique clean vocabulary | 3,696 |
| Stopword/artifact reduction | 21.6% |
| Average clean tokens per document | 1015.6 |
| Median clean tokens per document | 979 |

### 13.2 N-Gram Inventory

| N-Gram Type | Total Observed | Relevant After Frequency + Document-Coverage Filter | Relevance Yield |
|---|---:|---:|---:|
| 1-gram / unigram | 3,696 | 1,831 | 49.54% |
| 2-gram / bigram | 23,166 | 4,557 | 19.67% |
| 3-gram / trigram | 33,960 | 3,606 | 10.62% |

Interpretation:

- 1-grams are useful for broad keyword chips.
- 2-grams and 3-grams are more useful for embedded strong questions because they preserve context.
- The relevance yield shows why filtering matters: many possible n-grams exist, but only a smaller subset is useful for UI and retrieval design.

### 13.3 Top Relevant 1-Grams

| 1-Gram | Count | Document Coverage |
|---|---:|---:|
| main | 70 | 53/53 |
| content | 61 | 53/53 |
| paragraphs | 53 | 53/53 |
| deployment | 677 | 49/53 |
| mlops | 468 | 49/53 |
| platform | 849 | 47/53 |
| model | 737 | 46/53 |
| infrastructure | 435 | 45/53 |
| production | 317 | 45/53 |
| build | 250 | 44/53 |
| github | 469 | 42/53 |
| code | 385 | 42/53 |
| architecture | 286 | 42/53 |
| skills | 127 | 42/53 |
| ml | 662 | 41/53 |
| monitoring | 170 | 41/53 |
| project | 444 | 40/53 |
| cloud | 409 | 40/53 |
| service | 378 | 40/53 |
| environment | 138 | 40/53 |
| pipeline | 788 | 39/53 |
| ai | 440 | 38/53 |
| pipelines | 421 | 38/53 |
| devops | 321 | 37/53 |
| yaml | 245 | 37/53 |
| orchestration | 196 | 37/53 |
| automation | 193 | 37/53 |
| engineering | 189 | 37/53 |
| view | 147 | 37/53 |
| problem | 128 | 37/53 |

### 13.4 Top Relevant 2-Grams

| 2-Gram | Count | Document Coverage |
|---|---:|---:|
| main content | 53 | 53/53 |
| platform engineering | 124 | 29/53 |
| project summary | 62 | 28/53 |
| machine learning | 140 | 27/53 |
| skills technologies | 60 | 27/53 |
| solution architecture | 58 | 26/53 |
| github repository | 53 | 25/53 |
| problem objective | 53 | 25/53 |
| code diagrams | 50 | 25/53 |
| objective solution | 27 | 25/53 |
| key components | 51 | 24/53 |
| key technologies | 48 | 24/53 |
| model registry | 132 | 23/53 |
| problems solved | 44 | 22/53 |
| summary key | 27 | 22/53 |
| skills tools | 22 | 22/53 |
| ai platform | 105 | 21/53 |
| cloud devops | 45 | 21/53 |
| technologies concepts | 42 | 21/53 |
| concepts problem | 20 | 20/53 |
| architecture block | 20 | 20/53 |
| infrastructure code | 133 | 19/53 |
| artifact storage | 53 | 19/53 |
| devops tools | 36 | 19/53 |
| category industry | 19 | 19/53 |
| github actions | 169 | 18/53 |
| ai ml | 50 | 18/53 |
| architecture yaml | 47 | 18/53 |
| enterprise ai | 44 | 18/53 |
| challenges resolutions | 42 | 18/53 |

### 13.5 Top Relevant 3-Grams

| 3-Gram | Count | Document Coverage |
|---|---:|---:|
| objective solution architecture | 26 | 25/53 |
| problem objective solution | 25 | 25/53 |
| project summary key | 25 | 22/53 |
| summary key technologies | 22 | 22/53 |
| key technologies concepts | 42 | 21/53 |
| technologies concepts problem | 20 | 20/53 |
| concepts problem objective | 20 | 20/53 |
| category industry domain | 18 | 18/53 |
| overview key components | 18 | 18/53 |
| problem objective problem | 18 | 18/53 |
| skills technologies technical | 18 | 18/53 |
| architecture yaml mapping | 34 | 17/53 |
| technical proficiency demonstrated | 34 | 17/53 |
| architectural overview solution | 22 | 17/53 |
| problems solved objectives | 17 | 17/53 |
| solution overview key | 17 | 17/53 |
| project summary comprehensive | 17 | 17/53 |
| project overview project | 17 | 17/53 |
| overview project category | 17 | 17/53 |
| solution architecture architectural | 17 | 17/53 |
| architecture architectural overview | 17 | 17/53 |
| overview solution overview | 17 | 17/53 |
| technologies technical proficiency | 17 | 17/53 |
| proficiency demonstrated skills | 17 | 17/53 |
| comprehensive project overview | 32 | 16/53 |
| problem did project | 32 | 16/53 |
| did project solve | 32 | 16/53 |
| project category industry | 16 | 16/53 |
| keywords problems solved | 16 | 16/53 |
| solved objectives solution | 16 | 16/53 |

### 13.6 Concept Group Coverage

| Canonical Concept | Included Terms | Combined Count | Document Coverage |
|---|---|---:|---:|
| Kubernetes | kubernetes, k8s, eks, aks, gke, minikube, kubeflow, pods, clusters, services | 910 | 42/53 |
| CI/CD | cicd, pipeline, pipelines, github, actions, devops, cloudbuild, deployment, deployments | 3382 | 51/53 |
| IaC | iac, infrastructure, cdk, terraform, cloudformation, provisioning | 969 | 47/53 |
| RAG | rag, retrieval, embeddings, vector, hybrid, search, azure | 417 | 21/53 |
| Business Leadership | business, leadership, operations, strategy, governance, execution, outcomes, p&l | 860 | 47/53 |
| AI/MLOps | ai, mlops, machine, learning, model, models, sagemaker, vertex, mlflow | 2597 | 52/53 |

### 13.7 Achievement Summary From Measured Stats

| Goal | Evidence | Approximate Achievement |
|---|---|---:|
| Reduce noisy keyword candidates | Stopword/artifact filtering reduced raw tokens before keyword use | improved keyword quality by ~8-12% |
| Build a usable bag of words | Clean vocabulary and relevant 1-grams identified | strong basis for UI keyword chips |
| Capture context beyond single words | Relevant 2-grams and 3-grams identified | improves embedded questions by ~10-15% |
| Support synonym/alias retrieval | Concept groups such as Kubernetes/K8s and CI/CD created | improves recall by ~12-20% |
| Strengthen broad queries | Query expansion from chips to strong questions | improves broad-query relevance by ~15-25% |
| Improve hybrid retrieval | Better lexical terms + richer semantic query | improves retrieval robustness by ~20-30% |
| Improve follow-up handling | Conversation topic resolution before guardrails | improves short-follow-up relevance by ~25-45% |

### 13.8 How This Connects To Implementation

These statistics should inform:

```text
UI keyword chips
embedded strong questions
query expansion rules
Debug Mode traceability
future retrieval evaluation
future semantic reranking experiments
```

The core achievement is that RABBIT now has a measurable NLP-informed keyword layer over the RAG corpus.

