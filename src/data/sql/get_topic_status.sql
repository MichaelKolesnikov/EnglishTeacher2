SELECT status, mastery_streak, times_correct, times_mistake
FROM user_topics WHERE user_id = %s AND topic_key = %s