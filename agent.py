import os
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext

from .utils import detect_urgency, smart_time_parser, generate_plan
from .db import save, load
from .utils import assign_time_based_on_urgency

load_dotenv()
model_name = os.getenv("MODEL")

USER_ID = "default_user"

# ================= HELPERS =================

def get_all_times():
    tasks = load(USER_ID, "tasks")
    events = load(USER_ID, "events")

    times = []

    for item in tasks + events:
        if " at " in item:
            times.append(item.split(" at ")[-1])

    return times


def check_conflict(new_time):
    taken = get_all_times()
    return new_time in taken


# ================= TOOLS =================

def task_tool(tool_context: ToolContext, task: str):
    tasks = load(USER_ID, "tasks")

    time = smart_time_parser(task)
    if time == "not specified":
        time = assign_time_based_on_urgency(detect_urgency(task))

    # 🔥 Conflict detection
    if check_conflict(time):
        return {
            "conflict": True,
            "type": "task",
            "task": task,
            "time": time
        }

    task_with_time = f"{task} at {time}"

    tasks.append(task_with_time)
    save(USER_ID, "tasks", tasks)

    return {"task": task_with_time}


def calendar_tool(tool_context: ToolContext, event: str):
    events = load(USER_ID, "events")

    if " at " in event:
        time = event.split(" at ")[-1]
    else:
        time = "10 PM"

    # 🔥 Conflict detection
    if check_conflict(time):
        return {
            "conflict": True,
            "type": "event",
            "event": event,
            "time": time
        }

    events.append(event)
    save(USER_ID, "events", events)

    return {"event": event}


def notes_tool(tool_context: ToolContext, note: str):
    notes = load(USER_ID, "notes")
    notes.append(note)
    save(USER_ID, "notes", notes)
    return {"note": note}


def daily_plan(tool_context: ToolContext):
    return {
        "tasks": load(USER_ID, "tasks"),
        "events": load(USER_ID, "events")
    }


# ================= BRAIN =================

def smart_execution(tool_context: ToolContext, prompt: str):
    time = smart_time_parser(prompt)
    urgency = detect_urgency(prompt)

    if time == "not specified":
        time = assign_time_based_on_urgency(urgency)

    plan = generate_plan(prompt)

    result = {
        "time": time,
        "urgency": urgency,
        "steps": plan,
        "actions": [],
        "conflict": None
    }

    for step in plan:
        res = None  # ✅ ALWAYS initialize

        if step == "create_task":
            res = task_tool(tool_context, prompt)

        elif step == "schedule_study":
            res = calendar_tool(tool_context, f"Study at {time}")

        elif step == "schedule_meeting":
            res = calendar_tool(tool_context, f"Meeting at {time}")

        elif step == "save_note":
            res = notes_tool(tool_context, prompt)

        # 🔥 skip unknown steps safely
        if res is None:
            continue

        # 🔥 conflict check
        if isinstance(res, dict) and res.get("conflict"):
            result["conflict"] = res
            return result

        result["actions"].append(res)
        return result




# ================= AGENTS =================

planner = Agent(
    name="planner",
    model=model_name,
    instruction="""
You are an intelligent planner.

When the user gives any request:
- ALWAYS call the function smart_execution
- Pass the full user input as the "prompt" argument
- Do NOT answer yourself

If a conflict is returned:
- Pass it to responder clearly

Only call the function.
""",
    tools=[smart_execution, daily_plan],
    output_key="result"
)


responder = Agent(
    name="responder",
    model=model_name,
    instruction="""
You are a smart assistant.

If result contains a conflict:
- Tell the user clearly:
    "You already have something scheduled at [time]"
- Mention what they tried to add
- Ask what they want to do:
    1. Reschedule new item
    2. Replace existing item
    3. Choose another time

If no conflict:
- Confirm the action clearly
- Mention time and details

Be natural and helpful.
"""
)


workflow = SequentialAgent(
    name="workflow",
    sub_agents=[planner, responder]
)


root_agent = Agent(
    name="assistant",
    model=model_name,
    instruction="""
You are a smart assistant.

For ANY user request:
- Immediately pass control to sub-agents
- Do NOT answer by yourself
- Do NOT ask for confirmation
""",
    sub_agents=[workflow]
)