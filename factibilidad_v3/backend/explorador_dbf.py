from dbfread import DBF

dbf_path = r"C:\Users\Rocha\.gemini\antigravity\scratch\proptech_mvp\IPT_Metropolitana\PRC\IPT_13_PRC_Providencia.dbf"

try:
    table = DBF(dbf_path, encoding='latin-1', load=True)
    print(f"Total registros: {len(table)}")
    print(f"Columnas disponibles: {table.field_names}")
    
    for i, record in enumerate(table):
        if i >= 3: break
        print(f"\n--- Registro {i+1} ---")
        for k, v in record.items():
            print(f"{k}: {v}")
except Exception as e:
    print(f"Error leyendo DBF: {e}")
