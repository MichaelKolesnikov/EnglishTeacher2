SELECT status, mastery_streak, times_correct, times_mistake,
       last_mastered, last_mistake
FROM user_topics WHERE user_id = %s AND topic_key = %s