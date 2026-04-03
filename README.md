# 🤖 Smart Assistant

## 🚀 Overview

Smart Assistant is an AI-powered task and event management system built on Google's Agent Development Kit (ADK). It processes natural language requests to intelligently create tasks, schedule events, and save notes while automatically detecting scheduling conflicts and adapting timelines based on urgency levels.

## 🎯 Problem Statement

Users struggle to manage multiple tasks, events, and notes efficiently through a unified interface. Manual scheduling often leads to time conflicts, and determining appropriate time slots for tasks of varying urgency requires constant attention. Existing solutions lack intelligent conflict detection and adaptive planning based on task priority.

## 💡 Solution

Smart Assistant uses a multi-agent architecture powered by Google's ADK to:
- **Parse natural language** to extract tasks, events, and metadata
- **Detect scheduling conflicts** before committing items to the database
- **Assign intelligent timeslots** based on task urgency
- **Orchestrate actions** through specialized agent roles: planner → executor → responder

The system processes requests through a workflow: a planner agent decodes intent, a sequential executor handles database operations, and a responder communicates outcomes including conflict resolution options.

## 🏗️ Architecture
FastAPI (Request) 
    ↓
Root Agent (ADK Router)
    ↓
Planner Agent (Decision) + Responder Agent (Communication)
    ↓
Vertex AI (NLP) 
    ↓
Utils (Parse, Check Conflict, Assign Time)
    ↓
Tools (Task/Calendar/Notes)
    ↓
Firestore (Persist)

## Tools Available:
• smart_execution() → Coordinates task flow with conflict detection
• daily_plan() → Returns current tasks & events
• task_tool() → Adds task with auto-assigned or parsed time
• calendar_tool() → Schedules events with conflict check
• notes_tool() → Saves notes to database

## Database: Google Firestore
├─ Collection: users
└─ Document fields: tasks, events, notes


## ⚙️ Tech Stack

**Backend:**
- Google Agent Development Kit (ADK) v1.14.0
- FastAPI – REST API framework
- Uvicorn – ASGI server
- Pydantic – Request validation

**AI/ML:**
- Google Generative AI (via `google-genai`)
- Google Vertex AI – Model orchestration
- Multi-agent workflow with sequential execution

**Database & Cloud:**
- Google Firestore – Document storage
- Google Cloud Logging – Observability
- Google Cloud Auth – Authentication

**Containerization:**
- Docker (Python 3.11 base)

## ✨ Features

- ✅ **Natural Language Processing** – Extracts tasks, events, and deadlines from user input
- ✅ **Intelligent Time Assignment** – Auto-assigns timeslots based on urgency (high → 6 PM, medium → 8 PM, low → 10 PM)
- ✅ **Scheduling Conflict Detection** – Prevents double-booking by checking existing times before confirming
- ✅ **Multi-Type Support** – Handles tasks, calendar events, and notes
- ✅ **Time Parsing** – Recognizes explicit times (e.g., "2 PM"), keywords ("morning" → 9 AM, "evening" → 7 PM)
- ✅ **Urgency Detection** – Identifies high-priority items via keywords ("urgent", "asap", "tomorrow")
- ✅ **Daily Schedule Retrieval** – Fetches current tasks and events
- ✅ **Multi-Agent Workflow** – Separates planning, execution, and response logic for reliability
- ✅ **Cloud-Native** – Integrated with Google Cloud services and Docker-ready

## 📂 Project Structure

smart_assistant/
├── agent.py              # Multi-agent workflow (planner, responder, root agent)
├── app.py                # FastAPI server with /chat endpoint
├── main.py               # Vertex AI initialization
├── db.py                 # Firestore database operations
├── utils.py              # Time parsing, urgency detection, planning
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container build config
├── .gitignore            # Git ignore rules
└── __init__.py           # Package marker


## 🧠 AI/ML Integration

**Model Used:** Google's Generative AI (configurable via `MODEL` environment variable)

**Where It's Used:**
1. **Planner Agent** – Receives user request, decides which tools to invoke
2. **Responder Agent** – Generates human-readable responses with conflict explanations

**What It Does:**
- Interprets free-form user requests within strict guardrails
- Enforces function-calling discipline (planner must call tools, responder must not invent data)
- Generates contextual responses referencing existing schedule when conflicts occur

**Execution Flow:**
- Planner calls `smart_execution()` which orchestrates task/event/note creation
- `smart_execution()` internally runs utilities to parse time, detect urgency, and generate steps
- Responder formats the final message to the user

## ⚠️ Limitations
-Time Parsing: Only recognizes explicit times (e.g., "2 PM") or keywords ("morning", "evening"). Relative times like "in 2 hours" not supported.
-Conflict Resolution: Detects conflicts but doesn't auto-reschedule; user must manually choose new time.
-Single User: Architecture assumes one user per deployment (USER_ID="default_user"). Multi-user support requires modification.
-Fixed Time Slots: High/medium/low urgency map to fixed times (6 PM, 8 PM, 10 PM) with no customization.
-Task Types: Only recognizes "study", "meeting", and "note" patterns. Other task types default to generic handling.
-Database Latency: Firestore operations are blocking; high request volumes may experience delays.
-No Persistence of Conflicts: Conflict information is only communicated to user, not logged for analytics.

## 🔮 Future Improvements
-Multi-User Support: Extract user ID from request headers or authentication token
-Advanced Time Parsing: Integrate chrono.rs or similar for relative time interpretation ("in 2 hours", "next Monday")
-Conflict Auto-Resolution: Suggest alternative times and allow one-click rescheduling
-Customizable Urgency Mapping: Allow users to define their own time assignments for urgency levels
-Calendar Integration: Sync with Google Calendar API for read-write access
-Natural Language Rescheduling: "Move my 3 PM meeting to 4 PM" without manual conflict checking
-Batch Operations: Handle multiple tasks in one request
-Analytics & Insights: Track task completion, identify scheduling patterns
-Recurring Tasks: Support "every Monday" or "daily" patterns
Notifications: Webhook or webhook support for reminders

