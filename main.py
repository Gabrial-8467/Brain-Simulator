import argparse
import os
import sys
import yaml

from core.brain import VirtualBrain
from decision.decision_engine import DecisionEngine
from memory.memory_manager import MemoryManager
from simulation.simulator import Simulator
from simulation.scenarios import build_structured_learning_scenario
from utils.logger import BrainLogger


# =====================================================
# ARGUMENT PARSER
# =====================================================

def parse_arguments():
    parser = argparse.ArgumentParser(description="Virtual Brain Engine")

    parser.add_argument(
        "--mode",
        type=str,
        default="simulate",
        choices=["simulate", "live"],
        help="Run mode of the brain"
    )

    parser.add_argument(
        "--deterministic",
        action="store_true",
        help="Run without stochastic noise"
    )

    parser.add_argument(
        "--cycles",
        type=int,
        default=100,
        help="Number of simulation cycles"
    )

    return parser.parse_args()


# =====================================================
# LOAD CONFIG
# =====================================================

def load_chemical_config():
    with open("config/chemicals.yaml", "r") as f:
        return yaml.safe_load(f)


def load_decision_config():
    with open("config/decision.yaml", "r") as f:
        payload = yaml.safe_load(f) or {}
    return payload.get("decision", payload)


# =====================================================
# MAIN
# =====================================================

def main():
    args = parse_arguments()

    logger = BrainLogger()
    logger.info("Starting Virtual Brain...")
    memory_manager = MemoryManager(storage_path="memory_store.json")

    loaded_state = None
    if os.path.exists("memory_store.json"):
        payload = memory_manager.load()
        if isinstance(payload, dict):
            loaded_state = payload
            logger.info("Loaded persisted brain state from memory_store.json")
        else:
            logger.warning("memory_store.json exists but is not a brain state snapshot; starting fresh.")

    chemical_configs = load_chemical_config()
    decision_config = load_decision_config()
    decision_engine = DecisionEngine(
        decision_config=decision_config,
        deterministic=args.deterministic,
    )

    brain = VirtualBrain(
        chemical_configs=chemical_configs["chemicals"],
        interaction_matrix=chemical_configs.get("interactions"),
        decision_engine=decision_engine,
        deterministic=args.deterministic
    )
    if loaded_state:
        brain.set_state(loaded_state)

    # ================================
    # SIMULATION MODE
    # ================================
    if args.mode == "simulate":

        logger.info(
            f"Running structured learning simulation for {args.cycles} cycles"
        )

        simulator = Simulator(brain, memory_manager=memory_manager)
        scenario = build_structured_learning_scenario(args.cycles)

        simulator.run_scenario(
            scenario_events=scenario,
            steps=args.cycles
        )

    # ================================
    # BASIC LIVE DEBUG MODE
    # ================================
    elif args.mode == "live":

        logger.info("Running in basic live debug mode")
        run_live_debug(brain, memory_manager=memory_manager)
        memory_manager.save(brain.get_state())

    logger.info("Shutting down Virtual Brain.")


# =====================================================
# BASIC LIVE DEBUG (OLD STYLE)
# =====================================================

def run_live_debug(brain, memory_manager=None):

    print("Virtual Brain Debug Mode. Type 'exit' to quit.\n")

    while True:
        user_input = input(">> ")

        if user_input.lower() == "exit":
            break

        brain.tick()

        state = brain.get_state()
        print(f"Current State: {state}\n")

        if memory_manager:
            memory_manager.save(state)


# =====================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(0)
