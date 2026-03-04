# AI Project Portfolio

A collection of practical AI applications focused on productivity and project management, built with Python and Claude.

## Projects

| Project | Description | Tech | Status |
|---------|-------------|------|--------|
| [Project Planner Agent](./agents/project_planner/) | Give it a goal, get a full phased plan with tasks and timelines | Claude, Streamlit | ✅ Live |
| [Meeting Summarizer](./agents/meeting_summarizer/) | Paste a transcript, get summary + action items | Claude | 🚧 Coming Soon |
| [Document Q&A (RAG)](./rag_apps/document_qa/) | Chat with your project docs using retrieval | Claude, ChromaDB | 🚧 Coming Soon |
| [Email Drafter](./automations/email_drafter/) | Turn bullet points into polished emails | Claude | 🚧 Coming Soon |

## Tech Stack

- **LLM:** Anthropic Claude (primary), Google Gemini
- **UI:** Streamlit
- **Language:** Python 3.11+
- **Other:** LangChain, ChromaDB, python-dotenv

## Getting Started

1. Clone the repo
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-project-portfolio.git
   cd ai-project-portfolio
   ```

2. Copy the env file and add your API keys
   ```bash
   cp .env.example .env
   ```

3. Navigate to any project folder and follow its `README.md`

## Structure

```
ai-project-portfolio/
├── agents/
│   ├── project_planner/       # AI-powered project breakdown agent
│   └── meeting_summarizer/    # Meeting transcript → action items
├── rag_apps/
│   └── document_qa/           # Chat with your documents
├── automations/
│   └── email_drafter/         # Bullet points → professional emails
└── notebooks/                 # Experiments and prototypes
```
