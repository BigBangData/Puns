import os
import statistics

os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('SECRET_KEY', 'test-secret')

from app import (
    CONFETTI_MAX_GAP,
    CONFETTI_MIN_GAP,
    animal_dict,
    build_confetti_schedule,
    get_confetti_go_list,
)


def test_confetti_schedule_has_guardrails():
    schedule = build_confetti_schedule(10000)
    events = sorted(schedule.items())

    assert events
    assert len(events) > 150

    gaps = [events[0][0]]
    gaps.extend(
        vote - previous_vote
        for (previous_vote, _), (vote, _) in zip(events, events[1:])
    )
    previous_animal = None
    for vote, animal in events:
        assert animal != previous_animal
        previous_animal = animal

    assert min(gaps) == CONFETTI_MIN_GAP
    assert max(gaps) == CONFETTI_MAX_GAP
    assert abs(statistics.mean(gaps) - 5) < 0.15


def test_confetti_go_list_handles_long_sequence_without_repeats():
    last_animal = None
    observed_events = []

    for total_votes in range(1, 1000):
        go_list = get_confetti_go_list(total_votes, animal_dict)
        active_animals = [
            animal
            for animal, is_go in zip(animal_dict.keys(), go_list)
            if is_go
        ]

        assert len(active_animals) <= 1

        if active_animals:
            animal = active_animals[0]
            if last_animal is not None:
                assert animal != last_animal
            last_animal = animal
            observed_events.append((total_votes, animal))

    assert observed_events
    gaps = [observed_events[0][0]]
    gaps.extend(
        next_vote - vote
        for (vote, _), (next_vote, _) in zip(observed_events, observed_events[1:])
    )
    assert min(gaps) >= CONFETTI_MIN_GAP
    assert max(gaps) <= CONFETTI_MAX_GAP


def test_confetti_schedule_runs_past_300_ratings():
    for total_votes in [300, 301, 500, 1000, 2500]:
        go_list = get_confetti_go_list(total_votes, animal_dict)
        active_animals = [
            animal
            for animal, is_go in zip(animal_dict.keys(), go_list)
            if is_go
        ]
        assert len(active_animals) <= 1
