import pygame
import time
from environment import WumpusWorld
from agent import HybridAgent
from gui import WumpusWorldUI
from gui import GameMode
from enum import Enum

def main():
    # Initialize game with a specific seed for reproducibility
    seed = 36
    world, agent, ui = _initialize_game(seed)

    auto_move_timer = 0
    auto_move_delay = 100  # milliseconds

    print(f"Game initialized with seed: {seed}")
    print("Enhanced features: Warning cells (⚠️), Danger cells (🚫), Risky pathfinding")
    print("Controls: Click buttons or use keyboard - SPACE (step), R (reset)")

    running = True
    game_over = False

    while running:
        dt = ui.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Handle button clicks
                action = ui.handle_button_click(event.pos)
                if action == "reset_game":
                    world, agent, ui = _reset_game(world.seed, ui)
                    print("Game reset!")
                elif action == "new_seed":
                    new_seed = int(time.time()) % 1000
                    world, agent, ui = _reset_game(new_seed, ui)
                    print(f"New game with seed: {new_seed}")

            elif game_over:
                # Only handle popup interaction
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    choice = ui.handle_game_over_click(event.pos)
                    if choice == "reset_game":
                        world, agent, ui = _reset_game(world.seed, ui)
                        game_over = False
                        print("Game reset!")
                    elif choice == "new_seed":
                        new_seed = int(time.time()) % 1000
                        world, agent, ui = _reset_game(new_seed, ui)
                        game_over = False
                        print(f"New game with seed: {new_seed}")
                continue

            elif event.type == pygame.KEYDOWN:
                if ui.mode == GameMode.STEP and event.key == pygame.K_SPACE:
                    if world.is_game_over() == "continue":
                        agent.update_knowledge(world.agent_pos, world.percepts, world)
                        action = agent.plan_next_action(world.agent_pos, world.agent_dir, world)
                        _execute_action(world, action)
                        print(f"Executed action: {action}")

        # AUTO mode: periodically generate and execute actions
        if ui.mode == GameMode.AUTO and world.is_game_over() == "continue":
            auto_move_timer += dt
            if auto_move_timer >= auto_move_delay:
                agent.update_knowledge(world.agent_pos, world.percepts, world)
                action = agent.plan_next_action(world.agent_pos, world.agent_dir, world)
                _execute_action(world, action)
                auto_move_timer = 0

        # Check and report game-over state
        state = world.is_game_over()
        if state != "continue" and not game_over:
            game_over = True
            if state == "win":
                print("🎉 VICTORY! Agent collected gold and returned to start!")
            else:
                print("💀 GAME OVER! Agent fell into a pit or was eaten by the Wumpus!")

        ui.render()

    pygame.quit()


def _initialize_game(seed):
    """Create a new world, agent, and UI given a seed."""
    world = WumpusWorld(seed=seed)
    agent = HybridAgent(world.grid_size)
    ui = WumpusWorldUI(world, agent)
    return world, agent, ui


def _reset_game(seed, ui):
    """Reset world and agent inside the existing UI, using the given seed."""
    world = WumpusWorld(seed=seed)
    agent = HybridAgent(world.grid_size)
    ui.world = world
    ui.agent = agent
    return world, agent, ui

def _execute_action(world, action):
    """Execute the given action string on the world."""
    if action == "move_forward":
        world.move_forward()
    elif action == "turn_left":
        world.turn_left()
    elif action == "turn_right":
        world.turn_right()
    elif action == "grab":
        world.grab_gold()
    elif action == "shoot":
        world.shoot_arrow()
    # 'wait' or unrecognized actions do nothing


if __name__ == "__main__":
    main()
