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

now + s1.length() => time later;

complex Z[FFT_SIZE/2];

while( now < later ) {
    fftx.upchuck() @=> blobX;
    ffty.upchuck() @=> blobY;
    blobX.fvals() @=> float Xmag[];
    blobY.fvals() @=> float Ymag[];
    blobY.cvals() @=> complex Yspec[];

    for ( 0 => int i; i < Xmag.cap(); i++ ) {
        Xmag[i] * ( Yspec[i] / Ymag[i] ) => Z[i];
    }
    ifft.transform(Z);
    HOP_SIZE::samp => now;
 }
