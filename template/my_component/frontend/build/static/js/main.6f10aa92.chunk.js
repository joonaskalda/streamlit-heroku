(this.webpackJsonpstreamlit_component_template=this.webpackJsonpstreamlit_component_template||[]).push([[0],{14:function(t,e,n){t.exports=n(23)},22:function(t,e,n){t.exports=n.p+"static/media/3321821.cdc1a338.wav"},23:function(t,e,n){"use strict";n.r(e);var a=n(5),o=n.n(a),c=n(12),s=n.n(c),r=n(0),u=n(1),i=n(2),l=n(10),p=n(22),d=function(t){Object(u.a)(n,t);var e=Object(i.a)(n);function n(){var t;Object(r.a)(this,n);for(var a=arguments.length,c=new Array(a),s=0;s<a;s++)c[s]=arguments[s];return(t=e.call.apply(e,[this].concat(c))).state={numClicks:0,isFocused:!1},t.audio=new Audio(p),t.render=function(){t.props.args.name;var e=t.props.theme,n={};if(e){var a="1px solid ".concat(t.state.isFocused?e.primaryColor:"gray");n.border=a,n.outline=a}return o.a.createElement("span",null,!t.state.numClicks&&o.a.createElement("div",null,o.a.createElement("button",{style:n,onClick:t.onClicked,disabled:t.props.disabled,onFocus:t._onFocus,onBlur:t._onBlur},"Play")))},t.onClicked=function(){t.setState((function(t){return{numClicks:t.numClicks+1}}),(function(){l.a.setComponentValue(t.state.numClicks),t.state.numClicks?t.audio.play():t.audio.pause()}))},t._onFocus=function(){t.setState({isFocused:!0})},t._onBlur=function(){t.setState({isFocused:!1})},t}return n}(l.b),m=Object(l.c)(d);s.a.render(o.a.createElement(o.a.StrictMode,null,o.a.createElement(m,null)),document.getElementById("root"))}},[[14,1,2]]]);
//# sourceMappingURL=main.6f10aa92.chunk.js.map