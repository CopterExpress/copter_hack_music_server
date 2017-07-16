import os
from threading import Thread

import time
import random
import pause
import pygame
from flask import Flask, request, abort, send_file


pygame.mixer.init()
app = Flask(__name__)


STORAGE = '/music'

dir = os.path.dirname(os.path.realpath(__file__))
files = os.listdir(dir + STORAGE)
melodies = {}

for file in files:
    filename = dir + STORAGE + '/' + file
    sound = pygame.mixer.Sound(file=filename)
    melodies[file] = sound


print 'Melodies: ', melodies.keys()


waiting = False


def play(melody):
    print 'play', melody
    melodies[melody].play()


def wait(start, melody):
    global waiting
    waiting = True
    print melody, 'wait until', start
    pause.until(start)
    play(melody)
    waiting = False


@app.route('/get')
def get_endpoint():
    melody = request.args.get('melody')
    if melody is None:
        melody = random.choice(melodies.keys())
    elif melody not in melodies.keys():
        return 'not found', 404
    return send_file(dir + STORAGE + '/' + melody, as_attachment=True)


@app.route('/play', methods=['POST'])
def play_endpoint():
    start = request.form.get('start')
    if start is not None:
        start = float(start)
    melody = request.form.get('melody')
    if melody is None:
        return 'no melody specified', 404
    elif melody not in melodies.keys():
        return melody + ' not found', 404
    if not pygame.mixer.get_busy() and not waiting:
        if start:
            if start - time.time() > 20:
                return 'too long time to wait (>20 s)', 409
            elif start < time.time():
                return 'can\'t play melody in the past', 409
            Thread(target=wait, args=[start, melody]).start()
        else:
            play(melody)
        return 'ok'
    else:
        return 'busy', 409


@app.route('/stop', methods=['POST'])
def stop_endpoint():
    pygame.mixer.stop()
    return 'ok'


app.run(debug=True)
