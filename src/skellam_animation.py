"""Animations for the presentation: why Skellam (1951) predicts a constant spread speed.

Three scenes on a square grid (scene 3 also without the walking-only line), each saved as its own video, with the radius of the explored
area plotted alongside:

1. One bird doing a random walk (each step to a random neighbouring square, or staying put),
   path drawn.
2. Many birds walking, no breeding: together they explore a circle, but its radius grows
   like the square root of time, so the spread slows down.
3. Birds that walk and breed (logistic growth up to K birds per square): the circle grows
   at a constant speed, c = 2 sqrt(rD), as in Skellam (1951).

Colours follow the map animation in 03_yearly-range. Scenes 1 and 2: visited squares light green,
the birds themselves dark green. Scene 3: dark green = birds in the square now, light green = visited
earlier. The dashed circle has the same area as the explored squares and
is centred on their centre (the population drifts by chance, so this is not exactly the
release point).

Output in figures/: skellam_1_one_bird.mp4, skellam_2_walking.mp4, skellam_3_breeding.mp4,
skellam_3_breeding_alone.mp4
(1920 x 1080, for slides) and the last frame of each as .png.
Run from the project root: python src/skellam_animation.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap

import plot_style  # colours (the script lives in src/, next to plot_style.py)
from matplotlib.lines import Line2D
from matplotlib.markers import MarkerStyle
from matplotlib.patches import Patch
from matplotlib.path import Path as MPath
from matplotlib.transforms import Affine2D

FIGURES = Path(__file__).resolve().parent.parent / "figures"
SEED = 7

# Simulation
HALF = 60              # grid runs from -HALF to HALF in both directions
STEPS = 150            # time steps in scenes 2 and 3
SINGLE_STEPS = 120     # time steps in scene 1
N_WALKERS = 150        # birds in scene 2
N_FOUNDERS = 4         # birds released at the start of scene 3
BIRTH_RATE = 0.20      # r: chance per step that a bird breeds, in an empty square
CAPACITY = 5           # K: birds per square at which breeding stops
# Each step: stay, or move to one of the 4 neighbours. Staying put sometimes avoids a grid artefact:
# with moves only, all birds stand on the same colour of a chessboard at any one time.
MOVES = np.array([[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1]])

# Animation
FPS = 20
START_FRAMES = FPS // 2  # pause on the first frame
HOLD_FRAMES = 3 * FPS    # pause on the last frame

# Colours: squares as in the 03_yearly-range map animation; curves from the project palette
NOW = plot_style.PRIMARY_DARK         # birds in the square now
EARLIER = plot_style.PRIMARY_LIGHT     # visited earlier
WALK_ONLY = plot_style.SECONDARY       # walking only
WALK_BREED = plot_style.PRIMARY_DARK   # walking and breeding
TEXT, MUTED, GRID = plot_style.TEXT, plot_style.MUTED, plot_style.GRID
BACKGROUND = "#fcfcfb"
SQUARE_CMAP = ListedColormap([EARLIER, NOW])  # 0 = earlier, 1 = now

# A small parakeet silhouette facing right (long tail), used as a marker
BIRD_PATH = MPath([
    (-1.00, -0.18), (-0.40, -0.06), (-0.15, -0.28), (0.20, -0.26), (0.42, -0.05),
    (0.62, -0.02), (0.50, 0.10), (0.40, 0.26), (0.18, 0.24), (-0.10, 0.12),
    (-0.40, 0.04), (-1.00, -0.08), (-1.00, -0.18),
])


def bird_marker(facing_left):
    """Bird marker, facing right or left."""
    return MarkerStyle(BIRD_PATH, transform=Affine2D().scale(-1 if facing_left else 1, 1))


def grid_of(positions):
    """Boolean grid with True where at least one position falls."""
    g = np.zeros((2 * HALF + 1, 2 * HALF + 1), bool)
    g[positions[:, 1] + HALF, positions[:, 0] + HALF] = True
    return g


YY, XX = np.mgrid[-HALF:HALF + 1, -HALF:HALF + 1]


def circle_of(explored):
    """Centre and radius of the circle with the same area and centre as the explored squares."""
    return XX[explored].mean(), YY[explored].mean(), np.sqrt(explored.sum() / np.pi)


# --- Simulations ------------------------------------------------------------------------
# Same random sequence as before, so the walks look the same

rng = np.random.default_rng(SEED)

# Scene 1: one bird
single_steps = MOVES[rng.integers(0, len(MOVES), SINGLE_STEPS)]
single = np.vstack([[0, 0], np.cumsum(single_steps, axis=0)])
SINGLE_LIMIT = max(12, int(np.abs(single).max()) + 2)  # map half-width for scene 1
facing_left = [False]  # turn the bird with its last sideways move
for dx in single_steps[:, 0]:
    facing_left.append(facing_left[-1] if dx == 0 else dx < 0)

# Scene 2: many birds, walking only
walk_steps = MOVES[rng.integers(0, len(MOVES), (STEPS, N_WALKERS))]
walkers = np.concatenate([np.zeros((1, N_WALKERS, 2), int), np.cumsum(walk_steps, axis=0)])
walkers = np.clip(walkers, -HALF, HALF)
walk_now = np.array([grid_of(walkers[t]) for t in range(STEPS + 1)])
walk_explored = np.logical_or.accumulate(walk_now, axis=0)
walk_circle = np.array([circle_of(e) for e in walk_explored])

# Scene 3: walking and breeding (each square holds up to CAPACITY birds)
birds = np.zeros((N_FOUNDERS, 2), int)
breed_birds = [birds.copy()]
for t in range(1, STEPS + 1):
    birds = np.clip(birds + MOVES[rng.integers(0, len(MOVES), len(birds))], -HALF, HALF)
    counts = np.zeros((2 * HALF + 1, 2 * HALF + 1))
    np.add.at(counts, (birds[:, 1] + HALF, birds[:, 0] + HALF), 1)
    crowding = counts[birds[:, 1] + HALF, birds[:, 0] + HALF] / CAPACITY
    breeds = rng.random(len(birds)) < BIRTH_RATE * np.clip(1 - crowding, 0, None)
    birds = np.vstack([birds, birds[breeds]])
    breed_birds.append(birds.copy())
breed_now = np.array([grid_of(b) for b in breed_birds])
breed_explored = np.logical_or.accumulate(breed_now, axis=0)
breed_circle = np.array([circle_of(e) for e in breed_explored])

D = 0.2  # diffusion coefficient of the walk: mean squared distance per step 4D = 4/5
print(f"Scene 3: {len(birds):,} birds at the end; Skellam speed 2 sqrt(rD) = {2 * np.sqrt(BIRTH_RATE * D):.2f} "
      f"squares/step, simulated (radius 75 -> 150 steps) = "
      f"{(breed_circle[150, 2] - breed_circle[75, 2]) / 75:.2f}")

# --- Drawing ------------------------------------------------------------------------------

plt.rcParams.update({"font.size": 18, "text.color": TEXT, "axes.labelcolor": TEXT,
                     "xtick.color": MUTED, "ytick.color": MUTED})
EXTENT = (-HALF - 0.5, HALF + 0.5, -HALF - 0.5, HALF + 0.5)


def new_figure():
    fig = plt.figure(figsize=(12.8, 7.2), dpi=150, facecolor=BACKGROUND)
    ax_map = fig.add_axes([0.03, 0.05, 0.50, 0.90])  # centre at half height
    ax_r = fig.add_axes([0.62, 0.20, 0.34, 0.60])    # same vertical centre as the map
    return fig, ax_map, ax_r


def setup_map(ax, limit, cell_grid):
    ax.clear()
    ax.set_facecolor(BACKGROUND)
    ax.set_xlim(-limit - 0.5, limit + 0.5)
    ax.set_ylim(-limit - 0.5, limit + 0.5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_color(GRID)
    if cell_grid:
        for v in np.arange(-limit - 0.5, limit + 1):
            ax.axhline(v, color=GRID, linewidth=0.6, zorder=0)
            ax.axvline(v, color=GRID, linewidth=0.6, zorder=0)


def draw_squares(ax, now, explored):
    """Dark: birds here now. Light: visited earlier, no birds now."""
    image = np.where(now, 1.0, np.where(explored, 0.0, np.nan))
    ax.imshow(image, extent=EXTENT, origin="lower", cmap=SQUARE_CMAP, vmin=0, vmax=1,
              interpolation="nearest", zorder=1)
    ax.legend(handles=[Patch(color=NOW, label="Birds here now"), Patch(color=EARLIER, label="Visited earlier")],
              loc="lower left", frameon=False, fontsize=16)


def draw_visited(ax, explored, bird_handle):
    """Scenes 1 and 2: all visited squares light; the birds themselves are drawn in dark green on top."""
    ax.imshow(np.where(explored, 0.0, np.nan), extent=EXTENT, origin="lower", cmap=SQUARE_CMAP, vmin=0, vmax=1,
              interpolation="nearest", zorder=1)
    ax.legend(handles=[bird_handle, Patch(color=EARLIER, label="Visited")],
              loc="lower left", frameon=False, fontsize=16)


def draw_circle(ax, cx, cy, r):
    a = np.linspace(0, 2 * np.pi, 200)
    ax.plot(cx + r * np.cos(a), cy + r * np.sin(a), color=TEXT, linewidth=2.5, linestyle="--", zorder=5)


def draw_radius_panel(ax, curves):
    """Radius of the explored area against time; `curves` is a list of (values, colour, label, up to step)."""
    ax.clear()
    ax.set_facecolor(BACKGROUND)
    ax.set_xlim(0, STEPS)
    ax.set_ylim(0, breed_circle[:, 2].max() * 1.1)
    ax.set_xlabel("Time (steps)")
    ax.set_ylabel("Radius of explored area\n(squares)")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(MUTED)
    for values, colour, label, upto in curves:
        ax.plot(np.arange(upto + 1), values[: upto + 1], color=colour, linewidth=2.5, label=label)
    if curves:
        ax.legend(frameon=False, loc="upper left", fontsize=16)


def draw_single(ax_map, ax_r, t):
    setup_map(ax_map, SINGLE_LIMIT, cell_grid=True)
    path = single[: t + 1]
    draw_visited(ax_map, grid_of(path),
                 Line2D([], [], marker=bird_marker(False), markersize=18, linestyle="", color=NOW, label="Bird"))
    ax_map.plot(path[:, 0], path[:, 1], color=TEXT, linewidth=1.5, alpha=0.6, zorder=2)
    ax_map.plot(0, 0, marker="o", markersize=6, color=MUTED, zorder=3)
    ax_map.plot(*path[-1], marker=bird_marker(facing_left[t]), markersize=46, color=NOW, zorder=4)
    ax_r.set_visible(False)  # no radius plot for a single bird


def draw_walk(ax_map, ax_r, t):
    setup_map(ax_map, HALF, cell_grid=False)
    draw_visited(ax_map, walk_explored[t],
                 Line2D([], [], marker="o", markersize=6, linestyle="", color=NOW, label="Birds"))
    if t:
        segments = np.stack([walkers[: t + 1, i] for i in range(N_WALKERS)])
        ax_map.add_collection(LineCollection(segments, colors=TEXT, linewidths=0.4, alpha=0.15, zorder=2))
    ax_map.scatter(walkers[t, :, 0], walkers[t, :, 1], s=18, color=NOW, zorder=3, linewidths=0)
    draw_circle(ax_map, *walk_circle[t])
    draw_radius_panel(ax_r, [(walk_circle[:, 2], WALK_ONLY, "walking only", t)])


def draw_breed(ax_map, ax_r, t):
    setup_map(ax_map, HALF, cell_grid=False)
    draw_squares(ax_map, breed_now[t], breed_explored[t])
    draw_circle(ax_map, *breed_circle[t])
    draw_radius_panel(ax_r, [(walk_circle[:, 2], WALK_ONLY, "walking only", STEPS),
                             (breed_circle[:, 2], WALK_BREED, "walking + breeding", t)])


def draw_breed_alone(ax_map, ax_r, t):
    """Scene 3 without the walking-only line in the radius plot (same axes)."""
    setup_map(ax_map, HALF, cell_grid=False)
    draw_squares(ax_map, breed_now[t], breed_explored[t])
    draw_circle(ax_map, *breed_circle[t])
    draw_radius_panel(ax_r, [(breed_circle[:, 2], WALK_BREED, "walking + breeding", t)])


SCENES = [
    ("skellam_1_one_bird", draw_single, SINGLE_STEPS),
    ("skellam_2_walking", draw_walk, STEPS),
    ("skellam_3_breeding", draw_breed, STEPS),
    ("skellam_3_breeding_alone", draw_breed_alone, STEPS),
]

FIGURES.mkdir(exist_ok=True)
for name, draw, n_steps in SCENES:
    steps = [0] * START_FRAMES + list(range(n_steps + 1)) + [n_steps] * HOLD_FRAMES
    fig, ax_map, ax_r = new_figure()
    animation = FuncAnimation(fig, lambda i: draw(ax_map, ax_r, steps[i]), frames=len(steps), blit=False)
    animation.save(FIGURES / f"{name}.mp4", writer=FFMpegWriter(fps=FPS, bitrate=4000),
                   savefig_kwargs={"facecolor": BACKGROUND})
    draw(ax_map, ax_r, n_steps)
    fig.savefig(FIGURES / f"{name}.png", facecolor=BACKGROUND)
    plt.close(fig)
    print(f"Saved {name}.mp4 ({len(steps) / FPS:.0f} s) and {name}.png")
