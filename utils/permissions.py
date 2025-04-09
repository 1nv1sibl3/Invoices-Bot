import json
import os
from discord import Member, Role

PERMS_FILE = "./data/permissions.json"

def load_permissions():
    if not os.path.exists(PERMS_FILE) or os.stat(PERMS_FILE).st_size == 0:
        return {}
    with open(PERMS_FILE, "r") as f:
        return json.load(f)

def save_permissions(perms):
    with open(PERMS_FILE, "w") as f:
        json.dump(perms, f, indent=4)

def user_has_permission(cog_name, member: Member):
    perms = load_permissions().get(cog_name.lower(), {})
    allowed_roles = perms.get("roles", [])
    allowed_users = perms.get("users", [])
    return member.id in allowed_users or any(role.id in allowed_roles for role in member.roles)

def add_perms(cog: str, roles: list[Role], users: list[Member]):
    cog = cog.lower()
    perms = load_permissions()
    if cog not in perms:
        perms[cog] = {"roles": [], "users": []}

    for role in roles:
        if role.id not in perms[cog]["roles"]:
            perms[cog]["roles"].append(role.id)
    for user in users:
        if user.id not in perms[cog]["users"]:
            perms[cog]["users"].append(user.id)

    save_permissions(perms)

def remove_perms(cog: str, roles: list[Role], users: list[Member]):
    cog = cog.lower()
    perms = load_permissions()
    if cog not in perms:
        return

    for role in roles:
        if role.id in perms[cog]["roles"]:
            perms[cog]["roles"].remove(role.id)
    for user in users:
        if user.id in perms[cog]["users"]:
            perms[cog]["users"].remove(user.id)

    save_permissions(perms)

def get_perms(cog: str):
    cog = cog.lower()
    return load_permissions().get(cog, {"roles": [], "users": []})
