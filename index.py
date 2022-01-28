from cv2 import cv2

from os import listdir
from src.logger import logger, loggerMapClicked
from random import randint
from random import random
import pygetwindow
import numpy as np
import mss
import pyautogui
import time
import sys

import yaml


msg_login = """
                                                
BOT FEITO POR: BRIAN/HXPE

Se quiser doar algo: 0xb45233C9892c58b6812C446df1B715A589B482eF

"""


print(msg_login)
time.sleep(1)
option = "A"
print("\nBot Rodando! Com a opção: ", option, "\nTODOS PARA TRABALHAR!,\nSe quiser parar o bot, digite CTRL+C, aperte S e depois ENTER")


if __name__ == '__main__':
    stream = open("config.yaml", 'r')
    c = yaml.safe_load(stream)

ct = c['threshold']
pause = c['time_intervals']['interval_between_movements']
pyautogui.PAUSE = pause
pyautogui.FAILSAFE = False
hero_clicks = 0
login_attempts = 0
last_log_is_progress = False

if option == "A" or option == "a":
    c['select_heroes_mode'] = "all"
    c['send_heroes_for_work'] = 25


def add_randomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)


def move_to_randomness(x, y, t):
    pyautogui.moveTo(add_randomness(x, 10), add_randomness(y, 10), t+random()/2)


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def load_images():
    file_names = listdir('./targets/')
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)
    return targets


images = load_images()
work_all = cv2.imread('targets/work-all.png')


def show(rectangles, img=None):

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    cv2.imshow('img', img)
    cv2.waitKey(0)


def click_btn(img, name=None, timeout=3, threshold=ct['default']):
    logger(None, progress_indicator=True)
    if not name is None:
        pass
    start = time.time()
    while True:
        matches = positions(img, threshold=threshold)
        if len(matches) == 0:
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                return False
            continue

        x, y, w , h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        move_to_randomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True


def print_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:, :, :3]


def positions(target, threshold=ct['default'], img=None):
    if img is None:
        img = print_screen()
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)
    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])
    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def scroll():
    commons = positions(images['common-text'], threshold=ct['common'])
    if len(commons) == 0:
        return
    x, y, w, h = commons[len(commons)-1]
    move_to_randomness(x, y, 1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0, -c['click_and_drag_amount'], duration=1, button='left')


def click_buttons():
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    for (x, y, w, h) in buttons:
        move_to_randomness(x+(w/2), y+(h/2), 1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        if hero_clicks > 20:
            return
    return len(buttons)


def is_working(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        is_below = y < (button_y + button_h)
        is_above = y > (button_y - button_h)
        if is_below and is_above:
            return False
    return True


def click_all():
    buttons = positions(images['work-all'], threshold=ct['work_all'])
    for (x, y, w, h) in buttons:
        move_to_randomness(x+(w/2), y+(h/2), 1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        if hero_clicks > 1:
            return
    return len(buttons)


def click_green_bars():
    offset = 130
    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    not_working_green_bars = []
    for bar in green_bars:
        if not is_working(bar, buttons):
            not_working_green_bars.append(bar)
    for (x, y, w, h) in not_working_green_bars:
        move_to_randomness(x+offset+(w/2), y+(h/2), 1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        if hero_clicks > 20:
            return
    return len(not_working_green_bars)


def go_to_heroes():
    if click_btn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0
    click_btn(images['hero-icon'])


def go_to_game():
    click_btn(images['x'])
    click_btn(images['x'])
    click_btn(images['treasure-hunt-icon'])


def refresh_heroes_position():
    logger('🔃 Refreshing Heroes Positions')
    click_btn(images['go-back-arrow'])
    time.sleep(20)
    click_btn(images['treasure-hunt-icon'])


def login():
    global login_attempts
    logger('🔒 Checando se nao tomou DC!')

    if login_attempts > 3:
        logger('🔃 Tentamos logar demais, recarregando a pagina...')
        login_attempts = 0
        pyautogui.hotkey('ctrl', 'f5')
        return

    if click_btn(images['connect-wallet'], name='connectWalletBtn', timeout=5):
        logger('🎉 Conectando a carteira!')
        login_attempts = login_attempts + 1

    if click_btn(images['select-wallet-2'], name='sign button', timeout=10):
        login_attempts = login_attempts + 1
        if click_btn(images['treasure-hunt-icon'], name='teasureHunt', timeout=15):
            login_attempts = 0
        return

    if not click_btn(images['select-wallet-1-no-hover'], name='selectMetamaskBtn'):
        if click_btn(images['select-wallet-1-hover'], name='selectMetamaskHoverBtn', threshold  = ct['select_wallet_buttons'] ):
            pass
    else:
        pass

    if click_btn(images['select-wallet-2'], name='signBtn', timeout=20):
        login_attempts = login_attempts + 1
        if click_btn(images['treasure-hunt-icon'], name='teasureHunt', timeout=25):
            login_attempts = 0

    if click_btn(images['ok'], name='okBtn', timeout=5):
        pass


def refresh_heroes():
    logger('Procurando Herois para trabalhar!')
    go_to_heroes()
    if c['select_heroes_mode'] == "all":
        logger('⚒️ Enviando todos herois para trabalhar!', 'green')
        click_all()
        go_to_game()
    elif c['select_heroes_mode'] == "green":
        logger('⚒️ Enviando herois com stamina verde para trabalhar!', 'green')
    else:
        logger('⚒️ Enviando todos herois para trabalhar!', 'green')

    buttons_clicked = 1
    empty_scrolls_attempts = c['scroll_attemps']
    while empty_scrolls_attempts > 0:
        if c['select_heroes_mode'] == 'green':
            buttons_clicked = click_green_bars()
        else:
            buttons_clicked = click_all()

        if buttons_clicked == 0:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
        scroll()
        time.sleep(2)
    logger('💪 {} Herois Enviados para trabalhar!'.format(hero_clicks))
    go_to_game()


def main():
    time.sleep(4)
    t = c['time_intervals']
    windows = []

    for w in pygetwindow.getWindowsWithTitle('bombcrypto'):
        windows.append({
            "window": w,
            "login": 0,
            "heroes": 0,
            "new_map": 0,
            "refresh_heroes": 0,
            })

    while True:
        now = time.time()

        for last in windows:
            last["window"].activate()

            if now - last["heroes"] > add_randomness(t['send_heroes_for_work'] * 60):
                last["heroes"] = now
                refresh_heroes()

            if now - last["login"] > add_randomness(t['check_for_login'] * 60):
                sys.stdout.flush()
                last["login"] = now
                login()

            if now - last["new_map"] > t['check_for_new_map_button']:
                last["new_map"] = now

                if click_btn(images['new-map']):
                    loggerMapClicked()

            if now - last["refresh_heroes"] > add_randomness( t['refresh_heroes_positions'] * 60):
                last["refresh_heroes"] = now
                refresh_heroes_position()

            logger(None, progress_indicator=True)
            sys.stdout.flush()
            time.sleep(2)


main()



