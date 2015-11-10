SndBuf s1 => FFT fftx => blackhole;
SndBuf s2 => FFT ffty => blackhole;
IFFT ifft => dac;

me.arg(0) => s1.read;
me.arg(1) => s2.read;

1024 => fftx.size => ffty.size => int FFT_SIZE;
512 => int WIN_SIZE;
WIN_SIZE / 4 => int HOP_SIZE;
Windowing.hann(WIN_SIZE) => fftx.window;
Windowing.hann(WIN_SIZE) => ffty.window;
Windowing.hann(WIN_SIZE) => ifft.window;

UAnaBlob blobX;
UAnaBlob blobY;

int lesser;
1 => int count;
time later;

if ( s1.samples() < s2.samples() ) { 0 => lesser; now + s2.length() => later; }
else { 1 => lesser; now + s1.length() => later; }

complex Z[FFT_SIZE/2];

while( now < later ) {
    fftx.upchuck() @=> blobX;
    ffty.upchuck() @=> blobY;
    blobX.fvals() @=> float Xmag[];
    blobY.fvals() @=> float Ymag[];
    blobY.cvals() @=> complex Yspec[];

    for ( 0 => int i; i < Xmag.cap(); i++ ) {
        Math.sqrt( Xmag[i] ) * Yspec[i] => Z[i];
    }
    ifft.transform(Z);
    HOP_SIZE +=> count;
    HOP_SIZE::samp => now;
    if ( lesser == 0 ) { if ( count > s1.samples() ) { 1 => s1.pos => count; } }
    else { if ( count > s2.samples() ) { 1 => s2.pos => count; } } 
}
