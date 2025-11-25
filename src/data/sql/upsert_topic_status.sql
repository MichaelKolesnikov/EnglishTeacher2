INSERT INTO user_topics AS u (
    user_id, topic_key, status, mastery_streak,
    times_correct, times_mistake,
    last_mastered, last_mistake, last_practiced
) VALUES (
    %s, %s, %s, %s, %s, %s,
    CASE WHEN %s THEN CURRENT_TIMESTAMP END,
    CASE WHEN %s THEN CURRENT_TIMESTAMP END,
    CURRENT_TIMESTAMP
)
ON CONFLICT (user_id, topic_key) DO UPDATE SET
    status = COALESCE(EXCLUDED.status, u.status),
    mastery_streak = COALESCE(EXCLUDED.mastery_streak, u.mastery_streak),
    times_correct = u.times_correct + COALESCE(EXCLUDED.times_correct, 0),
    times_mistake = u.times_mistake + COALESCE(EXCLUDED.times_mistake, 0),
    last_mastered = COALESCE(EXCLUDED.last_mastered, u.last_mastered),
    last_mistake = COALESCE(EXCLUDED.last_mistake, u.last_mistake),
    last_practiced = EXCLUDED.last_practiced