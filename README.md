
# ACL Agent System

## Overview

This repository contains a simple agent-based access control system using the `uagents` library. It includes a core agent (`agent.py`) that manages an Access Control List (ACL) and allows an admin agent (`admin.py`) to add or remove members. A member agent (`member.py`) can then access restricted resources if they are added to the ACL by the admin.

## Components

### 1. `agent.py`
- **Port:** `8000`
- **Description:** The core agent that manages the ACL. It listens for messages to:
  - Add or remove members (`add`, `remove`).
  - Handle access requests from members.
- **Initial Admin:** The admin address must be set to control access (`INITIAL_ADMIN`).
- **Message Types:**
  - `AdminActionRequest` with actions like `add` or `remove` and a list of `member_addresses`.
  - `MemberActionRequest` for members requesting access to specific resources with `resource_id` and optional `data`.

### 2. `admin.py`
- **Port:** `8001`
- **Description:** Simulates an admin that can send requests to `agent.py` to add or remove members.
- **Usage:** Automatically sends a message to add members when it starts. Uncomment lines to remove members instead.
- **Message Type:** `AdminActionRequest` specifying `add` or `remove` actions and the target member addresses.
- **Response Handling:** Processes responses or errors from `agent.py` to log results.

### 3. `member.py`
- **Port:** `8002`
- **Description:** Simulates a member attempting to access a restricted resource managed by `agent.py`.
- **Usage:** Sends an `access` request with `resource_id` and optional `data` on startup.
- **Message Type:** `MemberActionRequest` specifying the `resource_id` and optional `data` for analysis.
- **Response Handling:** Logs responses or errors from `agent.py`.

## How to Run

1. **Start the Core Agent**:
   ```bash
   python agent.py
   ```

2. **Run the Admin Agent** to add members:
   ```bash
   python admin.py
   ```
   - This sends a request to add `member1-address` and `member2-address` to the ACL.
   - To remove members, uncomment the `send_remove_members_request` function in the `admin.py` script.

3. **Run the Member Agent** to access a resource:
   ```bash
   python member.py
   ```
   - This sends an access request to `agent.py` to analyze a set of data (e.g., a list of numbers).

## Expected Output

- **Admin Agent**:
   - Logs messages when sending requests to add or remove members.
   - Logs responses or error messages received from the core agent.

- **Core Agent**: 
   - Logs received requests and actions performed (e.g., adding/removing members, processing member access requests).
   - Logs responses sent back to admin and member agents.

- **Member Agent**:
   - Logs when sending an access request to the core agent.
   - Logs the response received (e.g., the result of data analysis) or any error messages.

## Example Usage

- **Adding Members**:
   ```bash
   python admin.py
   ```
   - Adds `member1-address` and `member2-address` to the ACL.
   - To remove these members, uncomment the relevant lines in `admin.py` and re-run the script.

- **Accessing Resources**:
   ```bash
   python member.py
   ```
   - The member requests analysis of a dataset with `resource_id="analyze_data"` and a list of numbers.
   - Example output:  
     `"Hello, member-address. The sum of your provided numbers is: 60."`

## Logging

- **Core Agent**:
   - Logs the processing of admin and member requests.
   - Logs successful responses and error messages sent to agents.

- **Admin Agent**:
   - Logs the actions performed (e.g., adding/removing members).
   - Logs the outcome of each request based on responses received from the core agent.

- **Member Agent**:
   - Logs the access request details and the responses received from the core agent.

## Dependencies

- `uagents`
- `pydantic`
- Python 3.12 or higher

Ensure you have the necessary environment variables set for `AGENT_SEED` and `AGENT_ADDRESS` where applicable.
