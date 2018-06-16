FoxDot
{

	classvar server;
	classvar midiout;

	*start
	{

		server = Server.default;

		server.options.memSize = 8192 * 16; // increase this if you get "alloc failed" messages
		server.options.maxNodes = 1024 * 32; // increase this if you are getting drop outs and the message "too many nodes"
		server.options.numOutputBusChannels = 2; // set this to your hardware output channel size, if necessary
		server.options.numInputBusChannels = 2; // set this to your hardware output channel size, if necessary
		server.boot();

		OSCFunc(
			{
				arg msg, time, addr, port;
				var fn;

				// Get local filename

				fn = msg[1].asString;

				// Print a message to the user

				("Loading SynthDef from" + fn).postln;

				// Add SynthDef to file

				fn = File(fn, "r");
				fn.readAllString.interpret;
				fn.close;

			},
			'foxdot'
		);

		StageLimiter.activate(2);

		"Listening for messages from FoxDot".postln;
	}

	*midi
	{
		arg port=[0];
		var m;

		MIDIClient.init;

		~midiout_tmp = [].grow(port.size);
		port.do({ arg item, i;  m = MIDIOut.newByName(item, item); ~midiout_tmp.add(m); m.postln;});

		OSCFunc(
			{
				arg msg, time, addr, port;
				var note, vel, sus, channel, nudge;

				// listen for specific MIDI trigger messages from FoxDot

				note    = msg[2];
				vel     = msg[3];
				sus     = msg[4];
				channel = msg[5];
				nudge   = msg[6];

				SystemClock.schedAbs(time + nudge, {~midiout_tmp[msg[7]].noteOn(channel, note, vel)});
				SystemClock.schedAbs(time + nudge + sus, {~midiout_tmp[msg[7]].noteOff(channel, note, vel)});

			},
			'foxdot_midi'

		);
		//port.do({ arg item, i; ("Sending FoxDot MIDI "+i+" messages to" + MIDIClient.destinations[item].name).postln });

	}
}