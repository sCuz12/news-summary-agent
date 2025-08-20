from state import NewsAgentState
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import os 
from datetime import datetime

OUTPUT_PATH = "output/voiceovers_audio"

model_id = "eleven_turbo_v2_5"

def generate_elevenlabs_script(state : NewsAgentState):

    eapiKey = os.getenv('ELEVENLABS_API_KEY')
    voiceId = os.getenv("ELEVENLABS_VOICE_ID","xAVsdcJvD1uegu8lFEE2") 


    if eapiKey == "":
        raise ValueError("Eleven labs api-key not defined")
    
    client = ElevenLabs(api_key=eapiKey)

    if not state.script_text:
        raise ValueError("Script text is not generated yet.")

    content_text = state.script_text

    # --- prepare output folder ---
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(OUTPUT_PATH, f"voiceover_{ts}.mp3")
    
    voice_settings = VoiceSettings(
        stability=0.25,          # lower = more expressive, higher = steadier
        similarity_boost=0.8,    # how closely to mimic the base voice
        style=0.6,               # higher = more “performative”
        use_speaker_boost=True   # a bit more presence/punch
    )

    response = client.text_to_speech.convert(
        voice_id=voiceId,
        output_format="mp3_44100_128",
        text=content_text,
        model_id="eleven_multilingual_v2",
        voice_settings=voice_settings,
    )

    with open(out_path,"wb") as f:
        for chunk in response:  
            f.write(chunk)

    print(f"🎙 Voiceover saved to {out_path}")

    return state