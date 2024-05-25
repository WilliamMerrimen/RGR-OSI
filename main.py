import os
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox
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
                create_desktop_shortcut(os.path.join(install_directory, icon_name))
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


window = tk.Tk()
window.title("Установка программы")
window.geometry('400x200')

program_name_label = tk.Label(window, text="Название программы: (не указано)")
program_name_label.pack()

update_program_name_label()

install_button = tk.Button(window, text="Установить", command=install_program)
install_button.pack()

uninstall_button = tk.Button(window, text="Удалить", command=uninstall_program)
uninstall_button.pack()

window.mainloop()