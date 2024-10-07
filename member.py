import os
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model

AGENT_SEED = os.getenv("AGENT_SEED", "member-seed")

class MemberActionRequest(Model):
    resource_id: str  # Identifier for the resource the member wants to access.
    data: dict = {}  # Optional data payload for analysis.


class Response(Model):
    text: str


class ErrorMessage(Model):
    error: str

PORT = 8002
member = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit",
)

fund_agent_if_low(member.wallet.address())

# Address of the core agent where the member sends access requests
CORE_AGENT_ADDRESS = os.getenv("CORE_AGENT_ADDRESS", "agent1qwkxyanl4e96yr6f2g5m60vssksuyw0x8y5j5arfem3qswk834tgzt46ze5")

@member.on_event("startup")
async def send_access_request(ctx: Context):
    ctx.logger.info(f"Agent started with address: {ctx.agent.address}")
    # Replace "analyze_data" with the ID of the resource the member wants to access.
    # Here we include a list of numbers for analysis.
    msg = MemberActionRequest(
        resource_id="analyze_data",
        data={"numbers": [10, 20, 30]}
    )
    await ctx.send(CORE_AGENT_ADDRESS, msg)
    ctx.logger.info(f"Sent access request to {CORE_AGENT_ADDRESS}")


@member.on_message(Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    """
    Handles responses from the core agent.
    """
    ctx.logger.info(f"Received response from {sender}: {msg.text}")


@member.on_message(ErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: ErrorMessage):
    """
    Handles error messages from the core agent.
    """
    ctx.logger.error(f"Received error from {sender}: {msg.error}")


if __name__ == "__main__":
    member.run()
