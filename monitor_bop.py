import requests
import pdfplumber
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

# URL del BOP
url = "https://bop.dipuleon.es/publica/consulta-de-bops/"

# Palabras clave de subasta
palabras = [
    "subasta",
    "subasta pública",
    "embargo",
    "enajenación",
    "remate",
    "licitación"
]

# Pueblos
lugares = [
    "pola de gordón",
    "la pola de gordón",
    "paradilla de gordón"
]

# Obtener HTML principal
pagina = requests.get(url).text
soup = BeautifulSoup(pagina, "html.parser")

# Buscar todos los links a PDFs
links = []
for a in soup.find_all("a"):
    if ".pdf" in str(a.get("href")):
        links.append(a.get("href"))

# Revisar PDFs
coincidencias = []

for pdf_link in links:
    r = requests.get(pdf_link)
    with open("boletin.pdf","wb") as f:
        f.write(r.content)

    with pdfplumber.open("boletin.pdf") as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text().lower()

        for palabra in palabras:
            for lugar in lugares:
                if palabra in texto and lugar in texto:
                    coincidencias.append(pdf_link)

# Enviar email si hay coincidencias
if coincidencias:
    msg = MIMEText(f"""
ALERTA BOP LEÓN

Se encontraron coincidencias en los siguientes boletines:

{coincidencias}
""")

    msg["Subject"] = "⚠️ Subasta detectada en BOP León"
    msg["From"] = "TU_CORREO"
    msg["To"] = "jairolands@hotmail.com"

    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login("TU_CORREO","TU_PASSWORD_APP")
    server.send_message(msg)
    server.quit()
