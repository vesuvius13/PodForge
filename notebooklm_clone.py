import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from datetime import datetime


class PerplexityResearcher:
    """Research topics using Perplexity Sonar API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
    def research_topic(self, topic: str, depth: str = "comprehensive") -> Dict:
        """
        Research a topic using Perplexity Sonar
        
        Args:
            topic: The topic to research
            depth: Research depth - "brief", "moderate", or "comprehensive"
        
        Returns:
            Dictionary containing research results
        """
        prompts = {
            "brief": f"Provide a concise overview of: {topic}",
            "moderate": f"Research and explain: {topic}. Include key facts, recent developments, and important context.",
            "comprehensive": f"Conduct a deep dive research on: {topic}. Include historical context, current state, key statistics, major players, recent developments, future trends, and interesting insights."
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant that provides well-structured, factual information with sources."
                },
                {
                    "role": "user",
                    "content": prompts.get(depth, prompts["comprehensive"])
                }
            ],
            "temperature": 0.2,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            return {
                "topic": topic,
                "content": result["choices"][0]["message"]["content"],
                "citations": result.get("citations", []),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error researching topic: {e}")
            return {"topic": topic, "content": "", "error": str(e)}


class PodcastScriptGenerator:
    """Generate conversational podcast scripts using Ollama"""
    
    def __init__(self, model: str = "llama3.1", ollama_host: str = "http://localhost:11434"):
        self.model = model
        self.ollama_host = ollama_host
        
    def generate_script(self, research_data: Dict, 
                       host1_name: str = "Alex",
                       host2_name: str = "Jordan",
                       style: str = "casual") -> List[Dict]:
        """
        Generate a conversational podcast script
        
        Args:
            research_data: Research content from Perplexity
            host1_name: Name of first host
            host2_name: Name of second host
            style: Conversation style - "casual", "professional", or "educational"
        
        Returns:
            List of dialogue segments with speaker and text
        """
        
        style_prompts = {
            "casual": "two friends having an engaging, casual conversation with humor and excitement",
            "professional": "two professional podcast hosts discussing the topic with expertise",
            "educational": "a teacher and curious student exploring the topic together"
        }
        
        system_prompt = f"""You are a podcast script writer. Create an engaging dialogue between {host1_name} and {host2_name}, 
{style_prompts.get(style, style_prompts['casual'])}. 

CRITICAL INSTRUCTIONS:
- Generate a COMPLETE conversation with 15-25 dialogue exchanges
- Start with a warm introduction
- Flow naturally with back-and-forth exchanges
- Include reactions ("Oh wow!", "That's fascinating!", "Wait, really?")
- Break down complex topics into digestible pieces
- End with a memorable conclusion and key takeaways
- Output ONLY valid JSON array, nothing else

Format as JSON array:
[
    {{"speaker": "{host1_name}", "text": "Hey everyone, welcome back!"}},
    {{"speaker": "{host2_name}", "text": "Hey! So excited about today's topic!"}}
]

DO NOT include ```json or ``` markers. Output ONLY the JSON array."""

        user_prompt = f"""Based on this research about {research_data['topic']}:

{research_data['content'][:3000]}

Create a complete 15-25 exchange podcast conversation between {host1_name} and {host2_name}.
Output ONLY the JSON array, no markdown, no explanations."""

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "options": {
                        "num_predict": 4096  # Increased token limit
                    }
                }
            )
            response.raise_for_status()
            
            script_text = response.json()["response"]
            
            # Extract JSON from response - handle markdown code blocks
            try:
                # Remove markdown code blocks if present
                clean_text = script_text.replace('```json', '').replace('```', '').strip()
                
                # Find JSON array
                start_idx = clean_text.find('[')
                end_idx = clean_text.rfind(']') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = clean_text[start_idx:end_idx]
                    script_json = json.loads(json_str)
                    
                    # Validate we got a reasonable script
                    if len(script_json) < 5:
                        print(f"⚠️ Script too short ({len(script_json)} segments), regenerating...")
                        # Fallback to basic script
                        script_json = self._create_basic_script(research_data, host1_name, host2_name)
                    
                    return script_json
                else:
                    print("⚠️ No JSON array found in response")
                    return self._create_basic_script(research_data, host1_name, host2_name)
                    
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Response preview: {script_text[:200]}")
                return self._create_basic_script(research_data, host1_name, host2_name)
            
        except Exception as e:
            print(f"Error generating script: {e}")
            return self._create_basic_script(research_data, host1_name, host2_name)
    
    def _create_basic_script(self, research_data: Dict, host1: str, host2: str) -> List[Dict]:
        """Create a basic script from research content"""
        content = research_data.get('content', '')
        topic = research_data.get('topic', 'this topic')
        
        # Split content into sentences
        sentences = [s.strip() + '.' for s in content[:1500].split('.') if len(s.strip()) > 20]
        
        script = [
            {"speaker": host1, "text": f"Hey everyone, welcome back! Today we're diving into {topic}."},
            {"speaker": host2, "text": "I'm really excited about this one. So, what's the big picture here?"}
        ]
        
        # Alternate speakers discussing key points
        for i, sentence in enumerate(sentences[:10]):
            speaker = host1 if i % 2 == 0 else host2
            script.append({"speaker": speaker, "text": sentence})
        
        script.append({"speaker": host1, "text": "Wow, that's really fascinating stuff!"})
        script.append({"speaker": host2, "text": "Absolutely. Thanks for tuning in, everyone!"})
        
        return script


class TTSGenerator:
    """Generate speech using ChatTTS"""
    
    def __init__(self):
        self.tts_model = None
        self._setup_backend()
    
    def _setup_backend(self):
        """Setup ChatTTS backend"""
        try:
            import ChatTTS
            self.tts_model = ChatTTS.Chat()
            print("Loading ChatTTS models...")
            self.tts_model.load(compile=False)
            print("✅ ChatTTS loaded")
        except ImportError:
            print("❌ ChatTTS not installed. Install with: pip install ChatTTS")
        except Exception as e:
            print(f"⚠️ ChatTTS loading issue: {e}")
            try:
                self.tts_model.load_models()
                print("✅ ChatTTS loaded")
            except:
                print("❌ ChatTTS failed to load")
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better TTS pronunciation"""
        import re
        
        # Replace special quotes and dashes
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace('–', '-').replace('—', '-')
        text = text.replace('…', '...')
        
        # Convert currency ($123.45 → "one hundred twenty three point four five dollars")
        def currency_to_words(match):
            amount = match.group(1)
            magnitude = match.group(2) if match.lastindex >= 2 else ""
            
            if '.' in amount:
                whole, decimal = amount.split('.')
                whole_int = int(whole) if whole else 0
                
                result = self._number_to_words(whole_int)
                result += " point"
                
                # Read each decimal digit individually
                for digit in decimal:
                    result += " " + self._number_to_words(int(digit))
                
                if magnitude:
                    result += " " + magnitude.lower()
                
                result += " dollars"
                return result
            else:
                whole_int = int(amount)
                result = self._number_to_words(whole_int)
                if magnitude:
                    result += " " + magnitude.lower()
                result += " dollar" + ("s" if whole_int != 1 else "")
                return result
        
        text = re.sub(r'\$(\d+(?:\.\d+)?)\s*(Billion|Million|Thousand|Trillion|billion|million|thousand|trillion)?', currency_to_words, text)
        
        # Convert ordinal numbers (1st, 2nd, 3rd, etc.)
        def ordinal_to_words(match):
            num = int(match.group(1))
            return self._ordinal_to_words(num)
        
        text = re.sub(r'\b(\d+)(?:st|nd|rd|th)\b', ordinal_to_words, text)
        
        # Convert years (1900-2099) to words
        def year_to_words(match):
            year = match.group(0)
            y = int(year)
            if 1900 <= y <= 1999:
                century = "nineteen"
                last_two = y % 100
                if last_two == 0:
                    return f"{century} hundred"
                elif last_two < 10:
                    return f"{century} oh {self._number_to_words(last_two)}"
                else:
                    return f"{century} {self._number_to_words(last_two)}"
            elif 2000 <= y <= 2099:
                if y == 2000:
                    return "two thousand"
                elif y < 2010:
                    return f"two thousand {self._number_to_words(y % 2000)}"
                else:
                    return f"twenty {self._number_to_words(y % 100)}"
            return year
        
        text = re.sub(r'\b(19\d{2}|20\d{2})\b', year_to_words, text)
        
        # Convert other numbers to words (1-999)
        def num_to_words(match):
            num = int(match.group(0))
            return self._number_to_words(num)
        
        text = re.sub(r'\b(\d{1,3})\b', num_to_words, text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _ordinal_to_words(self, n: int) -> str:
        """Convert number to ordinal words (1 → first, 2 → second, etc.)"""
        ordinals = {
            1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
            6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
            11: "eleventh", 12: "twelfth", 13: "thirteenth", 14: "fourteenth", 15: "fifteenth",
            16: "sixteenth", 17: "seventeenth", 18: "eighteenth", 19: "nineteenth", 20: "twentieth",
            30: "thirtieth", 40: "fortieth", 50: "fiftieth", 60: "sixtieth", 
            70: "seventieth", 80: "eightieth", 90: "ninetieth"
        }
        
        if n in ordinals:
            return ordinals[n]
        elif n < 100:
            tens = (n // 10) * 10
            ones = n % 10
            return self._number_to_words(tens) + " " + ordinals[ones]
        else:
            return self._number_to_words(n) + "th"
    
    def _number_to_words(self, n: int) -> str:
        """Convert number to words (0-999)"""
        if n == 0:
            return "zero"
        
        ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", 
                "sixteen", "seventeen", "eighteen", "nineteen"]
        
        if n < 10:
            return ones[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
        else:
            return ones[n // 100] + " hundred" + (" " + self._number_to_words(n % 100) if n % 100 != 0 else "")
    
    def generate_audio(self, script: List[Dict], output_path: str = "podcast_output.wav"):
        """Generate audio from script"""
        if not self.tts_model:
            print("❌ TTS model not loaded")
            return None
        
        return self._generate_chattts(script, output_path)
    
    def _generate_chattts(self, script, output_path):
        """Generate audio using ChatTTS"""
        try:
            import numpy as np
            import soundfile as sf
            
            print(f"🎙️ Generating audio with ChatTTS...")
            audio_segments = []
            sample_rate = 24000
            
            for i, segment in enumerate(script):
                text = segment["text"]
                speaker = segment["speaker"]
                
                # Normalize text for better TTS
                normalized_text = self._normalize_text(text)
                
                print(f"  [{i+1}/{len(script)}] {speaker}: {text[:50]}...")
                if text != normalized_text:
                    print(f"    → Normalized: {normalized_text[:50]}...")
                
                wavs = self.tts_model.infer([normalized_text])
                audio_segments.append(wavs[0])
            
            pause = np.zeros(int(sample_rate * 0.5), dtype=np.float32)
            
            combined = []
            for segment in audio_segments:
                if segment.dtype != np.float32:
                    segment = segment.astype(np.float32)
                combined.append(segment)
                combined.append(pause)
            
            final_audio = np.concatenate(combined)
            
            max_val = np.abs(final_audio).max()
            if max_val > 0:
                final_audio = final_audio / max_val * 0.95
            
            sf.write(output_path, final_audio, sample_rate)
            
            print(f"✅ Audio generated: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None


class NotebookLMClone:
    """Main application class"""
    
    def __init__(self, perplexity_key: str = None, ollama_model: str = None):
        self.researcher = PerplexityResearcher(perplexity_key) if perplexity_key else None
        self.script_gen = PodcastScriptGenerator(model=ollama_model) if ollama_model else None
        self.tts_gen = TTSGenerator()
        
    def create_podcast(self, topic: str = None, 
                      host1_name: str = "Alex",
                      host2_name: str = "Jordan",
                      voice_samples: Optional[Dict[str, str]] = None,
                      output_dir: str = "output",
                      style: str = "casual",
                      research_depth: str = "comprehensive",
                      research_file: str = None,
                      script_file: str = None) -> Dict:
        """
        Create a complete podcast from a topic
        
        Args:
            topic: Topic to research and discuss (required if no research_file)
            host1_name: First host name
            host2_name: Second host name
            voice_samples: Dict mapping host names to voice sample file paths
            output_dir: Output directory for files
            style: Conversation style
            research_depth: How deep to research
            research_file: Path to existing research JSON (skip research step)
            script_file: Path to existing script JSON (skip research and script steps)
            
        Returns:
            Dictionary with paths to generated files
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # If script file provided, load it and skip to audio generation
        if script_file:
            print(f"\n📜 Loading existing script: {script_file}")
            with open(script_file, 'r', encoding='utf-8') as f:
                script = json.load(f)
            
            # Extract topic from filename or use generic name
            clean_topic = Path(script_file).stem.replace('_script', '')
            
            print(f"✅ Script loaded with {len(script)} segments")
            
        else:
            # Need topic for research/script generation
            if not topic:
                return {"error": "Topic required when not using existing script file"}
            
            clean_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_topic = clean_topic.replace(' ', '_')[:50]
            
            # Load or generate research
            if research_file:
                print(f"\n📊 Loading existing research: {research_file}")
                with open(research_file, 'r', encoding='utf-8') as f:
                    research = json.load(f)
                print(f"✅ Research loaded")
            else:
                if not self.researcher:
                    return {"error": "Perplexity API key required for research"}
                    
                print(f"\n🔍 Researching topic: {topic}")
                research = self.researcher.research_topic(topic, depth=research_depth)
                
                if "error" in research:
                    print(f"❌ Research failed: {research['error']}")
                    return {"error": research['error']}
                
                # Save research
                research_file = output_path / f"{clean_topic}_research.json"
                with open(research_file, 'w', encoding='utf-8') as f:
                    json.dump(research, f, indent=2)
                print(f"✅ Research saved: {research_file}")
            
            # Generate script
            print(f"\n📝 Generating podcast script...")
            script = self.script_gen.generate_script(
                research, host1_name, host2_name, style
            )
            
            if not script:
                print("❌ Script generation failed")
                return {"error": "Script generation failed"}
            
            # Save script
            script_file = output_path / f"{clean_topic}_script.json"
            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump(script, f, indent=2)
            print(f"✅ Script saved: {script_file}")
            
            # Print script preview
            print(f"\n📜 Script Preview:")
            for i, segment in enumerate(script[:4]):
                print(f"  {segment['speaker']}: {segment['text'][:80]}...")
            if len(script) > 4:
                print(f"  ... and {len(script) - 4} more segments")
        
        # Generate audio
        print(f"\n🎙️ Generating audio...")
        audio_file = output_path / f"{clean_topic}_podcast.wav"
        
        self.tts_gen.generate_audio(script, str(audio_file))
        
        return {
            "research": str(research_file) if 'research_file' in locals() else None,
            "script": str(script_file),
            "audio": str(audio_file),
            "topic": topic or clean_topic
        }


def main():
    parser = argparse.ArgumentParser(description="Open Source NotebookLM - Generate podcast from any topic")
    parser.add_argument("topic", nargs='?', help="Topic to research and create podcast about")
    parser.add_argument("--perplexity-key", help="Perplexity API key (not needed if using --script-file)")
    parser.add_argument("--ollama-model", default="llama3.1", help="Ollama model to use")
    parser.add_argument("--tts-backend", choices=["chattts", "f5-tts-mlx", "f5-tts"], 
                       default="chattts", help="TTS backend (chattts recommended)")
    parser.add_argument("--host1", default="Alex", help="First host name")
    parser.add_argument("--host2", default="Jordan", help="Second host name")
    parser.add_argument("--voice1", help="Voice sample for host 1 (path to .wav file)")
    parser.add_argument("--voice2", help="Voice sample for host 2 (path to .wav file)")
    parser.add_argument("--style", choices=["casual", "professional", "educational"],
                       default="casual", help="Conversation style")
    parser.add_argument("--depth", choices=["brief", "moderate", "comprehensive"],
                       default="comprehensive", help="Research depth")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    
    # New options for loading existing files
    parser.add_argument("--research-file", help="Path to existing research JSON file (skip research)")
    parser.add_argument("--script-file", help="Path to existing script JSON file (skip research & script generation)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.script_file and not args.topic:
        parser.error("Either 'topic' or '--script-file' is required")
    
    if not args.script_file and not args.research_file and not args.perplexity_key:
        parser.error("--perplexity-key required when not using --research-file or --script-file")
    
    args = parser.parse_args()
    
    # Prepare voice samples if provided
    voice_samples = {}
    if args.voice1:
        voice_samples[args.host1] = args.voice1
    if args.voice2:
        voice_samples[args.host2] = args.voice2
    
    # Create podcast
    app = NotebookLMClone(
        perplexity_key=args.perplexity_key,
        ollama_model=args.ollama_model,
        tts_backend=args.tts_backend
    )
    
    result = app.create_podcast(
        topic=args.topic,
        host1_name=args.host1,
        host2_name=args.host2,
        voice_samples=voice_samples if voice_samples else None,
        output_dir=args.output_dir,
        style=args.style,
        research_depth=args.depth,
        research_file=args.research_file,
        script_file=args.script_file
    )
    
    if "error" not in result:
        print("\n✨ Podcast creation complete!")
        print(f"📁 Files saved in: {args.output_dir}/")
        if result.get('research'):
            print(f"   - Research: {result['research']}")
        print(f"   - Script: {result['script']}")
        print(f"   - Audio: {result['audio']}")
    else:
        print(f"\n❌ Error: {result['error']}")


if __name__ == "__main__":
    main()
