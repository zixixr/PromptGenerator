import aiofiles
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from src.models.session import Session

logger = logging.getLogger(__name__)


class FileStorage:
    """Async file storage for session history."""

    def __init__(self, directory: str = "./conversations"):
        self.directory = Path(directory)

    async def save_history(self, session: Session) -> None:
        """
        Save session history to JSON file.

        Args:
            session: Session object to save

        Note:
            Errors are logged but not raised (non-blocking operation)
            Each session has one JSON file that gets updated on every message
        """
        try:
            # Create directory if not exists
            self.directory.mkdir(parents=True, exist_ok=True)

            # Fixed filename per session: sessionid.json
            filename = f"{session.session_id}.json"
            filepath = self.directory / filename

            # Delete old session files with timestamp prefix (for backward compatibility)
            pattern = f"*_{session.session_id}.json"
            for old_file in self.directory.glob(pattern):
                try:
                    old_file.unlink()
                    logger.debug(f"Deleted old session file: {old_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete old file {old_file}: {e}")

            # Prepare session data for JSON
            session_data = {
                "session_id": session.session_id,
                "system_prompt_template": session.system_prompt_template,
                "resolved_system_prompt": session.resolved_system_prompt,
                "variables": session.variables,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "rounds": [
                    {
                        "round_number": r.round_number,
                        "user_message": r.user_message,
                        "assistant_response": r.assistant_response,
                        "timestamp": r.timestamp.isoformat(),
                    }
                    for r in session.rounds
                ],
            }

            # Write to temp file first (atomic write)
            temp_filepath = filepath.with_suffix(".tmp")
            async with aiofiles.open(temp_filepath, "w", encoding="utf-8") as f:
                await f.write(
                    json.dumps(session_data, ensure_ascii=False, indent=2)
                )

            # Replace existing file (atomic on Windows/Unix)
            temp_filepath.replace(filepath)
            logger.debug(f"Saved session history to {filepath}")

        except Exception as e:
            logger.error(f"Failed to save session history for {session.session_id}: {e}")
            # Don't raise - file I/O should not block API responses
