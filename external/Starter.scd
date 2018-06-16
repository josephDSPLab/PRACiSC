(
~suffix = "loopMIDI Port";
~numarray = Array.series(10, start: 1, step: 1);
~port_list = List.new(size:~numarray.size);
~numarray.do({arg items, idx; ~port_list.insert(idx,~suffix+items.asString());});
~port_list;
)

FoxDot.start;
~port_list;
FoxDot.midi(~port_list);

