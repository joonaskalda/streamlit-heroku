import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
  } from "streamlit-component-lib"
  import createBuffer from "audio-buffer-from"
  import React, { ReactNode } from "react"
  import { 
    Table,
    FloatVector,
    DateVector
  } from 'apache-arrow';
  const Osoon = require("./audio/3321821.wav")
  interface State {
    numClicks: number
    isFocused: boolean
  }
  
  /**
   * This is a React-based component template. The `render()` function is called
   * automatically when your component should be re-rendered.
   */
  class MyComponent extends StreamlitComponentBase<State> {
    public state = { numClicks: 0, isFocused: false }
    public audio = new Audio(Osoon);
    
    public render = (): ReactNode => {
      //console.log(this.audio.src);
      // Arguments that are passed to the plugin in Python are accessible
      // via `this.props.args`. Here, we access the "name" arg.
      const name = this.props.args["name"]
      const fileName = this.props.args["audio"]
      if (fileName === "sample") {
        //this.audio.src = "./audio/3321821.wav" 
         const newAudio = new Audio(require("./audio/3321821.wav"));
         this.audio = newAudio;
        //  block of code to be executed if the condition is true
      } else {
        const newAudio = new Audio(require("./audio/" + fileName));
        this.audio = newAudio;
        //  block of code to be executed if the condition is false
      }
      console.log(this.audio.src);
      //debugger;
      // var audioElement = document.createElement("audio");
      // const audioBuffer = createBuffer(audio, { sampleRate: 16000 });
      // const blob = new Blob([audioBuffer], { type: "audio/wav" });
      // audioElement.src = window.URL.createObjectURL(blob);
      //this.audio = audioElement;
      //debugger;
      //console.log(audioElement.src)      
      
      // const LENGTH = 2000;

      // const rainAmounts = Float32Array.from(
      //   { length: LENGTH },
      //   () => Number((Math.random() * 20).toFixed(1)));

      // const rainDates = Array.from(
      //   { length: LENGTH },
      //   (_, i) => new Date(Date.now() - 1000 * 60 * 60 * 24 * i));

      // const rainfall = Table.new(
      //   [FloatVector.from(rainAmounts), DateVector.from(rainDates)],
      //   ['precipitation', 'date']
      // );

      // console.log(rainfall.getColumn('precipitation').toArray());


      // Streamlit sends us a theme object via props that we can use to ensure
      // that our component has visuals that match the active theme in a
      // streamlit app.
      const { theme } = this.props;
      const style: React.CSSProperties = {};

      // Maintain compatibility with older versions of Streamlit that don't send
      // a theme object.
      if (theme) {
        // Use the theme object to style our button border. Alternatively, the
        // theme style is defined in CSS vars.
        const borderStyling = `1px solid ${
          this.state.isFocused ? theme.primaryColor : "gray"
        }`
        style.border = borderStyling
        style.outline = borderStyling
      }
  
      // Show a button and some text.
      // When the button is clicked, we'll increment our "numClicks" state
      // variable, and send its new value back to Streamlit, where it'll
      // be available to the Python program.
      return (
        <span>
          {!this.state.numClicks && <div>
          <button
            style={style}
            onClick={this.onClicked}
            disabled={this.props.disabled}
            onFocus={this._onFocus}
            onBlur={this._onBlur}
          >
          Play
          </button></div>}
        </span>
      )
    }
  
    /** Click handler for our "Click Me!" button. */
    private onClicked = (): void => {
      // Increment state.numClicks, and pass the new value back to
      // Streamlit via `Streamlit.setComponentValue`.
      this.setState(
        prevState => ({ numClicks: prevState.numClicks + 1 }),
        () => {Streamlit.setComponentValue(this.state.numClicks);
          this.state.numClicks ? this.audio.play() : this.audio.pause()}
      )
    }
  
    /** Focus handler for our "Click Me!" button. */
    private _onFocus = (): void => {
      this.setState({ isFocused: true })
    }
  
    /** Blur handler for our "Click Me!" button. */
    private _onBlur = (): void => {
      this.setState({ isFocused: false })
    }
  }
  
  // "withStreamlitConnection" is a wrapper function. It bootstraps the
  // connection between your component and the Streamlit app, and handles
  // passing arguments from Python -> Component.
  //
  // You don't need to edit withStreamlitConnection (but you're welcome to!).
  export default withStreamlitConnection(MyComponent)
  