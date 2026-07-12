from app.models.database import db


class AiRequestRepository:
    async def create_request(
        self,
        request_id: str,
        user_id: int,
        match_id: int | None,
        request: str,
        model: str,
        system_instruction: str,
        response_mime_type: str,
        response_schema: str,
        thinking_level: str
    ):
        """Create AI request log row."""
        conn = await db.get_connection()
        # Create a started request row before the paid Gemini call.
        await conn.execute('''
            INSERT INTO ai_requests (
                request_id,
                user_id,
                match_id,
                request,
                model,
                system_instruction,
                response_mime_type,
                response_schema,
                thinking_level,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request_id,
            user_id,
            match_id,
            request,
            model,
            system_instruction,
            response_mime_type,
            response_schema,
            thinking_level,
            'started'
        ))
        await conn.commit()

    async def save_response(self, request_id: str, response: str):
        """Save AI request successful response."""
        conn = await db.get_connection()
        # Finish the existing request row with the parsed Gemini response.
        await conn.execute('''
            UPDATE ai_requests
            SET response_finished_at = CURRENT_TIMESTAMP,
                response = ?,
                status = ?
            WHERE request_id = ?
        ''', (response, 'completed', request_id))
        await conn.commit()

    async def save_error(self, request_id: str, error: str):
        """Save AI request failed response."""
        conn = await db.get_connection()
        # Finish the existing request row with the Gemini error text.
        await conn.execute('''
            UPDATE ai_requests
            SET response_finished_at = CURRENT_TIMESTAMP,
                status = ?,
                error = ?
            WHERE request_id = ?
        ''', ('failed', error, request_id))
        await conn.commit()


ai_request_repository = AiRequestRepository()
