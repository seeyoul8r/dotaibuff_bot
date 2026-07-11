import json
from datetime import datetime, UTC
from pathlib import Path

from app.core.config import LoggingConfig, load_logging_config


AI_REQUESTS_DIR = Path('data') / 'ai_requests'


class AiRequestLogService:
    def __init__(self):
        """Create AI request log session id."""
        self.config: LoggingConfig = load_logging_config()
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    async def save_request(
        self,
        user_id: int,
        match_id: int | None,
        model: str,
        contents: str,
        system_instruction: str,
        response_mime_type: str,
        response_schema: dict,
        thinking_level: str
    ):
        """Save AI request to JSONL file."""
        # Skip directory and file creation when request logging is disabled.
        if not self.config.log_requests:
            return
        AI_REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
        file_match_id = 'unknown' if match_id is None else match_id
        file_path = AI_REQUESTS_DIR / f'{self.session_id}_{user_id}_{file_match_id}.jsonl'
        request = {
            'timestamp': datetime.now(UTC).isoformat(),
            'user_id': user_id,
            'match_id': match_id,
            'model': model,
            'contents': contents,
            'system_instruction': system_instruction,
            'response_mime_type': response_mime_type,
            'response_schema': response_schema,
            'thinking_level': thinking_level
        }
        # Append one exact model request per line for simple later analysis.
        with file_path.open('a', encoding='utf-8') as file:
            file.write(json.dumps(request, ensure_ascii=False) + '\n')


ai_request_log_service = AiRequestLogService()
