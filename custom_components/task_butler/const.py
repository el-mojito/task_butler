"""Constants for the Task Butler integration."""

DOMAIN = "task_butler"

# Platforms
PLATFORMS = ["binary_sensor", "sensor", "switch"]

# Configuration keys
CONF_TASK_NAME = "task_name"
CONF_INTERVAL_DAYS = "interval_days"
CONF_SCHEDULE_TYPE = "schedule_type"
CONF_ENABLED = "enabled"

# Schedule types
SCHEDULE_FIXED = "fixed"
SCHEDULE_COMPLETION_BASED = "completion_based"

# Default values
DEFAULT_INTERVAL_DAYS = 30
DEFAULT_ENABLED = True

# Entity attributes
ATTR_NEXT_DUE_DATE = "next_due_date"
ATTR_DAYS_OVERDUE = "days_overdue"
ATTR_LAST_COMPLETED = "last_completed"
ATTR_SCHEDULE_TYPE = "schedule_type"
ATTR_INTERVAL_DAYS = "interval_days"
