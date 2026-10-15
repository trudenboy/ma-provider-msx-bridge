const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(require('node:path').join(require('node:path').dirname(process.argv[2]), 'bridge.js'), 'utf8');
let handler;
const browserWindow = {location: {protocol: 'http:', host: 'msx.test:8099'}, addEventListener: (name, fn) => events[name] = fn};
const sockets = [], actions = [], warnings = [], timeouts = new Map(), intervals = new Map();
const events = {};
let nextTimer = 1;
class WebSocket {
  static OPEN = 1;
  constructor(url) { this.url = url; this.readyState = 1; this.sent = []; sockets.push(this); }
  send(text) { this.sent.push(JSON.parse(text)); }
  close() { this.readyState = 3; if (this.onclose) this.onclose({code: 1000}); }
}
const context = {
  window: browserWindow,
  document: {querySelectorAll: () => [], body: {}},
  console: {log() {}, warn: (...args) => warnings.push(args)},
  localStorage: {getItem: () => 'smoke-tv'},
  WebSocket,
  tvx: {
    PluginTools: {onReady: callback => callback()},
    InteractionPlugin: {
      setupHandler: value => handler = value,
      init() {},
      executeAction: (...args) => actions.push(args)
    }
  },
  setTimeout: (fn, ms) => { const id = nextTimer++; timeouts.set(id, {fn, ms}); return id; },
  clearTimeout: id => timeouts.delete(id),
  setInterval: fn => { const id = nextTimer++; intervals.set(id, fn); return id; },
  clearInterval: id => intervals.delete(id)
};
browserWindow.tvx = context.tvx;
vm.runInNewContext(source, context, {filename: process.argv[2]});
handler = new browserWindow.MSXBridgeHandler();
let menu;
handler.handleRequest('init', null, value => menu = value.menu);
assert.equal(menu.length, 7);
assert.equal(sockets.length, 1);
let repeatMenu;
handler.handleRequest('init', null, value => repeatMenu = value.menu);
assert.equal(repeatMenu.length, 7);
assert.equal(sockets.length, 1);
const ws = sockets[0];
assert.equal(ws.url, 'ws://msx.test:8099/ws?device_id=smoke-tv');
ws.onopen();
assert.equal(timeouts.size, 0, 'connection must not schedule abandoned debug payloads');
ws.onmessage({data: JSON.stringify({type: 'playlist', url: '/msx/queue-playlist/msx_smoke.json', playback_id: 'p1', source_offset: 10, source_duration: 180, served_duration: 170})});
assert(actions.some(([action]) => action.startsWith('playlist:http://msx.test:8099/msx/queue-playlist/')));
handler.handleEvent({event: 'video:play'});
handler.handleEvent({event: 'video:pause'});
assert(ws.sent.some(message => message.type === 'resume' && message.playback_id === 'p1'));
assert(ws.sent.some(message => message.type === 'pause' && message.playback_id === 'p1'));
ws.onmessage({data: JSON.stringify({type: 'seek', position: 12})});
handler.handleEvent({event: 'video:seek', position: 12});
assert.equal(ws.sent.filter(message => message.type === 'seek').length, 0);
handler.handleEvent({event: 'video:seek', position: 25});
assert.equal(ws.sent.filter(message => message.type === 'seek').length, 1);
assert.equal(ws.sent.at(-1).position, 25);
assert(!ws.sent.some(message => message.type === 'debug_info'));
assert.equal(warnings.length, 0);
ws.onmessage({data: JSON.stringify({type: 'volume', level: 25})});
assert(actions.some(([action]) => action === 'volume:set:25'));
ws.onmessage({data: JSON.stringify({type: 'volume', level: 1000})});
assert.equal(actions.at(-1)[0], 'volume:set:100');
const beforeInvalidVolume = actions.length;
ws.onmessage({data: JSON.stringify({type: 'volume', level: 'oops'})});
assert.equal(actions.length, beforeInvalidVolume);
let inputReady = false;
const keyboardMessages = [];
context.InputHandler = function() {
  this.ready = () => { inputReady = true; };
  this.handleData = data => keyboardMessages.push(data.message);
};
context.TVXPluginTools = context.tvx.PluginTools;
context.TVXInteractionPlugin = context.tvx.InteractionPlugin;
context.TVXInteractionPlugin.init = () => handler.ready();
const inputSource = fs.readFileSync(require('node:path').join(require('node:path').dirname(process.argv[2]), 'input.js'), 'utf8');
vm.runInNewContext(inputSource.slice(inputSource.lastIndexOf('TVXPluginTools.onReady(function()')), context);
assert(inputReady);
assert.equal(sockets.filter(socket => socket.readyState === 1).length, 1);
const searchSocket = sockets.at(-1);
handler.handleData({message: 'input:a'});
assert.deepEqual(keyboardMessages, ['input:a']);
handler.handleEvent({event: 'video:pause'});
assert(searchSocket.sent.some(message => message.type === 'pause'));
events.pagehide();
assert.equal(searchSocket.readyState, 3);
assert.equal(intervals.size, 0);
assert.equal(timeouts.size, 0);
console.log('Client smoke passed: init/menu, WS open, queue playlist, native pause/resume/seek, seek echo suppression, pagehide cleanup.');
