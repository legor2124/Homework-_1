#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from converter import ConfigConverter

def main():
    parser = argparse.ArgumentParser(
        description='Конвертер учебного конфигурационного языка в TOML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  %(prog)s config.conf                    # Конвертация файла config.conf
  %(prog)s --test                         # Запуск тестов
  %(prog)s --example                      # Показать примеры
        
Формат учебного языка:
  Комментарии: ' Это комментарий
  Числа: 123, 456, 789
  Массивы: << 1, 2, 3 >>
  Словари: { ключ -> значение. другой_ключ -> значение }
  Константы: имя := значение;
  Ссылки на константы: ?(имя)
        """
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        type=Path,
        help='Входной файл на учебном конфигурационном языке'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Выходной файл TOML (по умолчанию - стандартный вывод)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Запустить тесты'
    )
    
    parser.add_argument(
        '--example',
        action='store_true',
        help='Показать примеры конфигураций'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Подробный вывод'
    )
    
    args = parser.parse_args()
    
    # Показать примеры
    if args.example:
        show_examples()
        return
    
    # Запустить тесты
    if args.test:
        run_tests()
        return
    
    # Проверка обязательного аргумента
    if not args.input_file:
        parser.print_help()
        sys.exit(1)
    
    # Конвертация
    converter = ConfigConverter()
    
    if args.verbose:
        print(f"Конвертация файла: {args.input_file}", file=sys.stderr)
    
    try:
        toml_output = converter.convert_file(args.input_file)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(toml_output)
            if args.verbose:
                print(f"Результат сохранен в: {args.output}", file=sys.stderr)
        else:
            print(toml_output)
            
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

def show_examples():
    """Показать примеры конфигураций"""
    print("Пример 1: Конфигурация веб-сервера")
    print("=" * 50)
    print("""' Конфигурация веб-сервера
server_name := "MyWebServer";
max_connections := 1000;
timeout := 30;

{
    server -> {
        name -> ?(server_name).
        port -> 8080.
        host -> "127.0.0.1".
        max_connections -> ?(max_connections).
        timeout -> ?(timeout)
    }.
    
    database -> {
        host -> "localhost".
        port -> 5432.
        name -> "app_db".
        pool_size -> 10
    }.
    
    logging -> {
        level -> "info".
        format -> "<< year, '-', month, '-', day, ' ', hour, ':', minute >>".
        rotate -> true
    }
}""")
    
    print("\n" + "=" * 50)
    print("\nПример 2: Конфигурация игры")
    print("=" * 50)
    print("""' Конфигурация игры
screen_width := 1920;
screen_height := 1080;
fov := 90.0;

{
    graphics -> {
        resolution -> << ?(screen_width), ?(screen_height) >>.
        fullscreen -> true.
        vsync -> true.
        fov -> ?(fov).
        shadows -> true.
        textures -> "high"
    }.
    
    controls -> {
        keys -> {
            forward -> 87.
            backward -> 83.
            left -> 65.
            right -> 68.
            jump -> 32.
            crouch -> 17
        }.
        mouse_sensitivity -> 1.5.
        invert_y -> false
    }.
    
    audio -> {
        master_volume -> 80.
        music_volume -> 60.
        sfx_volume -> 90.
        enable_3d_audio -> true
    }.
    
    game -> {
        difficulty -> "medium".
        language -> "ru".
        subtitles -> true.
        autosave_interval -> 300
    }
}""")

def run_tests():
    """Запуск тестов"""
    import test_parser
    import unittest
    
    # Запуск тестов
    suite = unittest.TestLoader().loadTestsFromModule(test_parser)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == '__main__':
    main()
