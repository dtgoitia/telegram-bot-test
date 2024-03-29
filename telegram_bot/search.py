import itertools
import logging
from typing import Dict, FrozenSet, List

from telegram_bot.exercises import Exercise

logger = logging.getLogger(__name__)

Utterance = str
_ExerciseIndex = Dict[Utterance, List[Exercise]]


def _index_exercises(exercises: List[Exercise]) -> _ExerciseIndex:
    logger.debug(f"Indexing exercises: {exercises}")
    utterances_to_exercise_map: Dict[FrozenSet[Utterance], Exercise] = {}
    for exercise in exercises:
        utterances: FrozenSet[Utterance] = frozenset()

        name_and_muscles = (exercise.name, *exercise.target_muscles)
        words = (word.split(" ") for word in name_and_muscles)
        clean_words = {word.strip() for word in itertools.chain.from_iterable(words)}
        utterances = utterances.union(clean_words)

        for word in clean_words:
            word_chunk = ""
            for character in word:
                word_chunk += character
                utterances = utterances.union({word_chunk})

        logger.debug(f"Exercise {exercise.name} indexed for: {utterances!r}")
        utterances_to_exercise_map[utterances] = exercise

    index: _ExerciseIndex = {}
    for utterances, exercise in utterances_to_exercise_map.items():
        for utterance in utterances:
            indexed_exercises = index.get(utterance, [])
            index[utterance] = [*indexed_exercises, exercise]

    return index


class ExerciseIndex:
    def __init__(self, exercises: List[Exercise]) -> None:
        self._exercises = exercises
        self._index = _index_exercises(exercises)

    def query(self, query: str) -> List[Exercise]:
        logger.debug(f"Querying {ExerciseIndex.__name__} with {query!r}")
        results = self._index.get(query, [])
        logger.debug(f"Results: {results}")
        return results
