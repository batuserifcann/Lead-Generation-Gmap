"""
Rate Limiter for Business Lead Automation System
Handles rate limiting for messaging and API calls
"""
import time
from typing import Dict, List, Optional
from collections import deque
from datetime import datetime, timedelta

from utils.config import config
from utils.logger import get_logger, log_info, log_error, log_warning

class RateLimiter:
    """Rate limiter for controlling message sending frequency"""

    def __init__(self, max_per_hour: int = None, delay_between: int = None):
        self.logger = get_logger('RateLimiter')

        # Configuration
        self.max_per_hour = max_per_hour or config.DEFAULT_MAX_MESSAGES_PER_HOUR
        self.delay_between = delay_between or config.DEFAULT_MESSAGE_DELAY

        # Tracking
        self.message_times = deque()  # Store timestamps of sent messages
        self.last_message_time = 0
        self.total_messages_sent = 0

        # Statistics
        self.start_time = time.time()
        self.hourly_counts = {}  # Track messages per hour

        log_info(f"RateLimiter initialized: {self.max_per_hour} messages/hour, {self.delay_between}s delay")

    def can_send_message(self) -> bool:
        """Check if a message can be sent now"""
        current_time = time.time()

        # Check delay between messages
        if self.last_message_time > 0:
            time_since_last = current_time - self.last_message_time
            if time_since_last < self.delay_between:
                return False

        # Check hourly limit
        if self._get_messages_in_last_hour() >= self.max_per_hour:
            return False

        return True

    def record_message_sent(self):
        """Record that a message was sent"""
        current_time = time.time()

        # Update tracking
        self.message_times.append(current_time)
        self.last_message_time = current_time
        self.total_messages_sent += 1

        # Update hourly statistics
        current_hour = datetime.now().strftime('%Y-%m-%d %H')
        self.hourly_counts[current_hour] = self.hourly_counts.get(current_hour, 0) + 1

        # Clean old message times (keep only last hour)
        self._clean_old_message_times()

        log_info(f"Message recorded. Total: {self.total_messages_sent}, Last hour: {self._get_messages_in_last_hour()}")

    def get_next_available_time(self) -> int:
        """Get seconds until next message can be sent"""
        current_time = time.time()

        # Check delay between messages
        delay_wait = 0
        if self.last_message_time > 0:
            time_since_last = current_time - self.last_message_time
            if time_since_last < self.delay_between:
                delay_wait = int(self.delay_between - time_since_last)

        # Check hourly limit
        hourly_wait = 0
        if self._get_messages_in_last_hour() >= self.max_per_hour:
            # Find the oldest message in the last hour
            if self.message_times:
                oldest_message_time = self.message_times[0]
                time_until_oldest_expires = 3600 - (current_time - oldest_message_time)
                hourly_wait = max(0, int(time_until_oldest_expires))

        return max(delay_wait, hourly_wait)

    def _get_messages_in_last_hour(self) -> int:
        """Get number of messages sent in the last hour"""
        current_time = time.time()
        hour_ago = current_time - 3600

        # Count messages in the last hour
        count = 0
        for message_time in self.message_times:
            if message_time > hour_ago:
                count += 1

        return count

    def _clean_old_message_times(self):
        """Remove message times older than 1 hour"""
        current_time = time.time()
        hour_ago = current_time - 3600

        # Remove old timestamps
        while self.message_times and self.message_times[0] < hour_ago:
            self.message_times.popleft()

    def reset_counters(self):
        """Reset all counters"""
        self.message_times.clear()
        self.last_message_time = 0
        self.total_messages_sent = 0
        self.hourly_counts.clear()
        self.start_time = time.time()

        log_info("Rate limiter counters reset")

    def get_statistics(self) -> Dict[str, any]:
        """Get rate limiting statistics"""
        current_time = time.time()
        session_duration = current_time - self.start_time

        # Calculate average messages per hour
        avg_per_hour = 0
        if session_duration > 0:
            avg_per_hour = (self.total_messages_sent / session_duration) * 3600

        return {
            'total_messages_sent': self.total_messages_sent,
            'messages_last_hour': self._get_messages_in_last_hour(),
            'max_per_hour': self.max_per_hour,
            'delay_between_messages': self.delay_between,
            'session_duration_minutes': session_duration / 60,
            'average_per_hour': round(avg_per_hour, 2),
            'next_available_in_seconds': self.get_next_available_time(),
            'can_send_now': self.can_send_message()
        }

    def update_settings(self, max_per_hour: Optional[int] = None, delay_between: Optional[int] = None):
        """Update rate limiting settings"""
        if max_per_hour is not None:
            self.max_per_hour = max_per_hour
            log_info(f"Updated max messages per hour: {max_per_hour}")

        if delay_between is not None:
            self.delay_between = delay_between
            log_info(f"Updated delay between messages: {delay_between}s")

    def wait_if_needed(self) -> int:
        """Wait if rate limiting requires it. Returns seconds waited."""
        wait_time = self.get_next_available_time()

        if wait_time > 0:
            log_info(f"Rate limiting: waiting {wait_time} seconds")
            time.sleep(wait_time)

        return wait_time

    def get_hourly_breakdown(self) -> Dict[str, int]:
        """Get breakdown of messages sent per hour"""
        # Clean old entries (keep last 24 hours)
        current_hour = datetime.now()
        cutoff_time = current_hour - timedelta(hours=24)
        cutoff_str = cutoff_time.strftime('%Y-%m-%d %H')

        # Remove old entries
        hours_to_remove = []
        for hour_str in self.hourly_counts:
            if hour_str < cutoff_str:
                hours_to_remove.append(hour_str)

        for hour_str in hours_to_remove:
            del self.hourly_counts[hour_str]

        return self.hourly_counts.copy()

    def is_within_limits(self) -> bool:
        """Check if current usage is within all limits"""
        return (
            self.can_send_message() and
            self._get_messages_in_last_hour() < self.max_per_hour
        )

    def get_time_until_next_slot(self) -> str:
        """Get human-readable time until next message slot"""
        wait_seconds = self.get_next_available_time()

        if wait_seconds == 0:
            return "Now"
        elif wait_seconds < 60:
            return f"{wait_seconds} seconds"
        elif wait_seconds < 3600:
            minutes = wait_seconds // 60
            seconds = wait_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = wait_seconds // 3600
            minutes = (wait_seconds % 3600) // 60
            return f"{hours}h {minutes}m"