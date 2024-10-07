import os
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model
from uagents.models import ErrorMessage

AGENT_SEED = os.getenv("AGENT_SEED", "non-member-seed")

class MemberActionRequest(Model):
    resource_id: str  # Identifier for the resource the member wants to access.
    data: dict = {}  # Optional data payload for analysis.


class Response(Model):
    text: str


class ErrorMessage(Model):
    error: str


PORT = 8004
non_member = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit",
)

fund_agent_if_low(non_member.wallet.address())

# Address of the core agent where the non-member sends access requests
CORE_AGENT_ADDRESS = os.getenv("CORE_AGENT_ADDRESS", "agent1qwkxyanl4e96yr6f2g5m60vssksuyw0x8y5j5arfem3qswk834tgzt46ze5")


@non_member.on_event("startup")
async def attempt_access_request(ctx: Context):
    # This non-member attempts to access a resource, which should be rejected by the core agent.
    msg = MemberActionRequest(
        resource_id="analyze_data",
        data={"numbers": [5, 15, 25]}
    )
    await ctx.send(CORE_AGENT_ADDRESS, msg)
    ctx.logger.info(f"Non-member sent access request to {CORE_AGENT_ADDRESS}")


@non_member.on_message(Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    """
    Handles successful responses from the core agent.
    """
    ctx.logger.info(f"Non-member received response from {sender}: {msg.text}")


@non_member.on_message(ErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: ErrorMessage):
    """
    Handles error messages from the core agent.
    """
    ctx.logger.error(f"Non-member received error from {sender}: {msg.error}")


if __name__ == "__main__":
    non_member.run()
