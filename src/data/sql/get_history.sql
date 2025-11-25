SELECT participant, message
FROM messages
WHERE user_id = %s
ORDER BY created_at DESC
LIMIT %s