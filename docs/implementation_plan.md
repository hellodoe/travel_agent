# Implementation Plan: OpenAI Agents Travel Assistant

This plan outlines the steps to build a functional multi-agent Travel Assistant CLI application using the OpenAI Agents SDK and Pydantic validation schemas.

## User Review Required

> [!IMPORTANT]
> - An `OPENAI_API_KEY` is required to run this application. You will need to add it to a local `.env` file.
> - The model used by default is `gpt-4o`. If you wish to use a different model (e.g., `gpt-4o-mini`), please let us know.

## Proposed Changes

We will create a new Python project structure under `c:\Projects\travel_agent`:

- [NEW] [requirements.txt](file:///c:/Projects/travel_agent/requirements.txt): List of dependencies (`openai-agents`, `pydantic`, `python-dotenv`).
- [NEW] [.env](file:///c:/Projects/travel_agent/.env): Local environment file for credentials (git-ignored/template).
- [NEW] [main.py](file:///c:/Projects/travel_agent/main.py): Main CLI runner and multi-agent implementation logic.

---

### Project Files

#### [NEW] [requirements.txt](file:///c:/Projects/travel_agent/requirements.txt)
Specifies the exact library versions needed to run the agents and process user requests.

```text
openai-agents>=0.1.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

#### [NEW] [.env](file:///c:/Projects/travel_agent/.env)
Stores the API credentials.

```env
OPENAI_API_KEY=your-openai-api-key-here
```

#### [NEW] [main.py](file:///c:/Projects/travel_agent/main.py)
Implements:
1. Pydantic request models (`FlightBookingRequest`, `HotelBookingRequest`).
2. Mock flight and hotel databases.
3. Search and booking tools.
4. Definition of `Triage Agent`, `Flight Specialist`, `Hotel Specialist`, and `Itinerary Specialist`.
5. An interactive CLI loop allowing you to speak directly with the agents and see handoffs live.

---

## Verification Plan

### Automated/Manual CLI Run
1. Initialize the virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```
2. Configure `.env` with a valid `OPENAI_API_KEY`.
3. Run the interactive CLI:
   ```powershell
   .venv\Scripts\python main.py
   ```
4. Run standard test flows:
   - **Flow 1 (Flights & Hotels)**: Ask "Can you find a flight from NYC to Paris on July 10th?" -> Confirm flight `AA-101` -> Ask to book standard hotel room -> Verify the handoffs happen automatically in the console.
   - **Flow 2 (Itinerary)**: Ask "What can I do in Paris?" -> Verify `Itinerary Specialist` is selected and recommends historical and museum tours.
