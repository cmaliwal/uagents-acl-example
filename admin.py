import os
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model

AGENT_SEED = os.getenv("AGENT_SEED", "admin-seed")

class AdminActionRequest(Model):
    action: str  # "add" or "remove"
    member_addresses: list[str]  # List of member addresses to add or remove.


class Response(Model):
    text: str


class ErrorMessage(Model):
    error: str

PORT = 8001
admin = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit",
)

fund_agent_if_low(admin.wallet.address())

# Address of the core agent where the admin sends commands
CORE_AGENT_ADDRESS = os.getenv("CORE_AGENT_ADDRESS", "agent1qwkxyanl4e96yr6f2g5m60vssksuyw0x8y5j5arfem3qswk834tgzt46ze5")


@admin.on_event("startup")
async def send_add_members_request(ctx: Context):
    ctx.logger.info(f"Agent started with address: {ctx.agent.address}")
    # Replace with a list of member addresses to add.
    msg = AdminActionRequest(
        action="add",
        member_addresses=["agent1qvvg5lpqgg8hd2x08tspfm56hl5mt23k5zcfatwyh9gmhcc2w94lxz278tq"]
    )
    await ctx.send(CORE_AGENT_ADDRESS, msg)
    ctx.logger.info(f"Sent add members request to {CORE_AGENT_ADDRESS}")


# @admin.on_event("startup")
# async def send_remove_members_request(ctx: Context):
    # Uncomment the following to send a remove request instead.
    # Replace with a list of member addresses to remove.
    # msg = AdminActionRequest(
    #     action="remove",
    #     member_addresses=["member1-address", "member2-address"]
    # )
    # await ctx.send(CORE_AGENT_ADDRESS, msg)
    # ctx.logger.info(f"Sent remove members request to {CORE_AGENT_ADDRESS}")


@admin.on_message(Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    """
    Handles responses from the core agent.
    """
    ctx.logger.info(f"Received response from {sender}: {msg.text}")


@admin.on_message(ErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: ErrorMessage):
    """
    Handles error messages from the core agent.
    """
    ctx.logger.error(f"Received error from {sender}: {msg.error}")


if __name__ == "__main__":
    admin.run()
