import numpy as np

import wavio
import pyaudio

def save_audio(data, file_path: str, sample_rate: int):
    """ Saves data as wave file 

        Keyword Arguments:
        ==================
        - data (np.array) -- audio data
        - file_path (str) -- path of the file to be created
        - sample_rate (int) -- audio sample rate
    """
    data = np.squeeze(data)
    wavio.write(file_path, data, sample_rate)

class Player:
    """ A Class designed to play sound from a raw buffer or a wave file. 
    
    See Player.play_from_buffer and PLayer.play_from_file
    """
    chunk_size = 1024,
    def __init__(self):
        self.audio = pyaudio.PyAudio()
    
    def play_from_buffer(self, buffer, sample_rate: int=16000, channel: int=1):
        """ Plays sound from an audio buffer 

        Keyword Arguments:
        ==================
        - buffer (np.array) -- audio data
        - sample_rate (int) -- output player sample rate (default 16000)
        - channel (int) -- number of channels (default 1)
        """
        stream = self.audio.open(format=pyaudio.paInt16,
                        channels=channel,
                        rate=sample_rate,
                        output=True)
        stream.write(buffer)
        stream.close()

    def play_from_file(self, file_path):
        """ Plays sound from a wave file
        
        Keyword Arguments:
        ==================     
        - file_path (str) -- wave file path
        """
        try:
            wav = wavio.read(file_path)
        except:
            print('Cannot read {}'.format(file_path))
        else:
            stream = self.audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=wav.rate,
                        output=True)
            stream.write(bytes(wav.data))
            stream.close()