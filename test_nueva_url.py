# test_completo.py
import psycopg2
from urllib.parse import quote_plus

opciones = [
    # streamlit_user con pooler
    ("streamlit_user + pooler", 
     "postgresql://streamlit_user:Elshow2026!@aws-1-us-west-2.pooler.supabase.com:5432/postgres"),
    
    # streamlit_user + pooler + SSL
    ("streamlit_user + pooler + SSL", 
     "postgresql://streamlit_user:Elshow2026!@aws-1-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"),
    
    # streamlit_user + directo
    ("streamlit_user + directo", 
     "postgresql://streamlit_user:Elshow2026!@db.qiyetiodyrgngidigmai.supabase.co:5432/postgres"),
    
    # streamlit_user + directo + SSL
    ("streamlit_user + directo + SSL", 
     "postgresql://streamlit_user:Elshow2026!@db.qiyetiodyrgngidigmai.supabase.co:5432/postgres?sslmode=require"),
    
    # postgres con pooler (si el user no funciona)
    ("postgres + pooler", 
     "postgresql://postgres:Elshow2026!@aws-1-us-west-2.pooler.supabase.com:5432/postgres"),
]

print("🔍 Probando todas las opciones...")
print("="*60)

for nombre, url in opciones:
    print(f"\n📡 {nombre}:")
    url_oculta = url.replace('Elshow2026!', '****')
    print(f"   {url_oculta[:80]}...")
    
    try:
        conn = psycopg2.connect(url)
        print("   ✅ ¡CONECTADO!")
        
        cur = conn.cursor()
        cur.execute("SELECT current_user")
        usuario = cur.fetchone()[0]
        print(f"   👤 Usuario: {usuario}")
        
        cur.close()
        conn.close()
        
        print(f"\n🎉 ¡ESTA FUNCIONA!")
        print(f'\n📝 Copia en .streamlit/secrets.toml:')
        print(f'DATABASE_URL = "{url}"')
        break
        
    except Exception as e:
        error_msg = str(e)[:80]
        if "authentication failed" in error_msg.lower():
            print(f"   ❌ Contraseña incorrecta")
        elif "closed the connection" in error_msg.lower():
            print(f"   ❌ Conexión cerrada - puede ser SSL o firewall")
        else:
            print(f"   ❌ {error_msg}")

print("\n" + "="*60)