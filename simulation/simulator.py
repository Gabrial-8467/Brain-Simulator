import time

from simulation.environment import SyntheticEnvironment


class Simulator:
    def __init__(
        self,
        brain,
        tick_delay=0.1,
        environment=None,
        memory_manager=None,
        detailed_logs=True,
        output_file=None,
    ):
        self.brain = brain
        self.tick_delay = tick_delay
        self.running = False
        self.memory_manager = memory_manager
        self.detailed_logs = detailed_logs
        self.environment = environment or SyntheticEnvironment(
            deterministic=getattr(brain, "deterministic", False)
        )
        self.output_file = output_file
        self.file_handle = None
        if self.output_file:
            self.file_handle = open(self.output_file, "w")

    def _write(self, text=""):
        """Write output to file or stdout."""
        if self.file_handle:
            self.file_handle.write(str(text) + "\n")
            self.file_handle.flush()
        else:
            print(text)

    def close_output(self):
        """Close output file if open."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

    @staticmethod
    def _safe_round(value, digits=3):
        if isinstance(value, (int, float)):
            return round(float(value), digits)
        return value

    @staticmethod
    def _short_text(text, max_len=90):
        if text is None:
            return ""
        clean = str(text).strip().replace("\n", " ")
        if len(clean) <= max_len:
            return clean
        return clean[: max_len - 3] + "..."

    def _format_perception_line(self, event):
        scene = getattr(event, "scene", None) or {}
        novelty = self._safe_round(scene.get("novelty", 0.0), 2)
        salience = self._safe_round(scene.get("salience", 0.0), 2)
        return (
            f"[Perception:{event.modality}] category={event.category} "
            f"valence={self._safe_round(event.valence, 2)} "
            f"intensity={self._safe_round(event.intensity, 2)} "
            f"novelty={novelty} salience={salience} "
            f'content="{self._short_text(event.content, max_len=70)}"'
        )

    def _format_focus_line(self):
        focus = getattr(self.brain, "current_focus", None)
        if not focus:
            return "[Focus] none"
        return (
            f"[Focus] source={focus.source} "
            f"emotional={self._safe_round(focus.emotional_weight, 2)} "
            f"novelty={self._safe_round(focus.novelty, 2)} "
            f"relevance={self._safe_round(focus.relevance_to_goals, 2)} "
            f'content="{self._short_text(focus.content, max_len=90)}"'
        )

    def _format_decision_line(self, decision):
        if not decision:
            return "[Decision] none"

        action = decision.get("action")
        probabilities = decision.get("probabilities", {}) or {}
        top_choice = None
        if isinstance(probabilities, dict) and probabilities:
            top_choice = max(probabilities.items(), key=lambda kv: kv[1])

        if top_choice:
            return (
                f"[Decision] action={action} "
                f"top={top_choice[0]}@{self._safe_round(top_choice[1], 3)}"
            )
        return f"[Decision] action={action}"

    def _print_cycle_log(self, step, state, previous_state, decision, perceived_events):
        self._write(f"Step {step}")

        for event in perceived_events:
            self._write(self._format_perception_line(event))

        self._write(self._format_focus_line())

        dopamine = state.get("dopamine", 0.0)
        cortisol = state.get("cortisol", 0.0)
        oxytocin = state.get("oxytocin", 0.0)
        serotonin = state.get("serotonin", 0.0)

        d_delta = dopamine - previous_state.get("dopamine", dopamine)
        c_delta = cortisol - previous_state.get("cortisol", cortisol)
        o_delta = oxytocin - previous_state.get("oxytocin", oxytocin)
        s_delta = serotonin - previous_state.get("serotonin", serotonin)

        self._write(
            "[Chemistry] "
            f"dopamine={self._safe_round(dopamine)} ({self._safe_round(d_delta)}) "
            f"cortisol={self._safe_round(cortisol)} ({self._safe_round(c_delta)}) "
            f"oxytocin={self._safe_round(oxytocin)} ({self._safe_round(o_delta)}) "
            f"serotonin={self._safe_round(serotonin)} ({self._safe_round(s_delta)})"
        )

        identity = state.get("identity_traits", {}) or {}
        competence = identity.get("competence", state.get("identity_competence", 0.0))
        social_value = identity.get("social_value", state.get("identity_social_value", 0.0))
        resilience = identity.get("resilience", state.get("identity_resilience", 0.0))
        intelligence = identity.get("intelligence", state.get("identity_intelligence", 0.0))
        self._write(
            "[Identity] "
            f"competence={self._safe_round(competence, 4)} "
            f"social_value={self._safe_round(social_value, 4)} "
            f"resilience={self._safe_round(resilience, 4)} "
            f"intelligence={self._safe_round(intelligence, 4)}"
        )

        self._write(
            "[Development] "
            f"stage={state.get('development_stage')} "
            f"xp={self._safe_round(state.get('experience_points', 0.0), 2)} "
            f"maturity={self._safe_round(state.get('maturity', 0.0), 3)} "
            f"reflection_depth={self._safe_round(state.get('reflection_depth', 0.0), 3)} "
            f"wisdom={self._safe_round(state.get('wisdom', 0.0), 3)} "
            f"consciousness={self._safe_round(state.get('consciousness_score', 0.0), 3)}"
        )

        narrative = self._short_text(state.get("self_narrative", ""), max_len=110)
        self._write(f'[Narrative] "{narrative}"')
        mood_state = state.get("mood_state", {}) or {}
        if mood_state:
            self._write(
                "[Mood] "
                f"tone={mood_state.get('tone', 'neutral')} "
                f"valence={self._safe_round(mood_state.get('valence', 0.0), 3)} "
                f"arousal={self._safe_round(mood_state.get('arousal', 0.0), 3)}"
            )

        beliefs = state.get("beliefs", []) or []
        if beliefs:
            ranked_beliefs = sorted(
                [b for b in beliefs if isinstance(b, dict)],
                key=lambda b: (
                    float(b.get("confidence", 0.0)),
                    int(b.get("evidence_count", 0)),
                ),
                reverse=True,
            )[:2]
            if ranked_beliefs:
                belief_parts = []
                for belief in ranked_beliefs:
                    belief_parts.append(
                        f"{belief.get('statement', '')}@{self._safe_round(belief.get('confidence', 0.0), 3)}"
                    )
                self._write("[Beliefs] " + " | ".join(belief_parts))

        concept_count = len(state.get("concept_memory", {}) or {})
        recent_count = len(state.get("recent_perceptions", []) or [])
        autobiographical_count = len(state.get("autobiographical_memory", []) or [])
        self._write(
            "[Memory] "
            f"recent_perceptions={recent_count} "
            f"concepts={concept_count} "
            f"autobiographical_events={autobiographical_count}"
        )

        top_concepts = state.get("learned_concepts", []) or []
        if top_concepts:
            top_slice = top_concepts[:3]
            rendered = []
            for item in top_slice:
                concept = item.get("concept")
                count = item.get("count", 0)
                modalities = item.get("modalities", {})
                rendered.append(f"{concept}:{count}:{modalities}")
            self._write("[TopConcepts] " + " | ".join(rendered))

        decision_debug = state.get("decision_debug", {}) or {}
        if decision_debug:
            self._write(
                "[DecisionGate] "
                f"path={decision_debug.get('decision_path')} "
                f"engine={decision_debug.get('engine_available')} "
                f"focus={decision_debug.get('focus_present')} "
                f"emotional={decision_debug.get('focus_emotional_weight')} "
                f"threshold={decision_debug.get('emotional_threshold')} "
                f"hits10={decision_debug.get('high_emotion_hits_last_10')} "
                f"gate={decision_debug.get('gate_pass')} "
                f"forced={decision_debug.get('forced_fallback')} "
                f"beliefs={decision_debug.get('belief_count')} "
                f"shift={decision_debug.get('belief_shift')} "
                f"mood={decision_debug.get('mood_tone')}"
            )

        self._write(self._format_decision_line(decision))
        self._write("-" * 72)

    def run_scenario(self, scenario_events, steps=50):

        self._write("\n--- Simulation Start ---\n")
        previous_state = self.brain.get_state()

        try:
            for step in range(steps):
                # Feed one lived experience into perception each cycle.
                env_event = self.environment.generate_event()
                self.brain.perceive(env_event)
                # Feed sensory perception events into the same pipeline.
                vision_event = self.environment.generate_vision_event()
                self.brain.perceive(vision_event)
                hearing_event = self.environment.generate_hearing_event()
                self.brain.perceive(hearing_event)

                # Inject event if available
                if step < len(scenario_events):
                    event = scenario_events[step]
                    self.brain.inject_event(
                        effects=event.get("effects", {}),
                        event_type=event.get("event_type"),
                        source=event.get("source"),
                        tags=event.get("tags")
                    )

                decision = self.brain.tick()
                state = self.brain.get_state()
                if self.detailed_logs:
                    self._print_cycle_log(
                        step=step,
                        state=state,
                        previous_state=previous_state,
                        decision=decision,
                        perceived_events=[env_event, vision_event, hearing_event],
                    )
                else:
                    self._write(
                        "State: "
                        f"dopamine={round(state.get('dopamine', 0.0), 3)} "
                        f"cortisol={round(state.get('cortisol', 0.0), 3)} "
                        f"oxytocin={round(state.get('oxytocin', 0.0), 3)} "
                        f"serotonin={round(state.get('serotonin', 0.0), 3)} "
                        f"stage={state.get('development_stage')} "
                        f"consciousness_score={round(state.get('consciousness_score', 0.0), 3)}"
                    )

                previous_state = state

                if self.memory_manager and (step + 1) % 100 == 0:
                    self.memory_manager.save(self.brain.get_state())

                time.sleep(self.tick_delay)
        finally:
            if self.memory_manager:
                self.memory_manager.save(self.brain.get_state())
            self.close_output()

        self._write("\n--- Simulation End ---\n")
