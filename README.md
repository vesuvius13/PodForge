# 🎙️ PodForge

**Transform any topic into engaging AI-powered podcast conversations**

PodForge automatically researches topics, generates natural dialogue scripts, and produces studio-quality audio podcasts using AI. Perfect for content creators, educators, and researchers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

## ✨ Features

- 🔍 **Intelligent Research** - Uses Perplexity AI for comprehensive topic research
- 📝 **Natural Script Generation** - Ollama-powered dialogue with customizable styles
- 🎤 **High-Quality TTS** - ChatTTS for natural-sounding conversations
- 🌐 **Interactive Web UI** - Built with Streamlit for ease of use
- 💾 **Resume from Files** - Save API credits by reusing research/scripts
- 🎨 **Customizable Styles** - Casual, professional, or educational conversations
- 🔄 **Auto-Detection** - Automatically finds installed Ollama models
- 📊 **Text Normalization** - Smart handling of numbers, dates, and currency

## 🎬 Demo

```bash
# Generate a podcast about any topic
python notebooklm_clone.py "The history of coffee" \
    --perplexity-key YOUR_KEY \
    --ollama-model llama3.1
```

**Output:** Professional 3-5 minute podcast with two AI hosts discussing your topic!

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com/) installed
- [Perplexity API key](https://www.perplexity.ai/settings/api)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/podforge.git
cd podforge

# Install dependencies
pip install -r requirements.txt

# Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1
ollama serve
```

### Usage

#### Web UI (Recommended)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser!

#### Command Line

```bash
# Create new podcast
python notebooklm_clone.py "Quantum Computing Explained" \
    --perplexity-key YOUR_API_KEY \
    --ollama-model llama3.1 \
    --style professional

# Generate audio from existing script (saves API credits!)
python notebooklm_clone.py \
    --script-file output/topic_script.json

# Resume from research (skip research step)
python notebooklm_clone.py "Your Topic" \
    --research-file output/topic_research.json \
    --perplexity-key YOUR_KEY
```

## 📖 Documentation

### Web UI Features

**Create New Tab**
- Enter any topic
- Select Ollama model (auto-detected)
- Choose conversation style
- Real-time progress tracking

**Resume from Files Tab**
- Generate audio from existing scripts
- Resume from research files
- Save API credits

**View Results Tab**
- Browse all generated podcasts
- Built-in audio player
- View scripts and metadata

### Command Line Options

```bash
python notebooklm_clone.py [TOPIC] [OPTIONS]

Options:
  --perplexity-key KEY       Perplexity API key
  --ollama-model MODEL       Ollama model (auto-detected in UI)
  --style STYLE             casual, professional, or educational
  --depth DEPTH             brief, moderate, or comprehensive
  --host1 NAME              First host name (default: Alex)
  --host2 NAME              Second host name (default: Jordan)
  --output-dir DIR          Output directory (default: output)
  --research-file FILE      Resume from research JSON
  --script-file FILE        Generate audio from script JSON
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file:

```bash
PERPLEXITY_API_KEY=your_key_here
OLLAMA_HOST=http://localhost:11434
```

### Ollama Models

PodForge automatically detects installed models. 

```bash
# Install models
ollama pull llama3.1
ollama pull llama3.2
ollama pull mistral
```

## 📁 Project Structure

```
podforge/
├── notebooklm_clone.py      # Core logic
├── app.py                   # Streamlit UI
├── requirements.txt         # Python dependencies
├── output/                  # Generated podcasts
│   ├── topic_research.json
│   ├── topic_script.json
│   └── topic_podcast.wav
└── README.md
```

## 🎨 Customization

### Conversation Styles

- **Casual**: Two friends discussing the topic with humor
- **Professional**: Expert hosts with formal tone
- **Educational**: Teacher-student dynamic

### Research Depth

- **Brief**: Quick overview (30 seconds)
- **Moderate**: Balanced coverage (1 minute)
- **Comprehensive**: Deep dive (2-3 minutes)

## 🔧 Troubleshooting

### Ollama not detected
```bash
ollama serve
ollama list
```

### ChatTTS loading issues
```bash
pip uninstall ChatTTS
pip install ChatTTS
```

### Script truncation
- Increase `num_predict` in script generation
- Use smaller research depth
- Try different Ollama model

### Audio quality issues
- Text normalization handles numbers, dates, currency
- Use brief sentences for better TTS
- Check sample rate (24kHz default)
