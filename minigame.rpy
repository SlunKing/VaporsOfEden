init python:
    
    # Функция отыечающая за взаимодействие деталей при перемещении
    def piece_dragged(drags, drop):
        
        if not drop:
            return
        
        # извлечение координат куска пазла и места его отпускания
        p_x = drags[0].drag_name.split("-")[0]
        p_y = drags[0].drag_name.split("-")[1]
        t_x = drop.drag_name.split("-")[0]
        t_y = drop.drag_name.split("-")[1]
        
        # связывание куска пазла с его новым местоположением
        a = []
        a.append(drop.drag_joined)
        a.append((drags[0], 3, 3))
        drop.drag_joined(a)
        
        #Проверка куска пазла на отпускание в правильном месте
        if p_x == t_x and p_y == t_y:

            renpy.music.play("put_puzzle.mp3", channel="sound")

            my_x = int(int(p_x)*active_area_size*x_scale_index)-int(grip_size*x_scale_index)+puzzle_field_offset_x
            my_y = int(int(p_y)*active_area_size*y_scale_index)-int(grip_size*y_scale_index)+puzzle_field_offset_y
            drags[0].snap(my_x,my_y, delay=0.1) # смещение детали на нужное место
            drags[0].draggable = False # отключение перемещения детали
            placedlist[int(p_x),int(p_y)] = True # присваивание детали значения True в общем списке деталей (True - расположен на верном месте)

            # Проверка расположения всех деталей на своём месте
            for i in range(0, grid_width):
                for j in range(0, grid_height):
                    if placedlist[i,j] == False:
                        return
            return True
        return

        
screen jigsaw: # Экран мини-игра на котором размещаются элементы
    
    add im.Scale("minigame/_puzzle_field.png", img_width, img_height) pos(puzzle_field_offset_x, puzzle_field_offset_y) # Размещение поля пазла на экране

    textbutton "Пропуск": # Кнопка пропуска
        xalign 0.9 yalign 0.1 action Return()

    draggroup:

        for i in range(0, grid_width): # Размещение невидимых пустых мест для деталей
            for j in range(0, grid_height):
                $ name = "%s-%s"%(i,j) # Для каждого пазла создаётся уникальное имя
                $ my_x = i*int(active_area_size*x_scale_index)+puzzle_field_offset_x
                $ my_y = j*int(active_area_size*y_scale_index)+puzzle_field_offset_y
                drag:
                    drag_name name
                    child im.Scale("minigame/_blank_space.png", int(active_area_size*x_scale_index), int(active_area_size*y_scale_index) )
                    draggable False # Пустые места неподвижны
                    xpos my_x ypos my_y
            
        for i in range(0, grid_width): # Размещение деталей пазла
            for j in range(0, grid_height):
                $ name = "%s-%s-piece"%(i,j)
                drag:
                    drag_name name
                    child imagelist[i,j] # У каждой детали свой кусок изначального изображения
                    dragged piece_dragged # При перемещении детали происходит вызов функции piece_dragged
                    xpos piecelist[i,j][0] ypos piecelist[i,j][1] # Определение позиции детали

image puzzle_background = "minigame/Minigamebg.png" # Определение фона на экране мини-игры

label puzzle:

    python:
        # Извлекаем размер изначального изображения
        img_width, img_height = renpy.image_size(chosen_img)
        
        
        # Уменьшаем размер изображения в зависимости от соотношения сторон
        if img_width >= img_height and img_width > puzzle_field_size:
            img_scale_down_index = round( (1.00 * puzzle_field_size / img_width), 6)
            img_to_play = im.FactorScale(chosen_img, img_scale_down_index)
            img_width = int(img_width * img_scale_down_index)
            img_height = int(img_height * img_scale_down_index)
            
        elif img_height >= img_width and img_height > puzzle_field_size:
            img_scale_down_index = round( (1.00 * puzzle_field_size / img_height), 6)
            img_to_play = im.FactorScale(chosen_img, img_scale_down_index)
            img_width = int(img_width * img_scale_down_index)
            img_height = int(img_height * img_scale_down_index)
        
        else:
            img_to_play = chosen_img
        
        # Вычисление коэффициентов масштабирования по горизонтали и вертикали для корректного размещения кусков пазла
        x_scale_index = round( (1.00 * (img_width/grid_width)/active_area_size), 6)
        y_scale_index = round( (1.00 * (img_height/grid_height)/active_area_size), 6)
        
        # Создание основного изображения к которому будут привязываться куски пазла
        mainimage = im.Composite((int(img_width+(grip_size*2)*x_scale_index), int(img_height+(grip_size*2)*y_scale_index)),(int(grip_size*x_scale_index), int(grip_size*y_scale_index)), img_to_play)
        
        # Определение индексов кусков пазла расположененых по краям
        top_row = []
        for i in range (0, grid_width):
            top_row.append(i)
            
        bottom_row = []
        for i in range (0, grid_width):
            bottom_row.append(grid_width*(grid_height-1)+i)
            
        left_column = []
        for i in range (0, grid_height):
            left_column.append(grid_width*i)
            
        right_column = []
        for i in range (0, grid_height):
            right_column.append(grid_width*i + (grid_width-1) )
        
        
        # jigsaw_grid содержит в себе информацию о форме каждого куска пазла
        # Образование деталей начинается с верхнего слоя слева направо до конца изображения вниз
        jigsaw_grid = []
        for i in range(0,grid_height):
            for j in range (0,grid_width):
                jigsaw_grid.append([9,9,9,9]) # [Сверху, Справа, Снизу, Слева]

        # В данном цикле происходит определение формы каждого куска пазла        
        for i in range(0,grid_height):
            for j in range (0,grid_width):
                if grid_width*i+j not in top_row:
                    if jigsaw_grid[grid_width*(i-1)+j][2] == 1:
                        jigsaw_grid[grid_width*i+j][0] = 2
                    else:
                        jigsaw_grid[grid_width*i+j][0] = 1
                else:
                    jigsaw_grid[grid_width*i+j][0] = 0
                    
                if grid_width*i+j not in right_column:
                    jigsaw_grid[grid_width*i+j][1] = renpy.random.randint(1,2)
                else:
                    jigsaw_grid[grid_width*i+j][1] = 0
                    
                if grid_width*i+j not in bottom_row:
                    jigsaw_grid[grid_width*i+j][2] = renpy.random.randint(1,2)
                else:
                    jigsaw_grid[grid_width*i+j][2] = 0
                    
                if grid_width*i+j not in left_column:
                    if jigsaw_grid[grid_width*i+j-1][1] == 1:
                        jigsaw_grid[grid_width*i+j][3] = 2
                    else:
                        jigsaw_grid[grid_width*i+j][3] = 1
                else:
                    jigsaw_grid[grid_width*i+j][3] = 0
                    
        
        # Словари для хранения информации о каждой детали пазла
        piecelist = dict()
        imagelist = dict()
        placedlist = dict()
        
        # Распределение каждой детали пазла на экране
        for i in range(0,grid_width):
            for j in range (0,grid_height):
                piecelist[i,j] = [int(renpy.random.randint(0, int(config.screen_width * 0.8 - puzzle_field_size))+puzzle_field_size / 1.5), int(renpy.random.randint(0, int(config.screen_height * 0.7)))]
                # Создание временного изображения для каждого куска пазла
                temp_img = im.Crop(mainimage, int(i*active_area_size*x_scale_index), int(j*active_area_size*y_scale_index), int(puzzle_piece_size*x_scale_index), int(puzzle_piece_size*y_scale_index))
        
        # Создание изображения для куска пазла на основе его формы
        # Вращает изображение для формирования верхней, правой, нижней и левой сторон детали пазла
                imagelist[i,j] = im.Composite(
        (int(puzzle_piece_size*x_scale_index), int(puzzle_piece_size*y_scale_index)),
        (0,0), im.AlphaMask(temp_img, im.Scale(im.Rotozoom("minigame/_00%s.png"%(jigsaw_grid[grid_width*j+i][0]), 0, 1.0), int(puzzle_piece_size*x_scale_index), int(puzzle_piece_size*y_scale_index))),
        (0,0), im.AlphaMask(temp_img, im.Scale(im.Rotozoom("minigame/_00%s.png"%(jigsaw_grid[grid_width*j+i][1]), 270, 1.0), int(puzzle_piece_size*x_scale_index), int(puzzle_piece_size*y_scale_index))),
        (0,0), im.AlphaMask(temp_img, im.Scale(im.Rotozoom("minigame/_00%s.png"%(jigsaw_grid[grid_width*j+i][2]), 180, 1.0), int(puzzle_piece_size*x_scale_index), int(puzzle_piece_size*y_scale_index))),
        (0,0), im.AlphaMask(temp_img, im.Scale(im.Rotozoom("minigame/_00%s.png"%(jigsaw_grid[grid_width*j+i][3]), 90, 1.0), int(puzzle_piece_size*x_scale_index), int(puzzle_piece_size*y_scale_index)))
        )
                placedlist[i,j] = False

    # Установка заднего фона, вызов экрана пазла и ссылка на конец при сборке
    show puzzle_background as puzzle_bg
    call screen jigsaw
    jump win
    
label win:
    show puzzle_background as puzzle_bg
    # Показ собранного изображения по центру
    show expression img_to_play as win_img at truecenter with dissolve 

    "Пазл собран"
    hide puzzle_bg
    hide win_img
    return # Возврат в основную игру
    
