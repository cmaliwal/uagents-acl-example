from typing import Any, Set
from uagents import Context
from uagents.storage import StorageAPI
from uagents.models import ErrorMessage


class ACL:
    """
    Basic Access Control List (ACL) for managing access permissions.
    """

    def __init__(self, storage: StorageAPI, initial_admin: str):
        """
        Initialize the ACL.

        Args:
            storage: The storage API for persisting ACL data.
            initial_admin: The address of the initial admin.
        """
        self.storage = storage
        self.admin_key = "acl_admin"
        self.members_key = "acl_members"

        # Set the initial admin if not already set
        if not self.storage.has(self.admin_key):
            self.storage.set(self.admin_key, initial_admin)

        # Initialize members list if not already set
        if not self.storage.has(self.members_key):
            # Store members as a list for JSON compatibility
            self.storage.set(self.members_key, [initial_admin])

    def is_admin(self, address: str) -> bool:
        """Check if the given address is the admin."""
        return self.storage.get(self.admin_key) == address

    def is_member(self, address: str) -> bool:
        """Check if the given address is a member of the ACL."""
        members = set(self.storage.get(self.members_key))
        return address in members

    def add_member(self, admin_address: str, member_address: str) -> bool:
        """Add a member to the ACL. Only the admin can add members."""
        if self.is_admin(admin_address):
            members = set(self.storage.get(self.members_key))
            members.add(member_address)
            self.storage.set(self.members_key, list(members))
            return True
        return False

    def remove_member(self, admin_address: str, member_address: str) -> bool:
        """Remove a member from the ACL. Only the admin can remove members."""
        if self.is_admin(admin_address):
            members = set(self.storage.get(self.members_key))
            if member_address in members:
                members.remove(member_address)
                self.storage.set(self.members_key, list(members))
                return True
        return False

    def transfer_ownership(self, current_admin: str, new_admin: str) -> bool:
        """Transfer admin ownership to another address."""
        if self.is_admin(current_admin):
            self.storage.set(self.admin_key, new_admin)
            self.add_member(new_admin, new_admin)
            return True
        return False

    def wrap(self, func):
        """Decorator to restrict access to a function to ACL members only."""
        async def decorator(ctx: Context, sender: str, msg: Any):
            if self.is_member(sender):
                await func(ctx, sender, msg)
            else:
                await ctx.send(
                    sender, ErrorMessage(error="Access denied. You are not a member.")
                )
            return

        return decorator
