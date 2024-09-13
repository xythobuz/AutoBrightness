var win = workspace.activeWindow;
var name = win.caption;
var pid = win.pid;
var state = (win.bufferGeometry == win.output.geometry);
var obj = { name: name, pid: pid, fullscreen: state };
print(JSON.stringify(obj));
