# Вариант 26. Разработка программы универсального инсталлятора.

Одним из компонентов современного коммерческого программного обеспечения
является инсталлятор – утилита, которая предназначена для установки программного
обеспечения (ПО) на компьютер пользователя. Инсталлятор обычно выполняет
следующий минимальный набор функций: 
*  копирование  файлов  ПО  в  указанные  пользователем  каталоги  (если  файлы 
хранятся в упакованном виде, то их предварительно надо распаковать); 
*  создание отдельной группы в главном меню; 
*  создание на рабочем столе ярлыка для запуска программы; 
*  сохранение начальных установок программы в системном реестре или в инициализационном файле с расширением .ini; 
*  деинсталляция ранее установленной программы.

В ранних версиях Windows вся информация о конфигурации системы и 
настройках программ хранилась в файлах типа .ini. Современные версии Windows 
требуют, чтобы вся информация хранилась в системном реестре (Registry), который имеет
иерархическую организацию и содержит много уровней ключей, субключей и параметров.

Реестр делит все свои данные на две категории:
1. Характеризующие компьютер:

| Наименование        | Значение                                                                                                                                                    |
|:--------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| Hkey_Local_Machine  | Информация  о  компьютере,  включая  конфигурацию  установленной аппаратуры и программного обеспечения                                                      |
| Hkey_Classes_Root   | Информация  об  ассоциациях  файлов,  OLE,  Drag&Drop,  клавишах быстрого доступа и пользовательском интерфейсе                                             |
| Hkey_Current_Config | Информация о текущеq конфигурации компьютера                                                                                                                |

2. Характеризующие пользователя:

| Наименование        | Значение                                                                |
|:--------------------|:------------------------------------------------------------------------|
| Hkey_Users          | Информация о зарегистрированных пользователях и их специфических данных |
| Hkey_Current_User   | Информация о текущем пользователе                                       |

Если настройки приложения не используются другими приложениями, то их 
хранение в реестре не всегда оправдано. В этом случае разумнее запоминать 
настройки в файле .ini. Файлы .ini - это текстовые файлы, информация в которых 
сгруппирована в соответствующие разделы.

Студентам предлагается разработать программу, с помощью которой можно 
устанавливать на компьютер пользователя любое программное обеспечение, для чего
необходимо описать весь процесс установки в специальном текстовом файле 
сценария. Сценарий установки предполагает указание имени программы, каталогов 
для установки, имен файлов, необходимости распаковки файлов и т.д.

Файл сценария должен содержать набор поименованных разделов, каждый из 
которых будет описывать определенный этап инсталляции. Ниже приведен пример 
сценария, содержащего 6 разделов (секций), имена которых заключаются в квадратные скобки.

```
[title]    // содержит имя устанавливаемой программы, выводится в окне инсталлятора    
MyProgram    
 
[archives]   // указывает имя архива, в котором записан дистрибутив устанавливаемой программы 
Myprog.zip  
 
[dir]           // указывает имя каталога, в который будет проводиться установка 
Dir=%ProgramFiles%\MyProgram   
 
[files]  // указывает имя файла и каталога, в который будет копироваться этот файл 
Myprog.exe   // копировать в Dir 

Myprog.hlp   // копировать в Dir 
Myprog.doc  Dir\Docum  // копировать в Dir\Docum 
Myprog.dll  %SystemRoot%\system32  // копировать в каталог system32 
 
[icons]    // указывает имя файла, для которого необходимо создать ярлык на рабочем столе  
Myprog.exe 
 
[registry] // указывает имя секции реестра и значения параметров для устанавливаемой программы 
LOCAL_MACHINE\SOFTWARE\ MyProgram 
Year=2021 
Month=январь 
State=0 
 
[end]
```

В приведенном примере описана установка программы с именем MyProgram, 
дистрибутив которой находится в архиве MyProg.zip и содержит 4 файла. Установка 
будет проводиться в каталог MyProgram, который надо создать в системном каталоге, 
предназначенном для хранения приложений. В реестре необходимо создать раздел 
LOCAL_MACHINE\SOFTWARE\ MyProgram, в который записываются три указанных 
в сценарии параметра. Инсталлятор последовательно читает каждый раздел 
сценария и исполняет указанные действия.

Помимо установки, программа должна иметь возможность деинсталляции ранее
установленной программы. Деинсталляция — это не просто удаление файлов с 
компьютера, которое может произвести любой пользователь вручную. Она подразумевает
удаление всех следов пребывания программы в системе (записей в реестре 
и других системных файлах, DLL-библиотек в папке Windows\System32 и т. п.).  

Деинсталлятор настраивается так, чтобы удалить только те файлы, которые 
были установлены ранее. Если при удалении файлов программы деинсталлятор обнаруживает
в ее папке файлы, которые не были туда установлены инсталлятором, 
то он не должен их удалять (например документы, созданные пользователем).