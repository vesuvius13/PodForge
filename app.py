import streamlit as st
import subprocess
import json
import os
from pathlib import Path
from notebooklm_clone import NotebookLMClone

# Page config
st.set_page_config(
    page_title="PodForge",
    page_icon="🎙️",
    layout="wide"
)

def get_ollama_models():
    """Get list of installed Ollama models"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            return models if models else ["llama3.1"]
        else:
            return ["llama3.1"]
    except Exception as e:
        st.warning(f"Could not detect Ollama models: {e}")
        return ["llama3.1"]

def get_existing_files(directory="output"):
    """Get existing research and script files"""
    path = Path(directory)
    if not path.exists():
        return [], []
    
    research_files = sorted([f.name for f in path.glob("*_research.json")])
    script_files = sorted([f.name for f in path.glob("*_script.json")])
    
    return research_files, script_files

# Title and description
st.title("🎙️ PodForge")
st.markdown("Generate engaging podcast conversations from any topic using AI")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key
    perplexity_key = st.text_input(
        "Perplexity API Key",
        type="password",
        help="Required for topic research"
    )
    
    # Ollama Model Selection
    st.subheader("🤖 Script Generation")
    with st.spinner("Detecting Ollama models..."):
        available_models = get_ollama_models()
    
    ollama_model = st.selectbox(
        "Ollama Model",
        options=available_models,
        help="Select the language model for script generation"
    )
    
    # Output directory
    output_dir = st.text_input("Output Directory", value="output")
    
    st.divider()
    st.caption("💡 Tip: Save your API key to avoid re-entering it")

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📝 Create New", "♻️ Resume from Files", "📊 View Results"])

with tab1:
    st.header("Create New Podcast")
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input(
            "Podcast Topic",
            placeholder="e.g., The history of artificial intelligence",
            help="What should the podcast be about?"
        )
        
        style = st.selectbox(
            "Conversation Style",
            options=["casual", "professional", "educational"],
            help="How should the hosts interact?"
        )
        
        host1 = st.text_input("Host 1 Name", value="Alex")
    
    with col2:
        research_depth = st.selectbox(
            "Research Depth",
            options=["brief", "moderate", "comprehensive"],
            index=2,
            help="How thorough should the research be?"
        )
        
        st.write("")  # Spacer
        st.write("")  # Spacer
        
        host2 = st.text_input("Host 2 Name", value="Jordan")
    
    st.divider()
    
    if st.button("🎬 Generate Podcast", type="primary", use_container_width=True):
        if not topic:
            st.error("Please enter a topic")
        elif not perplexity_key:
            st.error("Please enter your Perplexity API key")
        else:
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Initialize
                status_text.text("🔧 Initializing...")
                app = NotebookLMClone(
                    perplexity_key=perplexity_key,
                    ollama_model=ollama_model
                )
                progress_bar.progress(10)
                
                # Research
                status_text.text("🔍 Researching topic...")
                st.info(f"Using {research_depth} research depth")
                progress_bar.progress(30)
                
                # Generate
                result = app.create_podcast(
                    topic=topic,
                    host1_name=host1,
                    host2_name=host2,
                    voice_samples=None,
                    output_dir=output_dir,
                    style=style,
                    research_depth=research_depth
                )
                
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("🎉 Podcast generated successfully!")
                    
                    # Display results
                    st.subheader("📁 Generated Files")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if result.get('research'):
                            st.code(result['research'], language=None)
                    
                    with col2:
                        st.code(result['script'], language=None)
                    
                    with col3:
                        st.code(result['audio'], language=None)
                    
                    # Audio player
                    st.subheader("🎧 Listen to Podcast")
                    audio_file = open(result['audio'], 'rb')
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format='audio/wav')
                    
            except Exception as e:
                st.error(f"Error generating podcast: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
            
            finally:
                progress_bar.empty()

with tab2:
    st.header("Resume from Existing Files")
    st.info("💡 Reuse research or scripts to save API credits")
    
    research_files, script_files = get_existing_files(output_dir)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Option 1: Resume from Script")
        st.caption("Generate only audio (skips research & script)")
        
        script_file = st.selectbox(
            "Select Script File",
            options=[""] + script_files,
            key="script_select"
        )
        
        if st.button("🎙️ Generate Audio Only", key="audio_only"):
            if not script_file:
                st.error("Please select a script file")
            else:
                try:
                    status = st.empty()
                    status.text("🎙️ Generating audio...")
                    
                    app = NotebookLMClone()
                    
                    result = app.create_podcast(
                        script_file=os.path.join(output_dir, script_file),
                        output_dir=output_dir
                    )
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.success("✅ Audio generated!")
                        
                        audio_file = open(result['audio'], 'rb')
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format='audio/wav')
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.subheader("Option 2: Resume from Research")
        st.caption("Generate script & audio (skips research)")
        
        research_file = st.selectbox(
            "Select Research File",
            options=[""] + research_files,
            key="research_select"
        )
        
        if research_file:
            topic_from_file = st.text_input(
                "Topic Name",
                value=research_file.replace("_research.json", "").replace("_", " "),
                key="topic_from_research"
            )
            
            style_2 = st.selectbox(
                "Conversation Style",
                options=["casual", "professional", "educational"],
                key="style_2"
            )
            
            if st.button("📝 Generate Script & Audio", key="script_audio"):
                if not research_file:
                    st.error("Please select a research file")
                else:
                    try:
                        status = st.empty()
                        status.text("📝 Generating script and audio...")
                        
                        app = NotebookLMClone(ollama_model=ollama_model)
                        
                        result = app.create_podcast(
                            topic=topic_from_file,
                            research_file=os.path.join(output_dir, research_file),
                            style=style_2,
                            output_dir=output_dir
                        )
                        
                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.success("✅ Script and audio generated!")
                            
                            audio_file = open(result['audio'], 'rb')
                            audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format='audio/wav')
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

with tab3:
    st.header("📊 View Generated Podcasts")
    
    # List all audio files
    output_path = Path(output_dir)
    if output_path.exists():
        audio_files = sorted(output_path.glob("*.wav"), key=os.path.getmtime, reverse=True)
        
        if audio_files:
            st.success(f"Found {len(audio_files)} podcast(s)")
            
            for audio_file in audio_files:
                with st.expander(f"🎧 {audio_file.stem}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Audio player
                        audio_bytes = open(audio_file, 'rb').read()
                        st.audio(audio_bytes, format='audio/wav')
                    
                    with col2:
                        # File info
                        file_size = audio_file.stat().st_size / 1024 / 1024
                        st.metric("Size", f"{file_size:.2f} MB")
                        
                        # Show related files
                        base_name = audio_file.stem.replace("_podcast", "")
                        research_path = output_path / f"{base_name}_research.json"
                        script_path = output_path / f"{base_name}_script.json"
                        
                        if research_path.exists():
                            st.caption("✅ Research file available")
                        if script_path.exists():
                            st.caption("✅ Script file available")
                            
                            # Show script preview
                            if st.button("👁️ View Script", key=f"view_{audio_file.name}"):
                                with open(script_path) as f:
                                    script_data = json.load(f)
                                
                                st.subheader("Script Preview")
                                for i, segment in enumerate(script_data[:5]):
                                    st.markdown(f"**{segment['speaker']}:** {segment['text']}")
                                
                                if len(script_data) > 5:
                                    st.caption(f"... and {len(script_data) - 5} more segments")
        else:
            st.info("No podcasts generated yet. Create one in the 'Create New' tab!")
    else:
        st.warning(f"Output directory '{output_dir}' not found")

# Footer
st.divider()
st.caption("Built with ❤️ using ChatTTS, Ollama, and Perplexity AI")
