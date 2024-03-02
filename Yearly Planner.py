import tkinter as tk
from functools import partial
import os
import yaml
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import datetime


class FramesData:
    def __init__(self):
        self.frames = []
        self.data = []


class EightFramesApp:
    def __init__(self):
        self.fresh_day_index = None
        self.checkbox_vars_today = []
        self.checkbox_today = {}
        self.avg = 0
        self.fresh_date = None
        self.fresh_day = {}
        self.checkbox_vars = None
        self.radio_button = None
        self.yaml_file_name = None
        self.yaml_data = None
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.frames = FramesData()
        # Add top content
        self.top_frame = tk.Frame(self.root, height=100, bg="gray")
        self.top_frame.place(x=1000, y=10.1, anchor="n", relwidth=1.9)  # Center the frame horizontally

        self.app_name_label = tk.Label(self.top_frame, text="Yearly Planner", font=("Helvetica", 24))
        self.app_name_label.place(x=1800, y=25.5, anchor="center")  # Center the label within the frame

        # Create frames for rectangles
        self.frames.frames.extend(self.create_frames())
        self.frames.data.extend(self.add_data_to_frames(frame_number=0))

    class ZeroVariable:
        def get(self):
            return 0

    def allocate_tasks(self, tasks_data, ignored_tasks=None):
        if ignored_tasks is None:
            ignored_tasks = {}

        # Convert ignoredTasks and tasks to strings
        ignored_tasks = {str(task_name): value for task_name, value in ignored_tasks.items()}

        # Initialize a mask to indicate which tasks to include
        include_mask = {}

        # Initialize a list to store ignored task names
        ignored_task_names = []

        # Initialize a dictionary to store scores for sorted tasks and average scores for ignored tasks
        scores_dict = {}

        # Mark ignored tasks in the mask and add ignored task names to the list
        for task_name, task_data in tasks_data.items():
            time_assigned = task_data[0]
            time_spent = task_data[1]
            priority = task_data[2]
            # Higher the number, lesser the priority.
            total_time = time_assigned - time_spent
            score = total_time / priority
            if total_time >= 0 and ignored_tasks.get(task_name, self.ZeroVariable()).get() != 1:
                include_mask[task_name] = score
                scores_dict[task_name] = score
            else:
                ignored_task_names.append(task_name)
                scores_dict[task_name] = 0  # Assigning a placeholder value for ignored tasks

        # Calculate the average score for non-ignored tasks
        avg_score = sum(scores_dict.values()) / len(scores_dict) if scores_dict else 0

        # Assign the average score to all ignored tasks in the scores_dict
        for ignored_task in ignored_task_names:
            scores_dict[ignored_task] = avg_score

        # Sort tasks based on scores (in descending order) while considering the mask
        sorted_tasks = sorted(include_mask.keys(), key=lambda x: include_mask[x], reverse=True)

        return sorted_tasks, ignored_task_names, scores_dict, avg_score

    def create_frames(self):
        frames = []
        num_rows = 2  # Number of rows
        num_cols = 4  # Number of columns
        frame_width = self.root.winfo_screenwidth() // num_cols  # Set frame width
        frame_height = (self.root.winfo_screenheight() - 100) // num_rows  # Set frame height

        for i in range(num_rows):
            for j in range(num_cols):
                x = j * frame_width  # Calculate x coordinate
                y = i * frame_height + 100  # Calculate y coordinate

                frame = tk.Frame(self.root, width=frame_width, height=frame_height, borderwidth=2,
                                 relief="solid")
                frame.place(x=x, y=y)  # Place the frame at (x, y)
                frames.append(frame)
        frames = frames[::-1]
        return frames

    def frame_obj(self, i, data, frame):
        # 0th frame is for accepting Name and age and creating / Loading database.
        if i == 0:
            data.append(tk.Label(frame, text="Name:"))
            data[-1].place(x=0, y=0)
            data.append(tk.Entry(frame))
            data[-1].place(x=60, y=0)
            data.append(tk.Label(frame, text="Age:"))
            data[-1].place(x=0, y=40)
            data.append(tk.Entry(frame))
            data[-1].place(x=60, y=40)
            data.append(tk.Button(frame, text="Proceed", command=partial(self.button_clicked, i)))
            data[-1].place(x=50, y=200)
        elif i == 4:
            x = [1, 2, 3, 4, 5]
            y = [2, 3, 5, 7, 11]

            width = frame.winfo_width()
            height = frame.winfo_height()

            # Create a new figure with appropriate size
            fig, ax = plt.subplots(figsize=(width / 100, height / 100))  # Adjust dimensions as needed
            # Plot the data
            ax.plot(x, y, marker='o', linestyle='-')

            # Set labels and title
            ax.set_xlabel('X Label')
            ax.set_ylabel('Y Label')
            ax.set_title('Sample Plot')

            # Embed the plot in the Tkinter app
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Fill and expand to fit the frame
        elif i == 1:
            data.append(tk.Label(frame, text="Task Name:"))
            data[-1].place(x=0, y=0)
            data.append(tk.Entry(frame))
            data[-1].place(x=60, y=0)
            data.append(tk.Label(frame, text="Time Assigned:"))
            data[-1].place(x=0, y=40)
            data.append(tk.Entry(frame))
            data[-1].place(x=60, y=40)
            data.append(tk.Label(frame, text="Priority:"))
            data[-1].place(x=0, y=80)
            data.append(tk.Entry(frame))
            data[-1].place(x=60, y=80)
            status_info = "Next"
            data.append(tk.Button(frame, text="Next", command=partial(self.button_clicked, i, status_info)))
            data[-1].place(x=50, y=200)
            status_info = "Moving On"
            data.append(
                tk.Button(frame, text="Moving On",
                          command=partial(self.button_clicked, i, status_info)))
            data[-1].place(x=150, y=200)
        elif i == 2:
            status_info = "Create"
            self.radio_button = tk.IntVar()
            data.append(tk.Button(frame, text="Create New Day", command=partial(self.button_clicked, i, status_info)))
            data[-1].place(x=20, y=100)
            status_info = "Basic"
            data.append(tk.Radiobutton(frame, text="Basic", variable=self.radio_button, value=4,
                                       command=partial(self.button_clicked, i, status_info)))
            data[-1].place(x=20, y=20)
            status_info = "Normal"
            data.append(tk.Radiobutton(frame, text="Normal", variable=self.radio_button, value=9,
                                       command=partial(self.button_clicked, i, status_info)))
            data[-1].place(x=20, y=40)
            status_info = "Expanded"
            data.append(tk.Radiobutton(frame, text="Expanded", variable=self.radio_button, value=12,
                                       command=partial(self.button_clicked, i, status_info)))
            data[-1].place(x=20, y=60)
        elif i == 3:
            data.append(tk.Label(frame, text="Select Mandatory Tasks for the Day", font=("Helvetica", 14)))
            data[-1].place(x=20, y=20)
            self.checkbox_vars = {}
            tasks_data = self.yaml_data["Tasks_List"]
            for j, key in enumerate(tasks_data.keys()):
                var = tk.IntVar()
                self.checkbox_vars[key] = var
                data.append(tk.Checkbutton(frame, text=key, variable=var))
                data[-1].place(x=10, y=40 + j * 30)

            continue_button = tk.Button(frame, text="Continue", command=partial(self.button_clicked, i))
            continue_button.place(x=10, y=40 + len(tasks_data) * 30)
        elif i == 5:
            # frame.title("Task Priorities")
            new_day = max(self.yaml_data['Days'].keys())
            tasks = self.yaml_data['Days'][new_day]['task_list']
            row = 0
            for task_name, task_data in tasks.items():
                time_allocated, score, ena_disa = task_data
                v = self.create_checkbox(task_name, score, row, frame, data, ena_disa)
                self.checkbox_today.update({task_name: v})
                row += 1
            width = frame.winfo_width()
            height = frame.winfo_height()
            submit_data = tk.Button(frame, text="submit", command=partial(self.button_clicked, i))
            submit_data.place(x=10, y=40 + len(tasks) * 30)
        return data

    def add_data_to_frames(self, frame_number):
        frames_data = []

        for i, frame in enumerate(self.frames.frames):
            data = []
            if i == frame_number:
                data = self.frame_obj(i, data, frame)
            frames_data.append(data)
        return frames_data

    def hide_all_widgets(self, frame):
        for child in frame.winfo_children():
            child.place_forget()

    def select_tasks_from_dict(self, root, tasks_data):
        selected_tasks = []

        def continue_clicked():
            nonlocal selected_tasks
            for key, var in checkbox_vars.items():
                if var.get() == 1:
                    selected_tasks.append(key)
            root.destroy()
            return selected_tasks

        checkbox_vars = {}

        for i, key in enumerate(tasks_data.keys()):
            var = tk.IntVar()
            checkbox_vars[key] = var
            checkbox = tk.Checkbutton(root, text=key, variable=var)
            checkbox.grid(row=i, column=0, sticky="w")

        continue_button = tk.Button(root, text="Continue", command=continue_clicked)
        continue_button.grid(row=len(tasks_data), column=0, pady=10)

        # root.mainloop()

        # return selected_tasks

    def check_if_all_tasks_for_day_complete(self, tasks):
        """
        Check if all tasks for the day are complete.

        Args:
            tasks (dict): A dictionary containing tasks as keys and their completion status as values.
                          Completion status is represented as 1 for complete and 0 for incomplete.

        Returns:
            bool: True if all tasks are complete, False otherwise.
        """
        for value in tasks.values():
            if value.get() != 1:
                return False
        return True

    def remove_after_session(self, input_str):
        """
        Remove everything after "-session-" in the input string and return the modified string.

        Args:
            input_str (str): The input string.

        Returns:
            str: The modified string after removing everything after "-session-".
        """
        if "-session-" in input_str:
            return input_str.split("-session-")[0]
        else:
            return input_str

    def update_main_task_list(self, frame_number=5):

        for index, (element, value) in enumerate(self.checkbox_today.items()):
            if value.get() == 1 and self.frames.data[frame_number][index]['state'] != 'disabled':
                element_stripped = self.remove_after_session(element).lower()
                self.yaml_data["Tasks_List"].get(element_stripped)[1] += 30

    def set_third_element_to_one(self, key=None):
        """
        Set the third element in the list to 1 for the specified key in the input dictionary,
        or for all keys if no key is provided.

        Args:
            input_dict (dict): A dictionary where the values are lists of at least 3 numbers.
            key (hashable, optional): The key for which to set the third element to 1. If not provided,
                                      the third element is set to 1 for all keys.

        Returns:
            dict: The modified dictionary with the third element set to 1 for the specified key,
                  or for all keys if no key is provided.
        """
        if key is not None:
            if key in self.yaml_data['Days'][self.fresh_day_index]['task_list']:
                self.yaml_data['Days'][self.fresh_day_index]['task_list'][key][2] = 1
        else:
            for key in self.yaml_data['Days'][self.fresh_day_index]['task_list']:
                self.yaml_data['Days'][self.fresh_day_index]['task_list'][key][2] = 1

    def remove_completed_tasks(self, man_tasks):
        return_tasks = []
        for index, task in enumerate(man_tasks):
            print(self.yaml_data['Tasks_List'][task][0])
            print(self.yaml_data['Tasks_List'][task][1])
            if self.yaml_data['Tasks_List'][task][0] - self.yaml_data['Tasks_List'][task][1] <= 0:
                print('removing ' + task + '\n')
            else:
                return_tasks.append(man_tasks[index])
        return return_tasks

    def button_clicked(self, frame_number, *args):
        print(f"Button from frame {frame_number} was clicked.")
        if frame_number == 0:
            Name = (self.frames.data[0][1].get())
            try:
                Age = int(self.frames.data[0][3].get())
            except:
                print('Age entered incorrectly, try again.')
                return
            file_name = f"{Name}_{Age}.yaml"
            self.yaml_file_name = file_name
            if not os.path.exists(file_name):
                print("No such file exists, creating afresh")
                yaml_text = {
                    "Name": f"{Name}",
                    "Age": Age,
                    "Year_start": "",
                    "Tasks_List": {
                        # Time assigned, time spent, priority.
                        # Lesser is the number for priority, higher is the priority.
                    },
                    "Days": {
                        0: {
                            "Date": "",
                            "task_list": {
                                # Time assigned, priority, ticked.
                            }
                        }
                    }
                }
                with open(file_name, "w") as yaml_file:
                    yaml.dump(yaml_text, yaml_file)
                self.yaml_data = yaml_text
                messagebox.showinfo("Pop-up", f"Created a fresh database for you {Name}!")
            else:
                # Read data from the YAML file into a dictionary
                with open(file_name, "r") as yaml_file:
                    data = yaml.safe_load(yaml_file)
                self.yaml_data = data
                messagebox.showinfo("Pop-up", f"Welcome Back {Name}!")

            if self.yaml_data["Year_start"] == "":
                self.hide_all_widgets(self.frames.frames[0])
                self.frames.data = self.add_data_to_frames(1)
            elif self.yaml_data["Year_start"] != "":
                if self.yaml_data['Days'][0]['Date'] != '':
                    if self.yaml_data['Days'][max(self.yaml_data['Days'].keys())]['Date'] == datetime.date.today():
                        messagebox.showinfo("Pop-up", f"Welcome Back! Current Day is Ongoing!!")
                        new_day = max(self.yaml_data['Days'].keys())
                        self.fresh_date = self.yaml_data['Days'][new_day]['Date']
                        self.fresh_day = self.yaml_data['Days'][new_day]['task_list']
                        self.avg = self.yaml_data['Days'][new_day]['avg']
                        self.fresh_day_index = new_day
                        self.hide_all_widgets(self.frames.frames[0])
                        self.frames.data = self.add_data_to_frames(5)

                    else:
                        self.hide_all_widgets(self.frames.frames[0])
                        self.frames.data = self.add_data_to_frames(2)
                else:
                    self.hide_all_widgets(self.frames.frames[0])
                    self.frames.data = self.add_data_to_frames(2)
        elif frame_number == 1:
            status = args[0]
            if status == "Next":
                Task_name = (self.frames.data[1][1].get())
                Task_name = Task_name.lower()
                Time_assigned = (self.frames.data[1][3].get())
                try:
                    Year_start = datetime.date.today()
                    # Add 4 weeks to today's date
                    Year_end = Year_start + datetime.timedelta(weeks=4)
                    Time_assigned = float(Time_assigned)
                    priority = (self.frames.data[1][5].get())
                    priority = float(priority)
                except:
                    print("Incorrect entry, try again")
                    return
                self.yaml_data["Year_start"] = Year_start
                dict_n = {Task_name: [Time_assigned, 0, priority]}
                self.yaml_data["Tasks_List"].update(dict_n)
                messagebox.showinfo("Pop-up", f"Added a new task!!")
            elif status == "Moving On":
                messagebox.showinfo("Pop-up", f"Moving On!!")
                self.hide_all_widgets(self.frames.frames[1])
                self.frames.data = self.add_data_to_frames(2)
        elif frame_number == 2:
            if args[0] == "Create":
                self.hide_all_widgets(self.frames.frames[2])
                self.frames.data = self.add_data_to_frames(3)

        elif frame_number == 3:
            list_tasks, man_tasks, values, avg = self.allocate_tasks(self.yaml_data['Tasks_List'], self.checkbox_vars)
            self.avg = avg
            print(list_tasks)
            print(man_tasks)
            print(avg)
            man_tasks = self.remove_completed_tasks(man_tasks)
            list_tasks = self.remove_completed_tasks(list_tasks)
            slots = self.radio_button.get()
            if not man_tasks and not list_tasks:
                self.hide_all_widgets(self.frames.frames[3])
                messagebox.showinfo("Pop-up", f"No more tasks remaining!!!!")
            else:
                if not man_tasks:
                    print("No mandatory tasks.")
                    total_tasks = list_tasks.copy()
                    remaining_slots = slots - len(total_tasks)
                    if remaining_slots > 0:
                        while len(total_tasks) < slots:
                            total_tasks.extend(list_tasks)
                    else:
                        total_tasks = total_tasks[:slots]
                    tasks_for_the_day = total_tasks[:slots]
                elif not list_tasks:
                    print("No additional tasks beyond mandatory ones")
                    total_tasks = man_tasks.copy()
                    remaining_slots = slots - len(total_tasks)
                    if remaining_slots > 0:
                        while len(total_tasks) < slots:
                            total_tasks.extend(man_tasks)
                    else:
                        total_tasks = total_tasks[:slots]
                    tasks_for_the_day = total_tasks[:slots]
                else:
                    total_tasks = list_tasks.copy()
                    remaining_slots = slots - len(total_tasks)
                    if remaining_slots > 0:
                        while len(total_tasks) < slots:
                            total_tasks.extend(man_tasks)
                            total_tasks.extend(total_tasks)
                    else:
                        total_tasks = total_tasks[:slots]
                    tasks_for_the_day = total_tasks[:slots]

                count_dict = {}
                for item in tasks_for_the_day:
                    count_dict[item] = count_dict.get(item, 0) + 1
                    if count_dict[item] > 1:
                        new_item = f"{item}-session-{count_dict[item]}"
                        self.fresh_day[new_item] = [30, values[item], 0]
                    else:
                        self.fresh_day[item] = [30, values[item], 0]
                    # priority, tick
                print(self.fresh_day)
                self.fresh_date = datetime.date.today()
                if self.yaml_data['Days'][0]['Date'] == '':
                    self.yaml_data['Days'][0]['Date'] = self.fresh_date
                    self.yaml_data['Days'][0]['task_list'] = self.fresh_day
                    self.yaml_data['Days'][0]['avg'] = self.avg
                    self.fresh_day_index = 0
                else:
                    new_day = max(self.yaml_data['Days'].keys())
                    new_day = new_day + 1
                    self.yaml_data['Days'][new_day] = {
                        'Date': self.fresh_date,
                        'task_list': self.fresh_day,
                        'avg': self.avg
                    }

                    self.fresh_day_index = new_day
                self.hide_all_widgets(self.frames.frames[3])
                self.frames.data = self.add_data_to_frames(5)
        elif frame_number == 5:
            print(self.fresh_date)
            print(self.checkbox_today)
            # day_task_list = self.yaml_data['Days'][self.fresh_day_index]['task_list']
            check = self.check_if_all_tasks_for_day_complete(self.checkbox_today)
            self.update_main_task_list()
            if check:
                self.set_third_element_to_one()
                self.hide_all_widgets(self.frames.frames[5])
                messagebox.showinfo("Pop-up", f"You are all done for the day Mate!!!")

            else:
                for index, (element, value) in enumerate(self.checkbox_today.items()):
                    if value.get() == 1:
                        self.set_third_element_to_one(element)
                        self.frames.data[5][index].config(state="disabled")

    def show_tasks(self, tasks):
        self.root = tk.Tk()

    def get_style(self, score, avg):
        # Define segments based on priority ranges
        if score > avg:
            return 'red', ("Verdana", 12 * 2, 'bold')
        elif score < avg:
            return 'green', ("Verdana", 8 * 2)
        else:
            return 'orange', ("Verdana", 10 * 2)

    def create_checkbox(self, task_name, priority, row, frame, data, ena_disa):
        var = tk.IntVar()
        color, font = self.get_style(priority, self.avg)
        data.append(tk.Checkbutton(frame, text=task_name, fg=color, font=font, variable=var))
        data[-1].place(x=0, y=row + (30 * row))
        if ena_disa:
            data[-1].config(state="disabled")
            var.set(1)
        return var

    def display_today(self):
        print("Hi mate, welcome to today!")
        # self.root.destroy()
        for frame in self.frames.frames:
            frame.destroy()
        new_day = max(self.yaml_data['Days'].keys())
        self.show_tasks(self.yaml_data['Days'][new_day]['task_list'])


def on_closing(root, app):
    print("Bye")
    if app.yaml_file_name is not None:
        with open(app.yaml_file_name, "w") as yaml_file:
            yaml.dump(app.yaml_data, yaml_file)
    root.destroy()


def main():
    app = EightFramesApp()
    # Define the function to be executed when the window is closed
    app.root.protocol("WM_DELETE_WINDOW", lambda: on_closing(app.root, app))
    app.root.mainloop()


if __name__ == "__main__":
    main()
