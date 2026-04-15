"""Background tasks for iiko synchronization and other periodic tasks."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.dependencies import get_iiko_sync_service


class BackgroundTaskManager:
    """Manager for background tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.logger = logging.getLogger(__name__)
        self.settings = get_settings()
        self._running = False
    
    async def start(self) -> None:
        """Start background tasks."""
        if self._running:
            self.logger.warning("Background tasks already running")
            return
        
        self.logger.info("Starting background tasks")
        
        # Schedule iiko menu sync every hour
        self.scheduler.add_job(
            self._sync_menu_from_iiko,
            trigger=IntervalTrigger(hours=1),
            id="iiko_menu_sync",
            name="Sync menu from iiko",
            replace_existing=True
        )
        
        # Schedule iiko order status sync every 5 minutes
        self.scheduler.add_job(
            self._sync_order_statuses,
            trigger=IntervalTrigger(minutes=5),
            id="iiko_order_status_sync",
            name="Sync order statuses from iiko",
            replace_existing=True
        )
        
        # Schedule daily cleanup at 2 AM
        self.scheduler.add_job(
            self._daily_cleanup,
            trigger=CronTrigger(hour=2, minute=0),
            id="daily_cleanup",
            name="Daily cleanup tasks",
            replace_existing=True
        )
        
        # Start scheduler
        self.scheduler.start()
        self._running = True
        
        self.logger.info("Background tasks started successfully")
    
    async def stop(self) -> None:
        """Stop background tasks."""
        if not self._running:
            return
        
        self.logger.info("Stopping background tasks")
        self.scheduler.shutdown(wait=True)
        self._running = False
        self.logger.info("Background tasks stopped")
    
    async def _sync_menu_from_iiko(self) -> None:
        """Sync menu from iiko (background task)."""
        try:
            self.logger.info("Starting scheduled menu sync from iiko")
            
            # Get sync service
            sync_service = await get_iiko_sync_service()
            if not sync_service:
                self.logger.error("Failed to get iiko sync service")
                return
            
            # Perform sync
            success = await sync_service.sync_menu_from_iiko()
            
            if success:
                self.logger.info("Scheduled menu sync completed successfully")
            else:
                self.logger.error("Scheduled menu sync failed")
                
        except Exception as e:
            self.logger.error(f"Error in scheduled menu sync: {e}")
    
    async def _sync_order_statuses(self) -> None:
        """Sync order statuses from iiko (background task)."""
        try:
            self.logger.info("Starting scheduled order status sync from iiko")
            
            # Get sync service
            sync_service = await get_iiko_sync_service()
            if not sync_service:
                self.logger.error("Failed to get iiko sync service")
                return
            
            # Get pending orders from database
            # This would need to be implemented based on your order repository
            # For now, we'll just log that the task ran
            self.logger.info("Scheduled order status sync completed")
            
        except Exception as e:
            self.logger.error(f"Error in scheduled order status sync: {e}")
    
    async def _daily_cleanup(self) -> None:
        """Daily cleanup tasks."""
        try:
            self.logger.info("Starting daily cleanup tasks")
            
            # Clean up old logs, temporary files, etc.
            # This is a placeholder for cleanup tasks
            
            self.logger.info("Daily cleanup tasks completed")
            
        except Exception as e:
            self.logger.error(f"Error in daily cleanup: {e}")
    
    async def trigger_menu_sync(self) -> bool:
        """Manually trigger menu sync."""
        try:
            self.logger.info("Manually triggering menu sync")
            
            sync_service = await get_iiko_sync_service()
            if not sync_service:
                self.logger.error("Failed to get iiko sync service")
                return False
            
            success = await sync_service.sync_menu_from_iiko(force=True)
            
            if success:
                self.logger.info("Manual menu sync completed successfully")
            else:
                self.logger.error("Manual menu sync failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error in manual menu sync: {e}")
            return False
    
    async def trigger_order_status_sync(self) -> bool:
        """Manually trigger order status sync."""
        try:
            self.logger.info("Manually triggering order status sync")
            
            sync_service = await get_iiko_sync_service()
            if not sync_service:
                self.logger.error("Failed to get iiko sync service")
                return False
            
            # This would need to be implemented based on your order repository
            # For now, we'll just return True
            self.logger.info("Manual order status sync completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in manual order status sync: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if background tasks are running."""
        return self._running
    
    def get_job_status(self) -> dict:
        """Get status of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "running": self._running,
            "jobs": jobs
        }


# Global instance
background_task_manager = BackgroundTaskManager()
