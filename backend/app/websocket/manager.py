"""
WebSocket connection manager.
Maps user_id -> active connections for real-time notifications.
Uses Redis pub/sub as backend for Socket.IO.
"""
