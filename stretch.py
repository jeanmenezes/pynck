#!/usr/bin/env python
#
# Paul's Extreme Sound Stretch (Paulstretch) - Python version
#
# by Nasca Octavian PAUL, Targu Mures, Romania
# http://www.paulnasca.com/
#
# http://hypermammut.sourceforge.net/paulstretch/
#
# this file is released under Public Domain
#
#

from numpy import *
import scipy.io.wavfile
import wave
import sys

def load_wav(filename):
    try:
        toload = wave.open(filename, 'r')
        towrite = wave.open("stripped.wav", 'w')
        towrite.setparams(toload.getparams())
        towrite.writeframes(toload.readframes(toload.getnframes()))
        toload.close()
        towrite.close()
        wavedata=scipy.io.wavfile.read("stripped.wav")
        samplerate=int(wavedata[0])
        smp=wavedata[1]*(1.0/32768.0)
        smp=smp.transpose()
        if len(smp.shape)==1: #convert to stereo
            smp=tile(smp,(2,1))
        return (samplerate,smp)
    except:
        print ("Error loading wav: "+filename)
        return None



def optimize_windowsize(n):
    orig_n=n
    while True:
        n=orig_n
        while (n%2)==0:
            n/=2
        while (n%3)==0:
            n/=3
        while (n%5)==0:
            n/=5

        if n<2:
            break
        orig_n+=1
    return orig_n


def paulstretch(samplerate,smp,stretch,windowsize_seconds,outfilename):
    nchannels=smp.shape[0]

    outfile=wave.open(outfilename,"wb")
    outfile.setsampwidth(2)
    outfile.setframerate(samplerate)
    outfile.setnchannels(nchannels)

    #make sure that windowsize is even and larger than 16
    windowsize=int(windowsize_seconds*samplerate)
    if windowsize<16:
        windowsize=16
    windowsize=optimize_windowsize(windowsize)
    windowsize=int(windowsize/2)*2
    half_windowsize=int(windowsize/2)

    #correct the end of the smp
    nsamples=smp.shape[1]
    end_size=int(samplerate*0.05)
    if end_size<16:
        end_size=16

    smp[:,nsamples-end_size:nsamples]*=linspace(1,0,end_size)


    #compute the displacement inside the input file
    start_pos=0.0
    displace_pos=(windowsize*0.5)/stretch

    #create Window window
    window=pow(1.0-pow(linspace(-1.0,1.0,windowsize),2.0),1.25)

    old_windowed_buf=zeros((2,windowsize))

    while True:
        #get the windowed buffer
        istart_pos=int(floor(start_pos))
        buf=smp[:,istart_pos:istart_pos+windowsize]
        if buf.shape[1]<windowsize:
            buf=append(buf,zeros((2,windowsize-buf.shape[1])),1)
        buf=buf*window

        #get the amplitudes of the frequency components and discard the phases
        freqs=abs(fft.rfft(buf))

        #randomize the phases by multiplication with a random complex number with modulus=1
        ph=random.uniform(0,2*pi,(nchannels,freqs.shape[1]))*1j
        freqs=freqs*exp(ph)

        #do the inverse FFT
        buf=fft.irfft(freqs)

        #window again the output buffer
        buf*=window

        #overlap-add the output
        output=buf[:,0:half_windowsize]+old_windowed_buf[:,half_windowsize:windowsize]
        old_windowed_buf=buf

        #remove the resulted amplitude modulation
        #update: there is no need to the new windowing function
        #output*=hinv_buf

        #clamp the values to -1..1
        output[output>1.0]=1.0
        output[output<-1.0]=-1.0

        #write the output to wav file
        outfile.writeframes(int16(output.ravel(1)*32767.0).tostring())

        start_pos+=displace_pos
        if start_pos>=nsamples:
            print ("100 %")
            break
        sys.stdout.write ("%d %% \r" % int(100.0*start_pos/nsamples))
        sys.stdout.flush()

    outfile.close()
