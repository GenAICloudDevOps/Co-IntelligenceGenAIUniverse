from fastapi import APIRouter, Depends
from app.database import get_database
from app.middleware.auth_middleware import get_current_active_user
import json
import os
import time
from datetime import datetime, timedelta
import psutil

router = APIRouter()

# Store startup time for uptime calculation
startup_time = time.time()

@router.get("/stats/public")
async def get_public_system_stats(database = Depends(get_database)):
    """Get basic system statistics without authentication"""
    try:
        # Get user count from database
        user_count_query = "SELECT COUNT(*) as count FROM users"
        user_result = await database.fetch_one(user_count_query)
        user_count = user_result['count'] if user_result else 0
        
        # Get apps configuration
        apps_config_path = "/app/config/apps.json"
        total_apps = 0
        active_apps = 0
        
        if os.path.exists(apps_config_path):
            with open(apps_config_path, 'r') as f:
                apps_data = json.load(f)
                apps = apps_data.get('apps', [])
                total_apps = len(apps)
                active_apps = len([app for app in apps if app.get('status') == 'active'])
        
        # Calculate uptime
        current_time = time.time()
        uptime_seconds = current_time - startup_time
        uptime_hours = uptime_seconds / 3600
        uptime_days = uptime_hours / 24
        
        # Format uptime string
        if uptime_days >= 1:
            uptime_str = f"{int(uptime_days)}d {int(uptime_hours % 24)}h"
        elif uptime_hours >= 1:
            uptime_str = f"{int(uptime_hours)}h {int((uptime_seconds % 3600) / 60)}m"
        else:
            uptime_str = f"{int(uptime_seconds / 60)}m {int(uptime_seconds % 60)}s"
        
        # AI Models information
        ai_models = [
            "Claude 3 Haiku",
            "Claude 3 Sonnet", 
            "Claude 3 Opus"
        ]
        
        return {
            "users": {
                "total": user_count,
                "active_sessions": 0  # Don't show active sessions for public
            },
            "apps": {
                "total": total_apps,
                "active": active_apps,
                "inactive": total_apps - active_apps
            },
            "ai_models": {
                "available": ai_models,
                "count": len(ai_models),
                "primary": "Claude 3 Haiku"
            },
            "uptime": {
                "seconds": int(uptime_seconds),
                "formatted": uptime_str,
                "started_at": datetime.fromtimestamp(startup_time).isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get system stats: {str(e)}",
            "users": {"total": 0, "active_sessions": 0},
            "apps": {"total": 0, "active": 0, "inactive": 0},
            "ai_models": {"count": 3, "available": ["Claude 3 Haiku", "Claude 3 Sonnet", "Claude 3 Opus"]},
            "uptime": {"formatted": "Unknown", "seconds": 0},
            "timestamp": datetime.now().isoformat()
        }

@router.get("/stats")
async def get_system_stats(
    database = Depends(get_database),
    current_user = Depends(get_current_active_user)
):
    """Get comprehensive system statistics"""
    try:
        # Get user count from database
        user_count_query = "SELECT COUNT(*) as count FROM users"
        user_result = await database.fetch_one(user_count_query)
        user_count = user_result['count'] if user_result else 0
        
        # Get apps configuration
        apps_config_path = "/app/config/apps.json"
        total_apps = 0
        active_apps = 0
        
        if os.path.exists(apps_config_path):
            with open(apps_config_path, 'r') as f:
                apps_data = json.load(f)
                apps = apps_data.get('apps', [])
                total_apps = len(apps)
                active_apps = len([app for app in apps if app.get('status') == 'active'])
        
        # Calculate uptime
        current_time = time.time()
        uptime_seconds = current_time - startup_time
        uptime_hours = uptime_seconds / 3600
        uptime_days = uptime_hours / 24
        
        # Format uptime string
        if uptime_days >= 1:
            uptime_str = f"{int(uptime_days)}d {int(uptime_hours % 24)}h"
        elif uptime_hours >= 1:
            uptime_str = f"{int(uptime_hours)}h {int((uptime_seconds % 3600) / 60)}m"
        else:
            uptime_str = f"{int(uptime_seconds / 60)}m {int(uptime_seconds % 60)}s"
        
        # AI Models information
        ai_models = [
            "Claude 3 Haiku",
            "Claude 3 Sonnet", 
            "Claude 3 Opus"
        ]
        
        # System resource usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "users": {
                "total": user_count,
                "active_sessions": 1 if current_user else 0  # Current user session
            },
            "apps": {
                "total": total_apps,
                "active": active_apps,
                "inactive": total_apps - active_apps
            },
            "ai_models": {
                "available": ai_models,
                "count": len(ai_models),
                "primary": "Claude 3 Haiku"
            },
            "uptime": {
                "seconds": int(uptime_seconds),
                "formatted": uptime_str,
                "started_at": datetime.fromtimestamp(startup_time).isoformat()
            },
            "system": {
                "cpu_usage": f"{cpu_percent:.1f}%",
                "memory_usage": f"{memory.percent:.1f}%",
                "disk_usage": f"{(disk.used / disk.total * 100):.1f}%",
                "memory_total": f"{memory.total / (1024**3):.1f}GB",
                "disk_total": f"{disk.total / (1024**3):.1f}GB"
            },
            "environment": {
                "deployment": os.getenv("DEPLOYMENT_ENV", "local"),
                "debug": os.getenv("DEBUG", "true").lower() == "true",
                "database": "PostgreSQL 15",
                "backend": "FastAPI + Uvicorn"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get system stats: {str(e)}",
            "users": {"total": 0, "active_sessions": 0},
            "apps": {"total": 0, "active": 0, "inactive": 0},
            "ai_models": {"count": 3, "available": ["Claude 3 Haiku", "Claude 3 Sonnet", "Claude 3 Opus"]},
            "uptime": {"formatted": "Unknown", "seconds": 0},
            "system": {"cpu_usage": "0%", "memory_usage": "0%", "disk_usage": "0%"},
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health")
async def health_check():
    """Enhanced health check with basic stats"""
    uptime_seconds = time.time() - startup_time
    uptime_hours = uptime_seconds / 3600
    
    if uptime_hours >= 1:
        uptime_str = f"{int(uptime_hours)}h {int((uptime_seconds % 3600) / 60)}m"
    else:
        uptime_str = f"{int(uptime_seconds / 60)}m {int(uptime_seconds % 60)}s"
    
    return {
        "status": "healthy",
        "service": "backend",
        "uptime": uptime_str,
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("DEPLOYMENT_ENV", "local")
    }
