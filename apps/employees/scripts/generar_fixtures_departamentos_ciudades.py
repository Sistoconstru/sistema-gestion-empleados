import csv
import json
import os

# Ruta de salida de los fixtures
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '../fixtures/departamentos')
if not os.path.exists(FIXTURE_DIR):
    os.makedirs(FIXTURE_DIR)

# Archivo fuente oficial DANE (descargar antes de ejecutar)
# Puedes descargar el CSV oficial de municipios desde:
# https://www.dane.gov.co/files/geografia/municipios_colombia.csv
# El archivo debe tener las columnas: COD_DEPTO, NOMBRE_DEPTO, COD_MPIO, NOMBRE_MPIO
FUENTE_CSV = os.path.join(os.path.dirname(__file__), 'municipios_colombia.csv')

def main():
    departamentos = {}
    ciudades = {}
    pk_departamento = 1
    pk_ciudad = 1

    with open(FUENTE_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        # Mostrar los nombres de las columnas para depuración
        print('Columnas detectadas:', reader.fieldnames)
        # Limpiar comillas de los nombres de columna
        columnas = [c.replace('"','').replace('\ufeff','').strip() for c in reader.fieldnames]
        col_depto = [c for c in columnas if 'Departamento' in c and 'Código' in c][0]
        col_nombre_depto = [c for c in columnas if 'Departamento' in c and 'Nombre' in c][0]
        col_mpio = [c for c in columnas if 'Municipio' in c and 'Código' in c][0]
        col_nombre_mpio = [c for c in columnas if 'Municipio' in c and 'Nombre' in c][0]
        for row in reader:
            # Limpiar las claves de la fila
            row_limpio = {k.replace('"','').replace('\ufeff','').strip(): v for k, v in row.items()}
            cod_depto = row_limpio[col_depto].strip().zfill(2)
            nombre_depto = row_limpio[col_nombre_depto].strip().title()
            cod_mpio = row_limpio[col_mpio].strip().zfill(3)
            nombre_mpio = row_limpio[col_nombre_mpio].strip().title()

            # Registrar departamento si no existe
            if cod_depto not in departamentos:
                departamentos[cod_depto] = {
                    'pk': pk_departamento,
                    'nombre': nombre_depto,
                    'codigo': cod_depto
                }
                pk_departamento += 1
            # Registrar ciudad
            depto_pk = departamentos[cod_depto]['pk']
            ciudades.setdefault(cod_depto, []).append({
                'pk': pk_ciudad,
                'nombre': nombre_mpio,
                'departamento': depto_pk
            })
            pk_ciudad += 1

    # Generar un fixture por departamento
    for cod_depto, depto in departamentos.items():
        fixture = [
            {
                'model': 'employees.departamento',
                'pk': depto['pk'],
                'fields': {
                    'nombre': depto['nombre'],
                    'codigo': depto['codigo']
                }
            }
        ]
        for ciudad in ciudades[cod_depto]:
            fixture.append({
                'model': 'employees.ciudad',
                'pk': ciudad['pk'],
                'fields': {
                    'nombre': ciudad['nombre'],
                    'departamento': ciudad['departamento']
                }
            })
        # Guardar archivo
        nombre_archivo = f"{depto['nombre'].lower().replace(' ', '_')}.json"
        with open(os.path.join(FIXTURE_DIR, nombre_archivo), 'w', encoding='utf-8') as out:
            json.dump(fixture, out, ensure_ascii=False, indent=2)
        print(f"Generado: {nombre_archivo} ({len(fixture)-1} ciudades)")

if __name__ == '__main__':
    main()
