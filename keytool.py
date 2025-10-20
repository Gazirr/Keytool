#!/usr/bin/env python3
"""
keytool_wrapper.py

Uso:
  python keytool_wrapper.py            -> muestra keytool -help (si keytool no recibe args)
  python keytool_wrapper.py genkeypair -> genera par clave (pregunta params)
  python keytool_wrapper.py list       -> lista el keystore (pide keystore y password)
  python keytool_wrapper.py exportcert -> exporta certificado (pide alias, keystore, password, archivo)
  python keytool_wrapper.py printcert  -> muestra un .cer (pide ruta del .cer)
  python keytool_wrapper.py help       -> muestra keytool -help

Genera salidas en la carpeta salidas_keytool/
"""

import subprocess
import os
import sys
import datetime
import getpass
import shlex

OUTPUT_DIR = "salidas_keytool"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_output(name, stdout, stderr):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(OUTPUT_DIR, f"{name}_output_{ts}.txt")
    err_path = os.path.join(OUTPUT_DIR, f"{name}_error_{ts}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(stdout)
    with open(err_path, "w", encoding="utf-8") as f:
        f.write(stderr)
    return out_path, err_path

def run_keytool(args_list, name):
    """
    Ejecuta keytool con args_list (lista con los argumentos, incluyendo 'keytool' al inicio).
    Devuelve (stdout, stderr, returncode).
    """
    try:
        # Ejecutar y capturar salida
        proc = subprocess.run(args_list, capture_output=True, text=True)
        stdout, stderr = proc.stdout, proc.stderr
        out_path, err_path = save_output(name, stdout, stderr)
        # Mostrar en consola (resumen)
        print(f"\n--- Resultado {name} (saved stdout -> {out_path}, stderr -> {err_path}) ---\n")
        if stdout:
            print(stdout)
        if stderr:
            print("\n--- STDERR ---\n")
            print(stderr)
        print(f"\n(returncode={proc.returncode})\n")
        return stdout, stderr, proc.returncode
    except FileNotFoundError:
        print("Error: 'keytool' no encontrado. Asegúrate de que el JDK esté instalado y keytool esté en el PATH.")
        sys.exit(2)
    except Exception as e:
        print("Error ejecutando keytool:", e)
        sys.exit(3)

def cmd_help():
    return run_keytool(["keytool", "-help"], "help")

def cmd_genkeypair():
    print("GENERAR PAR DE CLAVES (genkeypair). Si quieres valores por defecto pulsa ENTER.")
    alias = input("Alias (miAlias): ").strip() or "miAlias"
    keystore = input("Ruta/archivo keystore (miKeystore.jks): ").strip() or "miKeystore.jks"
    keyalg = input("Algoritmo (RSA): ").strip() or "RSA"
    keysize = input("Keysize (2048): ").strip() or "2048"
    validity = input("Validez en días (365): ").strip() or "365"

    print("\nIntroduce los datos del Subject (puedes dejar por defecto):")
    cn = input("  CN (Nombre completo) [Juan Perez]: ").strip() or "Juan Perez"
    ou = input("  OU (Unidad) [Desarrollo]: ").strip() or "Desarrollo"
    o  = input("  O (Organización) [MiEmpresa]: ").strip() or "MiEmpresa"
    l  = input("  L (Localidad/Ciudad) [Ciudad]: ").strip() or "Ciudad"
    st = input("  ST (Provincia) [Provincia]: ").strip() or "Provincia"
    c  = input("  C (País 2 letras) [ES]: ").strip() or "ES"

    dname = f"CN={cn}, OU={ou}, O={o}, L={l}, ST={st}, C={c}"

    # Pedir contraseña del keystore
    storepass = getpass.getpass("Contraseña del keystore (se usará como storepass): ")

    # Nota de seguridad: -storepass dejará la contraseña visible en la línea de comando de procesos
    cmd = [
        "keytool", "-genkeypair",
        "-alias", alias,
        "-keyalg", keyalg,
        "-keysize", keysize,
        "-keystore", keystore,
        "-storepass", storepass,
        "-validity", validity,
        "-dname", dname
    ]

    print("\nEjecutando keytool -genkeypair ...")
    return run_keytool(cmd, "genkeypair")

def cmd_list():
    keystore = input("Ruta/archivo keystore (miKeystore.jks): ").strip() or "miKeystore.jks"
    storepass = getpass.getpass("Contraseña del keystore: ")
    cmd = ["keytool", "-list", "-v", "-keystore", keystore, "-storepass", storepass]
    return run_keytool(cmd, "list")

def cmd_exportcert():
    alias = input("Alias a exportar (miAlias): ").strip() or "miAlias"
    keystore = input("Ruta/archivo keystore (miKeystore.jks): ").strip() or "miKeystore.jks"
    storepass = getpass.getpass("Contraseña del keystore: ")
    outfile = input("Archivo de salida (.cer) (miCert.cer): ").strip() or "miCert.cer"
    cmd = ["keytool", "-exportcert", "-alias", alias, "-file", outfile, "-keystore", keystore, "-storepass", storepass]
    return run_keytool(cmd, "exportcert")

def cmd_printcert():
    certfile = input("Ruta del certificado (.cer): ").strip()
    if not certfile:
        print("Se requiere la ruta del .cer")
        return
    cmd = ["keytool", "-printcert", "-file", certfile]
    return run_keytool(cmd, "printcert")

def main():
    if len(sys.argv) <= 1:
        # sin argumentos -> help (igual que keytool sin argumentos)
        return cmd_help()

    cmd = sys.argv[1].lower()
    if cmd in ("-h", "--help", "help"):
        return cmd_help()
    elif cmd == "genkeypair":
        return cmd_genkeypair()
    elif cmd == "list":
        return cmd_list()
    elif cmd == "exportcert":
        return cmd_exportcert()
    elif cmd == "printcert":
        return cmd_printcert()
    else:
        print(f"Comando desconocido: {cmd}\nMostrando help de keytool:\n")
        return cmd_help()

if __name__ == "__main__":
    main()
