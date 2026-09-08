"""This module contains the main process of the robot."""

from datetime import datetime, timedelta
import json
import time

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from robot_framework import config
from robot_framework.exceptions import BusinessError


def process(orchestrator_connection: OrchestratorConnection, queue_element: QueueElement | None = None) -> None:
    """
    Hold a dispatched spool job until SAP has had time to generate it, then hand it
    over to the performer.

    Why this robot exists: the dispatcher and the performer both drive the SAP GUI,
    so both have to be blocking triggers, and a blocking robot sitting idle waiting
    for a spool job to generate occupies a scheduler that could be doing real work.
    This robot does the waiting instead. It needs neither SAP nor a database.

    The wait is only a head start, not a guarantee. The performer still polls the
    spool overview when it takes over, and still fails if the job never appears.
    """
    orchestrator_connection.log_trace("Running process.")

    udtraek_id, spool_job = parse_queue_element(queue_element)

    # created_date is stamped by OpenOrchestrator when the dispatcher creates the
    # element, so the timestamp travels with the element and nothing has to be
    # embedded in the data. Both sides use naive local time; that is only sound
    # while the schedulers share a timezone and a synced clock, which is the case
    # on the domain.
    ready_at = queue_element.created_date + timedelta(minutes=config.WAIT_MINUTES)
    remaining_s = (ready_at - datetime.now()).total_seconds()



    if remaining_s > 0:
        orchestrator_connection.log_trace(
            f"Spool job {spool_job} was submitted at "
            f"{queue_element.created_date:%H:%M:%S}; waiting {remaining_s:.0f}s "
            f"until {ready_at:%H:%M:%S}."
        )
        time.sleep(remaining_s)
    else:
        orchestrator_connection.log_trace(
            f"Spool job {spool_job} has already had its {config.WAIT_MINUTES} minute "
            "head start; queueing it immediately."
        )

    orchestrator_connection.create_queue_element(
        config.PERFORMER_QUEUE_NAME,
        spool_job,
        json.dumps({"UdtraekId": udtraek_id, "SpoolJob": spool_job}),
        orchestrator_connection.process_name,
    )

    orchestrator_connection.log_trace(
        f"Handed window {udtraek_id} ({spool_job}) to {config.PERFORMER_QUEUE_NAME}."
    )


def parse_queue_element(queue_element: QueueElement | None) -> tuple[int, str]:
    """
    Read the window id and spool job name the dispatcher put on the wait element.

    Raises BusinessError on anything malformed: a broken element should fail on its
    own without taking the rest of the run down, and the window it refers to is
    recovered anyway by the stale sweep in usp_CJI3_ReserverUdtraek.
    """
    if queue_element is None:
        raise BusinessError("No queue element to process.")

    data = (queue_element.data or "").strip()
    if not data:
        raise BusinessError(f"Wait element {queue_element.reference} has no data.")

    try:
        payload = json.loads(data)
    except json.JSONDecodeError as error:
        raise BusinessError(f"Wait element data is not valid JSON: {data}") from error

    spool_job = payload.get("SpoolJob")
    udtraek_id = payload.get("UdtraekId")

    if not spool_job or udtraek_id is None:
        raise BusinessError(
            f"Wait element must carry SpoolJob and UdtraekId, got: {data}"
        )

    return udtraek_id, spool_job
