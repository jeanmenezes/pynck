// chuck this with other shreds to record to file
// example> chuck foo.ck bar.ck rec (see also rec2.ck)

// pull samples from the dac
// WvOut2 -> stereo operation
dac => WvOut2 w => blackhole;

// set the prefix, which will prepended to the filename
// do this if you want the file to appear automatically
// in another directory.  if this isn't set, the file
// should appear in the directory you run chuck from
// with only the date and time.

// this is the output file name
me.arg(0) => w.wavFilename;
me.arg(1).toFloat() => float duration;

// print it out
<<<"writing to file: ", w.filename()>>>;

// any gain you want for the output
.75 => w.fileGain;

// temporary workaround to automatically close file on remove-shred
null @=> w;

now + duration::second => time later;

// infinite time loop...
// ctrl-c will stop it, or modify to desired duration
while( now <= later ) { 1::ms => now; }

0.5::second => now;
