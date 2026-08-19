"""This module handles resetting the state of the computer so the robot can work with a clean slate."""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection


def reset(orchestrator_connection: OrchestratorConnection) -> None:
    """Clean up, close/kill all programs and start them again."""
    orchestrator_connection.log_trace("Resetting.")
    clean_up(orchestrator_connection)
    close_all(orchestrator_connection)
    kill_all(orchestrator_connection)
    open_all(orchestrator_connection)


def clean_up(orchestrator_connection: OrchestratorConnection) -> None:
    """Do any cleanup needed to leave a blank slate."""
    orchestrator_connection.log_trace("Doing cleanup.")


def close_all(orchestrator_connection: OrchestratorConnection) -> None:
    """Gracefully close all applications used by the robot."""
    orchestrator_connection.log_trace("Closing all applications.")


def kill_all(orchestrator_connection: OrchestratorConnection) -> None:
    """Forcefully close all applications used by the robot.

    Intentionally empty. The dispatcher and performer kill saplogon/sapgui here, but
    this robot uses neither - and since it is meant to run on a scheduler alongside
    other work, killing SAP would take down a process that has nothing to do with it.
    """
    orchestrator_connection.log_trace("Nothing to kill; this robot uses no applications.")


def open_all(orchestrator_connection: OrchestratorConnection) -> None:
    """Open all programs used by the robot.

    Intentionally empty: this robot needs no SAP session and no database connection,
    only OpenOrchestrator itself.
    """
    orchestrator_connection.log_trace("Nothing to open.")
