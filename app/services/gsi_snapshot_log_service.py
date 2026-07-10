import json
import logging
from datetime import datetime, UTC
from pathlib import Path


GSI_SNAPSHOTS_DIR = Path('data') / 'gsi_snapshots'
logger = logging.getLogger(__name__)


class GsiSnapshotLogService:
    def __init__(self):
        """Create snapshot log session id."""
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        logger.info(f'GSI snapshot log session: {self.session_id}')

    async def save_snapshot(self, user_id: int, match_id: int | None, payload: dict):
        """Save GSI snapshot to JSONL file."""
        GSI_SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        file_match_id = 'unknown' if match_id is None else match_id
        file_path = GSI_SNAPSHOTS_DIR / f'{self.session_id}_{user_id}_{file_match_id}.jsonl'
        snapshot = {
            'saved_at': datetime.now(UTC).isoformat(),
            'user_id': user_id,
            'match_id': match_id,
            'payload': payload
        }
        # Append one JSON snapshot per line for simple later analysis.
        with file_path.open('a', encoding='utf-8') as file:
            file.write(json.dumps(snapshot, ensure_ascii=False) + '\n')


gsi_snapshot_log_service = GsiSnapshotLogService()
