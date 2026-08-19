"""This module contains configuration constants used across the framework"""

# The number of times the robot retries on an error before terminating.
MAX_RETRY_COUNT = 1

# Whether the robot should be marked as failed if MAX_RETRY_COUNT is reached.
FAIL_ROBOT_ON_TOO_MANY_ERRORS = True

# Error screenshot config
SMTP_SERVER = "smtp.adm.aarhuskommune.dk"
SMTP_PORT = 25
SCREENSHOT_SENDER = "sapcji3@aarhus.dk"

# Constant/Credential names
ERROR_EMAIL = "Error Email"


# Queue specific configs
# ----------------------

# The queue this robot reads: one wait element per spool job the dispatcher
# submitted to SAP.
QUEUE_NAME = "SAPCJI3Wait"

# The queue this robot writes: work for the performer.
PERFORMER_QUEUE_NAME = "SAPCJI3"

# The limit on how many queue elements to process.
# The dispatcher creates one wait element per window, so this needs to be at least
# as high as the dispatcher's WINDOWS_PER_RUN for a night's batch to drain in one go.
MAX_TASK_COUNT = 100

# ----------------------


# Waiting
# ----------------------

# How long after the dispatcher submitted a spool job before the performer is
# allowed to go looking for it. Only a head start: the performer still polls the
# spool overview and still fails if the job never turns up.
#
# Each element waits out the remainder of its own 15 minutes, so a batch does not
# cost 15 minutes per window. The dispatcher creates them one per window as it works
# through SAP, so each element is already most of the way ripe when its turn comes
# and only sleeps the gap since the previous one. Ten windows submitted 90 seconds
# apart take about 15 minutes in total, not 150.
WAIT_MINUTES = 15

# Safety net against a wrong created_date or an unsynced clock: never sleep longer
# than this in a single element.
MAX_SLEEP_S = 3600

# ----------------------
