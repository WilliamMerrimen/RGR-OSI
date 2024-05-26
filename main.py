import os
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import winshell
from win32com.client import Dispatch
import winreg

def copy_files(source, destination):
    if not os.path.exists(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination))
    shutil.copy(source, destination)



def check_for_install_script():
    try:
        with open('install_script.txt', 'r') as file:
            for line in file:
                if line.startswith('[title]'):
                    return line.split('=')[1].strip()
    except FileNotFoundError:
        messagebox.showerror("Ошибка",
                             "Файл сценария не найден, убедитесь, что файл install_script.txt находится в одной папке с установщиком и перезапустите программу")
        return None


def create_desktop_shortcut(file_name):
    program_name = check_for_install_script()
    if program_name:
        desktop = winshell.desktop()
        path = os.path.join(desktop, f"{program_name}.lnk")
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = file_name
        shortcut.WorkingDirectory = os.path.dirname(file_name)
        shortcut.save()


def create_start_menu_shortcut(file_name):
    program_name = check_for_install_script()
    if program_name:
        try:
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            all_progs = shell.SpecialFolders("AllUsersStartMenu")
            my_prog_dir = os.path.join(all_progs, program_name)
            if not os.path.exists(my_prog_dir):
                os.makedirs(my_prog_dir)
            shortcut = shell.CreateShortCut(os.path.join(my_prog_dir, f"{program_name}.lnk"))
            shortcut.Targetpath = file_name
            shortcut.WorkingDirectory = os.path.dirname(file_name)
            shortcut.save()
        except ImportError:
            messagebox.showerror("Ошибка", "pywin32 не установлен. Раздел в главном меню не была создана.")


def save_to_registry(data):
    current_key = None
    for line in data:
        line = line.strip()
        if line.startswith('HKEY_'):
            if current_key:
                current_key.Close()
            root_key, sub_key = line.split("\\\\", 1)
            current_key = winreg.CreateKeyEx(winreg.__dict__[root_key], sub_key, 0, winreg.KEY_ALL_ACCESS)
        elif '=' in line:
            name, value = line.split('=')
            winreg.SetValueEx(current_key, name.strip(), 0, winreg.REG_SZ, value.strip())
        elif line == '[end]':
            if current_key:
                current_key.Close()
            break
    if current_key:
        current_key.Close()




def install_program():
    program_name = check_for_install_script()
    if program_name:
        file_path = 'install_script.txt'
        archive_name = None
        registry_section = None
        with open(file_path, 'r') as file:
            lines = file.readlines()
            data = []
            for line in lines:
                line = line.strip()
                if line.startswith('[title]') and '=' in line:
                    title = line.split('=')[1].strip()
                elif line.startswith('[archives]') and '=' in line:
                    archive_name = line.split('=')[1].strip()
                elif line.startswith('[dir]') and '=' in line:
                    install_directory = line.split('=')[1].strip()
                    os.makedirs(install_directory, exist_ok=True)
                elif line.startswith('[files]') and '=' in line:
                    file_data = line.split(' ', 1)[1].strip().split()
                    if len(file_data) == 2:
                        copy_files(file_data[0], os.path.join(install_directory, file_data[1]))
                    elif len(file_data) == 3:
                        copy_files(file_data[0], os.path.join(install_directory, file_data[2]))
                elif line.startswith('[icons]') and '=' in line:
                    icon_name = line.split('=')[1].strip()
                elif line.startswith('[registry]'):
                    registry_section = True
                elif registry_section:
                    data.append(line)
            if archive_name:
                unpack_archive(archive_name, install_directory)
                if shrCutsCh.get():
                    create_desktop_shortcut(os.path.join(install_directory, icon_name))
                if mMenuCh.get():
                    create_start_menu_shortcut(os.path.join(install_directory, icon_name))
                save_to_registry(data)
                messagebox.showinfo("Установка завершена", f"Установка {program_name} завершена успешно")
            else:
                messagebox.showerror("Ошибка", "Архив не найден")
    else:
        return

def unpack_archive(archive_name, install_directory):
    with zipfile.ZipFile(archive_name, 'r') as zip_ref:
        zip_ref.extractall(install_directory)


def delete_registry_entry(data):
    current_key = None
    for line in data:
        line = line.strip()
        if line.startswith('HKEY_'):
            root_key, sub_key = line.split("\\\\", 1)
            current_key = winreg.DeleteKey(winreg.__dict__[root_key], sub_key)


def delete_start_menu_shortcut():
    program_name = check_for_install_script()
    if program_name:
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        all_progs = shell.SpecialFolders("AllUsersPrograms")
        my_prog_dir = os.path.join(all_progs, program_name)
        if os.path.exists(my_prog_dir):
            shutil.rmtree(my_prog_dir, ignore_errors=True)


def uninstall_program():
    program_name = check_for_install_script()
    if program_name:
        with open('install_script.txt', 'r') as file:
            lines = file.readlines()
            data = []
            registry_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('[dir]'):
                    install_directory = line.split('=')[1].strip()
                    shutil.rmtree(install_directory, ignore_errors=True)
                elif line.startswith('[registry]'):
                    registry_section = True
                elif registry_section:
                    data.append(line)
            delete_start_menu_shortcut()
            delete_registry_entry(data)
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        desktop_shortcut = os.path.join(desktop, f"{program_name}.lnk")
        if os.path.exists(desktop_shortcut):
            os.remove(desktop_shortcut)
        messagebox.showinfo("Удаление", f"Программа {program_name} удалена")
    else:
        return


def update_program_name_label():
    program_name = check_for_install_script()
    if program_name:
        program_name_label.config(text=f"Название программы: {program_name}")
    else:
        program_name_label.config(text="Название программы: (не указано)")

def browseDir(lab: tk.Label):
    dirlb = filedialog.askdirectory()
    install_directory = ""
    program_name = check_for_install_script()
    if program_name:
        file_path = 'install_script.txt'
        with open(file_path, 'r') as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('[dir]'):
                lines[i] = f"[dir]={dirlb}/kmeleon\n"
        with open(file_path, "w+") as file:
            file.writelines(lines)
    lab.config(text = f"{dirlb}/kmelion")

def switchDir(win: tk.Tk):
    install_directory = ""
    program_name = check_for_install_script()
    if program_name:
        file_path = 'install_script.txt'
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith('[dir]'):
                    install_directory = line.split('=')[1].strip()
    label = tk.Label(win, text=install_directory)
    return label
        

window = tk.Tk()
window.title("Установка программы")
window.geometry('500x300')
window.resizable(width = False, height = False)

shrCutsCh = tk.BooleanVar(window,True)
mMenuCh = tk.BooleanVar(window,True)

program_name_label = tk.Label(window, text="Название программы: (не указано)")
program_name_label.pack()
programDirLabel = switchDir(window)

update_program_name_label()

install_button = tk.Button(window,
                           text="Установить",
                           command=install_program,
                           width = 10,
                           height = 1)
install_button.place(x = 50, y = 230)

uninstall_button = tk.Button(window, 
                             text="Удалить", 
                             command=uninstall_program,
                             width = 10,
                             height = 1)
uninstall_button.place(x = 380, y = 230)

broweDirButton = tk.Button(window,
                           text="Browse",
                           command=lambda : browseDir(programDirLabel),
                           width = 10,
                           height = 1)
broweDirButton.place(x = 380, y = 198)

programDirLabel.place(x = 50, y = 198)

shortCutsChBox = tk.Checkbutton(window,
                                text = "Создать ярлык на Рабочем столе",
                                variable = shrCutsCh,
                                onvalue = True,
                                offvalue = False,
                                )
shortCutsChBox.place(x = 50, y = 140)

mainMenuChBox = tk.Checkbutton(window,
                               text = "Создать ярлык на Главном Меню(Пуск)",
                                variable = mMenuCh,
                                onvalue = True,
                                offvalue = False,
                                )
mainMenuChBox.place(x = 50, y = 160)

window.mainloop()