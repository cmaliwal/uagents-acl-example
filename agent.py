import os
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model, Protocol
from uagents.models import ErrorMessage
from acl import ACL

AGENT_SEED = os.getenv("AGENT_SEED", "acl-test-agent")

class AdminActionRequest(Model):
    action: str  # "add" or "remove"
    member_addresses: list[str]  # List of member addresses to add or remove


class MemberActionRequest(Model):
    resource_id: str  # Identifier for the resource the member wants to access.
    data: dict = {}  # Optional data payload for analysis.


class Response(Model):
    text: str


PORT = 8000
agent = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit",
)

fund_agent_if_low(agent.wallet.address())

proto = Protocol(name="ACL-Example", version="0.1.0")

# Define the initial admin
INITIAL_ADMIN = os.getenv("INITIAL_ADMIN", "agent1qdudrm4nfq45sus52mjq3nva84jl74m02zz5s8a2vx5aj6ggp3wxqd56h33")

# Initialize ACL with the initial admin
acl = ACL(agent.storage, initial_admin=INITIAL_ADMIN)


@agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"Agent started with address: {ctx.agent.address}")


@proto.on_message(AdminActionRequest, replies={Response, ErrorMessage})
async def handle_admin_request(ctx: Context, sender: str, msg: AdminActionRequest):
    ctx.logger.info(f"Received admin request from {sender} with action '{msg.action}' for members {msg.member_addresses}")
    if msg.action == "add":
        added_members = []
        for member_address in msg.member_addresses:
            if acl.add_member(sender, member_address):
                added_members.append(member_address)
        
        if added_members:
            response_text = f"Members added to ACL: {', '.join(added_members)}"
            await ctx.send(sender, Response(text=response_text))
            ctx.logger.info(f"Sent response to {sender}: {response_text}")

        else:
            error_text = "Failed to add members. Admin access required."
            await ctx.send(sender, ErrorMessage(error=error_text))
            ctx.logger.error(f"Sent error to {sender}: {error_text}")
    
    elif msg.action == "remove":
        removed_members = []
        for member_address in msg.member_addresses:
            if acl.remove_member(sender, member_address):
                removed_members.append(member_address)
        
        if removed_members:
            response_text = f"Members removed from ACL: {', '.join(removed_members)}"
            await ctx.send(sender, Response(text=response_text))
            ctx.logger.info(f"Sent response to {sender}: {response_text}")
        else:
            error_text = "Failed to remove members. Admin access required."
            await ctx.send(sender, ErrorMessage(error=error_text))
            ctx.logger.error(f"Sent error to {sender}: {error_text}")
    
    else:
        error_text = "Invalid action. Use 'add' or 'remove'."
        await ctx.send(sender, ErrorMessage(error=error_text))
        ctx.logger.error(f"Sent error to {sender}: {error_text}")



@proto.on_message(MemberActionRequest, replies={Response, ErrorMessage})
@acl.wrap
async def handle_member_request(ctx: Context, sender: str, msg: MemberActionRequest):
    """
    Handles simple requests from members to access resources.
    """
    ctx.logger.info(f"Received member request from {sender} for resource '{msg.resource_id}'")
    if msg.resource_id == "analyze_data":
        # Example: Calculate the sum of a list of numbers provided in `data`.
        numbers = msg.data.get("numbers", [])
        if isinstance(numbers, list) and all(isinstance(num, (int, float)) for num in numbers):
            result = sum(numbers)
            response_text = f"Hello, {sender}. The sum of your provided numbers is: {result}."
        else:
            response_text = f"Hello, {sender}. Please provide a list of 'numbers' for analysis."
    else:
        response_text = f"Hello, {sender}. Resource '{msg.resource_id}' is not recognized."

    # Send the response back to the member
    await ctx.send(sender, Response(text=response_text))
    ctx.logger.info(f"Sent response to {sender}: {response_text}")


agent.include(proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
