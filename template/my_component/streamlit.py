import streamlit as st
import time
import numpy as np
import IPython.display as ipd
#ipd.Audio(audio, rate=16000)

from online_scd.model import SCDModel
from online_scd.streaming import StreamingDecoder
import timeit


from online_scd.utils import load_wav_file

import multiprocessing
import playsound

import queue
import time
from typing import List

import numpy as np
import pydub
from pydub.playback import play
import streamlit as st

from streamlit_webrtc import (
    ClientSettings,
    WebRtcMode,
    webrtc_streamer,
)

def stream_mic():
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        client_settings=ClientSettings(
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={"video": False, "audio": True},
        ),
    )


    status_indicator = st.empty()

    if not webrtc_ctx.state.playing:
        return

    status_indicator.write("Loading...")
    text_output = st.empty()
    stream = None

    last_rows = np.zeros((1,1))
    chart = st.line_chart(last_rows)

    model = SCDModel.load_from_checkpoint("test/sample_model/checkpoints/epoch=102.ckpt")
    streaming_decoder = StreamingDecoder(model)
    frame_number = 0
    status_indicator.write("Model loaded.")


    ct=0
    while True:
        if webrtc_ctx.audio_receiver:

            sound_chunk = pydub.AudioSegment.empty()
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                status_indicator.write("No frame arrived.")
                continue

            status_indicator.write("Running. Say something!")

            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            

            if len(sound_chunk) > 0:
                
                sound_chunk = sound_chunk.set_channels(1).set_frame_rate(
                    16000
                )
                buffer = np.array(sound_chunk.get_array_of_samples())
                text_output.markdown(f"{ct/16000} seconds")
                buffer = np.array(buffer)/32768
                ct+=len(buffer)
                #text_output.markdown(f"burh{ct}")
                for i in range(0, len(buffer), 1000):

                    for probs in streaming_decoder.process_audio(buffer[i: i+1000]):
                        new_rows = np.zeros((1, 1))
                        new_rows[0,0] = probs[1].detach().numpy()

                        chart.add_rows(new_rows)
                        
                        frame_number += 1
                    
        else:
            status_indicator.write("AudioReciver is not set. Abort.")
            break
# rerun.
    st.button("Re-run")

def stream(file_name):

    sound = pydub.AudioSegment.from_wav(file_name)
    sound = sound.set_channels(1).set_frame_rate(16000)
    audio = np.array(sound.get_array_of_samples())/32768

    last_rows = np.zeros((1,1))
    chart = st.line_chart(last_rows)
    text_output = st.empty()

    model = SCDModel.load_from_checkpoint("test/sample_model/checkpoints/epoch=102.ckpt")

    streaming_decoder = StreamingDecoder(model)
    frame_number = 0

    #p = multiprocessing.Process(target=playsound.playsound, args=(file_name,))
    import simpleaudio as sa

    wave_obj = sa.WaveObject.from_wave_file(file_name)
    #play_obj = wave_obj.play()
    p = multiprocessing.Process(target=lambda x:x.play(), args=(wave_obj,))
    p.start()
    start_0 = timeit.default_timer()
    for i in range(0, len(audio), 1000):
        start = timeit.default_timer()
        
        for probs in streaming_decoder.process_audio(audio[i: i+1000]):
            new_rows = np.zeros((1, 1))
            new_rows[0,0] = probs[1].detach().numpy()
            chart.add_rows(new_rows)

            
            frame_number += 1


        end = timeit.default_timer()
        text_output.markdown(f"{end-start_0} seconds")
        time.sleep(max(0,1/16-end+start))
    st.button("Re-run")


def main():
    option = st.selectbox(
        'Which audio source would you like to use?',
        ('microphone', 'sample wav (osoon)'), 0)
    if option == 'sample wav (osoon)':
        file_name = "3321821.wav"
        stream(file_name)
    elif option == 'microphone':
        stream_mic()
    

if __name__ == "__main__":
    main()