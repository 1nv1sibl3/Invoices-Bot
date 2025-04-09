import discord
import shlex
from datetime import datetime

def apply_format(member: discord.Member, fmt: str, dateformat: str) -> str:
    fmt = fmt.replace("%n", member.display_name)
    fmt = fmt.replace("%i", str(member.id))
    fmt = fmt.replace("%u", str(member))
    fmt = fmt.replace("%c", member.created_at.strftime(dateformat))
    fmt = fmt.replace("%j", member.joined_at.strftime(dateformat) if member.joined_at else "N/A")
    return fmt

def get_filtered_members(members, *, has_roles=[], no_roles=False):
    filtered = []
    for m in members:
        if no_roles and len(m.roles) <= 1:
            filtered.append(m)
        elif has_roles and any(r in m.roles for r in has_roles):
            filtered.append(m)
        elif not has_roles and not no_roles:
            filtered.append(m)
    return filtered

def sort_members(members, key="name", desc=False):
    try:
        return sorted(members, key=lambda m: getattr(m, key) or "", reverse=desc)
    except Exception:
        return members

def parse_dump_flags(guild: discord.Guild, args: str):
    try:
        tokens = shlex.split(args)
    except Exception:
        return None

    config = {
        "has_roles": [],
        "no_roles": False,
        "order": "name",
        "desc": False,
        "limit": 0,
        "format": "%n (%i)",
        "dateformat": "%Y-%m-%d",
        "enumerate": False,
        "separator": "\n"
    }

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token in ("-r", "--has-roles"):
            i += 1
            while i < len(tokens) and not tokens[i].startswith("-"):
                role = discord.utils.get(guild.roles, mention=tokens[i]) or discord.utils.get(guild.roles, name=tokens[i])
                if role:
                    config["has_roles"].append(role)
                i += 1
            continue

        if token in ("--order", "-o"):
            i += 1
            if i < len(tokens):
                config["order"] = tokens[i]

        elif token in ("--limit", "-l"):
            i += 1
            if i < len(tokens):
                try:
                    config["limit"] = int(tokens[i])
                except ValueError:
                    pass

        elif token in ("--format", "-f"):
            i += 1
            if i < len(tokens):
                config["format"] = tokens[i]

        elif token == "--dateformat":
            i += 1
            if i < len(tokens):
                config["dateformat"] = tokens[i]

        elif token in ("--separator", "-s"):
            i += 1
            if i < len(tokens):
                config["separator"] = tokens[i].encode().decode("unicode_escape")

        elif token in ("--desc", "-d"):
            config["desc"] = True

        elif token in ("--no-roles",):
            config["no_roles"] = True

        elif token in ("--enumerate", "-e"):
            config["enumerate"] = True

        i += 1

    return config
