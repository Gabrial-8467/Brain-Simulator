import argparse
import sys
import yaml

from core.brain import VirtualBrain
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


# =====================================================
# MAIN
# =====================================================

def main():
    args = parse_arguments()

    logger = BrainLogger()
    logger.info("Starting Virtual Brain...")

    chemical_configs = load_chemical_config()

    brain = VirtualBrain(
        chemical_configs=chemical_configs["chemicals"],
        interaction_matrix=chemical_configs.get("interactions"),
        deterministic=args.deterministic
    )

    # ================================
    # SIMULATION MODE
    # ================================
    if args.mode == "simulate":

        logger.info(
            f"Running structured learning simulation for {args.cycles} cycles"
        )

        simulator = Simulator(brain)
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
        run_live_debug(brain)

    logger.info("Shutting down Virtual Brain.")


# =====================================================
# BASIC LIVE DEBUG (OLD STYLE)
# =====================================================

def run_live_debug(brain):

    print("Virtual Brain Debug Mode. Type 'exit' to quit.\n")

    while True:
        user_input = input(">> ")

        if user_input.lower() == "exit":
            break

        brain.tick()

        state = brain.get_state()
        print(f"Current State: {state}\n")


# =====================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(0)
