#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar y verificar las fuentes personalizadas

Uso:
    python install_fonts.py          # Verificar fuentes instaladas
"""

import os
from pathlib import Path

# Fuentes requeridas (búsqueda insensible a mayúsculas)
REQUIRED_FONTS = {
    'Love Twist Sans': ['lovetwtistsans-regular.ttf', 'lovetwtistsans.ttf', 'lovetwistsans-regular.ttf'],
    'Twiggy': ['twiggy-regular.ttf', 'twiggy.ttf', 'chalkboy.ttf'],
    'Pinewood': ['pinewood-regular.ttf', 'pinewood.ttf'],
}

# Fuentes opcionales del sistema
SYSTEM_FONTS = {
    'Arial': ['arial.ttf', 'liberationsans-regular.ttf'],
    'Times New Roman': ['times.ttf', 'liberationserif-regular.ttf'],
    'Courier New': ['cour.ttf', 'liberationmono-regular.ttf'],
}

def get_fonts_dir():
    """Obtener la ruta del directorio de fuentes del proyecto"""
    return Path(__file__).parent

def find_font_file(fonts_dir, font_patterns):
    """Buscar un archivo de fuente insensible a mayúsculas"""
    # Obtener todos los .ttf en la carpeta
    ttf_files = []
    for file in fonts_dir.glob('*'):
        if file.suffix.lower() == '.ttf':
            ttf_files.append(file.name.lower())

    # Buscar el patrón
    for pattern in font_patterns:
        pattern_lower = pattern.lower()
        for ttf_file in ttf_files:
            if ttf_file == pattern_lower:
                return next(f for f in fonts_dir.glob('*') if f.name.lower() == ttf_file)

    return None

def check_fonts():
    """Verificar qué fuentes están instaladas"""
    fonts_dir = get_fonts_dir()

    print("=" * 70)
    print("VERIFICACION DE FUENTES PERSONALIZADAS")
    print("=" * 70)
    print("\nDirectorio de fuentes: {}".format(fonts_dir))

    # Listar archivos TTF
    ttf_files = list(fonts_dir.glob('*.ttf')) + list(fonts_dir.glob('*.TTF'))
    print("Archivos .ttf encontrados: {}".format(len(ttf_files)))
    for ttf in ttf_files:
        print("  - {}".format(ttf.name))
    print()

    # Verificar fuentes requeridas
    print("FUENTES PERSONALIZADAS (REQUERIDAS):")
    print("-" * 70)
    for font_name, font_patterns in REQUIRED_FONTS.items():
        font_file = find_font_file(fonts_dir, font_patterns)
        if font_file:
            print("  [OK] {}: {}".format(font_name, font_file.name))
        else:
            print("  [NO] {}: NO ENCONTRADA".format(font_name))
            print("       Busca por: {}".format(', '.join(font_patterns)))

    # Verificar fuentes del sistema
    print("\nFUENTES DEL SISTEMA (OPCIONALES):")
    print("-" * 70)
    for font_name, font_patterns in SYSTEM_FONTS.items():
        font_file = find_font_file(fonts_dir, font_patterns)
        if font_file:
            print("  [OK] {}: {} (en carpeta del proyecto)".format(font_name, font_file.name))
        else:
            print("  [*] {}: en el sistema (fallback)".format(font_name))

    print("\n" + "=" * 70)
    print("INSTRUCCIONES PARA AGREGAR FUENTES FALTANTES:")
    print("=" * 70)
    print("""
1. Descarga las fuentes desde Google Fonts (https://fonts.google.com/):
   - Busca "Love Twist Sans", "Twiggy", "Pinewood"
   - Descarga el archivo .ttf regular

2. Coloca los archivos .ttf en esta carpeta:
   {}

3. Los nombres de archivo pueden ser:
   - Love Twist Sans: LoveTwistSans-Regular.ttf
   - Twiggy: Twiggy-Regular.ttf
   - Pinewood: Pinewood-Regular.ttf

4. Ejecuta de nuevo este script para verificar
    """.format(fonts_dir))

def main():
    """Función principal"""
    check_fonts()

if __name__ == '__main__':
    main()
