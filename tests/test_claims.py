"""Jede Zahl aus der README wird hier über dieselben Auswertungsfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Netze der Messreihen: die acht festen Netze `SWEEP_SEEDS` je Zelle, n = 200 (Experiment 2: 120; Experiment 3: vollständiger Graph mit 400 Betrieben; Experiment 4: 240 Betriebe, c = 12), c = 6, zufälliger
Start (Experiment 1 und 2), Median über die Netze. Alle Läufe sind deterministisch (feste Seeds, Mittelung ohne Zufall im Verfahren selbst); Lager, Gruppen und Anteile stehen auf zwei bzw. vier
Nachkommastellen, die Bänder fangen die Rundung."""

from functools import lru_cache

import pytest

import bvt_constants as C
import bvt_evaluation as ev

SW = C.SWEEP_SEEDS
N, CC, ORDER_N = 200, 6, 120
EXPECT = {'E1': [{'typ': 'Vollständig (jeder kennt jeden)',
         'eps': 0.1,
         'camps': 4.0,
         'largest': 0.3125,
         'groups': 4.0,
         'consensus': 0.0,
         'steps': 7.0,
         'converged': True,
         'nets': 8},
        {'typ': 'Vollständig (jeder kennt jeden)',
         'eps': 0.15,
         'camps': 2.5,
         'largest': 0.505,
         'groups': 2.5,
         'consensus': 0.0,
         'steps': 7.0,
         'converged': True,
         'nets': 8},
        {'typ': 'Vollständig (jeder kennt jeden)',
         'eps': 0.2,
         'camps': 2.0,
         'largest': 0.5475,
         'groups': 2.0,
         'consensus': 0.125,
         'steps': 6.5,
         'converged': True,
         'nets': 8},
        {'typ': 'Vollständig (jeder kennt jeden)',
         'eps': 0.25,
         'camps': 1.0,
         'largest': 1.0,
         'groups': 1.0,
         'consensus': 0.875,
         'steps': 9.5,
         'converged': True,
         'nets': 8},
        {'typ': 'Vollständig (jeder kennt jeden)', 'eps': 0.3, 'camps': 1.0, 'largest': 1.0, 'groups': 1.0, 'consensus': 1.0, 'steps': 4.0, 'converged': True, 'nets': 8},
        {'typ': 'Vollständig (jeder kennt jeden)', 'eps': 0.4, 'camps': 1.0, 'largest': 1.0, 'groups': 1.0, 'consensus': 1.0, 'steps': 3.0, 'converged': True, 'nets': 8},
        {'typ': 'Vollständig (jeder kennt jeden)', 'eps': 0.5, 'camps': 1.0, 'largest': 1.0, 'groups': 1.0, 'consensus': 1.0, 'steps': 2.0, 'converged': True, 'nets': 8},
        {'typ': 'Zufallsnetz', 'eps': 0.1, 'camps': 3.0, 'largest': 0.3484, 'groups': 61.5, 'consensus': 0.0, 'steps': 1396.0, 'converged': True, 'nets': 8},
        {'typ': 'Zufallsnetz', 'eps': 0.15, 'camps': 2.0, 'largest': 0.6583, 'groups': 22.5, 'consensus': 0.0, 'steps': 615.5, 'converged': True, 'nets': 8},
        {'typ': 'Zufallsnetz', 'eps': 0.2, 'camps': 1.0, 'largest': 0.9298, 'groups': 13.0, 'consensus': 0.0, 'steps': 155.5, 'converged': True, 'nets': 8},
        {'typ': 'Zufallsnetz', 'eps': 0.25, 'camps': 1.0, 'largest': 0.9623, 'groups': 8.0, 'consensus': 0.0, 'steps': 111.5, 'converged': True, 'nets': 8},
        {'typ': 'Zufallsnetz', 'eps': 0.3, 'camps': 1.0, 'largest': 0.9774, 'groups': 5.5, 'consensus': 0.0, 'steps': 99.5, 'converged': True, 'nets': 8},
        {'typ': 'Zufallsnetz', 'eps': 0.4, 'camps': 1.0, 'largest': 0.9925, 'groups': 2.5, 'consensus': 0.5, 'steps': 93.5, 'converged': True, 'nets': 8},
        {'typ': 'Zufallsnetz', 'eps': 0.5, 'camps': 1.0, 'largest': 1.0, 'groups': 1.0, 'consensus': 1.0, 'steps': 94.0, 'converged': True, 'nets': 8},
        {'typ': 'Potenzgesetz-Netz', 'eps': 0.1, 'camps': 3.0, 'largest': 0.2225, 'groups': 96.5, 'consensus': 0.0, 'steps': 463.5, 'converged': True, 'nets': 8},
        {'typ': 'Potenzgesetz-Netz', 'eps': 0.15, 'camps': 2.0, 'largest': 0.45, 'groups': 59.5, 'consensus': 0.0, 'steps': 408.0, 'converged': True, 'nets': 8},
        {'typ': 'Potenzgesetz-Netz', 'eps': 0.2, 'camps': 1.0, 'largest': 0.7775, 'groups': 37.5, 'consensus': 0.0, 'steps': 341.0, 'converged': True, 'nets': 8},
        {'typ': 'Potenzgesetz-Netz', 'eps': 0.25, 'camps': 1.0, 'largest': 0.8575, 'groups': 25.5, 'consensus': 0.0, 'steps': 157.5, 'converged': True, 'nets': 8},
        {'typ': 'Potenzgesetz-Netz', 'eps': 0.3, 'camps': 1.0, 'largest': 0.905, 'groups': 18.5, 'consensus': 0.0, 'steps': 145.5, 'converged': True, 'nets': 8},
        {'typ': 'Potenzgesetz-Netz', 'eps': 0.4, 'camps': 1.0, 'largest': 0.965, 'groups': 7.5, 'consensus': 0.125, 'steps': 145.0, 'converged': True, 'nets': 8},
        {'typ': 'Potenzgesetz-Netz', 'eps': 0.5, 'camps': 1.0, 'largest': 1.0, 'groups': 1.0, 'consensus': 0.625, 'steps': 140.5, 'converged': True, 'nets': 8},
        {'typ': 'Skalenfreies Netz (BA)', 'eps': 0.1, 'camps': 3.0, 'largest': 0.2675, 'groups': 72.0, 'consensus': 0.0, 'steps': 479.5, 'converged': True, 'nets': 8},
        {'typ': 'Skalenfreies Netz (BA)', 'eps': 0.15, 'camps': 2.0, 'largest': 0.5025, 'groups': 38.5, 'consensus': 0.0, 'steps': 889.0, 'converged': True, 'nets': 8},
        {'typ': 'Skalenfreies Netz (BA)', 'eps': 0.2, 'camps': 1.0, 'largest': 0.9075, 'groups': 19.5, 'consensus': 0.0, 'steps': 146.5, 'converged': True, 'nets': 8},
        {'typ': 'Skalenfreies Netz (BA)', 'eps': 0.25, 'camps': 1.0, 'largest': 0.94, 'groups': 12.5, 'consensus': 0.0, 'steps': 98.0, 'converged': True, 'nets': 8},
        {'typ': 'Skalenfreies Netz (BA)', 'eps': 0.3, 'camps': 1.0, 'largest': 0.9625, 'groups': 8.0, 'consensus': 0.0, 'steps': 92.0, 'converged': True, 'nets': 8},
        {'typ': 'Skalenfreies Netz (BA)', 'eps': 0.4, 'camps': 1.0, 'largest': 0.985, 'groups': 4.0, 'consensus': 0.25, 'steps': 86.0, 'converged': True, 'nets': 8},
        {'typ': 'Skalenfreies Netz (BA)', 'eps': 0.5, 'camps': 1.0, 'largest': 1.0, 'groups': 1.0, 'consensus': 1.0, 'steps': 84.5, 'converged': True, 'nets': 8},
        {'typ': 'Verbünde', 'eps': 0.1, 'camps': 3.0, 'largest': 0.335, 'groups': 69.5, 'consensus': 0.0, 'steps': 1085.5, 'converged': True, 'nets': 8},
        {'typ': 'Verbünde', 'eps': 0.15, 'camps': 2.0, 'largest': 0.6842, 'groups': 29.5, 'consensus': 0.0, 'steps': 603.5, 'converged': True, 'nets': 8},
        {'typ': 'Verbünde', 'eps': 0.2, 'camps': 1.0, 'largest': 0.9075, 'groups': 17.0, 'consensus': 0.0, 'steps': 250.5, 'converged': True, 'nets': 8},
        {'typ': 'Verbünde', 'eps': 0.25, 'camps': 1.0, 'largest': 0.935, 'groups': 12.5, 'consensus': 0.0, 'steps': 227.0, 'converged': True, 'nets': 8},
        {'typ': 'Verbünde', 'eps': 0.3, 'camps': 1.0, 'largest': 0.9698, 'groups': 7.0, 'consensus': 0.125, 'steps': 228.0, 'converged': True, 'nets': 8},
        {'typ': 'Verbünde', 'eps': 0.4, 'camps': 1.0, 'largest': 0.995, 'groups': 2.0, 'consensus': 0.75, 'steps': 213.5, 'converged': True, 'nets': 8},
        {'typ': 'Verbünde', 'eps': 0.5, 'camps': 1.0, 'largest': 1.0, 'groups': 1.0, 'consensus': 1.0, 'steps': 212.5, 'converged': True, 'nets': 8},
        {'typ': 'Ring mit Abkürzungen', 'eps': 0.1, 'camps': 2.0, 'largest': 0.0875, 'groups': 90.0, 'consensus': 0.0, 'steps': 706.0, 'converged': True, 'nets': 8},
        {'typ': 'Ring mit Abkürzungen', 'eps': 0.15, 'camps': 3.5, 'largest': 0.3, 'groups': 45.0, 'consensus': 0.0, 'steps': 2574.5, 'converged': True, 'nets': 8},
        {'typ': 'Ring mit Abkürzungen', 'eps': 0.2, 'camps': 1.0, 'largest': 0.825, 'groups': 20.5, 'consensus': 0.0, 'steps': 1805.5, 'converged': True, 'nets': 8},
        {'typ': 'Ring mit Abkürzungen', 'eps': 0.25, 'camps': 1.0, 'largest': 0.9025, 'groups': 13.0, 'consensus': 0.0, 'steps': 1356.0, 'converged': True, 'nets': 8},
        {'typ': 'Ring mit Abkürzungen', 'eps': 0.3, 'camps': 1.0, 'largest': 0.955, 'groups': 7.0, 'consensus': 0.0, 'steps': 1199.5, 'converged': True, 'nets': 8},
        {'typ': 'Ring mit Abkürzungen', 'eps': 0.4, 'camps': 1.0, 'largest': 0.99, 'groups': 3.0, 'consensus': 0.5, 'steps': 1100.5, 'converged': True, 'nets': 8},
        {'typ': 'Ring mit Abkürzungen', 'eps': 0.5, 'camps': 1.0, 'largest': 1.0, 'groups': 1.0, 'consensus': 1.0, 'steps': 1033.5, 'converged': True, 'nets': 8},
        {'typ': 'Gitter', 'eps': 0.1, 'camps': 2.0, 'largest': 0.0944, 'groups': 93.5, 'consensus': 0.0, 'steps': 1028.0, 'converged': True, 'nets': 8},
        {'typ': 'Gitter', 'eps': 0.15, 'camps': 3.5, 'largest': 0.2628, 'groups': 57.5, 'consensus': 0.0, 'steps': 4038.0, 'converged': True, 'nets': 8},
        {'typ': 'Gitter', 'eps': 0.2, 'camps': 2.0, 'largest': 0.6378, 'groups': 25.5, 'consensus': 0.0, 'steps': 3379.0, 'converged': True, 'nets': 8},
        {'typ': 'Gitter', 'eps': 0.25, 'camps': 2.0, 'largest': 0.8087, 'groups': 14.5, 'consensus': 0.0, 'steps': 2930.5, 'converged': True, 'nets': 8},
        {'typ': 'Gitter', 'eps': 0.3, 'camps': 1.0, 'largest': 0.9362, 'groups': 9.5, 'consensus': 0.0, 'steps': 2460.0, 'converged': True, 'nets': 8},
        {'typ': 'Gitter', 'eps': 0.4, 'camps': 1.0, 'largest': 0.9898, 'groups': 3.0, 'consensus': 0.375, 'steps': 2262.0, 'converged': True, 'nets': 8},
        {'typ': 'Gitter', 'eps': 0.5, 'camps': 1.0, 'largest': 1.0, 'groups': 1.0, 'consensus': 1.0, 'steps': 2255.5, 'converged': True, 'nets': 8}],
 'E2': {'eps': 0.2,
        'order': [{'typ': 'Vollständig (jeder kennt jeden)', 'reversed': 0, 'runs': 8, 'first': None},
                  {'typ': 'Zufallsnetz', 'reversed': 8, 'runs': 8, 'first': 1.0},
                  {'typ': 'Potenzgesetz-Netz', 'reversed': 8, 'runs': 8, 'first': 1.0},
                  {'typ': 'Skalenfreies Netz (BA)', 'reversed': 8, 'runs': 8, 'first': 1.0},
                  {'typ': 'Verbünde', 'reversed': 8, 'runs': 8, 'first': 1.0},
                  {'typ': 'Ring mit Abkürzungen', 'reversed': 8, 'runs': 8, 'first': 1.0},
                  {'typ': 'Gitter', 'reversed': 8, 'runs': 8, 'first': 1.0}],
        'identity': [{'typ': 'Vollständig (jeder kennt jeden)', 'max_dev': 6.66e-16, 'runs': 8},
                     {'typ': 'Zufallsnetz', 'max_dev': 4.8e-13, 'runs': 8},
                     {'typ': 'Potenzgesetz-Netz', 'max_dev': 1.93e-12, 'runs': 8},
                     {'typ': 'Skalenfreies Netz (BA)', 'max_dev': 5.27e-13, 'runs': 8},
                     {'typ': 'Verbünde', 'max_dev': 2.03e-12, 'runs': 8},
                     {'typ': 'Ring mit Abkürzungen', 'max_dev': 9.59e-12, 'runs': 8},
                     {'typ': 'Gitter', 'max_dev': 1.36e-11, 'runs': 8}]},
 'E3': {'n': 400,
        'equi': [{'eps': 0.1, 'camps': 4, 'largest': 0.2625, 'groups': 4, 'consensus': False},
                 {'eps': 0.1025, 'camps': 4, 'largest': 0.2575, 'groups': 4, 'consensus': False},
                 {'eps': 0.105, 'camps': 3, 'largest': 0.5, 'groups': 3, 'consensus': False},
                 {'eps': 0.1075, 'camps': 4, 'largest': 0.255, 'groups': 4, 'consensus': False},
                 {'eps': 0.11, 'camps': 3, 'largest': 0.475, 'groups': 3, 'consensus': False},
                 {'eps': 0.1125, 'camps': 3, 'largest': 0.465, 'groups': 3, 'consensus': False},
                 {'eps': 0.115, 'camps': 3, 'largest': 0.455, 'groups': 3, 'consensus': False},
                 {'eps': 0.1175, 'camps': 3, 'largest': 0.445, 'groups': 3, 'consensus': False},
                 {'eps': 0.12, 'camps': 3, 'largest': 0.43, 'groups': 3, 'consensus': False},
                 {'eps': 0.1225, 'camps': 3, 'largest': 0.42, 'groups': 3, 'consensus': False},
                 {'eps': 0.125, 'camps': 3, 'largest': 0.405, 'groups': 3, 'consensus': False},
                 {'eps': 0.1275, 'camps': 3, 'largest': 0.395, 'groups': 3, 'consensus': False},
                 {'eps': 0.13, 'camps': 3, 'largest': 0.38, 'groups': 3, 'consensus': False},
                 {'eps': 0.1325, 'camps': 3, 'largest': 0.37, 'groups': 3, 'consensus': False},
                 {'eps': 0.135, 'camps': 3, 'largest': 0.355, 'groups': 3, 'consensus': False},
                 {'eps': 0.1375, 'camps': 3, 'largest': 0.345, 'groups': 3, 'consensus': False},
                 {'eps': 0.14, 'camps': 3, 'largest': 0.335, 'groups': 3, 'consensus': False},
                 {'eps': 0.1425, 'camps': 3, 'largest': 0.34, 'groups': 3, 'consensus': False},
                 {'eps': 0.145, 'camps': 3, 'largest': 0.345, 'groups': 3, 'consensus': False},
                 {'eps': 0.1475, 'camps': 3, 'largest': 0.35, 'groups': 3, 'consensus': False},
                 {'eps': 0.15, 'camps': 3, 'largest': 0.355, 'groups': 3, 'consensus': False},
                 {'eps': 0.1525, 'camps': 3, 'largest': 0.36, 'groups': 3, 'consensus': False},
                 {'eps': 0.155, 'camps': 3, 'largest': 0.3675, 'groups': 3, 'consensus': False},
                 {'eps': 0.1575, 'camps': 3, 'largest': 0.3725, 'groups': 3, 'consensus': False},
                 {'eps': 0.16, 'camps': 3, 'largest': 0.3775, 'groups': 3, 'consensus': False},
                 {'eps': 0.1625, 'camps': 3, 'largest': 0.3825, 'groups': 3, 'consensus': False},
                 {'eps': 0.165, 'camps': 3, 'largest': 0.39, 'groups': 3, 'consensus': False},
                 {'eps': 0.1675, 'camps': 3, 'largest': 0.395, 'groups': 3, 'consensus': False},
                 {'eps': 0.17, 'camps': 3, 'largest': 0.4025, 'groups': 3, 'consensus': False},
                 {'eps': 0.1725, 'camps': 3, 'largest': 0.41, 'groups': 3, 'consensus': False},
                 {'eps': 0.175, 'camps': 3, 'largest': 0.425, 'groups': 3, 'consensus': False},
                 {'eps': 0.1775, 'camps': 2, 'largest': 0.4875, 'groups': 3, 'consensus': False},
                 {'eps': 0.18, 'camps': 2, 'largest': 0.4925, 'groups': 3, 'consensus': False},
                 {'eps': 0.1825, 'camps': 2, 'largest': 0.4975, 'groups': 3, 'consensus': False},
                 {'eps': 0.185, 'camps': 2, 'largest': 0.4975, 'groups': 3, 'consensus': False},
                 {'eps': 0.1875, 'camps': 2, 'largest': 0.495, 'groups': 3, 'consensus': False},
                 {'eps': 0.19, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.1925, 'camps': 2, 'largest': 0.5, 'groups': 2, 'consensus': False},
                 {'eps': 0.195, 'camps': 2, 'largest': 0.5, 'groups': 2, 'consensus': False},
                 {'eps': 0.1975, 'camps': 2, 'largest': 0.5, 'groups': 2, 'consensus': False},
                 {'eps': 0.2, 'camps': 2, 'largest': 0.5, 'groups': 2, 'consensus': False},
                 {'eps': 0.2025, 'camps': 2, 'largest': 0.5, 'groups': 2, 'consensus': False},
                 {'eps': 0.205, 'camps': 2, 'largest': 0.5, 'groups': 2, 'consensus': False},
                 {'eps': 0.2075, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.21, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.2125, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.215, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.2175, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.22, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.2225, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.225, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.2275, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.23, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.2325, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.235, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.2375, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.24, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.2425, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.245, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.2475, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True},
                 {'eps': 0.25, 'camps': 1, 'largest': 1.0, 'groups': 1, 'consensus': True}],
        'random': [{'eps': 0.1, 'p_consensus': 0.0, 'mean_camps': 3.75, 'runs': 12},
                   {'eps': 0.11, 'p_consensus': 0.0, 'mean_camps': 3.5, 'runs': 12},
                   {'eps': 0.12, 'p_consensus': 0.0, 'mean_camps': 3.167, 'runs': 12},
                   {'eps': 0.13, 'p_consensus': 0.0, 'mean_camps': 2.917, 'runs': 12},
                   {'eps': 0.14, 'p_consensus': 0.0, 'mean_camps': 2.833, 'runs': 12},
                   {'eps': 0.15, 'p_consensus': 0.0, 'mean_camps': 2.667, 'runs': 12},
                   {'eps': 0.16, 'p_consensus': 0.0, 'mean_camps': 2.417, 'runs': 12},
                   {'eps': 0.17, 'p_consensus': 0.0, 'mean_camps': 2.167, 'runs': 12},
                   {'eps': 0.18, 'p_consensus': 0.0, 'mean_camps': 2.0, 'runs': 12},
                   {'eps': 0.19, 'p_consensus': 0.0, 'mean_camps': 2.0, 'runs': 12},
                   {'eps': 0.2, 'p_consensus': 0.0833, 'mean_camps': 1.917, 'runs': 12},
                   {'eps': 0.21, 'p_consensus': 0.1667, 'mean_camps': 1.833, 'runs': 12},
                   {'eps': 0.22, 'p_consensus': 0.3333, 'mean_camps': 1.667, 'runs': 12},
                   {'eps': 0.23, 'p_consensus': 0.6667, 'mean_camps': 1.333, 'runs': 12},
                   {'eps': 0.24, 'p_consensus': 0.8333, 'mean_camps': 1.167, 'runs': 12},
                   {'eps': 0.25, 'p_consensus': 0.8333, 'mean_camps': 1.167, 'runs': 12}]},
 'E4': [{'inside': 0.5, 'eps': 0.1, 'mode': 'Zufällig gleichverteilt', 'camps': 3.0, 'largest': 0.4917, 'nets': 8},
        {'inside': 0.5, 'eps': 0.1, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 4.0, 'largest': 0.3333, 'nets': 8},
        {'inside': 0.5, 'eps': 0.25, 'mode': 'Zufällig gleichverteilt', 'camps': 1.0, 'largest': 0.9958, 'nets': 8},
        {'inside': 0.5, 'eps': 0.25, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 1.0, 'largest': 1.0, 'nets': 8},
        {'inside': 0.8, 'eps': 0.1, 'mode': 'Zufällig gleichverteilt', 'camps': 3.0, 'largest': 0.4813, 'nets': 8},
        {'inside': 0.8, 'eps': 0.1, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 6.0, 'largest': 0.1667, 'nets': 8},
        {'inside': 0.8, 'eps': 0.25, 'mode': 'Zufällig gleichverteilt', 'camps': 1.0, 'largest': 0.9917, 'nets': 8},
        {'inside': 0.8, 'eps': 0.25, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 1.0, 'largest': 1.0, 'nets': 8},
        {'inside': 0.9, 'eps': 0.1, 'mode': 'Zufällig gleichverteilt', 'camps': 3.0, 'largest': 0.3958, 'nets': 8},
        {'inside': 0.9, 'eps': 0.1, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 6.0, 'largest': 0.1667, 'nets': 8},
        {'inside': 0.9, 'eps': 0.25, 'mode': 'Zufällig gleichverteilt', 'camps': 1.0, 'largest': 0.9917, 'nets': 8},
        {'inside': 0.9, 'eps': 0.25, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 1.0, 'largest': 1.0, 'nets': 8},
        {'inside': 0.95, 'eps': 0.1, 'mode': 'Zufällig gleichverteilt', 'camps': 4.0, 'largest': 0.3187, 'nets': 8},
        {'inside': 0.95, 'eps': 0.1, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 6.0, 'largest': 0.1667, 'nets': 8},
        {'inside': 0.95, 'eps': 0.25, 'mode': 'Zufällig gleichverteilt', 'camps': 1.0, 'largest': 0.9917, 'nets': 8},
        {'inside': 0.95, 'eps': 0.25, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 1.0, 'largest': 1.0, 'nets': 8},
        {'inside': 0.99, 'eps': 0.1, 'mode': 'Zufällig gleichverteilt', 'camps': 8.0, 'largest': 0.1588, 'nets': 8},
        {'inside': 0.99, 'eps': 0.1, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 6.0, 'largest': 0.1667, 'nets': 8},
        {'inside': 0.99, 'eps': 0.25, 'mode': 'Zufällig gleichverteilt', 'camps': 2.0, 'largest': 0.8542, 'nets': 8},
        {'inside': 0.99, 'eps': 0.25, 'mode': 'Nach Verbünden ausgerichtet', 'camps': 3.0, 'largest': 0.6667, 'nets': 8}],
 'presets': {'Vollständiger Graph: die Treppe (Voreinstellung)': {'n': 100,
                                                                  'm': 100,
                                                                  'edges': 4950,
                                                                  'steps': 4,
                                                                  'camps': [2, 0.62, 0, 2],
                                                                  'reversal': None,
                                                                  'consensus': False,
                                                                  'span0': 0.9782,
                                                                  'kind': 'info',
                                                                  'verdict': 'Nach 4 Schritten steht das Netz bei Vertrauensradius 20 % still: 2 Lager (das größte mit '
                                                                             '62,0 % der Betriebe), 2 Gruppen insgesamt.'},
             'Dünnes Netz: ein Block und viele Splitter': {'n': 150,
                                                           'm': 150,
                                                           'edges': 450,
                                                           'steps': 102,
                                                           'camps': [1, 0.96, 6, 7],
                                                           'reversal': 1,
                                                           'consensus': False,
                                                           'span0': 0.99,
                                                           'kind': 'info',
                                                           'verdict': 'Nach 102 Schritten steht das Netz bei Vertrauensradius 25 % still: 1 Lager (das größte mit 96,0 % '
                                                                      'der Betriebe) und 6 Betriebe in kleinen Gruppen (Splittern, insgesamt 7 Gruppen). In Schritt 1 '
                                                                      'kehrte sich die Reihenfolge der Meinungen zum ersten Mal um.'},
             'Gleichabständig: der Konsens kehrt zurück': {'n': 100,
                                                           'm': 100,
                                                           'edges': 4950,
                                                           'steps': 73,
                                                           'camps': [1, 1.0, 0, 1],
                                                           'reversal': None,
                                                           'consensus': True,
                                                           'span0': 1.0,
                                                           'kind': 'success',
                                                           'verdict': 'Nach 73 Schritten einigen sich 100,0 % der Betriebe auf 0,500 (Vertrauensradius 19 %: Konsens).'},
             'Zwei Lager bleiben': {'n': 100,
                                    'm': 100,
                                    'edges': 4950,
                                    'steps': 1,
                                    'camps': [2, 0.5, 0, 2],
                                    'reversal': None,
                                    'consensus': False,
                                    'span0': 0.7589,
                                    'kind': 'info',
                                    'verdict': 'Nach 1 Schritten steht das Netz bei Vertrauensradius 30 % still: 2 Lager (das größte mit 50,0 % der Betriebe), 2 Gruppen '
                                               'insgesamt.'},
             'Verbünde halten Lager': {'n': 120,
                                       'm': 120,
                                       'edges': 720,
                                       'steps': 34,
                                       'camps': [6, 0.1667, 0, 6],
                                       'reversal': 1,
                                       'consensus': False,
                                       'span0': 0.9899,
                                       'kind': 'info',
                                       'verdict': 'Nach 34 Schritten steht das Netz bei Vertrauensradius 10 % still: 6 Lager (das größte mit 16,7 % der Betriebe), 6 '
                                                  'Gruppen insgesamt. In Schritt 1 kehrte sich die Reihenfolge der Meinungen zum ersten Mal um.'},
             'Reihenfolge kehrt sich um': {'n': 100,
                                           'm': 100,
                                           'edges': 271,
                                           'steps': 122,
                                           'camps': [1, 0.97, 3, 4],
                                           'reversal': 1,
                                           'consensus': False,
                                           'span0': 0.9782,
                                           'kind': 'info',
                                           'verdict': 'Nach 122 Schritten steht das Netz bei Vertrauensradius 25 % still: 1 Lager (das größte mit 97,0 % der Betriebe) '
                                                      'und 3 Betriebe in kleinen Gruppen (Splittern, insgesamt 4 Gruppen). In Schritt 1 kehrte sich die Reihenfolge der '
                                                      'Meinungen zum ersten Mal um.'}},
 'V_E1': 'Konsens (das größte Lager hat mindestens 99 % der Betriebe) gibt es in mindestens der Hälfte der Netze bei Vertrauensradius: „Vollständig (jeder kennt jeden)“ '
         'ab 0,25; „Zufallsnetz“ ab 0,40; „Potenzgesetz-Netz“ ab 0,50; „Skalenfreies Netz (BA)“ ab 0,50; „Verbünde“ ab 0,40; „Ring mit Abkürzungen“ ab 0,40; „Gitter“ ab '
         '0,50. Bei ε = 0,10 zerfällt „Potenzgesetz-Netz“ im Median in 96 Gruppen (3 Lager, größter Anteil 22 %), der vollständige Graph in 4 (4 Lager).',
 'V_E2': 'Bei Vertrauensradius 0,20 kehrt sich die Reihenfolge der Meinungen in jedem Lauf um in: „Zufallsnetz“, „Potenzgesetz-Netz“, „Skalenfreies Netz (BA)“, '
         '„Verbünde“, „Ring mit Abkürzungen“, „Gitter“; nie in: „Vollständig (jeder kennt jeden)“. Für einen Radius über der Spanne weicht der Endwert um höchstens 1,4 '
         '· 10⁻¹¹ von der DeGroot-Formel Σ (d + 1) x / Σ (d + 1) ab.',
 'V_E3': 'Im vollständigen Graphen mit 400 Betrieben gibt es bei gleichabständigem Start Konsens bei ε = 0,1900, obwohl er bei ε = 0,1925 fehlt: der Konsens kehrt bei '
         'sinkendem Radius kurz zurück. Bei zufälligem Start (12 Läufe je Radius) steigt der Anteil der Läufe mit Konsens dagegen monoton mit ε.',
 'V_E4': 'Bei Vertrauensradius 0,10 und zufälligem Start hat das Netz bei 50 % Kanten innerhalb der Verbünde 3 Lager, bei 99 % 8; beginnt jeder Verbund bei seiner '
         'eigenen Meinung, sind es 4 bzw. 6.'}


@lru_cache(maxsize=None)
def _e1():
    return ev.staircase_rows(N, CC, seeds=SW)


@lru_cache(maxsize=None)
def _e2():
    return ev.order_rows(ORDER_N, CC, seeds=SW)


@lru_cache(maxsize=None)
def _e3():
    return ev.lorenz_rows()


@lru_cache(maxsize=None)
def _e4():
    return ev.community_rows(seeds=SW)


def _band(x, digits):
    return pytest.approx(x, abs=0.6 * 10.0**-digits)


# --- E1: Treppe und Netz -----------------------------------------------------------------------------------------------------------------------------


def test_staircase_table():
    rows = _e1()
    assert len(rows) == len(EXPECT["E1"]) == len(C.ALL_TYPES) * len(C.STAIR_EPS)
    for got, exp in zip(rows, EXPECT["E1"]):
        assert (got["typ"], got["eps"], got["nets"], got["converged"]) == (exp["typ"], exp["eps"], exp["nets"], exp["converged"]), exp
        assert got["camps"] == _band(exp["camps"], 2) and got["largest"] == _band(exp["largest"], 4) and got["groups"] == _band(exp["groups"], 2) and got["consensus"] == _band(exp["consensus"], 3) and got["steps"] == _band(exp["steps"], 1), exp
    assert ev.verdict_staircase(rows)[1] == EXPECT["V_E1"]


def test_the_complete_graph_is_a_staircase_with_consensus_from_a_quarter():
    rows = _e1()
    camps = [ev.stair_cell(rows, C.T_COMPLETE, e)["camps"] for e in C.STAIR_EPS]
    assert camps == sorted(camps, reverse=True) and camps[0] >= 4 and camps[-1] == 1.0
    cons = [ev.stair_cell(rows, C.T_COMPLETE, e)["consensus"] for e in C.STAIR_EPS]
    assert cons == sorted(cons) and cons[2] < 0.5 <= cons[3] and cons[4] == 1.0                                              # Konsens in der Hälfte der Läufe ab ε = 0,25
    assert ev.first_consensus(rows, C.T_COMPLETE) == 0.25


def test_sparse_networks_need_a_much_larger_radius_and_fragment_into_a_block_with_splinters():
    rows = _e1()
    for typ in C.GENERATED_TYPES:
        assert ev.stair_cell(rows, typ, 0.25)["consensus"] == 0.0 and 0.8 <= ev.stair_cell(rows, typ, 0.25)["largest"] < C.CONSENSUS_SHARE, typ         # bei ε = 0,25: ein Block, aber kein Konsens
        assert ev.first_consensus(rows, typ) in (0.4, 0.5), typ
        assert ev.stair_cell(rows, typ, 0.1)["groups"] > 50 > 4 >= ev.stair_cell(rows, C.T_COMPLETE, 0.1)["groups"]                                     # viele gestrandete Einzelne
        assert ev.stair_cell(rows, typ, 0.5)["consensus"] >= 0.5
    assert ev.stair_cell(rows, C.T_POWER, 0.5)["consensus"] < 1.0 and all(ev.stair_cell(rows, t, 0.5)["consensus"] == 1.0 for t in (C.T_RANDOM, C.T_BA, C.T_COMMUNITIES, C.T_RING, C.T_GRID))


# --- E2: Reihenfolge und Identität ---------------------------------------------------------------------------------------------------------------


def test_order_reversal_and_the_degroot_bridge():
    res = _e2()
    assert res["eps"] == EXPECT["E2"]["eps"] == C.ORDER_EPS
    for got, exp in zip(res["order"], EXPECT["E2"]["order"]):
        assert (got["typ"], got["reversed"], got["runs"]) == (exp["typ"], exp["reversed"], exp["runs"]) and (exp["first"] is None or got["first"] == _band(exp["first"], 1)), exp
    by = {r["typ"]: r for r in res["order"]}
    assert by[C.T_COMPLETE]["reversed"] == 0 and all(by[t]["reversed"] == by[t]["runs"] == 8 and by[t]["first"] == 1.0 for t in C.GENERATED_TYPES)            # in Netzen schon im ersten Schritt
    for got, exp in zip(res["identity"], EXPECT["E2"]["identity"]):
        assert got["typ"] == exp["typ"] and got["max_dev"] < 1e-10 and exp["max_dev"] < 1e-10 and got["runs"] == exp["runs"]
    assert ev.verdict_order(res)[1] == EXPECT["V_E2"]


# --- E3: Konsens kehrt zurück --------------------------------------------------------------------------------------------------------------------


def test_equidistant_start_brings_the_consensus_back_but_the_random_start_does_not():
    res = _e3()
    assert res["n"] == EXPECT["E3"]["n"] == C.LORENZ_N and len(res["equi"]) == len(EXPECT["E3"]["equi"]) == len(C.LORENZ_GRID)
    for got, exp in zip(res["equi"], EXPECT["E3"]["equi"]):
        assert (got["eps"], got["camps"], got["groups"], got["consensus"]) == (exp["eps"], exp["camps"], exp["groups"], exp["consensus"]) and got["largest"] == _band(exp["largest"], 4), exp
    assert ev.comeback_eps(res["equi"]) == [0.19]
    consensus = [r["eps"] for r in res["equi"] if r["consensus"]]
    assert consensus == [0.19] + [e for e in C.LORENZ_GRID if e >= 0.2075]                                                          # Konsens bei 0,19 und ab 0,2075; dazwischen zwei Lager
    assert [r["camps"] for r in res["equi"] if 0.1925 <= r["eps"] <= 0.205] == [2] * 6
    for got, exp in zip(res["random"], EXPECT["E3"]["random"]):
        assert (got["eps"], got["runs"]) == (exp["eps"], exp["runs"]) and got["p_consensus"] == _band(exp["p_consensus"], 4) and got["mean_camps"] == _band(exp["mean_camps"], 3)
    ps = [r["p_consensus"] for r in res["random"]]
    assert ps == sorted(ps) and ev.biggest_drop(res["random"]) == 0.0 and ps[0] == 0.0 and ps[-1] >= 0.8
    assert ev.verdict_lorenz(res)[1] == EXPECT["V_E3"]


# --- E4: Verbünde ------------------------------------------------------------------------------------------------------------------------------------


def test_communities_hold_camps_only_with_very_few_cross_edges_or_an_aligned_start():
    rows = _e4()
    assert len(rows) == len(EXPECT["E4"]) == len(C.COMM_INSIDES) * len(C.COMM_EPS) * 2
    for got, exp in zip(rows, EXPECT["E4"]):
        assert (got["inside"], got["eps"], got["mode"], got["nets"]) == (exp["inside"], exp["eps"], exp["mode"], exp["nets"]) and got["camps"] == _band(exp["camps"], 2) and got["largest"] == _band(exp["largest"], 4), exp
    cell = ev.community_cell
    assert cell(rows, 0.99, 0.1, C.M_RANDOM)["camps"] > 2 * cell(rows, 0.5, 0.1, C.M_RANDOM)["camps"] and cell(rows, 0.9, 0.1, C.M_RANDOM)["camps"] <= cell(rows, 0.5, 0.1, C.M_RANDOM)["camps"]
    assert all(cell(rows, i, 0.1, C.M_COMM)["camps"] == C.BLOCKS for i in (0.8, 0.9, 0.95, 0.99))                                          # ausgerichteter Start: sechs Lager ab 80 % innen
    assert all(cell(rows, i, 0.25, C.M_RANDOM)["camps"] == 1.0 for i in (0.5, 0.8, 0.9, 0.95)) and cell(rows, 0.99, 0.25, C.M_RANDOM)["camps"] >= 2.0 and cell(rows, 0.99, 0.25, C.M_COMM)["camps"] >= 3.0
    assert ev.verdict_communities(rows)[1] == EXPECT["V_E4"]


# --- Presets ------------------------------------------------------------------------------------------------------------------------------------------


def test_presets_numbers():
    assert set(EXPECT["presets"]) == set(C.PRESETS)
    for name, exp in EXPECT["presets"].items():
        an = ev.analyse(ev.Settings(**C.PRESETS[name]))
        assert (an.inst.n, an.m, int(an.a.sum() // 2), an.steps, an.run["first_reversal"], an.consensus) == (exp["n"], exp["m"], exp["edges"], exp["steps"], exp["reversal"], exp["consensus"]), name
        assert [an.camps[0], round(an.camps[1], 4), an.camps[2], an.camps[3]] == pytest.approx(exp["camps"], abs=0.00006) and an.span0 == _band(exp["span0"], 4), name
        assert ev.verdict_main(an) == (exp["kind"], exp["verdict"]), name
