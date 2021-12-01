from dataclasses import dataclass
from typing import List

Muscle = str
Seconds = int
Kg = int


@dataclass
class Exercise:
    name: str
    reps: int
    series: int
    rest: Seconds
    target_muscles: List[Muscle]

    def to_str(self) -> str:
        raise NotImplementedError()

    def _format_rest(self) -> str:
        return f'    # {self.rest}"'

    def _format_muscles(self) -> str:
        muscles = ", ".join(self.target_muscles)
        return f"    # {muscles}"


@dataclass
class MachineExercise(Exercise):
    weight: Kg

    def to_str(self) -> str:
        lines = [
            self.name,
            f"  {self.weight}kg {self.reps}r {self.series}",
        ]

        if self.rest:
            lines.append(self._format_rest())

        if self.target_muscles:
            lines.append(self._format_muscles())

        return "\n".join(lines)


@dataclass
class BodyweightExercise(Exercise):
    reps: int

    def to_str(self) -> str:
        lines = [
            self.name,
            f"  wb {self.reps}r {self.series}",
        ]

        if self.rest:
            lines.append(self._format_rest())

        if self.target_muscles:
            lines.append(self._format_muscles())

        return "\n".join(lines)


class Muscles(object):
    abs = "abdominals"
    biceps = "biceps"
    glutes = "glutes"
    glutes = "glutes"
    hamstrings = "hamstrings"
    lats = "lats"
    lower_back = "lower_back"
    middle_delt = "middle delt"
    pectoral = "pectoral"
    read_delt = "rear delt"
    triceps = "triceps"
    upper_back = "upper back"


MACHINE_EXERCISES = [
    MachineExercise(
        name="lat pulldown",
        weight=32,
        reps=10,
        series=3,
        rest=30,
        target_muscles=[Muscles.lats, Muscles.biceps],
    ),
    MachineExercise(
        name="standing cable pull triceps",
        weight=14,
        reps=10,
        series=3,
        rest=30,
        target_muscles=[
            Muscles.triceps,
            Muscles.lats,
            Muscles.upper_back,
            Muscles.read_delt,
        ],
    ),
    MachineExercise(
        name="seated cable row",
        weight=27,
        reps=10,
        series=3,
        rest=30,
        target_muscles=[Muscles.upper_back, Muscles.biceps],
    ),
    MachineExercise(
        name="lateral raise machine",
        weight=32,
        reps=10,
        series=3,
        rest=30,
        target_muscles=[Muscles.middle_delt],
    ),
    MachineExercise(
        name="pect fly machine",
        weight=52,
        reps=10,
        series=2,
        rest=30,
        target_muscles=[Muscles.pectoral],
    ),
    MachineExercise(
        name="assisted dip",
        weight=27,
        reps=10,
        series=3,
        rest=30,
        target_muscles=[Muscles.triceps, Muscles.pectoral],
    ),
    MachineExercise(
        name="seated hip abduction",
        weight=39,
        reps=10,
        series=3,
        rest=30,
        target_muscles=[Muscles.glutes],
    ),
    MachineExercise(
        name="arm curl machine",
        weight=18,
        reps=10,
        series=3,
        rest=30,
        target_muscles=[Muscles.biceps],
    ),
]

BODYWEIGHT_EXERCISES = [
    BodyweightExercise(
        name="back raises with body weight",
        reps=10,
        series=3,
        rest=30,
        target_muscles=[Muscles.glutes, Muscles.lower_back, Muscles.hamstrings],
    ),
    BodyweightExercise(
        name="abs", reps=15, series=3, rest=30, target_muscles=[Muscles.abs]
    ),
    BodyweightExercise(
        name="superman",
        reps=15,
        series=3,
        rest=30,
        target_muscles=[Muscles.upper_back, Muscles.read_delt],
    ),
]

AVAILABLE_EXERCISES = [*MACHINE_EXERCISES, *BODYWEIGHT_EXERCISES]
