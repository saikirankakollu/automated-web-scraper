"""Scheduler module wrapping APScheduler for periodic scraping jobs."""

from typing import Any, Callable, List, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.logger import setup_logger

logger = setup_logger(__name__)


class Scheduler:
    """Manage scheduled scraping jobs using APScheduler.

    Wraps a :class:`~apscheduler.schedulers.background.BackgroundScheduler`
    to provide a simple interface for adding cron, interval, and custom
    triggered jobs.

    Example::

        scheduler = Scheduler()
        scheduler.add_interval_job(my_scrape_fn, minutes=30, job_id="daily")
        scheduler.start()
        # … application runs …
        scheduler.stop()
    """

    def __init__(self) -> None:
        """Initialise the background scheduler."""
        self._scheduler = BackgroundScheduler(
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 60,
            }
        )
        logger.info("Scheduler initialised.")

    # ------------------------------------------------------------------
    # Job management
    # ------------------------------------------------------------------

    def add_job(
        self,
        func: Callable,
        trigger: Any,
        job_id: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Add a job with an arbitrary APScheduler trigger.

        Args:
            func: Callable to execute when the trigger fires.
            trigger: An APScheduler trigger instance or trigger-name string.
            job_id: Optional stable identifier for the job.  Auto-generated
                when omitted.
            **kwargs: Extra keyword arguments forwarded to
                :meth:`~apscheduler.schedulers.base.BaseScheduler.add_job`.

        Returns:
            The job ID string assigned by APScheduler.
        """
        job = self._scheduler.add_job(func, trigger, id=job_id, **kwargs)
        logger.info("Job '%s' added with trigger %s.", job.id, trigger)
        return job.id

    def add_cron_job(
        self,
        func: Callable,
        cron_expression: str,
        job_id: Optional[str] = None,
    ) -> str:
        """Add a job that runs on a cron schedule.

        Args:
            func: Callable to execute.
            cron_expression: Standard 5-field cron expression
                (e.g. ``"0 6 * * *"`` for 06:00 every day).
            job_id: Optional stable job identifier.

        Returns:
            The assigned job ID string.

        Raises:
            ValueError: When *cron_expression* cannot be parsed.
        """
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError(
                f"Expected 5-field cron expression, got: '{cron_expression}'"
            )
        minute, hour, day, month, day_of_week = parts
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
        )
        return self.add_job(func, trigger, job_id=job_id)

    def add_interval_job(
        self,
        func: Callable,
        minutes: int = 60,
        job_id: Optional[str] = None,
    ) -> str:
        """Add a job that runs at a fixed interval.

        Args:
            func: Callable to execute.
            minutes: Interval in minutes between executions.
            job_id: Optional stable job identifier.

        Returns:
            The assigned job ID string.
        """
        trigger = IntervalTrigger(minutes=minutes)
        return self.add_job(func, trigger, job_id=job_id)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background scheduler.

        The scheduler runs in a daemon thread and will not block the main
        thread.

        Raises:
            RuntimeError: When the scheduler is already running.
        """
        if self._scheduler.running:
            raise RuntimeError("Scheduler is already running.")
        self._scheduler.start()
        logger.info("Scheduler started.")

    def stop(self, wait: bool = True) -> None:
        """Stop the background scheduler.

        Args:
            wait: When ``True`` (default), wait for currently executing jobs
                to finish before stopping.
        """
        if self._scheduler.running:
            self._scheduler.shutdown(wait=wait)
            logger.info("Scheduler stopped.")

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_jobs(self) -> List[Any]:
        """Return a list of all scheduled jobs.

        Returns:
            List of APScheduler :class:`~apscheduler.job.Job` objects.
        """
        return self._scheduler.get_jobs()

    def remove_job(self, job_id: str) -> None:
        """Remove a job by its identifier.

        Args:
            job_id: The ID string of the job to remove.

        Raises:
            KeyError: When no job with *job_id* exists.
        """
        self._scheduler.remove_job(job_id)
        logger.info("Job '%s' removed.", job_id)
