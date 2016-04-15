'''
Created on May 13, 2012

@author: Anthony Honstain
'''

import os
import unittest
from uploadresults.rcscoringprotxtparser import RCScoringProTXTParser

# Switch to the current directory where all the tests files are located.
os.chdir(os.path.dirname(__file__))


class TestSingleRaceSimpleTextFile(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_SingleRaceSimple.txt"
        with open(os.path.join(os.getcwd(), self.filename)) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_filename(self):
        self.assertEqual(self.filename, self.singe_test_race.filename)

    def test_racerOne(self):
        # Note - this test verifies racer one, it expects empty laps at the end
        # (since he did not complete the same number of laps as the leader).
        expectedLaps = ["24.5", "18.04", "17.53", "17.34", "17.13", "17.30", "17.21", "17.42", "17.14", "17.18", "17.47", "17.01", "17.21", "19.16", "17.03", "19.43", "17.24", "17.43", "17.31", "16.90", "17.33", "17.17", "24.36", "21.31", "17.24", "17.02", "20.17", ""]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[0])

    def test_racerTwo(self):
        expectedLaps = ["20.58", "17.09", "16.93", "17.11", "17.25", "17.25", "16.99", "17.44", "17.33", "17.56", "17.31", "17.35", "18.07", "17.31", "18.23", "17.40", "17.32", "17.15", "17.31", "17.47", "17.31", "17.42", "18.37", "17.47", "17.34", "17.36", "17.27", "17.14"]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[1])

    def test_racerTen(self):
        expectedLaps = ["23.92", "18.13", "17.26", "19.10", "18.50", "17.19", "19.47", "17.26", "17.34", "22.36", "17.75", "19.70", "18.20", "21.60", "17.80", "17.22", "17.19", "17.65", "17.12", "17.58", "18.30", "17.48", "17.91", "17.49", "23.20", "17.66", "", ""]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[9])

    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.singe_test_race.trackName)
        self.assertEqual("MODIFIED BUGGY", self.singe_test_race.raceClass)
        self.assertEqual(2, self.singe_test_race.mainEvent)
        self.assertEqual(None, self.singe_test_race.mainEventRoundNum)
        self.assertEqual("B Main", self.singe_test_race.mainEventParsed)
        self.assertEqual("3", self.singe_test_race.roundNumber)
        self.assertEqual("16", self.singe_test_race.raceNumber)

        self.assertEqual(self.singe_test_race.raceHeaderData[-1],
                         {"Driver": "TOM WAGGONER",
                          "Car#": 9,
                          "Laps": 26,
                          "RaceTime": "8:07.943",
                          "Fast Lap": "17.063",
                          "Behind": "6.008",
                          "Final Position": 10})


class TestMoreThanTenTextFile(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_12manrace.txt"
        with open(self.filename) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_filename(self):
        self.assertEqual(self.filename, self.singe_test_race.filename)

    def test_columns(self):
        expected_column_line = " ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__ ___11__ ___12__ ___13__ ___14__ ___15__ ___16__ ___17__ ___18__ ___19__ ___20__"
        self.assertEqual(expected_column_line, self.singe_test_race._columnHeaders)

    def test_racerTwelve(self):
        expectedLaps = ["26.71", "17.82", "17.47", "17.55", "16.88", "18.07", "18.56", "17.64", "17.28", "22.71", "23.33", "20.20", "17.49", "17.80", "17.27", "17.59", "17.98", "17.97", "20.91", "18.00", "19.47", "20.52", "19.17", "17.08", "17.42", "20.00", "", "", "", ]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[11])


class TestSingleRaceModified(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_SingleRaceModified.txt"
        with open(self.filename) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_racerOne(self):
        # Note - this test verifies racer one, it expects empty laps at the end
        # (since he did not complete the same number of laps as the leader).
        expectedLaps = ["35.00", "15.85", "", "15.79", "15.90", "16.06", "15.85", "15.86", "16.16", "17.00", "15.82", "16.32", "16.23", "17.29", "18.50", "16.30", "16.60", "18.49", "16.06", "16.56", "15.98", "16.39"]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[0])

    def test_racerFour(self):
        expectedLaps = ["20.26", "17.01", "16.73", "16.16", "16.08", "16.59", "16.68", "16.48", "16.19", "16.08", "16.32", "16.75", "16.31", "16.60", "16.60", "16.11", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[3])

    def test_racerTen(self):
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(len(expectedLaps), len(self.singe_test_race.lapRowsTime[9]))
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[9])

    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.singe_test_race.trackName)
        self.assertEqual("4WD MODIFIED", self.singe_test_race.raceClass)
        self.assertEqual(1, self.singe_test_race.mainEvent)
        self.assertEqual(2, self.singe_test_race.mainEventRoundNum)
        self.assertEqual("3", self.singe_test_race.roundNumber)
        self.assertEqual("30", self.singe_test_race.raceNumber)

        self.assertEqual(self.singe_test_race.raceHeaderData[-1],
                         {"Driver": "MATESA, TANNER",
                          "Car#": 9,
                          "Laps": 4,
                          "RaceTime": "1:20.392",
                          "Fast Lap": "17.097",
                          "Behind": "",
                          "Final Position": 9})


class TestSingleRaceRacerDropped(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_SingleRace_EarlyDrop.txt"
        with open(self.filename) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_racerOne(self):
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[0])

        self.assertEqual(2, self.singe_test_race.mainEvent)

    def test_racerTwo(self):
        expectedLaps = ["24.85", "20.00", "20.41", "19.97", "20.28", "20.27", "20.29", "20.27", "20.00", "19.14", "20.27", "19.92", "23.70", "20.33", "21.26", "22.50"]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[1])

    def test_initial_processing(self):

        expected_column_line = " ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__"
        self.assertEqual(expected_column_line, self.singe_test_race._columnHeaders)

        expected_lap_lines = ['         1/24.85 3/27.50 2/26.13                                                ',
                              '         1/20.00 3/20.19 2/21.22                                                ',
                              '         1/20.41 2/21.93 3/22.72                                                ',
                              '         1/19.97 3/24.01 2/21.98                                                ',
                              '         1/20.28 3/20.81 2/20.87                                                ',
                              '         1/20.27 3/19.15 2/20.24                                                ',
                              '         1/20.29 3/21.15 2/19.61                                                ',
                              '         1/20.27 2/21.07 3/25.53                                                ',
                              '         1/20.00 2/21.00 3/20.11                                                ',
                              '         1/19.14 2/22.12 3/20.78                                                ',
                              '         1/20.27 3/20.87 2/19.54                                                ',
                              '         1/19.92 3/20.39 2/21.28                                                ',
                              '         1/23.70 3/23.00 2/21.27                                                ',
                              '         1/20.33 3/20.16 2/20.78                                                ',
                              '         1/21.26         2/22.43                                                ',
                              '         1/22.50                                                                ']
        self.assertEqual(expected_lap_lines, self.singe_test_race._lapRowsRaw)

        expected_header_data = ['Scoring Software by www.RCScoringPro.com                8:29:37 PM  01/14/2012\n',
                                '\n',
                                '                               TACOMA R/C RACEWAY\n',
                                '\n',
                                'MODIFIED SHORT COURSE B Main                                  Round# 3, Race# 18\n',
                                '\n',
                                '________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_\n',
                                'JONES, GREG\t\t\t#2 \t\t16\t\t 5:33.539\t\t 19.147\t\t          \n',
                                'LEONARD, DMITRI\t\t\t#4 \t\t15\t\t 5:24.548\t\t 19.540\t\t          \n',
                                'KILE, CORRY\t\t\t#3 \t\t14\t\t 5:03.416\t\t 19.153\t\t          \n',
                                'MIKE CRAIG\t\t\t#1 \t\t 0\t\t    0.000\t\t       \t\t          \n',
                                '\n']
        self.assertEqual(expected_header_data, self.singe_test_race._raceHeaderData_RAW)


class TestSingleRaceBrokeRacer(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_SingleRace_BrokeRacer.txt"
        with open(self.filename) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.singe_test_race.trackName)
        self.assertEqual("4WD MODIFIED", self.singe_test_race.raceClass)
        self.assertEqual(1, self.singe_test_race.mainEvent)
        self.assertEqual("3", self.singe_test_race.roundNumber)
        self.assertEqual("22", self.singe_test_race.raceNumber)

        # Gilley, Tres            #10         1           21.675
        self.assertEqual(self.singe_test_race.raceHeaderData[9],
                         {"Driver": "Gilley, Tres",
                          "Car#": 10,
                          "Laps": 1,
                          "RaceTime": "",
                          "Fast Lap": "",
                          "Behind": "",
                          "Final Position": 10})
        # SCHOETLER, MICHAEL            #1         23         6:15.854         15.552
        self.assertEqual(self.singe_test_race.raceHeaderData[0],
                         {"Driver": "SCHOETLER, MICHAEL",
                          "Car#": 1,
                          "Laps": 23,
                          "RaceTime": "6:15.854",
                          "Fast Lap": "15.552",
                          "Behind": "",
                          "Final Position": 1})


class TestSingleRaceWithPaceData(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_SingleRace_PaceData.txt"
        with open(self.filename) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_racer4_laptimes(self):
        # 18 laps
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[3])


class TestElevenManPaceData(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_SingleRace_11manPaceData.txt"
        with open(self.filename) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_racer3_laptimes(self):
        # 23 laps
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[2])

    def test_racer12_laptimes(self):
        # 23 laps
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[11])

    def test_racer7_laptimes(self):
        # 23 laps
        expectedLaps = ["254.2", "23.01", "28.15", "23.90", "21.09", "21.30", "22.15", "26.00", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[6])


class TestOldBremertonFromat(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_SingleRace_OldBremertonFormat.txt"
        with open(self.filename) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_headerData(self):
        # RankedRacer1    #2      12     6:22.032     30.964
        self.assertEqual(self.singe_test_race.raceHeaderData[0],
                         {"Driver": "RankedRacer1",
                          "Car#": 2,
                          "Laps": 12,
                          "RaceTime": "6:22.032",
                          "Fast Lap": "30.964",
                          "Behind": "",
                          "Final Position": 1})
        # RankedRacer2    #1      10     6:17.466     34.078
        self.assertEqual(self.singe_test_race.raceHeaderData[1],
                         {"Driver": "RankedRacer2",
                          "Car#": 1,
                          "Laps": 10,
                          "RaceTime": "6:17.466",
                          "Fast Lap": "34.078",
                          "Behind": "",
                          "Final Position": 2})


class TestPoundCharInRacername(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_SingleRace_InvalidChars.txt"
        with open(self.filename) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_headerData(self):
        # Race Driver1    #2      13     5:12.435     22.964
        self.assertEqual(self.singe_test_race.raceHeaderData[0],
                         {"Driver": "Race Driver1",
                          "Car#": 2,
                          "Laps": 13,
                          "RaceTime": "5:12.435",
                          "Fast Lap": "22.964",
                          "Behind": "",
                          "Final Position": 1})

class TestBrokenLapTimes(unittest.TestCase):

    def setUp(self):
        self.filename = "TestFile_SingleRace_BrokenLapTimes.txt"
        with open(self.filename) as f:
            content = f.readlines()
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_headerData(self):
        self.assertEqual(self.singe_test_race.lapRowsTime[0], ['3.514'])


if __name__ == '__main__':
    unittest.main()
