from tkinter import *
from tkinter import messagebox
from src import assembler
from tkinter.ttk import *
from tkinter import filedialog
import threading
import queue
import matplotlib.pyplot as plt
from tkinter import PhotoImage
from PIL import Image, ImageTk

root = Tk()
root.title("DL Language Tool")

# Constants & Functions
languages = ['alphaAAB', 'bravoABB', 'charlieBCB', 'deltaACA', 'echoACB']

default = "-"
default_grammar = "Pick a pre-defined grammar"


class Std_redirector():
    def __init__(self, widget):
        self.widget = widget

    def flush(self):
        pass

    def write(self, string):
        self.widget.write(string)


class ThreadSafeText(Text):
    def __init__(self, master, **options):
        Text.__init__(self, master, **options)
        self.queue = queue.Queue()
        self.update_me()

    def write(self, line):
        self.queue.put(line)

    def update_me(self):
        while not self.queue.empty():
            line = self.queue.get_nowait()
            self.insert(END, line)
            self.see(END)
            self.update_idletasks()
        self.after(10, self.update_me)


def execute():
    if check_parameters(get_parameters()):
        if dropdown_grammars.get() in languages:
            grammar_file = "../grammars/grammar_" + dropdown_grammars.get() + ".txt"
        else:
            grammar_file = dropdown_grammars.get()
        text.grid(row=8, columnspan=4)

        trainig_data_size = int(entry_training_date.get())
        generated_text_size = int(entry_generated_text.get())

        if int(entry_mode.get()) == 1:
            print("Running the THRESHOLD mode")
            my_assembler = assembler.Assembler(grammar_file, True, float(entry_threshold.get()))
            my_assembler.execute(trainig_data_size, generated_text_size, int(entry_max_epochs.get()), True)
        elif int(entry_mode.get()) == 2:
            print("Running the COMPARISON mode")
            if dropdown_grammars_second.get() in languages:
                grammar_file_second = "../grammars/grammar_" + dropdown_grammars_second.get() + ".txt"
            else:
                grammar_file_second = dropdown_grammars_second.get()

            # Run model for the first language
            my_assembler = assembler.Assembler(grammar_file, True, 1)
            accuracies_first = my_assembler.execute(trainig_data_size, generated_text_size, int(entry_epochs.get()), True)


            # Run model for the second language
            my_assembler_second = assembler.Assembler(grammar_file_second, True, 1)
            accuracies_second = my_assembler_second.execute(trainig_data_size, generated_text_size, int(entry_epochs.get()), True)

            print("Accuracies of the first model:", accuracies_first)
            print("Accuracies of the second model:", accuracies_second)

            plt.figure()
            plt.title("Comparison of training performance")
            plt.plot(range(1, len(accuracies_first) + 1), accuracies_first, c='r', label=dropdown_grammars.get())
            plt.plot(range(1, len(accuracies_first) + 1), accuracies_second, c='b', label=dropdown_grammars_second.get())
            plt.xlabel("Epoch")
            plt.ylabel("Accuracy")
            plt.xticks(range(1, len(accuracies_first) + 1))
            plt.legend()
            plt.savefig("Sample.jpg")

            image = Image.open("Sample.jpg")
            photo = ImageTk.PhotoImage(image)
            label_image = Label(image=photo)
            label_image.image = photo  # keep a reference!
            label_image.grid(row=8, columnspan=4)


        else:
            print("Running the BASIC mode")
            my_assembler = assembler.Assembler(grammar_file)
            my_assembler.execute(trainig_data_size, generated_text_size, int(entry_epochs.get()), True)

    else:
        messagebox.showwarning("Warning", "Enter valid parameters")


def selectfile():
    file_chosen = filedialog.askopenfilename(initialdir="../", title="Select file",
                                             filetypes=(("txt files", "*.txt"), ("all files", "*.*")))

    language = file_chosen.split("/")[-1]
    dropdown_grammars.set(language)
    print(language)


def selectfile_second():
    file_chosen = filedialog.askopenfilename(initialdir="../", title="Select file",
                                             filetypes=(("txt files", "*.txt"), ("all files", "*.*")))

    language = file_chosen.split("/")[-1]
    dropdown_grammars_second.set(language)
    print(language)


def get_parameters():
    parameters = []
    parameters.append(dropdown_grammars.get())
    parameters.append(entry_training_date.get())
    parameters.append(entry_generated_text.get())
    parameters.append(entry_mode.get())
    if int(entry_mode.get()) == 1:
        parameters.append(entry_max_epochs.get())
        parameters.append(entry_threshold.get())
    elif int(entry_mode.get()) == 2:
        parameters.append(entry_epochs.get())
        parameters.append(dropdown_grammars_second.get())

    else:
        parameters.append(entry_epochs.get())
    return parameters


def check_parameters(parameters):
    return not (default in parameters)


def show_parameters():
    params = get_parameters()
    # if check_parameters(params):
    #  params_label = Label(root, text=params).grid(row=5, column=0)

    # else:
    #   messagebox.showwarning("Warning", "Enter valid parameters")
    params_label = Label(root, text=params)
    params_label.grid(row=8, column=1)


def toggle_basic():
    entry_epochs.grid(row=5, column=1, padx=10, pady=10)
    entry_epochs_label.grid(row=5, column=0, padx=10, pady=10)

    entry_mode.delete(0, END)
    entry_mode.insert(0, 0)

    dropdown_grammars_label.config(text="Choose a language:")
    entry_max_epochs_label.grid_forget()
    entry_max_epochs.grid_forget()
    entry_threshold_label.grid_forget()
    entry_threshold.grid_forget()
    dropdown_grammars_second.grid_forget()
    dropdown_grammars_second_label.grid_forget()
    select_file_button_second.grid_forget()
    or_label_second.grid_forget()


def toggle_checkpointed():
    entry_max_epochs.grid(row=5, column=1, padx=10, pady=10)
    entry_max_epochs_label.grid(row=5, column=0, padx=10, pady=10)
    entry_threshold.grid(row=6, column=1, padx=10, pady=10)
    entry_threshold_label.grid(row=6, column=0, padx=10, pady=10)

    entry_mode.delete(0, END)
    entry_mode.insert(0, 1)

    dropdown_grammars_label.config(text="Choose a language:")
    entry_epochs_label.grid_forget()
    entry_epochs.grid_forget()
    dropdown_grammars_second.grid_forget()
    dropdown_grammars_second_label.grid_forget()
    select_file_button_second.grid_forget()
    or_label_second.grid_forget()


def toggle_comparison():
    dropdown_grammars_label.config(text="Choose first language:")
    dropdown_grammars_second_label.grid(row=2, column=0)
    dropdown_grammars_second.grid(row=2, column=1)
    or_label_second.grid(row=2, column=2)
    select_file_button_second.grid(row=2, column=3)
    entry_epochs.grid(row=5, column=1, padx=10, pady=10)
    entry_epochs_label.grid(row=5, column=0, padx=10, pady=10)

    entry_mode.delete(0, END)
    entry_mode.insert(0, 2)

    entry_max_epochs_label.grid_forget()
    entry_max_epochs.grid_forget()
    entry_threshold_label.grid_forget()
    entry_threshold.grid_forget()


# Define parts of the UI
button_quit = Button(root, text="Exit", command=root.quit)

entry_training_date_label = Label(root, text="Number of training sentences: ")
entry_training_date = Entry(root)
entry_training_date.insert(0, "-")

entry_generated_text = Entry(root)
entry_generated_text_label = Label(root, text="Number of generated sentences: ")
entry_generated_text.insert(0, "-")

entry_epochs = Entry(root)
entry_epochs_label = Label(root, text="Number of epochs: ")
entry_epochs.insert(0, "-")

trainig_data_size = entry_training_date.get()

dropdown_grammars = Combobox(root, values=languages)
dropdown_grammars.set(default)
dropdown_grammars_label = Label(root, text="Pick a pre-defined grammar:")

# Checkpointed mode
entry_threshold = Entry(root)
entry_threshold_label = Label(root, text="Pick desired accuracy (between 0 and 1)")
entry_threshold.insert(0, "-")

entry_max_epochs = Entry(root)
entry_max_epochs_label = Label(root, text="Maximum number of epochs: ")
entry_max_epochs.insert(0, "-")

# Comparison mode
dropdown_grammars_second = Combobox(root, values=languages)
dropdown_grammars_second.set(default)
dropdown_grammars_second_label = Label(root, text="Choose second language:")

or_label_second = Label(root, text='or')
select_file_button_second = Button(root, text="Custom grammar", command=selectfile_second)

or_label = Label(root, text="or")
# test_button = Button(root, text="Show paramters", command=show_parameters)

text = ThreadSafeText(root)
sys.stdout = Std_redirector(text)

thread1 = threading.Thread(target=execute)

select_file_button = Button(root, text="Custom grammar", command=selectfile)
execute_button = Button(root, text="Run experiment", command=thread1.start)

entry_mode = Entry(root)
entry_mode.insert(0, 0)

mode_label = Label(root, text="Choose a mode")
mode_basic = Button(root, text="Basic", command=toggle_basic)
mode_checkpointed = Button(root, text="Threshold", command=toggle_checkpointed)
mode_comparison = Button(root, text="Comparison", command=toggle_comparison)

# Put widgets onto screen

mode_label.grid(row=0, column=0, padx=5, pady=10)
mode_basic.grid(row=0, column=1, padx=5, pady=10)
mode_checkpointed.grid(row=0, column=2, padx=5, pady=10)
mode_comparison.grid(row=0, column=3, padx=5, pady=10)

dropdown_grammars_label.grid(row=1, column=0, padx=10, pady=10)
dropdown_grammars.grid(row=1, column=1, padx=10, pady=10)
or_label.grid(row=1, column=2)
select_file_button.grid(row=1, column=3, padx=10, pady=10)

entry_training_date.grid(row=3, column=1, padx=10, pady=10)
entry_training_date_label.grid(row=3, column=0, padx=10, pady=10)

entry_generated_text.grid(row=4, column=1, padx=10, pady=10)
entry_generated_text_label.grid(row=4, column=0, padx=10, pady=10)

button_quit.grid(row=7, column=1, padx=10, pady=10)
execute_button.grid(row=7, column=0, padx=10, pady=10)

#test_buttton = Button(root, text="Show params", command=show_parameters)
#test_buttton.grid(row=7, column=2)
root.mainloop()
