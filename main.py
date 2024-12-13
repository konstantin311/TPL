import json
import io  
import sys  
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import networkx as nx


class DFA:
    def __init__(self, alphabet, substring, modulus):
        self.alphabet = alphabet
        self.substring = substring
        self.modulus = modulus
        self.states = {}
        self.start_state = "q1"
        self.final_states = set()
        self.transitions = {}
        self.state_counter = 1

        self._build_dfa()

    def _build_dfa(self):
        substring_length = len(self.substring)
        state_mapping = {}

        for i in range(substring_length + 1):
            for mod in range(self.modulus):
                logical_state = (i, mod)
                state_name = f"q{self.state_counter}"
                self.states[state_name] = logical_state
                state_mapping[logical_state] = state_name
                print(f"Создано состояние {state_name}: {logical_state}")
                self.state_counter += 1

        for i in range(substring_length + 1):
            for mod in range(self.modulus):
                current_state = state_mapping[(i, mod)]

                for char in self.alphabet:
                    if i < substring_length:
                        if char == self.substring[i]:
                            next_state = (i + 1, (mod + 1) % self.modulus)
                            print(f"Символ '{char}' , переходим в состояние {next_state}")
                        elif char == self.substring[0]:
                            next_state = (1, (mod + 1) % self.modulus)
                            print(f"Символ '{char}' , переходим в состояние {next_state}")
                        else:
                            next_state = (0, (mod + 1) % self.modulus)
                            print(f"Символ '{char}' , переходим в состояние {next_state}")
                    else:
                        next_state = (i, (mod + 1) % self.modulus)
                        print(f"Символ '{char}' , переходим в состояние {next_state}")

                    self.transitions[(current_state, char)] = state_mapping[next_state]
                   
                if i == substring_length and mod == 0:
                    self.final_states.add(current_state)

    def visualize(self):
        graph = nx.DiGraph()
        edges = {}

        for (state, char), next_state in self.transitions.items():
            if (state, next_state) not in edges:
                edges[(state, next_state)] = []
            edges[(state, next_state)].append(char)

        for (state, next_state), labels in edges.items():
            graph.add_edge(state, next_state, label=",".join(labels))

        pos = nx.spring_layout(graph)

        plt.figure(figsize=(10, 8))
        colors = []
        for node in graph.nodes:
            if node == self.start_state:
                colors.append("green")
            elif node in self.final_states:
                colors.append("violet")
            else:
                colors.append("lightblue")

        nx.draw(
            graph, pos, with_labels=True, node_color=colors, node_size=2000, font_size=10
        )
        edge_labels = nx.get_edge_attributes(graph, "label")
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
        plt.title("DFA Graph")
        plt.show()

    def transition_table(self):
        table = [["State", "Start/Final"] + self.alphabet]
        for state in self.states.keys():
            row = [state]
            if state == self.start_state:
                row.append("Start")
            elif state in self.final_states:
                row.append("Final")
            else:
                row.append("")
            for char in self.alphabet:
                row.append(self.transitions.get((state, char), "-"))
            table.append(row)
        return table

    def format_transition_table(self):
        table = self.transition_table()
        formatted_table = ""
        for row in table:
            formatted_table += "\t".join(row) + "\n"
        return formatted_table
    
    def save_to_json(self, file_path="dfa_transitions.json"):
        data = {
            "states": list(self.states.keys()),
            "start_state": self.start_state,
            "final_states": list(self.final_states),
            "transitions": {
                f"{state},{char}": next_state
                for (state, char), next_state in self.transitions.items()
            },
        }
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def process_string(self, string):
        output_log = []
        current_state = self.start_state
        output_log.append(f"Начальное состояние: {current_state}\n")
        for idx, char in enumerate(string):
            if (current_state, char) not in self.transitions:
                output_log.append(
                    f"Ошибка: символ '{char}' из строки не имеет перехода из состояния {current_state} => символ не принадлежит алфавиту языка.\n"
                )
                return False, "".join(output_log)
            next_state = self.transitions[(current_state, char)]
            output_log.append(
                f"Шаг {idx + 1}: символ '{char}', текущее состояние {current_state} → следующее состояние {next_state}\n"
            )
            current_state = next_state
        output_log.append(f"Конечное состояние: {current_state}\n")
        return current_state in self.final_states, "".join(output_log)


def validate_input(alphabet, substring, modulus):
    errors = []

    # Validate alphabet
    if not alphabet:
        errors.append("Алфавит не должен быть пустым.")
    else:
        alphabet_set = set(alphabet.split(","))
        if "" in alphabet_set:
            errors.append("Алфавит содержит пустые элементы.")
        if any(len(char) != 1 for char in alphabet_set):
            errors.append("Алфавит должен состоять из одиночных символов, разделенных запятыми.")

    # Validate substring
    if not substring:
        errors.append("Обязательная подцепочка не должна быть пустой.")
    else:
        if alphabet_set and not set(substring).issubset(alphabet_set):
            errors.append("Обязательная подцепочка должна состоять только из символов алфавита.")

    # Validate modulus
    try:
        modulus_value = int(modulus)
        if modulus_value <= 0:
            errors.append("Кратность цепочек должна быть положительным числом.")
    except ValueError:
        errors.append("Кратность цепочек должна быть целым числом.")

    return errors


def show_author_info():
    
    sg.popup(
        "Автор: студент группы ИП-113 Ефремов Константин\n\n"
        "Тема: Написать программу, которая по предложенному описанию языка построит детерминированный конечный автомат, "
        "распознающий этот язык, и проверит вводимые с клавиатуры цепочки на их принадлежность языку. Предусмотреть "
        "возможность поэтапного отображения на экране процесса проверки цепочек. Функция переходов ДКА может изображаться "
        "в виде таблицы и графа (выбор вида отображения посредством меню).\n\n"
        "Варианты задания языка:\n"
        "- Алфавит\n"
        "- Обязательная фиксированная подцепочка\n"
        "- Кратность длины всех цепочек языка"
    )


def show_help():
    
    sg.popup(
        "Пример входных данных:\n\n"
        "Алфавит: a,b\n"
        "Обязательная подцепочка: ab\n"
        "Кратность длины цепочек: 2\n\n"
        "Описание:\n"
        "- Алфавит — символы, из которых состоят строки языка (например: a,b,c).\n"
        "- Обязательная подцепочка — фиксированная последовательность символов, которая должна быть в строках (например: ab).\n"
        "- Кратность длины цепочек — длина строк должна делиться на указанное число (например: 2).\n\n"
        "После ввода этих данных создайте ДКА и проверьте строки."
    )


def main():
    layout = [
        [sg.Button("Автор/Тема", key="author_button"), sg.Button("Справка", key="help_button")],
        [sg.Text("Загрузить входные данные из файла:"), sg.Input(key="file_path"), sg.FileBrowse(), sg.Button("Загрузить файл")],
        [sg.Text("Введите алфавит через запятую:"), sg.InputText(key="alphabet", size=(30, 1))],
        [sg.Text("Введите обязательную подцепочку:"), sg.InputText(key="substring", size=(30, 1))],
        [sg.Text("Введите кратность длины цепочек:"), sg.InputText(key="modulus", size=(30, 1))],
        [sg.Button("Создать ДКА"), sg.Button("Визуализировать")],
        [sg.Text("Введите строку для проверки:"), sg.InputText(key="test_string", size=(30, 1))],
        [sg.Button("Проверить строку"), sg.Text("", key="result", size=(40, 1))],
        [sg.Text("Шаги выполнения проверки:")],
        [sg.Multiline("", key="process_log", size=(60, 15), disabled=True)],
        [sg.Text("Таблица переходов и отладочная информация:")],  # Изменён текст
        [sg.Multiline("", key="transition_table", size=(60, 15), disabled=True)],
    ]

    window = sg.Window("DFA Creator", layout, finalize=True, resizable=True)
    dfa = None
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "author_button":
            show_author_info()
        elif event == "help_button":
            show_help()
        elif event == "Загрузить файл":
            try:
                file_path = values["file_path"]
                with open(file_path, "r") as file:
                    data = json.load(file)
                window["alphabet"].update(",".join(data["alphabet"]))
                window["substring"].update(data["substring"])
                window["modulus"].update(str(data["modulus"]))
                sg.popup("Данные из файла успешно загружены!")
            except Exception as e:
                sg.popup(f"Ошибка загрузки файла: {e}")
        elif event == "Создать ДКА":
            try:
                alphabet = values["alphabet"]
                substring = values["substring"]
                modulus = values["modulus"]

                validation_errors = validate_input(alphabet, substring, modulus)
                if validation_errors:
                    sg.popup("Ошибки ввода:\n" + "\n".join(validation_errors))
                    continue

                alphabet = alphabet.split(",")  
                modulus = int(modulus)  

                output_stream = io.StringIO()
                sys.stdout = output_stream

                dfa = DFA(alphabet, substring, modulus)
                dfa.save_to_json("dfa_transitions.json")

                sys.stdout = sys.__stdout__

                debug_output = output_stream.getvalue()
                formatted_table = dfa.format_transition_table()
                window["transition_table"].update(debug_output + "\n\n" + formatted_table)

                sg.popup("DFA успешно создан!")
            except Exception as e:
                sys.stdout = sys.__stdout__  
                sg.popup(f"Ошибка: {e}")
        elif event == "Визуализировать":
            if dfa:
                dfa.visualize()
            else:
                sg.popup("Сначала создайте DFA.")
        elif event == "Проверить строку":
            if dfa:
                test_string = values["test_string"]
                belongs, process_log = dfa.process_string(test_string)
                result = "Принадлежит языку." if belongs else "Не принадлежит языку."
                window["result"].update(result)
                window["process_log"].update(process_log)
            else:
                sg.popup("Сначала создайте DFA.")

    window.close()


if __name__ == "__main__":
    main()
