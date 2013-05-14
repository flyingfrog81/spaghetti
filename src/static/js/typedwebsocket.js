
// Copyright (c) 2013 Marco Bartolini, marco.bartolini@gmail.com
//
// Permission is hereby granted, free of charge, to any person
// obtaining a copy of this software and associated documentation
// files (the "Software"), to deal in the Software without
// restriction, including without limitation the rights to use,
// copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following
// conditions:
//
// The above copyright notice and this permission notice shall be
// included in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
// OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
// NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
// OTHER DEALINGS IN THE SOFTWARE.
//
function typedWebSocket(url, dtype){
  var ws = new WebSocket(url);
  ws.binaryType = "arraybuffer";
  ws.data_type = dtype;
  switch(dtype){
    case "int8":
      ws.get_data = function(buffer){
         return new Int8Array(buffer);
      };
      break;
    case "int16":
      ws.get_data = function(buffer){
         return new Int16Array(buffer);
      };
      break;
    case "int32":
      ws.get_data = function(buffer){
         return new Int32Array(buffer);
      };
      break;
    case "uint8":
      ws.get_data = function(buffer){
         return new Uint8Array(buffer);
      };
      break;
    case "uint16":
      ws.get_data = function(buffer){
         return new Uint16Array(buffer);
      };
      break;
    case "uint32":
      ws.get_data = function(buffer){
         return new Uint32Array(buffer);
      };
      break;
    case "float32":
      ws.get_data = function(buffer){
         return new Float32Array(buffer);
      };
      break;
    case "float64":
      ws.get_data = function(buffer){
         return new Float64Array(buffer);
      };
      break;
    default:
      throw new Error("TypedArray does not support type: " + dtype);
  }
  ws.onmessage = function(evt){
    this.ondata(this.get_data(evt.data));
  }
  return ws;
}
