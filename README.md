# ToyProject - 2D Simulation

A Python-based 2D simulation using **PyOpenGL** and **ImGui**.
It features a world with autonomous Hamsters and a Chasing Cat, with configurable AI parameters and physics optimization.

## Features
*   **Characters**:
    *   **Hamsters**: Wander randomly, flee from Cat when detected.
    *   **Cat**: Chases hamsters based on hunger. Dies if it starves.
*   **Optimization**:
    *   **Spatial Grid**: O(N) collision detection for high performance.
    *   **Bounding Sphere**: Pre-pass collision check.
*   **Visualization**:
    *   **Debug Draw**: View AABB (Red) and Bounding Spheres (Green) wireframes.
    *   **UI Controls**: Real-time adjustment of AI parameters (Speed, Radius, Hunger Rate) and World Settings.
    *   **Metrics**: FPS, SPS, and Collision Check counters.

## Dependencies

*   Python 3.x
*   `PyOpenGL`
*   `imgui`
*   `numpy`

## Installation

```bash
uv pip install -r requirements.txt
# OR
pip install -r requirements.txt
```

## How to Run

```bash
uv run main.py
# OR
python main.py
```

## Controls

*   **Right Mouse Drag**: Pan Camera.
*   **Mouse Wheel**: Zoom In/Out.
*   **UI Panel** (Right Side):
    *   **World Settings**: Adjust entity counts and speeds.
    *   **Performance**: View FPS/Collision Stats.
    *   **Debug Visualization**: Toggle logic wireframes.
