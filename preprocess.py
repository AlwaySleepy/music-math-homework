import music21 as ms
import numpy as np
import os
from population import Individual, Population
from constants import *
from fitfunction import FitFunction

# write hleper functions or classes freely when needed
# remember to name them as _example_method()
# you can change the parameters of methods begin with _

class Converter:
    """
    Class for converting data between music files and arrays
    """
    def __init__(self):
        # change this part when in need
        pass

    def music2arrays(self, file: str) -> np.ndarray:
        """
        Convert the given file to an numpy array
        """
        stream = ms.converter.parse(DATAPATH + file)
        array = np.array([], dtype=np.int64)

        for note in stream.flatten().notes:
            pitch = note.pitch.midi

            duration = note.duration.quarterLength
            duration = (duration * 2) - 1
            assert int(duration) == duration
            duration = int(duration)

            array = np.append(array, pitch)
            for dur in range(duration):
                array = np.append(array, EXTEND[0])

        array = np.reshape(array, (-1, 8))
        # the array will be like:[[60,-1,-1,-1,72,-1,-1,-1],
        #                         [56,-1,58,-1,59,68,60,60],...]
        return array

    def individual2music(self, result: Individual, file_path: str) -> None:
        """
        Convert <result> to a music file, and save it in <file_path>
        If file_path is an empty string, then show it instead of save it.
        """
        melody = result.melody
        measures = list(map(self._to_measure, melody))

        stream = ms.stream.Stream(measures)
        stream.metadata = ms.metadata.Metadata()
        stream.metadata.title = 'Test'
        stream.metadata.composer = 'None'
        stream.insert(0, ms.meter.TimeSignature('4/4'))
        stream.insert(0, ms.key.Key('C'))

        if file_path == '':
            stream.show()
        else:
            stream.write('xml', DATAPATH + file_path)

    def _to_measure(self, melody: np.ndarray) -> ms.stream.Measure:
        """ Convert a 1d array to a measure in key of C """
        m = ms.stream.Measure()
        m.keySignature = ms.key.KeySignature(0)
        for data in melody:
            if data in EXTEND:
                # TODO: Here I add a rest to the measure if the
                # beginning element is EXTEND. Need to change it
                # to the last note of previous measure. Maybe do
                # this in individual2music method or in a new method
                if len(m) == 0:
                    m.append(ms.note.Rest('eighth'))
                    continue
                m[-1].duration.quarterLength += 0.5
            else:  # add a new note
                note = ms.note.Note(data)
                note.duration.quarterLength = 0.5
                # note.volume.velocity = 64  # from 0 to 127
                # note.activeSite.instrument.midiProgram = 0  # 0 means piano
                m.append(note)
        return m

    def array2music(self, arr: np.ndarray, file_path: str) -> None:
        """
        Convert <arr> to a music file, and save it in <file_path>
        If file_path is an empty string, then show it instead of save it.

        Note that <arr> can be either array of strings or array of numbers.
        """
        self.individual2music(Individual(arr), file_path)

    def generate_population(self, file_paths: list[str]) -> Population:
        """
        Read the files in <file_paths> and generate a Population
        consisting of them
        """
        if file_paths == []:
            raise Exception("Cannot convert empty file list to population")

        members = []
        for file in file_paths:
            array = self.music2arrays(file)
            members.append(Individual(array))
        population = Population(members, FitFunction(), MUTATE_RATE)
        return population

if __name__ == '__main__':
    if 'data' not in os.listdir('.'):
        os.mkdir('data/')
    converter = Converter()
    test_melody = np.array([
            ['C', '', '', 'D', 'E', '', '', 'C'],
            ['E', '', 'C', '', 'E', '', '', ''],
            ['D', '', '', 'E', 'F', 'F', 'E', 'D'],
            ['F', '', '', '', '', '', '', ''],
            ['E', '', '', 'F', 'G', '', '', 'E'],
            ['G', '', 'E', '', 'G', '', '', ''],
            ['F', '', '', 'G', 'A', 'A', 'G', 'F'],
            ['A', '', '', '', '', '', '', ''],
            ['G', '', '', 'C', 'D', 'E', 'F', 'G'],
            ['A', '', '', '', '', '', '', ''],
            ['A', '', '', 'D', 'E', 'F', 'G', 'A'],
            ['B', '', '', '', '', '', '', ''],
            ['B', '', '', 'E', 'F', 'G', 'A', 'B'],
            ['C5', '', '', '', '', '', 'C5', 'B'],
            ['A', '', 'F', '', 'B', '', 'G', ''],
            ['C5', '', 'G', '', 'E', '', 'D', '']])
    test_ind = Individual(test_melody)
    converter.individual2music(test_ind, 'test.xml')
    test_ind = Individual(converter.music2arrays('test.xml'))
    test_ind.mutate(1)
    test_ind.mutate(2)
    test_ind.mutate(2)
    print(test_ind.melody)
    converter.individual2music(test_ind, '')
    # print(converter.generate_population(['test.xml']).adaptibilty)
