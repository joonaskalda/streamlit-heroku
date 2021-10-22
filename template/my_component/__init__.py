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

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

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
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("my_component", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def my_component(name, key=None):
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
    component_value = _component_func(name=name, key=key, default=0)

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/__init__.py`
if __name__ == "__main__":
    import streamlit as st


    st.subheader("Component with variable args")

    # Create a second instance of our component whose `name` arg will vary
    # based on a text_input widget.
    #
    # We use the special "key" argument to assign a fixed identity to this
    # component instance. By default, when a component's arguments change,
    # it is considered a new instance and will be re-mounted on the frontend
    # and lose its current state. In this case, we want to vary the component's
    # "name" argument without having it get recreated.
    name_input = st.text_input("Enter a name", value="Streamlit")

    model = SCDModel.load_from_checkpoint("template/my_component/test/sample_model/checkpoints/epoch=102.ckpt")
    file_name = "template/my_component/frontend/src/audio/3321821.wav"
    sound = pydub.AudioSegment.from_wav(file_name)
    sound = sound.set_channels(1).set_frame_rate(16000)
    audio = np.array(sound.get_array_of_samples())/32768

    last_rows = np.zeros((1,1))
    chart = st.line_chart(last_rows)
    text_output = st.empty()


    streaming_decoder = StreamingDecoder(model)
    frame_number = 0

    #p = multiprocessing.Process(target=playsound.playsound, args=(file_name,)) 

    #play_obj = wave_obj.play()

    start_0 = timeit.default_timer()
    was_clicked = my_component("test", key="foo")
    
    if was_clicked:
        for i in range(0, len(audio), 1000):
            # while (num_clicks%2 == 0):
            #     time.sleep(0.1)
            start = timeit.default_timer()
            
            for probs in streaming_decoder.process_audio(audio[i: i+1000]):
                new_rows = np.zeros((1, 1))
                new_rows[0,0] = probs[1].detach().numpy()
                chart.add_rows(new_rows)

                
                frame_number += 1


            end = timeit.default_timer()
            # text_output.markdown(f"{end-start_0} seconds")
            time.sleep(max(0,1/16-end+start))
        # st.button("Re-run")