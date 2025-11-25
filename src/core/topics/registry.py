from typing import TypedDict


class TopicInfo(TypedDict):
    name: str
    category: str  # grammar | vocabulary | functions | pronunciation
    cefr: str  # A1–C1


TOPICS: dict[str, TopicInfo] = {
    # ===================================================================
    # A1 — Elementary
    # ===================================================================
    "be_present": {"name": "Verb to be (am/is/are)", "category": "grammar", "cefr": "A1"},
    "present_simple": {"name": "Present Simple", "category": "grammar", "cefr": "A1"},
    "present_continuous": {"name": "Present Continuous", "category": "grammar", "cefr": "A1"},
    "there_is_are": {"name": "There is / There are", "category": "grammar", "cefr": "A1"},
    "have_got": {"name": "Have got", "category": "grammar", "cefr": "A1"},
    "can_ability_permission": {"name": "Can (ability & permission)", "category": "grammar", "cefr": "A1"},
    "articles_a_an_the_zero": {"name": "Articles (a/an/the/zero)", "category": "grammar", "cefr": "A1"},
    "possessive_adjectives": {"name": "Possessive adjectives (my, your...)", "category": "grammar", "cefr": "A1"},
    "possessive_s": {"name": "Possessive 's", "category": "grammar", "cefr": "A1"},
    "object_pronouns": {"name": "Object pronouns (me, you, him...)", "category": "grammar", "cefr": "A1"},
    "prepositions_place_basic": {"name": "Prepositions of place (in/on/at)", "category": "grammar", "cefr": "A1"},
    "prepositions_adjectives": {"name": "Adjective position", "category": "grammar", "cefr": "A1"},
    "daily_routine": {"name": "Daily routine", "category": "vocabulary", "cefr": "A1"},
    "family_members": {"name": "Family members", "category": "vocabulary", "cefr": "A1"},
    "numbers_1_100": {"name": "Numbers 1–100", "category": "vocabulary", "cefr": "A1"},
    "days_months_seasons": {"name": "Days, months seasons", "category": "vocabulary", "cefr": "A1"},
    "telling_time": {"name": "Telling the time", "category": "functions", "cefr": "A1"},
    "basic_questions": {"name": "Basic questions (What/Where/When/Who)", "category": "functions", "cefr": "A1"},

    # ===================================================================
    # A2 — Pre-Intermediate
    # ===================================================================
    "past_simple_be": {"name": "Past Simple of 'be'", "category": "grammar", "cefr": "A2"},
    "past_simple_regular": {"name": "Past Simple — regular verbs", "category": "grammar", "cefr": "A2"},
    "past_simple_irregular": {"name": "Past Simple — irregular verbs", "category": "grammar", "cefr": "A2"},
    "past_continuous": {"name": "Past Continuous", "category": "grammar", "cefr": "A2"},
    "present_perfect_simple": {"name": "Present Perfect (ever/never/just/already/yet)", "category": "grammar",
                               "cefr": "A2"},
    "going_to": {"name": "Going to (plans)", "category": "grammar", "cefr": "A2"},
    "will_future": {"name": "Will (predictions, spontaneous decisions)", "category": "grammar", "cefr": "A2"},
    "can_could_permission": {"name": "Can/Could (polite requests)", "category": "grammar", "cefr": "A2"},
    "must_have_to": {"name": "Must / Have to", "category": "grammar", "cefr": "A2"},
    "should_advice": {"name": "Should / Shouldn't", "category": "grammar", "cefr": "A2"},
    "comparatives": {"name": "Comparatives (-er than, more... than)", "category": "grammar", "cefr": "A2"},
    "superlatives": {"name": "Superlatives (the -est, the most...)", "category": "grammar", "cefr": "A2"},
    "prepositions_time": {"name": "Prepositions of time (at/in/on)", "category": "grammar", "cefr": "A2"},
    "adverbs_frequency": {"name": "Adverbs of frequency", "category": "grammar", "cefr": "A2"},
    "countable_uncountable": {"name": "Countable Uncountable (some/any/a lot of)", "category": "grammar", "cefr": "A2"},
    "food_drink": {"name": "Food drink", "category": "vocabulary", "cefr": "A2"},
    "clothes": {"name": "Clothes accessories", "category": "vocabulary", "cefr": "A2"},
    "jobs": {"name": "Jobs professions", "category": "vocabulary", "cefr": "A2"},
    "describing_people": {"name": "Describing people (appearance personality)", "category": "vocabulary", "cefr": "A2"},
    "directions": {"name": "Giving directions", "category": "functions", "cefr": "A2"},

    # ===================================================================
    # B1 — Intermediate
    # ===================================================================
    "present_perfect_vs_past_simple": {"name": "Present Perfect vs Past Simple", "category": "grammar", "cefr": "B1"},
    "present_perfect_continuous": {"name": "Present Perfect Continuous", "category": "grammar", "cefr": "B1"},
    "past_perfect": {"name": "Past Perfect", "category": "grammar", "cefr": "B1"},
    "used_to": {"name": "Used to", "category": "grammar", "cefr": "B1"},
    "zero_conditional": {"name": "Zero Conditional", "category": "grammar", "cefr": "B1"},
    "first_conditional": {"name": "First Conditional", "category": "grammar", "cefr": "B1"},
    "second_conditional": {"name": "Second Conditional", "category": "grammar", "cefr": "B1"},
    "modal_verbs_obligation": {"name": "Modals: obligation, prohibition, advice", "category": "grammar", "cefr": "B1"},
    "modal_verbs_deduction": {"name": "Modals of deduction (must/can't/might)", "category": "grammar", "cefr": "B1"},
    "passive_voice_simple": {"name": "Passive voice (Present Past Simple)", "category": "grammar", "cefr": "B1"},
    "relative_clauses_defining": {"name": "Defining relative clauses (who/which/that/where)", "category": "grammar",
                                  "cefr": "B1"},
    "too_enough": {"name": "Too / Enough", "category": "grammar", "cefr": "B1"},
    "so_such": {"name": "So / Such", "category": "grammar", "cefr": "B1"},
    "travel_vocabulary": {"name": "Travel holidays", "category": "vocabulary", "cefr": "B1"},
    "health_body": {"name": "Health the body", "category": "vocabulary", "cefr": "B1"},
    "education": {"name": "Education school subjects", "category": "vocabulary", "cefr": "B1"},
    "environment": {"name": "Environment climate change", "category": "vocabulary", "cefr": "B1"},
    "asking_giving_opinion": {"name": "Asking for giving opinion", "category": "functions", "cefr": "B1"},
    "agreeing_disagreeing": {"name": "Agreeing disagreeing", "category": "functions", "cefr": "B1"},

    # ===================================================================
    # B2 — Upper-Intermediate
    # ===================================================================
    "future_forms": {"name": "Future forms (will, going to, Present Continuous)", "category": "grammar", "cefr": "B2"},
    "future_continuous_perfect": {"name": "Future Continuous Perfect", "category": "grammar", "cefr": "B2"},
    "third_conditional": {"name": "Third Conditional", "category": "grammar", "cefr": "B2"},
    "mixed_conditionals": {"name": "Mixed conditionals", "category": "grammar", "cefr": "B2"},
    "wish_if_only": {"name": "Wish / If only", "category": "grammar", "cefr": "B2"},
    "passive_all_tenses": {"name": "Passive voice (all tenses)", "category": "grammar", "cefr": "B2"},
    "causative_have_get": {"name": "Have/Get something done", "category": "grammar", "cefr": "B2"},
    "reported_speech_statements": {"name": "Reported speech (statements)", "category": "grammar", "cefr": "B2"},
    "reported_questions_commands": {"name": "Reported questions commands", "category": "grammar", "cefr": "B2"},
    "relative_clauses_non_defining": {"name": "Non-defining relative clauses", "category": "grammar", "cefr": "B2"},
    "participle_clauses": {"name": "Participle clauses (-ing / -ed)", "category": "grammar", "cefr": "B2"},
    "inversion": {"name": "Inversion (Never have I..., No sooner...)", "category": "grammar", "cefr": "B2"},
    "gerund_infinitive_advanced": {"name": "Gerund vs Infinitive (advanced cases)", "category": "grammar",
                                   "cefr": "B2"},
    "collocations_strong": {"name": "Strong collocations", "category": "vocabulary", "cefr": "B2"},
    "phrasal_verbs_separable": {"name": "Separable phrasal verbs", "category": "vocabulary", "cefr": "B2"},
    "idioms_expressions": {"name": "Idioms common expressions", "category": "vocabulary", "cefr": "B2"},
    "crime_law": {"name": "Crime law", "category": "vocabulary", "cefr": "B2"},
    "science_technology": {"name": "Science technology", "category": "vocabulary", "cefr": "B2"},
    "making_suggestions": {"name": "Making suggestions", "category": "functions", "cefr": "B2"},
    "discussing_pros_cons": {"name": "Discussing advantages disadvantages", "category": "functions", "cefr": "B2"},

    # ===================================================================
    # C1 — Advanced
    # ===================================================================
    "future_perfect_continuous": {"name": "Future Perfect Continuous", "category": "grammar", "cefr": "C1"},
    "mixed_conditionals_advanced": {"name": "Advanced mixed conditionals", "category": "grammar", "cefr": "C1"},
    "inversion_advanced": {"name": "Advanced inversion (Not only..., Hardly...)", "category": "grammar", "cefr": "C1"},
    "cleft_sentences": {"name": "Cleft sentences (What I love is...)", "category": "grammar", "cefr": "C1"},
    "ellipsis_substitution": {"name": "Ellipsis Substitution (so do I, neither can I)", "category": "grammar",
                              "cefr": "C1"},
    "nominalisation": {"name": "Nominalisation (verbs → nouns)", "category": "grammar", "cefr": "C1"},
    "advanced_modals": {"name": "Advanced modals (may have, should have, etc.)", "category": "grammar", "cefr": "C1"},
    "phrasal_verbs_advanced": {"name": "Advanced multi-word verbs", "category": "vocabulary", "cefr": "C1"},
    "academic_collocations": {"name": "Academic collocations", "category": "vocabulary", "cefr": "C1"},
    "formal_informal_register": {"name": "Formal vs informal register", "category": "functions", "cefr": "C1"},
    "nuance_word_choice": {"name": "Nuance subtle differences (e.g. big/large/huge)", "category": "vocabulary",
                           "cefr": "C1"},
    "discourse_markers": {"name": "Advanced discourse markers", "category": "functions", "cefr": "C1"},
}

TOPIC_LIST = ", ".join(TOPICS.keys())
