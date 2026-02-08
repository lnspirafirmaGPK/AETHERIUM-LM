# AETHERIUM LM - Production-Grade LLM System

A robust, asynchronous LLM management system featuring a mobile-first configuration console. Built to provide a unified interface for interacting with multiple AI providers (OpenAI, Anthropic, Google, etc.) with production-grade reliability.

## 🚀 Key Features

*   **Multi-Provider Support**: Seamlessly switch between OpenAI, Anthropic, Google Gemini, Groq, Ollama, and 20+ other providers via [LiteLLM](https://docs.litellm.ai/).
*   **Mobile-First Console**: A responsive configuration UI built with [Flet](https://flet.dev/), designed for easy on-the-go management.
*   **Async Architecture**: Fully asynchronous database operations (SQLAlchemy + aiosqlite) and non-blocking API calls for high performance.
*   **Robust Configuration**: Centralized validation logic ensures API keys and model parameters are correct before use.
*   **Extensible Design**: Service-Oriented Architecture (SOA) separates UI concerns from business logic, making it easy to add new features.

## 🛠️ Tech Stack

*   **UI Framework**: Flet (Flutter for Python)
*   **LLM Abstraction**: LiteLLM
*   **Database**: SQLAlchemy (AsyncIO) with SQLite
*   **Configuration**: Pydantic Settings

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/aetherium-lm.git
    cd aetherium-lm
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Usage

Run the mobile configuration console:

```bash
python main.py
```

The app will launch in a new window (or your browser), allowing you to:
1.  Select an AI Provider.
2.  Enter your Model Name (e.g., `gpt-4o`, `claude-3-opus`).
3.  Input your API Key.
4.  Click **"Validate & Save Config"** to test the connection in real-time.

## 📂 Documentation & Architecture

For a deep dive into the system's design, please refer to the generated architecture reports in the `docs/` folder:

*   **[Project Structure Report](docs/architecture_reports/project_structure_report.txt)**: A detailed breakdown of every file in the codebase and its purpose.
*   **[Data Flow Simulation](docs/architecture_reports/data_flow_simulation.md)**: Visual diagrams (Mermaid) illustrating how data moves from the UI to the backend and external APIs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request
