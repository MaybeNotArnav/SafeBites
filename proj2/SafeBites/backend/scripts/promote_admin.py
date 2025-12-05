"""Utility script to promote an existing SafeBites user to admin."""
from __future__ import annotations

import argparse
import getpass
import os
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote a SafeBites user to admin role")
    parser.add_argument(
        "--mongo-uri",
        dest="mongo_uri",
        default=os.getenv("MONGO_URI"),
        help="MongoDB connection string (defaults to MONGO_URI env var)",
    )
    parser.add_argument(
        "--database",
        dest="database",
        default=os.getenv("MONGO_DB", "safebites"),
        help="Database name (default: safebites or MONGO_DB env var)",
    )
    parser.add_argument(
        "--username",
        dest="username",
        required=True,
        help="Username of the account to update",
    )
    parser.add_argument(
        "--role",
        dest="role",
        default="admin",
        help='Role to assign (default: "admin")',
    )
    return parser.parse_args()


def resolve_uri(mongo_uri: Optional[str]) -> str:
    if mongo_uri:
        return mongo_uri
    # Prompt securely if not provided
    return getpass.getpass(prompt="Enter MongoDB connection string: ")


def main() -> None:
    args = parse_args()
    mongo_uri = resolve_uri(args.mongo_uri)
    client = MongoClient(mongo_uri)
    db = client[args.database]

    try:
        result = db.users.update_one(
            {"username": args.username},
            {"$set": {"role": args.role}},
        )
        if result.matched_count == 0:
            print(f"No user found with username '{args.username}'.")
            return
        user = db.users.find_one({"username": args.username}, {"username": 1, "role": 1, "_id": 0})
        print(f"Updated user: {user}")
    except PyMongoError as exc:
        print(f"Failed to update user: {exc}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
