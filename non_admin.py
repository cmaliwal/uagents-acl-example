import os
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model
from uagents.models import ErrorMessage

AGENT_SEED = os.getenv("AGENT_SEED", "non-admin-seed")

class AdminActionRequest(Model):
    action: str  # "add" or "remove"
    member_addresses: list[str]  # List of member addresses to add or remove.


class Response(Model):
    text: str


class ErrorMessage(Model):
    error: str


PORT = 8003
non_admin = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit",
)

fund_agent_if_low(non_admin.wallet.address())

# Address of the core agent where the non-admin sends commands
CORE_AGENT_ADDRESS = os.getenv("CORE_AGENT_ADDRESS", "agent1qwkxyanl4e96yr6f2g5m60vssksuyw0x8y5j5arfem3qswk834tgzt46ze5")


@non_admin.on_event("startup")
async def attempt_admin_action(ctx: Context):
    # This non-admin attempts to add members, which should be rejected by the core agent.
    msg = AdminActionRequest(
        action="add",
        member_addresses=["non-member1-address", "non-member2-address"]
    )
    await ctx.send(CORE_AGENT_ADDRESS, msg)
    ctx.logger.info(f"Non-admin sent add members request to {CORE_AGENT_ADDRESS}")


@non_admin.on_message(Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    """
    Handles successful responses from the core agent.
    """
    ctx.logger.info(f"Non-admin received response from {sender}: {msg.text}")


@non_admin.on_message(ErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: ErrorMessage):
    """
    Handles error messages from the core agent.
    """
    ctx.logger.error(f"Non-admin received error from {sender}: {msg.error}")


if __name__ == "__main__":
    non_admin.run()
