# 🏎️ AI Neural Racing - Self-Driving Cars with Neural Networks

An AI simulation where cars learn to drive around a race track using neural networks and genetic evolution. Watch as each generation gets smarter!

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎮 Features

- **Neural Network AI** - Cars use custom neural networks to make driving decisions
- **Genetic Evolution** - Best performers breed to create smarter generations
- **Real-time Visualization** - Watch cars learn with colorful sensor displays
- **Professional Track** - Oval racing track with curbs, grass, and pit lane
- **Two Versions**:
  - `self_driving_car.py` - Desktop version with NEAT-Python (full features)
  - `main.py` - Web-compatible version (runs in browser)

## 🚀 Quick Start

### Desktop Version (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-neural-racing.git
cd ai-neural-racing

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python self_driving_car.py
```

### Web Version (Browser)

```bash
# Install pygbag
pip install pygbag

# Build and run
python -m pygbag --port 8000 .

# Open http://localhost:8000 in your browser
```

## 🎯 Controls

| Key | Action |
|-----|--------|
| `R` | Restart simulation |
| `P` / `Space` | Pause/Resume |
| `S` | Skip to next generation |
| `F` / `F11` | Toggle Fullscreen (desktop only) |
| `Q` / `ESC` | Quit |

## 🧠 How It Works

1. **Sensors** - Each car has 5 sensors detecting distance to walls
2. **Neural Network** - 5 inputs → 6 hidden neurons → 2 outputs (turn left/right)
3. **Fitness** - Cars earn points for staying alive and driving distance
4. **Evolution** - Top performers pass genes to next generation with mutations

## 📁 Project Structure

```
ai-neural-racing/
├── self_driving_car.py  # Desktop version (NEAT-Python)
├── main.py              # Web version (custom neural network)
├── neat_config.txt      # NEAT algorithm configuration
├── requirements.txt     # Python dependencies
└── README.md
```

## 🛠️ Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "AI_Neural_Racing" --add-data "neat_config.txt;." self_driving_car.py
```

The executable will be in the `dist/` folder.

## 🌐 Deploy to Web

1. Build with pygbag: `python -m pygbag --archive --build .`
2. Upload `build/web.zip` to [itch.io](https://itch.io) as HTML game
3. Or drag `build/web` folder to [Netlify Drop](https://app.netlify.com/drop)

## 📋 Requirements

- Python 3.8+
- pygame
- neat-python (desktop version only)

## 🎨 Sensor Colors

- 🟢 **Green** - Safe distance from walls
- 🔴 **Red** - Danger! Close to collision

## 📜 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Pull requests welcome! Feel free to improve the AI, add new tracks, or enhance visuals.

---

Made with ❤️ using Python and Pygame
