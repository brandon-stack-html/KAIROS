"""Shared rate-limiter instance (slowapi + in-memory store).

Import this module in routers to apply @limiter.limit() decorators.
The app must attach it to app.state.limiter in main.py.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
