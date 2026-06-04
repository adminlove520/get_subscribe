#!/usr/bin/env python3
"""get_subscribe - CLI entry point

This module provides the command-line interface for the get-subscribe package.
"""

from .fetcher import GetSubscribe

def main():
    """CLI entry point for get-subscribe command."""
    GetSubscribe.main()

if __name__ == "__main__":
    main()
