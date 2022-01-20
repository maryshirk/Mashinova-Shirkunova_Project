import pygame, sys
import random
import copy
from pygame import mixer

mainClock = pygame.time.Clock()
from pygame.locals import *


pygame.init()
size = 900, 600
screen = pygame.display.set_mode(size) # размер экрана
pygame.display.set_caption('Морской бой')
block_size = 30
left_margin = 90
upper_margin = 150
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
font_size = int(block_size / 1.5)
font = pygame.font.SysFont('assets/myfont.ttf', 30)
game_over_font_size = 3 * block_size
game_over_font = pygame.font.SysFont('assets/myfont.ttf', game_over_font_size)
computer_available_to_fire_set = {(x, y)
                                  for x in range(16, 26) for y in range(1, 11)}
around_last_computer_hit_set = set()
dotted_set_for_computer_not_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
hit_blocks = set()
dotted_set = set()
destroyed_computer_ships = []

mixer.music.load('assets/volnyi-pleschutsya-more-okean-pobereje-41080.wav')  # загрузка музыки
mixer.music.set_volume(0.5)     # величение или уменьшение громкости
mixer.music.play(-1)


def draw_text(text, font, color, surface, x, y):  # для текста
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def print_text(message, x, y, font_color=(0, 0, 0), font_type='assets/myfont.ttf', font_size=30):
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))


class Button:
    def __init__(self, x_offset, button_title, message_to_show):
        self.title = button_title
        self.title_width, self.title_height = font.size(self.title)
        self.message = message_to_show
        self.button_width = self.title_width + block_size
        self.button_height = self.title_height + block_size
        self.x_start = x_offset
        self.y_start = upper_margin + 10 * block_size + self.button_height
        self.rect_for_draw = self.x_start, self.y_start, self.button_width, self.button_height
        self.rect = pygame.Rect(self.rect_for_draw)
        self.rect_for_button_title = self.x_start + self.button_width / 2 - \
            self.title_width / 2, self.y_start + \
            self.button_height / 2 - self.title_height / 2
        self.color = (0, 0, 0)

    def draw_button(self, color=None):
        if not color:
            color = self.color
        pygame.draw.rect(screen, color, self.rect_for_draw)
        text_to_blit = font.render(self.title, True, (255, 255, 255))
        screen.blit(text_to_blit, self.rect_for_button_title)

    def change_color_on_hover(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.draw_button('#a59ba8')

    def print_message_for_button(self):
        message_width, message_height = font.size(self.message)
        rect_for_message = self.x_start / 2 - message_width / \
            2, self.y_start + self.button_height / 2 - message_height / 2
        text = font.render(self.message, True, (0, 0, 0))
        screen.blit(text, rect_for_message)


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.left = 0
        self.top = 0
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # создание тетрадного листа
    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color('#78ccf0'),
                                 (x * self.cell_size + self.left, y * self.cell_size + self.top,
                                  self.cell_size, self.cell_size), 1)
        pygame.draw.line(screen, pygame.Color('#cc0000'), (0, 90), (950, 90), 1)

    # создание поля 1 игрока
    def drawer_field_2(self):
        for i in range(11):
            # горизонталь
            pygame.draw.line(screen, pygame.Color('#0000e6'), (left_margin, upper_margin + i * block_size),
                             (left_margin + 10 * block_size, upper_margin + i * block_size), 1)
            # вертикаль
            pygame.draw.line(screen, pygame.Color('#0000e6'), (left_margin + i * block_size, upper_margin),
                             (left_margin + i * block_size, upper_margin + 10 * block_size), 1)

            if i < 10:
                num_ver = font.render(str(i + 1), True, pygame.Color('#0000e6'))
                letters_hor = font.render(letters[i], True, pygame.Color('#0000e6'))

                num_ver_width = num_ver.get_width()
                num_ver_height = num_ver.get_height()
                letters_hor_width = letters_hor.get_width()

                screen.blit(num_ver, (left_margin - (block_size // 2 + num_ver_width // 2),
                                      upper_margin + i * block_size + (block_size // 2 - num_ver_height // 2)))
                screen.blit(letters_hor, (left_margin + i * block_size + (block_size //
                                                                          2 - letters_hor_width // 2),
                                          upper_margin + 10 * block_size))

    # создание поля 2 игрока
    def drawer_field_1(self):
        for i in range(11):
            pygame.draw.line(screen, pygame.Color('#0000e6'), (left_margin + 15 * block_size, upper_margin +
                                                               i * block_size),
                             (left_margin + 25 * block_size, upper_margin + i * block_size), 1)
            pygame.draw.line(screen, pygame.Color('#0000e6'), (left_margin + (i + 15) * block_size, upper_margin),
                             (left_margin + (i + 15) * block_size, upper_margin + 10 * block_size), 1)

            if i < 10:
                num_ver = font.render(str(i + 1), True, pygame.Color('#0000e6'))
                letters_hor = font.render(letters[i], True, pygame.Color('#0000e6'))

                num_ver_width = num_ver.get_width()
                num_ver_height = num_ver.get_height()
                letters_hor_width = letters_hor.get_width()

                screen.blit(num_ver, (left_margin - (block_size // 2 + num_ver_width // 2) + 15 *
                                      block_size,
                                      upper_margin + i * block_size + (block_size // 2 - num_ver_height // 2)))
                screen.blit(letters_hor, (left_margin + i * block_size + (block_size // 2 -
                                                                          letters_hor_width // 2) + 15 * block_size,
                                          upper_margin + 10 * block_size))


class Ships:  # автомотическая постройка корабля
    def __init__(self, offset):
        self.offset = offset
        self.available_blocks = {(x, y) for x in range(
            1 + self.offset, 11 + self.offset) for y in range(1, 11)}
        self.ships_set = set()
        self.ships = self.populate_grid()
        self.orientation = None
        self.direction = None

    def create_start_block(self, available_blocks):  # выбор стартовой клеточки постройки корабля
        self.orientation = random.randint(0, 1)
        self.direction = random.choice((-1, 1))
        x, y = random.choice(tuple(available_blocks))
        return x, y, self.orientation, self.direction

    def get_new_block_for_ship(self, coor, direction, orientation, ship_coordinates):
        self.direction = direction
        self.orientation = orientation
        if (coor <= 1 - self.offset * (self.orientation - 1) and self.direction == -1) or (
                coor >= 10 - self.offset * (self.orientation - 1) and self.direction == 1):
            self.direction *= -1
            return self.direction, ship_coordinates[0][self.orientation] + self.direction
        else:
            return self.direction, ship_coordinates[-1][self.orientation] + self.direction

    def create_ship(self, number_of_blocks, available_blocks):  # создание корабля в виде кортежа координат
        ship_coordinates = []
        x, y, self.orientation, self.direction = self.create_start_block(
            available_blocks)
        for _ in range(number_of_blocks):
            ship_coordinates.append((x, y))
            if not self.orientation:
                self.direction, x = self.get_new_block_for_ship(
                    x, self.direction, self.orientation, ship_coordinates)
            else:
                self.direction, y = self.get_new_block_for_ship(
                    y, self.direction, self.orientation, ship_coordinates)
        if self.is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.create_ship(number_of_blocks, available_blocks)

    def is_ship_valid(self, new_ship):  # проверка на вхождение корабля (доступ по клеткам)
        ship = set(new_ship)
        return ship.issubset(self.available_blocks)

    def add_new_ship_to_set(self, new_ship):  # добавлять корабль в сет
        self.ships_set.update(new_ship)

    def update_available_blocks_for_creating_ships(self, new_ship):  # поиск доступных клеток для постройки корабля
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if self.offset < (elem[0] + k) < 11 + self.offset and 0 < (elem[1] + m) < 11:
                        self.available_blocks.discard(
                            (elem[0] + k, elem[1] + m))

    def populate_grid(self):  # создания вложенного списка с координатами кораблей
        ships_coordinates_list = []
        for number_of_blocks in range(4, 0, -1):
            for _ in range(5 - number_of_blocks):
                new_ship = self.create_ship(
                    number_of_blocks, self.available_blocks)
                ships_coordinates_list.append(new_ship)
                self.add_new_ship_to_set(new_ship)
                self.update_available_blocks_for_creating_ships(new_ship)
        return ships_coordinates_list


def draw_ships(ships_coordinates_list):  # отрисовка корабля
    human = Ships(15)
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width = block_size
            ship_height = block_size * len(ship)
        else:
            ship_width = block_size * len(ship)
            ship_height = block_size
        x = block_size * (x_start - 1) + left_margin
        y = block_size * (y_start - 1) + upper_margin
        if ships_coordinates_list == human.ships:
            x += 15 * block_size
        pygame.draw.rect(
            screen, pygame.Color('#0000e6'), ((x, y), (ship_width, ship_height)), width=block_size//10)


def draw_from_dotted_set(dotted_set_to_draw_from):
    for elem in dotted_set_to_draw_from:
        pygame.draw.circle(screen, (0, 0, 0), (block_size * (
            elem[0] - 0.5) + left_margin, block_size * (elem[1] - 0.5) + upper_margin), block_size // 6)


def draw_hit_blocks(hit_blocks_to_draw_from):
    for block in hit_blocks_to_draw_from:
        x1 = block_size * (block[0] - 1) + left_margin
        y1 = block_size * (block[1] - 1) + upper_margin
        pygame.draw.line(screen, (255, 0, 0), (x1, y1),
                         (x1 + block_size, y1 + block_size), block_size // 6)
        pygame.draw.line(screen, (255, 0, 0), (x1, y1 + block_size),
                         (x1 + block_size, y1), block_size // 6)
        bullet_sound = mixer.Sound('assets/vzryiv-ruchnoy-granatyi---padayut-kuski-zemli-27959.wav')
        bullet_sound.play()


def add_missed_block_to_dotted_set(fired_block):
    dotted_set.add(fired_block)
    dotted_set_for_computer_not_to_shoot.add(fired_block)


def computer_shoots(set_to_shoot_from):
    pygame.time.delay(500)
    computer_fired_block = random.choice(tuple(set_to_shoot_from))
    computer_available_to_fire_set.discard(computer_fired_block)
    return computer_fired_block


def computer_first_hit(fired_block):
    x_hit, y_hit = fired_block
    if x_hit > 16:
        around_last_computer_hit_set.add((x_hit - 1, y_hit))
    if x_hit < 25:
        around_last_computer_hit_set.add((x_hit + 1, y_hit))
    if y_hit > 1:
        around_last_computer_hit_set.add((x_hit, y_hit - 1))
    if y_hit < 10:
        around_last_computer_hit_set.add((x_hit, y_hit + 1))


def computer_hits_twice():
    last_hits_list.sort()
    new_around_last_hit_set = set()
    for i in range(len(last_hits_list) - 1):
        x1 = last_hits_list[i][0]
        x2 = last_hits_list[i + 1][0]
        y1 = last_hits_list[i][1]
        y2 = last_hits_list[i + 1][1]
        if x1 == x2:
            if y1 > 1:
                new_around_last_hit_set.add((x1, y1 - 1))
            if y2 < 10:
                new_around_last_hit_set.add((x1, y2 + 1))
        elif y1 == y2:
            if x1 > 16:
                new_around_last_hit_set.add((x1 - 1, y1))
            if x2 < 25:
                new_around_last_hit_set.add((x2 + 1, y1))
    return new_around_last_hit_set


def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only=True):
    global dotted_set
    x, y = fired_block
    a = 15 * computer_turn
    b = 11 + 15 * computer_turn
    hit_blocks_for_computer_not_to_shoot.add(fired_block)
    hit_blocks.add(fired_block)
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (not diagonal_only or i != 0 and j != 0) and a < x + i < b and 0 < y + j < 11:
                add_missed_block_to_dotted_set((x + i, y + j))
    dotted_set -= hit_blocks


def update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy):
    ship = sorted(opponents_ships_list_original_copy[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(ship[i], computer_turn, False)


def update_around_last_computer_hit(fired_block, computer_hits):
    global around_last_computer_hit_set, computer_available_to_fire_set
    if computer_hits and fired_block in around_last_computer_hit_set:
        around_last_computer_hit_set = computer_hits_twice()
    elif computer_hits and fired_block not in around_last_computer_hit_set:
        computer_first_hit(fired_block)
    elif not computer_hits:
        around_last_computer_hit_set.discard(fired_block)

    around_last_computer_hit_set -= dotted_set_for_computer_not_to_shoot
    around_last_computer_hit_set -= hit_blocks_for_computer_not_to_shoot
    computer_available_to_fire_set -= around_last_computer_hit_set
    computer_available_to_fire_set -= dotted_set_for_computer_not_to_shoot


def update_used_blocks(ship, method):
    for block in ship:
        for i in range(-1, 2):
            for j in range(-1, 2):
                method((block[0]+i, block[1]+j))


def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, opponents_ships_list_original_copy,
                      opponents_ships_set):
    for elem in opponents_ships_list:
        diagonal_only = True
        if fired_block in elem:
            # для отрисовки точки и уничтоженных кораблей
            ind = opponents_ships_list.index(elem)
            if len(elem) == 1:
                diagonal_only = False
            update_dotted_and_hit_sets(
                fired_block, computer_turn, diagonal_only)
            elem.remove(fired_block)
            # проверка выиграл или нет
            opponents_ships_set.discard(fired_block)
            if computer_turn:
                last_hits_list.append(fired_block)
                update_around_last_computer_hit(fired_block, True)
            # если корабль уничтожен
            if not elem:
                update_destroyed_ships(
                    ind, computer_turn, opponents_ships_list_original_copy)
                if computer_turn:
                    last_hits_list.clear()
                    around_last_computer_hit_set.clear()
                else:
                    destroyed_computer_ships.append(computer.ships[ind])
            return True
    add_missed_block_to_dotted_set(fired_block)
    if computer_turn:
        update_around_last_computer_hit(fired_block, False)
    return False


def ship_is_valid(ship_set, blocks_for_manual_drawing):
    return ship_set.isdisjoint(blocks_for_manual_drawing)


def show_message_at_rect_center(message, rect, which_font=font, color=(255, 0, 0)):
    message_width, message_height = which_font.size(message)
    message_rect = pygame.Rect(rect)
    x_start = message_rect.centerx - message_width / 2
    y_start = message_rect.centery - message_height / 2
    background_rect = pygame.Rect(
        x_start - block_size / 2, y_start, message_width + block_size, message_height)
    message_to_blit = which_font.render(message, True, color)
    screen.fill((255, 255, 255), background_rect)
    screen.blit(message_to_blit, (x_start, y_start))


def check_ships_numbers(ship, num_ships_list):
    return (5 - len(ship)) > num_ships_list[len(ship)-1]


computer = Ships(0)
computer_ships_working = copy.deepcopy(computer.ships)

auto_button_place = left_margin + 17 * block_size
manual_button_place = left_margin + 20 * block_size
how_to_create_ships_message = "Как вы хотите создать корабли? Нажмите кнопку"
auto_button = Button(auto_button_place, "АВТО", how_to_create_ships_message)
manual_button = Button(manual_button_place, "ВРУЧНУЮ",
                       how_to_create_ships_message)
undo_message = "Для отмены последнего корабля нажмите кнопку"
undo_button_place = left_margin + 12 * block_size
undo_button = Button(undo_button_place, "ОТМЕНА", undo_message)


human_ships_to_draw = []
human_ships_working = []
computer_turn = []
human_ships_set = []


def main():
    global human_ships_set
    global human_ships_working
    global computer_turn
    ships_creation_not_decided = True
    ships_not_created = True
    drawing = False
    game_over = False
    computer_turn = False
    start = (0, 0)
    ship_size = (0, 0)
    global human_ships_to_draw
    rect_for_grids = (0, 0, size[0], upper_margin + 12 * block_size)
    rect_for_messages_and_buttons = (
        0, upper_margin + 11 * block_size, size[0], 5 * block_size)
    message_rect_for_drawing_ships = (undo_button.rect_for_draw[0] + undo_button.rect_for_draw[2],
                                      upper_margin + 11 * block_size, size[0] - (undo_button.rect_for_draw[0]
                                                                                 + undo_button.rect_for_draw[2]),
                                      4 * block_size)
    message_rect_computer = (left_margin - 2 * block_size, upper_margin +
                             11 * block_size, 14 * block_size, 4 * block_size)
    message_rect_human = (left_margin + 15 * block_size, upper_margin +
                          11 * block_size, 10 * block_size, 4 * block_size)
    human_ships_set = set()
    used_blocks_for_manual_drawing = set()
    num_ships_list = [0, 0, 0, 0]

    screen.fill(('#f0f8ff'))
    board = Board(30, 30)
    board.render(screen)
    board.drawer_field_1()
    print_text('Заполните поле кораблями автоматически или вручную', 60, 60)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        while ships_creation_not_decided:
            auto_button.draw_button()
            manual_button.draw_button()
            auto_button.change_color_on_hover()
            manual_button.change_color_on_hover()
            auto_button.print_message_for_button()

            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    ships_creation_not_decided = False
                    ships_not_created = False
                elif event.type == pygame.MOUSEBUTTONDOWN and auto_button.rect.collidepoint(mouse):
                    human = Ships(15)
                    human_ships_to_draw = human.ships
                    human_ships_working = copy.deepcopy(human.ships)
                    human_ships_set = human.ships_set
                    ships_creation_not_decided = False
                    ships_not_created = False
                elif event.type == pygame.MOUSEBUTTONDOWN and manual_button.rect.collidepoint(mouse):
                    ships_creation_not_decided = False

            pygame.display.update()
            screen.fill((('#f0f8ff')), rect_for_messages_and_buttons)

        while ships_not_created:
            screen.fill(('#f0f8ff'))
            board = Board(30, 30)
            board.render(screen)
            board.drawer_field_1()
            print_text('Располагайте корабли', 60, 60)
            screen.fill((('#f0f8ff')), rect_for_messages_and_buttons)
            undo_button.draw_button()
            undo_button.print_message_for_button()
            undo_button.change_color_on_hover()
            mouse = pygame.mouse.get_pos()
            if not human_ships_to_draw:
                undo_button.draw_button((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ships_not_created = False
                    game_over = True
                elif undo_button.rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                    if human_ships_to_draw:
                        screen.fill((255, 255, 255), message_rect_for_drawing_ships)
                        deleted_ship = human_ships_to_draw.pop()
                        num_ships_list[len(deleted_ship) - 1] -= 1
                        update_used_blocks(
                            deleted_ship, used_blocks_for_manual_drawing.discard)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    drawing = True
                    x_start, y_start = event.pos
                    start = x_start, y_start
                    ship_size = (0, 0)
                elif drawing and event.type == pygame.MOUSEMOTION:
                    x_end, y_end = event.pos
                    end = x_end, y_end
                    ship_size = x_end - x_start, y_end - y_start
                elif drawing and event.type == pygame.MOUSEBUTTONUP:
                    x_end, y_end = event.pos
                    drawing = False
                    ship_size = (0, 0)
                    start_block = ((x_start - left_margin) // block_size + 1,
                                   (y_start - upper_margin) // block_size + 1)
                    end_block = ((x_end - left_margin) // block_size + 1,
                                 (y_end - upper_margin) // block_size + 1)
                    if start_block > end_block:
                        start_block, end_block = end_block, start_block
                    temp_ship = []
                    if 15 < start_block[0] < 26 and 0 < start_block[1] < 11 and 15 < end_block[0] < 26 and 0 < \
                            end_block[1] < 11:
                        screen.fill((255, 255, 255), message_rect_for_drawing_ships)
                        if start_block[0] == end_block[0] and (end_block[1] - start_block[1]) < 4:
                            for block in range(start_block[1], end_block[1] + 1):
                                temp_ship.append((start_block[0], block))
                        elif start_block[1] == end_block[1] and (end_block[0] - start_block[0]) < 4:
                            for block in range(start_block[0], end_block[0] + 1):
                                temp_ship.append((block, start_block[1]))
                        else:
                            show_message_at_rect_center(
                                "КОРАБЛЬ СЛИШКОМ БОЛЬШОЙ!", message_rect_for_drawing_ships)
                    else:
                        show_message_at_rect_center(
                            "КОРАБЛЬ ЗА ПРЕДЕЛАМИ СЕТКИ!", message_rect_for_drawing_ships)
                    if temp_ship:
                        temp_ship_set = set(temp_ship)
                        if ship_is_valid(temp_ship_set, used_blocks_for_manual_drawing):
                            if check_ships_numbers(temp_ship, num_ships_list):
                                num_ships_list[len(temp_ship) - 1] += 1
                                human_ships_to_draw.append(temp_ship)
                                human_ships_set |= temp_ship_set
                                update_used_blocks(
                                    temp_ship, used_blocks_for_manual_drawing.add)
                            else:
                                show_message_at_rect_center(
                                    f"УЖЕ ДОСТАТОЧНО {len(temp_ship)}-ПАЛУБНЫХ КОРАБЛЕЙ",
                                    message_rect_for_drawing_ships)
                        else:
                            show_message_at_rect_center(
                                "КОРАБЛИ ПРИКАСАЮТСЯ!", message_rect_for_drawing_ships)
                if len(human_ships_to_draw) == 10:
                    ships_not_created = False
                    human_ships_working = copy.deepcopy(human_ships_to_draw)
                    screen.fill((255, 255, 255), rect_for_messages_and_buttons)
            pygame.draw.rect(screen, (0, 0, 0), (start, ship_size), 3)
            draw_ships(human_ships_to_draw)
            pygame.display.update()
        pygame.draw.rect(screen, (0, 0, 0), (start, ship_size), 3)
        screen.fill(('#f0f8ff'))
        board = Board(30, 30)
        board.render(screen)
        board.drawer_field_1()
        print_text('Классическая игра "Морской бой"', 60, 60)
        draw_ships(human_ships_to_draw)
        pygame.display.update()
        board.drawer_field_2()
        while not game_over:
            game()


class Let(pygame.sprite.Sprite):       # препятствия во втором уровне
    def __init__(self, x, speed, filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect(center=(x, random.randint(0, 500)))
        self.speed = speed

    def update(self, *args):
        if self.rect.x > args[0]:
            self.rect.x -= self.speed
        else:
            self.kill()


class SecondLevel:
    def __init__(self):
        self.count_of_sprites = 0
        self.water = pygame.image.load('assets/water_texture.png')
        self.background1 = pygame.image.load('assets/list.jpg')
        self.waterXpos = 0
        self.game_over_bg = pygame.image.load('assets/GameOver.png')

    def game(self):
        ship = pygame.image.load('assets/ship_png.png')
        ship = pygame.transform.scale(ship, (230, 150))
        ship_rect = ship.get_rect(center=(140, 0))
        pygame.time.set_timer(pygame.USEREVENT, 4000)
        running = True
        gravity = 2
        W = -200
        group = pygame.sprite.Group()
        group.add(Let(800, random.randint(1, 4), 'assets/island.png'))
        self.count_of_sprites += 1

        def draw_water():
            screen.blit(self.water, (self.waterXpos, 445))
            screen.blit(self.water, (self.waterXpos + 288, 445))

        def collide_isl():
            for isl in group:
                if ship_rect.collidepoint(isl.rect.center):
                    return 1

        while running:
            screen.fill((0, 0, 0))
            screen.blit(self.background1, (0, 0))
            group.draw(screen)
            screen.blit(ship, ship_rect)
            draw_text(f"СЧЁТ:{self.count_of_sprites}", font, (255, 0, 0), screen, 30, 30)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        ship_rect.y -= 70
                if event.type == pygame.USEREVENT:
                    group.add(Let(900, random.randint(1, 4), 'assets/island.png'))
                    self.count_of_sprites += 1
            a = collide_isl()
            if a:
                self.game_over()
            if ship_rect.y > 310:
                ship_rect.y = 320
            elif ship_rect.y < -10:
                ship_rect.y = 10
            else:
                ship_rect.y += gravity
            self.waterXpos -= 5  # скорость текстуры воды
            draw_water()
            if self.waterXpos <= -288:
                self.waterXpos = 0

            pygame.display.update()
            mainClock.tick(60)
            group.update(W)

    def game_over(self):
        running = True
        while running:
            screen.fill((0, 0, 0))
            screen.blit(self.game_over_bg, (0, 0))
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()


def game():
    global human_ships_working
    global human_ships_to_draw
    global human_ships_set
    global computer_turn
    click = False
    message_rect_computer = (left_margin - 2 * block_size, upper_margin +
                             11 * block_size, 14 * block_size, 4 * block_size)
    message_rect_human = (left_margin + 15 * block_size, upper_margin +
                          11 * block_size, 10 * block_size, 4 * block_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        draw_ships(destroyed_computer_ships)
        draw_ships(human_ships_to_draw)
        if not (dotted_set | hit_blocks):
            show_message_at_rect_center(
                "ИГРА НАЧАЛАСЬ! ВАШ ХОД!", message_rect_computer)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (left_margin < x < left_margin + 10 * block_size) and (
                        upper_margin < y < upper_margin + 10 * block_size):
                    fired_block = ((x - left_margin) // block_size + 1,
                                   (y - upper_margin) // block_size + 1)
                    computer_turn = not check_hit_or_miss(fired_block, computer_ships_working, False, computer.ships,
                                                          computer.ships_set)
                    draw_from_dotted_set(dotted_set)
                    draw_hit_blocks(hit_blocks)
                    screen.fill((255, 255, 255), message_rect_computer)
                    show_message_at_rect_center(
                        f"Ваш последний ход: {letters[fired_block[0] - 1] + str(fired_block[1])}",
                        message_rect_computer,
                        color=(0, 0, 0))
                else:
                    show_message_at_rect_center(
                        "ВЫСТРЕЛ ЗА ПРЕДЕЛЫ СЕТКИ!", message_rect_computer)
        if computer_turn:
            set_to_shoot_from = computer_available_to_fire_set
            if around_last_computer_hit_set:
                set_to_shoot_from = around_last_computer_hit_set
            fired_block = computer_shoots(set_to_shoot_from)
            computer_turn = check_hit_or_miss(
                fired_block, human_ships_working, True, human_ships_to_draw, human_ships_set)
            draw_from_dotted_set(dotted_set)
            draw_hit_blocks(hit_blocks)
            screen.fill((255, 255, 255), message_rect_human)
            show_message_at_rect_center(f"Последний ход компьютера: "
                                        f"{letters[fired_block[0] - 16] + str(fired_block[1])}", message_rect_human,
                                        color=(0, 0, 0))
        if not computer.ships_set:
            menu = Menu2('win')
            menu.main_menu()
        if not human_ships_set:
            menu = Menu2('lose')
            menu.main_menu()
        pygame.display.update()


class Menu2:
    def __init__(self, win_lose):
        global draw_text
        self.click = False
        self.font = pygame.font.SysFont('assets/myfont.ttf', 50)
        self.background = pygame.image.load('assets/list.jpg')
        self.win_lose = win_lose

    def main_menu(self):
        while True:
            screen.fill((0, 0, 0))
            screen.blit(self.background, (0, 0))
            mx, my = pygame.mouse.get_pos()
            if self.win_lose == 'win':
                next_button = pygame.Rect(350, 250, 200, 50)
                if next_button.collidepoint((mx, my)):
                    if self.click:
                        level = SecondLevel()
                        level.game()
                draw_text('Вы выиграли', self.font, (255, 0, 0), screen, 350, 190)
                draw_text('к уровню', self.font, (255, 0, 0), screen, 360, 255)
                pygame.draw.rect(screen, (255, 0, 0), next_button, 2)
            else:
                again_button = pygame.Rect(350, 250, 200, 50)
                if again_button.collidepoint((mx, my)):
                    if self.click:
                        menu = Menu(font)
                        menu.main_menu()
                draw_text('Вы проиграли!', self.font, (255, 0, 0), screen, 350, 190)
                draw_text('сначала', self.font, (255, 0, 0), screen, 360, 255)
                pygame.draw.rect(screen, (255, 0, 0), again_button, 2)

            self.click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True

            pygame.display.update()
            mainClock.tick(60)


class Menu:   # меню игры
    def __init__(self, font):
        global draw_text
        self.click = False
        self.font = font
        self.background = pygame.image.load('assets/game_menu.png')
        self.bg = pygame.image.load('assets/list.jpg')

    def main_menu(self):
        while True:
            screen.fill((0, 0, 0))
            screen.blit(self.background, (0, 0))
            mx, my = pygame.mouse.get_pos()
            button_1 = pygame.Rect(370, 200, 200, 50)
            button_2 = pygame.Rect(700, 555, 200, 50)
            if button_1.collidepoint((mx, my)):
                if self.click:
                    self.game()
            if button_2.collidepoint((mx, my)):
                if self.click:
                    self.options()
            pygame.draw.rect(screen, (0, 0, 0), button_1, 2)
            pygame.draw.rect(screen, (0, 0, 0), button_2, 2)
            draw_text('старт', self.font, (0, 0, 0), screen, 430, 210)

            self.click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True

            pygame.display.update()
            mainClock.tick(60)

    def game(self):
        running = True
        while running:
            screen.fill(('#f0f8ff'))
            board = Board(30, 30)
            board.render(screen)
            board.drawer_field_1()
            draw_text('Заполните поле кораблями автоматически или вручную', self.font, (0, 0, 0), screen, 80, 30)
            main()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            mainClock.tick(60)

    def options(self):
        running = True
        x = 10
        y = 150
        sl = {}
        click = False
        with open('rules.txt', encoding='utf8') as f:
            f = f.read().split('\n')
            for i in range(len(f)):
                sl[f[i]] = (x, y)
                y += 40
        while running:
            screen.fill((0, 0, 0))
            screen.blit(self.bg, (0, 0))
            mx, my = pygame.mouse.get_pos()
            go_back = pygame.Rect(370, 400, 200, 50)
            if go_back.collidepoint((mx, my)):
                if click:
                    self.main_menu()
            pygame.draw.rect(screen, (0, 0, 0), go_back, 2)
            draw_text('назад', font, (0, 0, 0), screen, 440, 420)

            click = False
            for key in sl.keys():
                a = sl[key]
                draw_text(key, font, (255, 0, 0), screen, a[0], a[1])
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True

            pygame.display.update()
            mainClock.tick(60)


try:
    menu = Menu(font)
    menu.main_menu()
except Exception as e:
    print(e)
