import math
from collections import defaultdict
from typing import Dict, List


class SimilarityEngine:

    def __init__(self):

        # event_type → list of stored experience profiles
        self.event_profiles = defaultdict(list)

        # controls
        self.max_profiles_per_event = 300
        self.similarity_threshold = 0.4
        self.identity_weight = 0.6
        self.chemical_weight = 0.4

    # -------------------------------------------------
    # RECORD EXPERIENCE
    # -------------------------------------------------

    def record_event_profile(
        self,
        event_type: str,
        chemical_delta: Dict[str, float],
        identity_snapshot: Dict[str, float]
    ):

        profile = {
            "chemicals": chemical_delta.copy(),
            "identity": identity_snapshot.copy()
        }

        self.event_profiles[event_type].append(profile)

        # bounded memory
        if len(self.event_profiles[event_type]) > self.max_profiles_per_event:
            self.event_profiles[event_type].pop(0)

    # -------------------------------------------------
    # SIMILARITY CALCULATION
    # -------------------------------------------------

    def _vector_distance(self, v1: Dict[str, float], v2: Dict[str, float]):

        keys = set(v1.keys()).union(v2.keys())

        total = 0.0
        for k in keys:
            total += (v1.get(k, 0) - v2.get(k, 0)) ** 2

        return math.sqrt(total)

    def _compute_similarity(self, profile, current_state):

        chemical_state = {
            k: current_state.get(k, 0)
            for k in profile["chemicals"].keys()
        }

        identity_state = {
            k: current_state.get(f"identity_{k}", 0)
            for k in profile["identity"].keys()
        }

        chem_dist = self._vector_distance(
            chemical_state,
            profile["chemicals"]
        )

        id_dist = self._vector_distance(
            identity_state,
            profile["identity"]
        )

        # Convert distance to similarity (inverse scaling)
        chem_sim = 1 / (1 + chem_dist)
        id_sim = 1 / (1 + id_dist)

        similarity = (
            chem_sim * self.chemical_weight +
            id_sim * self.identity_weight
        )

        return similarity

    # -------------------------------------------------
    # FIND SIMILAR EXPERIENCES
    # -------------------------------------------------

    def find_similar_profiles(
        self,
        event_type: str,
        current_state: Dict[str, float],
        top_k: int = 5
    ) -> List[Dict]:

        profiles = self.event_profiles.get(event_type, [])

        if not profiles:
            return []

        scored = []

        for profile in profiles:
            sim = self._compute_similarity(profile, current_state)

            if sim >= self.similarity_threshold:
                scored.append((sim, profile))

        # sort by similarity descending
        scored.sort(key=lambda x: x[0], reverse=True)

        return [p for _, p in scored[:top_k]]

    # -------------------------------------------------
    # BLEND EMOTIONAL EXPECTATION
    # -------------------------------------------------

    def blended_emotional_prediction(
        self,
        event_type: str,
        current_state: Dict[str, float]
    ) -> Dict[str, float]:

        similar = self.find_similar_profiles(
            event_type,
            current_state
        )

        if not similar:
            return {}

        blended = defaultdict(float)
        total_weight = 0

        for profile in similar:

            sim = self._compute_similarity(profile, current_state)

            for chem, value in profile["chemicals"].items():
                blended[chem] += value * sim

            total_weight += sim

        if total_weight == 0:
            return {}

        for chem in blended:
            blended[chem] /= total_weight

        return dict(blended)

    # -------------------------------------------------
    # CONFIDENCE ESTIMATION
    # -------------------------------------------------

    def get_event_confidence(self, event_type: str):

        count = len(self.event_profiles.get(event_type, []))

        return min(1.0, count / 50.0)

    # -------------------------------------------------
    # DEBUG
    # -------------------------------------------------

    def get_memory_snapshot(self):

        return {
            event: len(profiles)
            for event, profiles in self.event_profiles.items()
        }
