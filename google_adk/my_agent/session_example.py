#!/usr/bin/env python
# coding=utf-8
import asyncio

from google.adk.sessions import InMemorySessionService, Session
from google.adk.sessions.database_session_service import DatabaseSessionService


async def run_one_session():
    # Create a simple session to examine its properties
    # temp_service = InMemorySessionService()
    db_url = "mysql+aiomysql://root:1234@localhost:3306/adk_sessions"
    print(f"--- Initializing DatabaseSessionService ---")
    temp_service = DatabaseSessionService(db_url=db_url)
    example_session = await temp_service.create_session(
        app_name="my_app",
        user_id="example_user",
        state={"initial_key": "initial_value"} # State can be initialized
    )

    print(f"--- Examining Session Properties ---")
    print(f"ID (`id`):                {example_session.id}")
    print(f"Application Name (`app_name`): {example_session.app_name}")
    print(f"User ID (`user_id`):         {example_session.user_id}")
    print(f"State (`state`):           {example_session.state}") # Note: Only shows initial state here
    print(f"Events (`events`):         {example_session.events}") # Initially empty
    print(f"Last Update (`last_update_time`): {example_session.last_update_time:.2f}")
    print(f"---------------------------------")

    # Clean up (optional for this example)
    input("Press Enter to continue...")
    await temp_service.delete_session(app_name=example_session.app_name,
                                      user_id=example_session.user_id, session_id=example_session.id)
    print("Session deleted")

    await temp_service.close()


if __name__ == "__main__":
    asyncio.run(run_one_session())