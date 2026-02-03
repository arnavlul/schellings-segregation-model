import numpy as np
import random
from collections import deque
import os
import uuid

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider
import pygame 

GRID_SIZE = 1000
PROBABILITY_DISTRIBUTION = (0.2,0.4,0.4) # 0, 1, 2
THRESHOLD = 0.7
# Standard deviation should be less than 0.5% of total population
STABILITY_STD_THRESHOLD = 0.005*((PROBABILITY_DISTRIBUTION[1] + PROBABILITY_DISTRIBUTION[2])*(GRID_SIZE**2))
PATIENCE_COUNTER_LIMIT = 200

WINDOW_SIZE = 200
CELL_SIZE = int(WINDOW_SIZE / GRID_SIZE)
FPS = 24

WHITE = (255, 255, 255)
RED = (220, 50, 50) #220, 50, 50
BLUE = (50, 50, 220) #50, 50, 220
BG = (30, 30, 30)


def calculate_board_state(board: np.ndarray, threshold: float) -> (list[list[int]], list[list[int]]):
    
    unhappy: list[list[int]] = []
    unoccupied: list[list[int]] = []
    x_dir = [0,0,1,1,1,-1,-1,-1]
    y_dir = [1,-1,1,0,-1,1,0,-1]


    size = board.shape
    
    for x in range(size[0]):
        for y in range(size[1]):
            if(board[x,y] == 0): # Unoccupied Square
                unoccupied.append([x,y]) # Adding to unoccupied list
                continue 

            num_1 = 0
            num_2 = 0
            for i in range(8):
                nx = (x + x_dir[i]) % GRID_SIZE
                ny = (y + y_dir[i]) % GRID_SIZE

                if(board[nx,ny] == 1): num_1 += 1
                if(board[nx,ny] == 2): num_2 += 1

            total_neightbours = num_1 + num_2
            if(total_neightbours == 0): continue

            if(board[x,y] == 1): score = float(num_1) / (total_neightbours) # If square is 1
            else: score = float(num_2) / (total_neightbours) # If square is 2

            if(score <= threshold): unhappy.append([x,y]) # If score is less than threshold, add to unhappy list
            
    return unhappy, unoccupied

def next_pos(board: np.ndarray, unhappy: list[list[int]], unoccupied: list[list[int]]) -> np.ndarray:


    random.shuffle(unhappy)
    random.shuffle(unoccupied)

    limit = min(len(unhappy), len(unoccupied))

    for i in range(limit):
        oldx, oldy = unhappy[i]
        newx, newy = unoccupied[i]
        identity = board[oldx, oldy]

        board[newx, newy] = identity
        board[oldx, oldy] = 0
    
    return board

def similarity_index(board: np.ndarray) -> float:

    x_dir = [0,0,1,1,1,-1,-1,-1]
    y_dir = [1,-1,1,0,-1,1,0,-1]

    size = board.shape

    count = 0
    similarity_index = 0.0
    for x in range(size[0]):
        for y in range(size[1]):
            if board[x,y] == 0: continue

            one_count = 0
            two_count = 0
            for i in range(8):
                nx = (x + x_dir[i]) % GRID_SIZE
                ny = (y + y_dir[i]) % GRID_SIZE
                

                if(board[nx,ny] == 1): one_count += 1
                if(board[nx,ny] == 2): two_count += 1
            
            total = one_count + two_count
            if(total == 0): continue

            count += 1

            if(board[x,y] == 1):
                similarity = one_count / total
            else:
                similarity = two_count / total
            
            similarity_index += similarity
    
    if count == 0: return 0
    else: return round(similarity_index / count, 2)
    
def draw_board(screen, board):
    screen.fill(BG)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r,c] == 1:
                pygame.draw.rect(screen, RED, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif board[r,c] == 2:
                pygame.draw.rect(screen, BLUE, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.display.flip()


def main(input_threshold: float = THRESHOLD, visualise: bool=True) -> float:

    THRESHOLD = input_threshold
    board = np.random.choice([0,1,2], size=(GRID_SIZE, GRID_SIZE), p=PROBABILITY_DISTRIBUTION)
    initial_unhappy, _ = calculate_board_state(board, THRESHOLD)
    max_unhappy_agents = len(initial_unhappy)
    stability_window = deque(maxlen=50)

    current_fps = FPS if visualise else 0

    os.makedirs("state_pics", exist_ok=True)
    os.makedirs("state_graphs", exist_ok=True)

    if visualise:
        try:
            plt.switch_backend('TkAgg')
        except:
            plt.switch_backend('Qt5Agg')
    else:
        plt.switch_backend('Agg') # No window

    if not visualise:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    else:
        if "SDL_VIDEODRIVER" in os.environ:
            del os.environ["SDL_VIDEODRIVER"]
    
# Setting up matplotlib
    
    plt.ion()   
    fig = plt.figure(figsize=(7,8))

# Setting up top (unhappy people) graph 


    ax1 = fig.add_axes([0.20, 0.55, 0.70, 0.35])

    unhappy_history: list[int] = []

    line1, = ax1.plot([], [], 'r-', label='Unhappy Count')
    ax1.set_title("Unhappiness vs Segregation")
    ax1.set_xlabel("Time (Steps)")
    ax1.set_ylabel("Number of Unhappy People")
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right')

    ax1.set_ylim(0, max_unhappy_agents+50)
    ax1.set_xlim(0, 100)

# Setting up bottom (segregation %) graph
    ax2 = fig.add_axes([0.20, 0.10, 0.70, 0.35])

    segregation_history = []

    line2, = ax2.plot([], [], 'b-', label='Segregation Index')
    ax2.set_ylabel("Segregation (%)")
    ax2.set_xlabel("Time (Steps)")
    ax2.grid(True, linestyle='--', alpha = 0.5)
    ax2.legend(loc='lower right')

    ax2.set_ylim(0, 100)
    ax2.set_xlim(0, 100)

# Setting up sliders 

    if visualise:
        ax_slider_x = fig.add_axes([0.20, 0.48, 0.70, 0.03])
        slider_x = RangeSlider(ax_slider_x, "Time (Steps)", 0, 100, valinit=(0, 100))

        ax_slider_y = fig.add_axes([0.05, 0.55, 0.03, 0.35])
        slider_y = RangeSlider(ax_slider_y, "Unhappy Count", 0, max_unhappy_agents + 50, valinit=(0, max_unhappy_agents + 50), orientation="vertical")

        plt.show(block=False)

        tk_root = fig.canvas.manager.window
    
    else:
        slider_x = None
        slider_y = None
        tk_root = None

# Setting up Pygame

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption(f"Schelling's Model Simulation (T={input_threshold})")

    clock = pygame.time.Clock()
    running = True
    paused = False
    step = 0
    patience_counter = 0
    min_unhappy_reached = float('inf')

    if visualise:
        last_x_val = slider_x.val
        last_y_val = slider_y.val
    else:
        last_x_val = (0, 100)
        last_y_val = (0, 0)


    while(running):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN: # Pause on pressing space
                if event.key == pygame.K_SPACE:
                    paused = not paused

                    if paused:
                        pygame.display.set_caption("Schelling's Model Simulation (Paused)")
                    else:
                        pygame.display.set_caption("Schelling's Model Simulation (Running)")

        if visualise and tk_root:
            try:
                tk_root.update()
            except:
                pass

        

    # Events to only do when unpaused    
        if not paused:
            unhappy, unoccupied = calculate_board_state(board, THRESHOLD)
            unhappy_history.append(len(unhappy))

            segregation_percentage = similarity_index(board) * 100
            segregation_history.append(segregation_percentage)

            if len(unhappy) > 0:
                board = next_pos(board, unhappy, unoccupied)


            stability_window.append(len(unhappy))
            if(len(stability_window) == stability_window.maxlen):
                current_std = np.std(stability_window)
                if(current_std < STABILITY_STD_THRESHOLD): 
                    print(f"T={input_threshold}: Equilibrium Reached")

                    if not visualise:
                        draw_board(screen, board)

                    suffix = f"_{uuid.uuid4().hex[:6]}"

                    pygame.display.set_caption("Schelling's Model (Equilirbium Reached)")
                    pygame.image.save(screen, f"state_pics/sm_pic_{THRESHOLD}{suffix}.png")
                    fig.savefig(f"state_graphs/sm_graph_{THRESHOLD}{suffix}.png")
                    paused = True
                    
                    if(__name__ != "__main__"):
                        break

            
            if(len(unhappy) < min_unhappy_reached):
                min_unhappy_reached = len(unhappy)
                patience_counter = 0
            else:
                patience_counter += 1
            
            if(patience_counter >= PATIENCE_COUNTER_LIMIT):
                print(f"T={input_threshold}: Patience limit reached")

                if not visualise:
                    draw_board(screen, board)

                suffix = f"_{uuid.uuid4().hex[:6]}"

                pygame.display.set_caption("Schelling's Model (Patience Limit Reached)")
                pygame.image.save(screen, f"state_pics/sm_pic_{THRESHOLD}{suffix}.png")
                fig.savefig(f"state_graphs/sm_graph_{THRESHOLD}{suffix}.png")
                paused = True
                
                if(__name__ != "__main__"):
                    break

            
            line1.set_xdata(range(len(unhappy_history)))
            line1.set_ydata(unhappy_history)

            line2.set_xdata(range(len(segregation_history)))
            line2.set_ydata(segregation_history)

            if visualise and step > slider_x.valmax:
                slider_x.valmax = step + 10
                slider_x.ax.set_xlim(slider_x.valmin, slider_x.valmax)
            
            step +=1

    # Events to always do (irrespective of if paused or not)
        
        if visualise:    
            screen.fill(BG)

            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if(board[r,c] == 1):
                        pygame.draw.rect(screen, RED, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    elif(board[r,c] == 2):
                        pygame.draw.rect(screen, BLUE, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
            pygame.display.flip()

            current_x_val = slider_x.val
            current_y_val = slider_y.val

            sliders_moved = (current_x_val != last_x_val) or (current_y_val != last_y_val)

            running_update = not paused and step % 5 == 0

            should_redraw = sliders_moved or running_update

            if should_redraw:
                x_min, x_max = slider_x.val
                y_min, y_max = slider_y.val

                ax1.set_xlim(x_min, x_max)
                ax1.set_ylim(y_min, y_max)
                
                ax2.set_xlim(x_min, x_max)
                ax2.set_ylim(0, 100)

                fig.canvas.draw()
        
        clock.tick(current_fps)

    pygame.quit()
    plt.ioff()
    if(__name__ == "__main__"):
        plt.show()
    else:
        plt.close()

    return segregation_history[-1]


if __name__ == "__main__":
    main()