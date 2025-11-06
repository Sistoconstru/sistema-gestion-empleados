#!/usr/bin/env python3
"""
Script para eliminar filtros validado=True de cálculos de puntos
Ya que los puntos no necesitan validación (solo los asignan admin/sistema)
"""

import re

def remove_validado_filters_from_file(file_path):
    """Remove validado=True filters from HistorialPuntos queries"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrones a reemplazar
    patterns = [
        # HistorialPuntos.objects.filter(empleado=empleado, validado=True)
        (r'HistorialPuntos\.objects\.filter\(\s*empleado=([^,]+),\s*validado=True\s*\)', 
         r'HistorialPuntos.objects.filter(empleado=\1)'),
        
        # HistorialPuntos.objects.filter(validado=True)
        (r'HistorialPuntos\.objects\.filter\(\s*validado=True\s*\)', 
         r'HistorialPuntos.objects.filter()'),
        
        # filter=Q(historialpuntos__validado=True)
        (r'filter=Q\(historialpuntos__validado=True\)', 
         r''),
        
        # Remove extra commas and spaces
        (r'\.filter\(\s*\)', r''),
        (r'Sum\([^,]+,\s*filter=\s*\)', lambda m: m.group(0).replace(', filter=', '')),
        (r'Count\([^,]+,\s*filter=\s*\)', lambda m: m.group(0).replace(', filter=', '')),
    ]
    
    # Apply replacements
    for pattern, replacement in patterns:
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    # Clean up empty filters and double commas
    content = re.sub(r'\.filter\(\s*\)\.', '.', content)
    content = re.sub(r',\s*,', ',', content)
    content = re.sub(r'\(\s*,', '(', content)
    content = re.sub(r',\s*\)', ')', content)
    
    return content

if __name__ == "__main__":
    file_path = "c:/Sisto/SIGHU/sistema-gestion-empleados-mi-rama/apps/recognition/views.py"
    
    new_content = remove_validado_filters_from_file(file_path)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Filtros validado=True eliminados de cálculos de puntos")