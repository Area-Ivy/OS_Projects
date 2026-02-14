import sys
import time
from functools import partial

from PyQt5.QtCore import QThread, pyqtSignal, QSize  
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLCDNumber, QLabel

class Example(QWidget):  # 主窗口

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()  # 主布局
        right_layout = QGridLayout()  # 右侧布局
        left_layout = QGridLayout()  # 左侧布局
        left_layout.setSpacing(0)
        right_layout.setSpacing(0)

        left_widget = QWidget()  # 左侧部件
        right_widget = QWidget()  # 右侧部件
        left_widget.setLayout(left_layout)  # 设置左侧布局
        right_widget.setLayout(right_layout)  # 设置右侧布局
        main_layout.addWidget(left_widget)  # 添加左侧部件到主布局
        main_layout.addWidget(right_widget)  # 添加右侧部件到主布局
        self.setLayout(main_layout)  # 设置主窗口布局

        elevator_button_labels = [f'{i}' for i in range(1, 21)]
        
        elevator_button_positions = [(row, col) for col in range(2) for row in range(10)]

        hallway_up_labels = [f'▲ {i}' for i in range(1, 21)]
        hallway_down_labels = [f'▼ {i}' for i in range(1, 21)]

        for elevator_index in range(5):
            lcd_display = QLCDNumber()  
            lcd_display.setObjectName(f"lcd_{elevator_index + 1}")
            lcd_display.setDigitCount(2)  
            lcd_display.setStyleSheet("""
                QLCDNumber {
                    border: 2px solid #4CAF50; 
                    border-radius: 5px;         
                    background: #e0f7fa;        
                    color: #333333;             
                }
            """)
            left_layout.addWidget(lcd_display, 0, 3 * elevator_index, 2, 2)  

        for elevator_index in range(5):
            fault_button = QPushButton("紧急按钮")  
            fault_button.setFont(QFont("Microsoft YaHei", 12))
            fault_button.setObjectName(f"fault_{elevator_index + 1}")
            fault_button.setMinimumHeight(40)
            fault_button.clicked.connect(partial(fault, elevator_index + 1))  
            fault_button.setStyleSheet("""
                QPushButton {
                    background-color: #ffcccc;
                    border: 1px solid #ff6666;
                    border-radius: 8px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #ff9999;
                }
                QPushButton:pressed {
                    background-color: #ff6666;
                }
            """)
            left_layout.addWidget(fault_button, 2, 3 * elevator_index, 1, 2)  

        for elevator_index in range(5):
            floor_number = 1
            for position, label in zip(elevator_button_positions, elevator_button_labels):
                if label == '':
                    continue
                floor_button = QPushButton(label)
                floor_button.setFont(QFont("Microsoft YaHei", 12))
                floor_button.setObjectName(f"floor_{elevator_index + 1}_{floor_number}")
                floor_button.clicked.connect(partial(set_goal, elevator_index + 1, floor_number))
                floor_number += 1
                floor_button.setMaximumHeight(60)  
                left_layout.addWidget(floor_button, position[0] + 3, position[1] + elevator_index * 3)  

        for elevator_index in range(5):
            open_button = QPushButton()
            open_button.setObjectName(f"open_{elevator_index + 1}")
            open_button.setMinimumHeight(80)
            left_layout.addWidget(open_button, 13, 3 * elevator_index, 1, 2)

        # 初始化楼道向上按钮
        for index, label in enumerate(hallway_up_labels):
            if index + 1 == 20:  # 跳过 20 楼的向上按钮
                continue
            up_button = QPushButton(label)
            up_button.setFont(QFont("Microsoft YaHei"))
            up_button.setObjectName(f"hallway_up_{index + 1}")
            up_button.setMinimumHeight(42)
            up_button.clicked.connect(partial(set_global_goal, 'up', index + 1))
            right_layout.addWidget(up_button, 20 - index, 0)

        # 初始化楼道向下按钮
        for index, label in enumerate(hallway_down_labels):
            if index + 1 == 1:  # 跳过 1 楼的向下按钮
                continue
            down_button = QPushButton(label)
            down_button.setFont(QFont("Microsoft YaHei"))
            down_button.setObjectName(f"hallway_down_{index + 1}")
            down_button.setMinimumHeight(42)
            down_button.clicked.connect(partial(set_global_goal, 'down', index + 1))
            right_layout.addWidget(down_button, 20 - index, 1)

        self.move(10, 10)
        self.setWindowTitle('Elevator-Dispatching-System')
        self.show()


class WorkThread(QThread):
    # 实例化一个信号对象
    trigger = pyqtSignal(int)

    def __init__(self, the_int):
        super(WorkThread, self).__init__()
        self.int = the_int
        self.trigger.connect(check)

    def run(self):
        while (1):
            # 检查是否需要开门
            if should_sleep[self.int - 1] == 1:
                button = ex.findChild(QPushButton, f"open_{self.int}")
                if button:
                    # 设置背景颜色为绿色
                    button.setStyleSheet("QPushButton { background-color: green; }")
                    time.sleep(2)
                    # 恢复默认背景颜色
                    button.setStyleSheet("QPushButton { background-color: none; }")

                should_sleep[self.int - 1] = 0

            # 检查是否需要向下运行时开门
            if should_sleep[self.int - 1 + 5] == 1:
                button = ex.findChild(QPushButton, f"open_{self.int}")
                if button:
                    # 设置背景颜色为绿色
                    button.setStyleSheet("QPushButton { background-color: green; }")
                    time.sleep(2)
                    # 恢复默认背景颜色
                    button.setStyleSheet("QPushButton { background-color: none; }")

                should_sleep[self.int - 1 + 5] = 0

            # 触发信号更新状态
            self.trigger.emit(self.int)
            time.sleep(1)


def check(the_int):
    """
    检查电梯状态并更新显示。
    :param the_int: 电梯编号
    """
    if pause[the_int - 1] == 0:  # 如果电梯处于故障状态
        return

    # 更新电梯当前楼层
    if state[the_int - 1] != 0:
        floor[the_int - 1] += state[the_int - 1]

    current_floor = floor[the_int - 1]

    # 更新显示器
    lcd = ex.findChild(QLCDNumber, f"lcd_{the_int}")
    if lcd:
        lcd.display(current_floor)

    # 清除内部按钮状态
    button = ex.findChild(QPushButton, f"floor_{the_int}_{current_floor}")
    if button:
        button.setStyleSheet("QPushButton { background-color: none; }")

    # 清除外部按钮状态（无论上行还是下行）
    up_btn = ex.findChild(QPushButton, f"hallway_up_{current_floor}")
    down_btn = ex.findChild(QPushButton, f"hallway_down_{current_floor}")
    if up_btn:
        up_btn.setStyleSheet("QPushButton { background-color: none; }")
    if down_btn:
        down_btn.setStyleSheet("QPushButton { background-color: none; }")

    # 检查是否需要停留
    if current_floor in elevator_goal[the_int - 1] or \
       (state[the_int - 1] == 1 and current_floor in people_up) or \
       (state[the_int - 1] == -1 and current_floor in people_down):
        should_sleep[the_int - 1 + (5 if state[the_int - 1] == -1 else 0)] = 1

    # 移除楼层请求
    people_up.discard(current_floor)
    people_down.discard(current_floor)
    elevator_goal[the_int - 1].discard(current_floor)

    # 更新电梯状态
    update_elevator_state(the_int - 1)


def update_elevator_state(elevator_index):
    """
    更新电梯状态。
    :param elevator_index: 电梯索引
    """
    goals = list(elevator_goal[elevator_index])
    if not goals:
        state[elevator_index] = 0
    elif state[elevator_index] == -1 and min(goals) > floor[elevator_index]:
        state[elevator_index] = 1
    elif state[elevator_index] == 1 and max(goals) < floor[elevator_index]:
        state[elevator_index] = -1
    elif state[elevator_index] == 0:
        if max(goals) > floor[elevator_index]:
            state[elevator_index] = 1
        elif min(goals) < floor[elevator_index]:
            state[elevator_index] = -1


def fault(elev):
    """
    切换电梯的故障状态。
    :param elev: 电梯编号
    """
    is_fault = pause[elev - 1] == 0
    pause[elev - 1] = 1 if is_fault else 0

    for flr in range(1, 21):
        button = ex.findChild(QPushButton, f"floor_{elev}_{flr}")
        if button:
            button.setStyleSheet("QPushButton { background-color: none; }" if is_fault else "QPushButton { background-color: red; }")

    if not is_fault:
        redistribute_goals(elev - 1)


def redistribute_goals(elevator_index):
    """
    重新分配故障电梯的目标楼层。
    :param elevator_index: 电梯索引
    """
    for flr in list(elevator_goal[elevator_index]):
        if task_source[elevator_index].get(flr) == 'external':
            closest_elevator = find_closest_elevator(elevator_index, flr)
            if closest_elevator is not None:
                elevator_goal[closest_elevator].add(flr)
                task_source[closest_elevator][flr] = 'external'

    # 清空故障电梯的目标楼层
    elevator_goal[elevator_index].clear()
    task_source[elevator_index].clear()
    state[elevator_index] = 0


def find_closest_elevator(excluded_index, target_floor):
    """
    查找距离目标楼层最近的未故障电梯。
    :param excluded_index: 排除的电梯索引
    :param target_floor: 目标楼层
    :return: 最近的电梯索引或 None
    """
    closest_elevator = None
    min_distance = float('inf')
    for i in range(5):
        if i != excluded_index and pause[i] == 1:
            distance = abs(floor[i] - target_floor)
            if distance < min_distance:
                min_distance = distance
                closest_elevator = i
    return closest_elevator


def set_goal(elev, flr):
    """
    设置目标楼层。
    :param elev: 电梯编号
    :param flr: 目标楼层编号
    """
    if pause[elev - 1] == 0:
        return

    # 更新按钮样式
    button = ex.findChild(QPushButton, f"floor_{elev}_{flr}")
    if button:
        button.setStyleSheet("QPushButton { background-color: yellow; }")

    # 添加目标楼层
    elevator_goal[elev - 1].add(flr)
    task_source[elev - 1][flr] = 'internal'


def set_global_goal(direction, flr):
    """
    设置楼道请求的目标楼层。
    :param direction: 请求方向
    :param flr: 目标楼层编号
    """
    button = ex.findChild(QPushButton, f"hallway_{direction}_{flr}")
    if button:
        button.setStyleSheet("QPushButton { background-color: yellow; }")

    if direction == 'up':
        people_up.add(flr)
    else:
        people_down.add(flr)

    closest_elevator = find_closest_elevator(None, flr)
    if closest_elevator is not None:
        elevator_goal[closest_elevator].add(flr)
        task_source[closest_elevator][flr] = 'external'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()

    # 初始化全局变量
    def initialize_elevator_goals(num_elevators):
        """初始化每部电梯的目标楼层集合"""
        return [set() for _ in range(num_elevators)]

    def initialize_list_with_value(num_elevators, value):
        """初始化指定长度的列表，并填充指定值"""
        return [value for _ in range(num_elevators)]

    def initialize_task_sources(num_elevators):
        """初始化每部电梯的任务来源字典"""
        return [{} for _ in range(num_elevators)]

    NUM_ELEVATORS = 5  # 电梯数量

    # 表示目标楼层
    elevator_goal = initialize_elevator_goals(NUM_ELEVATORS)

    # 此数组表示电梯状态：0表示停止，1表示向上运行，-1表示向下运行
    state = initialize_list_with_value(NUM_ELEVATORS, 0)

    # 指示该电梯是否暂停运行：1表示正常，0表示暂停
    pause = initialize_list_with_value(NUM_ELEVATORS, 1)

    # 表示当前楼层
    floor = initialize_list_with_value(NUM_ELEVATORS, 1)

    # 表示楼道里的向上的请求
    people_up = set()

    # 表示楼道里的向下的请求
    people_down = set()

    # 每部电梯一个字典，键为楼层，值为任务来源（'internal' 或 'external'）
    task_source = initialize_task_sources(NUM_ELEVATORS)

    # 初始化 should_sleep 变量
    should_sleep = [0] * (NUM_ELEVATORS * 2)  # 每部电梯有两个状态：正常运行和向下运行

    # 五个线程对应五部电梯，每隔一定时间检查每部电梯的状态和 elevator_goal 数组，并作出相应的行动
    threads = [WorkThread(i + 1) for i in range(NUM_ELEVATORS)]
    for thread in threads:
        thread.start()

    sys.exit(app.exec_())