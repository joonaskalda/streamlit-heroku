import os
import streamlit.components.v1 as components

import streamlit as st
import time
import numpy as np
import IPython.display as ipd
#ipd.Audio(audio, rate=16000)

from online_scd.model import SCDModel
from online_scd.streaming import StreamingDecoder
import timeit

import base64
import scipy.io.wavfile

from online_scd.utils import load_wav_file

import multiprocessing
#import playsound

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
from pathlib import Path
import os, time, sys
# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = False
upload_counter = 0
# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "my_component",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
    model = SCDModel.load_from_checkpoint("template/my_component/test/sample_model/checkpoints/epoch=102.ckpt")
    #file_path = "template/my_component/frontend/src/audio"
    file_name = "template/my_component/frontend/src/audio/3321821.wav"
    build_dir = "template/my_component/frontend/src"
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("my_component", path=build_dir)

    model = SCDModel.load_from_checkpoint("template/my_component/test/sample_model/checkpoints/epoch=102.ckpt")
    #file_path = "template/my_component/frontend/src/audio"
    file_name = "template/my_component/frontend/src/audio/3321821.wav"

# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def my_component(name, audio, key=None):
    """Create a new instance of "my_component".

    Parameters
    ----------
    name: str
        The name of the thing we're saying hello to. The component will display
        the text "Hello, {name}!"
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    int
        The number of times the component's "Click Me" button has been clicked.
        (This is the value passed to `Streamlit.setComponentValue` on the
        frontend.)

    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    component_value = _component_func(name=name, audio=audio, key=key, default=0)

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/__init__.py`
def stream_sample():

    st.subheader("Streaming a sample .wav")

    # Create a second instance of our component whose `name` arg will vary
    # based on a text_input widget.
    #
    # We use the special "key" argument to assign a fixed identity to this
    # component instance. By default, when a component's arguments change,
    # it is considered a new instance and will be re-mounted on the frontend
    # and lose its current state. In this case, we want to vary the component's
    # "name" argument without having it get recreated.
    
    sound = pydub.AudioSegment.from_wav(file_name)
    sound = sound.set_channels(1).set_frame_rate(16000)
    audio = np.array(sound.get_array_of_samples())/32768

    #enc=base64.b64encode(open(file_name, "rb").read())
    last_rows = np.zeros((1,1))
    chart = st.line_chart(last_rows)
    frame_number = 0

    #p = multiprocessing.Process(target=playsound.playsound, args=(file_name,)) 

    #play_obj = wave_obj.play()
    
    start_0 = timeit.default_timer()
    was_clicked = my_component(name="test", audio = "sample", key="foo")
    
    if was_clicked:
        for i in range(0, len(audio), 1000):
            # while (num_clicks%2 == 0):
            #     time.sleep(0.1)
            start = timeit.default_timer()
            
            for probs in st.session_state.model.process_audio(audio[i: i+1000]):
                new_rows = np.zeros((1, 1))
                new_rows[0,0] = probs[1].detach().numpy()
                chart.add_rows(new_rows)

                
                frame_number += 1


            end = timeit.default_timer()
            # text_output.markdown(f"{end-start_0} seconds")
            time.sleep(max(0,1/16-end+start))
        # st.button("Re-run")

def stream_mic():
    st.subheader("Streaming from microphone")

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

                    for probs in st.session_state.model.process_audio(buffer[i: i+1000]):
                        new_rows = np.zeros((1, 1))
                        new_rows[0,0] = probs[1].detach().numpy()

                        chart.add_rows(new_rows)
                        
                        frame_number += 1
                    
        else:
            status_indicator.write("AudioReciver is not set. Abort.")
            break
file_changed = False
def upload_file():
    global file_changed
    file_changed = True
if 'upload' not in st.session_state:
    st.session_state['upload'] = 'value'
if 'model' not in st.session_state:
    st.session_state['model'] = StreamingDecoder(model)

def stream_upload():
    #global upload_counter

    st.subheader("Streaming an upload")

    # Create a second instance of our component whose `name` arg will vary
    # based on a text_input widget.
    #
    # We use the special "key" argument to assign a fixed identity to this
    # component instance. By default, when a component's arguments change,
    # it is considered a new instance and will be re-mounted on the frontend
    # and lose its current state. In this case, we want to vary the component's
    # "name" argument without having it get recreated.
    # name_input = st.text_input("Enter a name", value="Streamlit")


    uploaded_file = st.file_uploader("Choose a file", on_change=upload_file())
    #if uploaded_file is not None
    #was_clicked = my_component(name="test",audio = file_name, key="foo")
    if uploaded_file is not None:
        if (uploaded_file.name != st.session_state['upload']):
            st.session_state['upload'] = uploaded_file.name
            #upload_counter+=1
            
            path = build_dir + "/audio"
            current_uploads = []
            for f in os.listdir(path):
                current_uploads.append(f.split(".")[0])
            i = 0
            while True:
                if str(i) not in current_uploads:
                    new_name = str(i)
                    break
                i+=1

            sound = pydub.AudioSegment.from_wav(uploaded_file)
            sound = sound.set_channels(1).set_frame_rate(16000)
            #only consider first minute of the file for uploads
            sound = sound[:60*1000]
            audio = np.array(sound.get_array_of_samples())/32768

            file_name = new_name + ".wav"
            save_location = build_dir +"/audio/"+ file_name
            sound = (sound[:2000]-1000) + sound
            sound.export(save_location, format="wav")

            st.session_state['file_name'] = file_name
            st.session_state['audio'] = audio
        #p = multiprocessing.Process(target=playsound.playsound, args=(file_name,)) 

        #play_obj = wave_obj.play()
        file_name = st.session_state['file_name']
        start_0 = timeit.default_timer()
        was_clicked = my_component(name="test2",audio = file_name)
        
        if was_clicked:
            #streaming_decoder = StreamingDecoder(model)
            frame_number = 0
            last_rows = np.zeros((1,1))
            chart = st.line_chart(last_rows)
            #audio = st.session_state['audio']
            for i in range(0, len(st.session_state.audio), 1000):
                # while (num_clicks%2 == 0):
                #     time.sleep(0.1)
                start = timeit.default_timer()
                
                for probs in st.session_state.model.process_audio(st.session_state.audio[i: i+1000]):
                    new_rows = np.zeros((1, 1))
                    new_rows[0,0] = probs[1].detach().numpy()
                    chart.add_rows(new_rows)

                    
                    frame_number += 1


                end = timeit.default_timer()
                # text_output.markdown(f"{end-start_0} seconds")
                time.sleep(max(0,1/16-end+start))
            # st.button("Re-run")
        #os.remove(save_location)

def main():
    st.header("Demo of Collar-Aware Training for Speaker Change Detection")
    st.markdown("The model uses a multi-layer LSTM on top of pre-trained speech embeddings, and a final softmax layer. The model uses a step size of 100 ms (i.e., it outputs 10 decisions per second). The model is implemented in Pytorch while this demo was built using Streamlit.")
    st.markdown("The model is trained using a special version of cross-entropy training which tolerates small errors in the hypothesized speaker change timestamps. Due to this, the softmax outputs of the trained model are very peaky and do not require any local maxima tracking for extracting the final speaker turn points. This makes the model suitable for online appications.")
    st.markdown("This demo visualizes the output of the model for an audio source. The audio source can be either a sample file, a microphone or an uploaded file, first 60 seconds of which is used.")
    option_1 = 'A sample file'
    option_2 = 'A microphone'
    option_3 = 'An uploaded .wav file'
    option = st.selectbox(
        'Which audio source would you like to use?',
        (option_1,option_2,option_3), 0)
    if option == option_1:
        #file_name = "3321821.wav"
        stream_sample()
    elif option == option_2:
        stream_mic()
    elif option == option_3:
        stream_upload()

    path = build_dir + "/audio"
    now = time.time()
    
    for f in os.listdir(path):
        if f!="3321821.wav" and f[-3:] == "wav":
            f = os.path.join(path, f)
            if os.stat(f).st_mtime < now - 3600:
                if os.path.isfile(f):
                    os.remove(f)

    

if __name__ == "__main__":
    main()