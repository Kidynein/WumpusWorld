import pygame
import time
import os
from environment import WumpusWorld
from agent import HybridAgent, RandomAgent
from gui import GUI, GameMode
from enum import Enum
from movingwumpus import MovingWumpusModule


os.environ['SDL_VIDEO_CENTERED'] = '1'
def main():
    pygame.init()
    screen = pygame.display.set_mode((480, 360))
    pygame.display.set_caption("Wumpus World")

    global world_size, k, pit_prob
    world_size, k, pit_prob = get_user_config(screen)

    seed = 195

    world, agent, ui = _initialize_game(seed)

    auto_move_timer = 0
    auto_move_delay = 100  # milliseconds
    agent_action_count = 0
    moving_module = MovingWumpusModule(world)
    print(f"Seed: {seed}")
    print("Controls: Click buttons or use keyboard - SPACE (step)")
    
    running = True
    game_over = False

    while running:
        dt = ui.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = ui.handle_button_click(event.pos)
                if action == "reset_game":
                    world, agent, ui = _reset_game(world.seed, ui)
                    agent_action_count = 0
                    moving_module = MovingWumpusModule(world)
                    game_over = False
                    print("Game reset!")
                elif action == "new_seed":
                    new_seed = int(time.time()) % 1000
                    world_size = int(time.time()) % 10 + 4
                    world, agent, ui = _reset_game(new_seed, ui)
                    agent_action_count = 0
                    moving_module = MovingWumpusModule(world)
                    game_over = False
                    print(f"New game with seed: {new_seed}")
                elif action == "switch_agent":
                    if ui.agent_type == "Hybrid":
                        agent = HybridAgent(world.grid_size)
                    else:
                        agent = RandomAgent()
                    ui._update(world, agent)
                    print(f"Switched to {ui.agent_type} agent.")


            elif game_over:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    choice = ui.handle_game_over_click(event.pos)
                    if choice == "reset_game":
                        world, agent, ui = _reset_game(world.seed, ui)
                        game_over = False
                        agent_action_count = 0
                        moving_module = MovingWumpusModule(world)
                        print("Game reset!")
                    elif choice == "new_seed":
                        new_seed = int(time.time()) % 1000
                        world, agent, ui = _reset_game(new_seed, ui)
                        game_over = False
                        agent_action_count = 0
                        moving_module = MovingWumpusModule(world)
                        print(f"New game with seed: {new_seed}")
            elif event.type == pygame.KEYDOWN:
                if ui.mode == GameMode.STEP and event.key == pygame.K_SPACE:
                    if world.is_game_over(agent) == "continue":
                        agent.update_knowledge(world.agent_pos, world.percepts, world)
                        action = agent.plan_next_action(world.agent_pos, world.agent_dir, world)
                        _execute_action(world, action)
                        agent_action_count += 1
                        print(f"Executed action: {action}")
                    if agent_action_count % 5 == 0 and ui.ADVANCE_MODE:
                        moving_module.update(world, ui, agent)
        if ui.mode == GameMode.AUTO and world.is_game_over(agent) == "continue":
            auto_move_timer += dt
            if auto_move_timer >= auto_move_delay:
                agent.update_knowledge(world.agent_pos, world.percepts, world)
                action = agent.plan_next_action(world.agent_pos, world.agent_dir, world)
                _execute_action(world, action)
                agent_action_count += 1
                auto_move_timer = 0
            if agent_action_count % 5 == 0 and ui.ADVANCE_MODE:
                moving_module.update(world, ui, agent)
        state = world.is_game_over(agent)
        if state != "continue" and not game_over:
            game_over = True

        ui.render()

    pygame.quit()


def _initialize_game(seed):
    world = WumpusWorld(world_size, k, pit_prob, seed=seed)
    agent = HybridAgent(world.grid_size)
    ui = GUI(world, agent)
    return world, agent, ui


def _reset_game(seed, ui):
    world = WumpusWorld(world_size, k, pit_prob, seed=seed)
    if ui.agent_type == "Hybrid":
        agent = HybridAgent(world.grid_size)
    else:
        agent = RandomAgent()
    ui._update(world, agent)
    return world, agent, ui

def _execute_action(world, action):
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
    elif action == "climb":
        world.climb_out()
    # else: wait or unknown actions => do nothing


def get_user_config(screen):
    font = pygame.font.SysFont(None, 28)
    input_boxes = [
        {"label": "Map Size (4-20):", "value": "", "rect": pygame.Rect(250, 100, 100, 32), "type": int, "min": 4, "max": 100},
        {"label": "Wumpus Count:", "value": "", "rect": pygame.Rect(250, 150, 100, 32), "type": int, "min": 1, "max": 10},
        {"label": "Pit Probability (0-1):", "value": "", "rect": pygame.Rect(250, 200, 100, 32), "type": float, "min": 0.0, "max": 1.0},
    ]
    active_box = None
    clock = pygame.time.Clock()

    ok_button = pygame.Rect(180, 270, 80, 30)
    cancel_button = pygame.Rect(280, 270, 80, 30)

    while True:
        screen.fill((30, 30, 30))

        for i, box in enumerate(input_boxes):
            label_surface = font.render(box["label"], True, (255, 255, 255))
            screen.blit(label_surface, (50, box["rect"].y + 5))
            pygame.draw.rect(screen, (255, 255, 255), box["rect"], 2)
            value_surface = font.render(box["value"], True, (255, 255, 255))
            screen.blit(value_surface, (box["rect"].x + 5, box["rect"].y + 5))

        pygame.draw.rect(screen, (100, 255, 100), ok_button)
        pygame.draw.rect(screen, (255, 100, 100), cancel_button)
        screen.blit(font.render("OK", True, (0, 0, 0)), (ok_button.x + 25, ok_button.y + 5))
        screen.blit(font.render("Default", True, (0, 0, 0)), (cancel_button.x + 10, cancel_button.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ok_button.collidepoint(event.pos):
                    try:
                        results = []
                        for box in input_boxes:
                            value = box["type"](box["value"])
                            if not (box["min"] <= value <= box["max"]):
                                raise ValueError
                            results.append(value)
                        return results
                    except:
                        print("Invalid input. Please try again.")

                elif cancel_button.collidepoint(event.pos):
                    return 8, 2, 0.2

                for i, box in enumerate(input_boxes):
                    if box["rect"].collidepoint(event.pos):
                        active_box = i

            elif event.type == pygame.KEYDOWN and active_box is not None:
                box = input_boxes[active_box]
                if event.key == pygame.K_RETURN:
                    active_box = None
                elif event.key == pygame.K_BACKSPACE:
                    box["value"] = box["value"][:-1]
                else:
                    box["value"] += event.unicode

        clock.tick(30)


if __name__ == "__main__":
    main()
