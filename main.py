from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime, timedelta
import os
import json

app = FastAPI()   # 🔥 CETTE LIGNE DOIT ÊTRE AU NIVEAU GLOBAL

app.add_middleware(
    SessionMiddleware,
    secret_key="CHANGE_MOI_EN_TRUC_LONG_RANDOM_987654321"
)
import unicodedata

def detectar_prioridade(texto):

    if not texto:
        return None

    # normaliser texte
    t = texto.lower()

    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")

    # =========================
    # PRIORITÉ PREMIÈRE
    # =========================

    palavras_primeira = [
        "primeiro",
        "1o",
        "1º",
        "first"
    ]

    for p in palavras_primeira:
        if p in t:
            return "primeira"

    # =========================
    # PRIORITÉ DERNIÈRE
    # =========================

    palavras_ultima = [
        "ultimo",
        "ultima",
        "last"
    ]

    for p in palavras_ultima:
        if p in t:
            return "ultima"

    return None

def normalizar_nome(nome_raw):

    import unicodedata
    import re

    if not nome_raw:
        return None

    # ================================
    # 1️⃣ Nettoyage du texte
    # ================================

    # Supprimer contenu entre parenthèses
    nome_raw = re.sub(r"\(.*?\)", "", nome_raw)

    # Supprimer texte après tiret
    nome_raw = nome_raw.split("-")[0]

    # Minuscule + trim
    nome = nome_raw.lower().strip()

    # Supprimer accents
    nome = unicodedata.normalize("NFD", nome)
    nome = "".join(c for c in nome if unicodedata.category(c) != "Mn")

    # Supprimer caractères spéciaux / emojis
    nome = re.sub(r"[^a-z0-9\s]", "", nome)

    nome = nome.strip()

    # ================================
    # 2️⃣ Mapping complet validé
    # ================================

    mapa = {

        # Surnoms / alias principaux
        "italian": "SERGIO OLEARO",
        "mazon": "ADEMIR MAZON",
        "lo": "LAURENT MORCRETTE",
        "laurent": "LAURENT MORCRETTE",

        "luiz": "LUIZ EDUARDO LOUREIRO",
        "goes": "LUIZ GOES",

        "doc": "MARCO OLIVEIRA",

        "caberna": "PAULO R CABERNITE",
        "ramires": "RICARDO RAMIREZ",

        "romi": "ROMIYOSHI SASAKI",
        "romiyoshi": "ROMIYOSHI SASAKI",

        "penna": "ALEXANDRE PENNA",
        "gus": "GUSTAVO MUNIZ",
        "charlao": "CHARLISTON JACOMAZI",
        "pi": "ALBERTO PI",
        "milton": "MILTON PASCOWITCH",
        "marcio": "MARCIO LUIS SERDOZ",
        "vitor": "VITOR ANDRADE",
        "diego": "DIEGO LOPES",
        "arnaldo": "ARNALDO MOHR",

        "andre r": "ANDRE RICARDO",

        # ANDRE EGOROFF variations
        "a egoroff": "ANDRE EGOROFF",
        "andre e": "ANDRE EGOROFF",
        "andre egoroff": "ANDRE EGOROFF",

        "renato": "RENATO ARAUJO",
        "andres": "ANDRES LOBATO",

        "william": "WILLIAM IBANEZ",

        "hebert": "HEBERT DOS ANJOS",
        "herbert": "HEBERT DOS ANJOS",

        "uipiquer": "UIPIQER GOMES",
        "uipiqer": "UIPIQER GOMES",

        "edu": "EDUARDO JACOB",
        "fernando s": "FERNANDO CORREA",
        "fernando a": "FERNANDO ATHAYDE",
        "fred": "FREDERICO DE MELLO",
        "j muniz": "JOAO MUNIZ",
        "mario": "MARIO BAPTISTA",
        "mansur": "MARCO MANSUR",
        "walter": "WALTER FERNANDES",
        "yama": "YAMA",
        "cezar": "Cezar Federmann",
        "kim": "KIM",
        "oliver": "OLIVER MOESGEN",
        "arthur": "ARTHUR MEIER"
    }

    # ================================
    # 3️⃣ Matching intelligent
    # ================================

    for chave in mapa:
        if nome == chave:
            return mapa[chave]

    # Fallback : si prénom exact dans clé
    for chave in mapa:
        if nome.startswith(chave + " "):
            return mapa[chave]

    return None
# ================= CHARGEMENT JOUEURS =================






@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):

    # TEMPORAIREMENT sans sécurité
    # if not request.session.get("admin"):
    #     return RedirectResponse("/login", status_code=303)

    jogadores = get_jogadores()

    html = "<h1>Administração</h1>"
    html += '<a href="/">Voltar</a><br><br>'

    html += """
    <form method="post" action="/add_jogador">
        Nome: <input type="text" name="name" required>
        Handicap: <input type="number" step="0.1" name="handicap" required>
        <button>Adicionar</button>
    </form>
    <hr>
    """

    for j in jogadores:
     html += f"""
        <div style="margin-bottom:5px;">
        {j['name']} (hcp {j['handicap']})
        <form action="/delete_jogador" method="post" style="display:inline;">
            <input type="hidden" name="name" value="{j['name']}">
            <button style="background:#B22222;color:white;border:none;padding:3px 6px;border-radius:4px;">
                Supprimer
            </button>
        </form>
       </div>
       """

    return html

    jogadores = get_jogadores()

    html = "<h1>Administração</h1>"
    html += '<a href="/">Voltar</a><br><br>'

    html += """
    <form method="post" action="/add_jogador">
        Nome: <input type="text" name="name" required>
        Handicap: <input type="number" step="0.1" name="handicap" required>
        <button>Adicionar</button>
    </form>
    <hr>
    """

    for j in jogadores:
        html += f"{j['name']} (hcp {j['handicap']})<br>"

    return html



# ================= DONNÉES =================

from database import get_connection

def get_jogadores():
    conn = get_connection()
    jogadores = conn.execute("SELECT * FROM jogadores").fetchall()
    conn.close()
    return [dict(j) for j in jogadores]

if os.path.exists("inscricoes.json"):
    with open("inscricoes.json", "r") as f:
        inscricoes = json.load(f)
else:
    inscricoes = []
saidas_geradas = {"1": [], "2": []}
horarios = {"1": [], "2": []}

data_jogo = ""
ranking = False
hcp_max_3 = None
hcp_max_4 = None
message_erreur = ""


# ================= HOME =================



@app.get("/", response_class=HTMLResponse)
def home():

    jogadores = get_jogadores()

    html = '<a href="/admin">Administração</a><br><br>'

    # ================= HEADER =================

    html += '''
    <div style="
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        margin-bottom:20px;
    ">
    '''

    html += '<h1 style="margin:0;">Inscrição para o jogo</h1>'

    html += '''
        <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex; gap:8px;">
                <a href="/gerar">
                    <button style="background:#2E8B57;color:white;padding:8px 15px;border:none;border-radius:6px;">
                        GERAR SAÍDAS
                    </button>
                </a>

                <form action="/reset_saidas" method="post">
                    <button style="background:#555;color:white;padding:8px 15px;border:none;border-radius:6px;">
                        NOVA TENTATIVA
                    </button>
                </form>
            </div>

            <div style="display:flex; gap:8px;">
                <a href="/pdf">
                    <button style="background:#1E90FF;color:white;padding:8px 15px;border:none;border-radius:6px;">
                        GERAR PDF
                    </button>
                </a>

                <form action="/cancelar_todas" method="post">
                    <button style="background:#B22222;color:white;padding:8px 15px;border:none;border-radius:6px;">
                        CANCELAR TODAS
                    </button>
                </form>
            </div>

            <a href="/export_whatsapp">
                <button style="background:#25D366;color:white;padding:8px 15px;border:none;border-radius:6px;">
                    EXPORT WHATSAPP
                </button>
            </a>
        </div>
    </div>
    '''

    # ================= MESSAGE ERREUR =================

    if message_erreur:
        html += f'''
        <div style="background:#B22222;color:white;padding:10px;border-radius:6px;margin-bottom:15px;">
            {message_erreur}
        </div>
        '''

    # ================= CONFIG =================

    html += f'''
    <form action="/configurar_jogo" method="post"
          style="background:#f5f5f5;padding:10px;border-radius:8px;margin-bottom:20px">
        Data: <input type="date" name="data" value="{data_jogo}">
        Ranking: <input type="checkbox" name="ranking_check" {"checked" if ranking else ""}>
        HCP grupo 3: <input type="number" step="0.1" name="hcp3" value="{hcp_max_3 if hcp_max_3 else ''}">
        HCP grupo 4: <input type="number" step="0.1" name="hcp4" value="{hcp_max_4 if hcp_max_4 else ''}">
        <button>Salvar</button>
    </form>
    '''

    # ================= CONTAINER PRINCIPAL =================

    html += '<div style="display:flex;flex-direction:column;gap:40px;">'

    html += '''
      <form action="/import_whatsapp" method="post">
      <textarea name="texto" rows="10" style="width:100%;" placeholder="Colle ici la liste WhatsApp"></textarea>
      <button style="margin-top:5px;">IMPORTER WHATSAPP</button>
      </form>
     <hr>
    '''

    # ================= JOUEURS =================

    html += '<div>'
    html += '<h2>Jogadores</h2>'

    for p in jogadores:

        inscrito = next((r["tee"] for r in inscricoes if r["name"] == p["name"]), None)

        style7 = "background:#FFD700;" if inscrito == "1" else ""
        style8 = "background:#FF8C00;color:white;" if inscrito == "2" else ""
        style0 = "background:#B22222;color:white;" if inscrito is None else ""

        html += '''
        <div style="
            display:grid;
            grid-template-columns: 320px 70px 70px 80px 160px 160px 110px;
            align-items:center;
            gap:6px;
            margin-bottom:6px;
        ">
        '''

        html += f'<div style="white-space:nowrap;font-weight:bold;">{p["name"]} (hcp {p["handicap"]})</div>'

        # 7h
        html += f'''
        <form action="/registrar" method="post">
            <input type="hidden" name="name" value="{p["name"]}">
            <input type="hidden" name="tee" value="1">
            <button style="width:100%;{style7}padding:4px;border:none;border-radius:4px;">7h</button>
        </form>
        '''

        # 8h
        html += f'''
        <form action="/registrar" method="post">
            <input type="hidden" name="name" value="{p["name"]}">
            <input type="hidden" name="tee" value="2">
            <button style="width:100%;{style8}padding:4px;border:none;border-radius:4px;">8h</button>
        </form>
        '''

        # Não
        html += f'''
        <form action="/nao_jogar" method="post">
            <input type="hidden" name="name" value="{p["name"]}">
            <button style="width:100%;{style0}padding:4px;border:none;border-radius:4px;">Não</button>
        </form>
        '''

        # Souhait
        html += f'''
        <form action="/souhait" method="post">
            <input type="hidden" name="name" value="{p["name"]}">
            <select name="souhait" onchange="this.form.submit()" style="width:100%;">
                <option value="">-- Souhait --</option>
        '''
        for autre in jogadores:
            if autre["name"] != p["name"]:
                selected = "selected" if p.get("souhait") == autre["name"] else ""
                html += f'<option value="{autre["name"]}" {selected}>{autre["name"]}</option>'
        html += '</select></form>'

        # Prioridade
        html += f'''
        <form action="/prioridade" method="post">
            <input type="hidden" name="name" value="{p["name"]}">
            <select name="prioridade" onchange="this.form.submit()" style="width:100%;">
                <option value="">-- Prioridade --</option>
                <option value="primeira" {"selected" if p.get("prioridade")=="primeira" else ""}>1ª Turma</option>
                <option value="ultima" {"selected" if p.get("prioridade")=="ultima" else ""}>Última Turma</option>
            </select>
        </form>
        '''

        # Convidado
        cor = "background:#2E8B57;color:white;" if p.get("convidado") else ""
        html += f'''
        <form action="/toggle_convidado" method="post">
            <input type="hidden" name="name" value="{p["name"]}">
            <button style="width:100%;{cor}padding:4px;border:1px solid #999;border-radius:4px;">
                CONVIDADO
            </button>
        </form>
        '''

        html += '</div>'

    html += '</div>'

    # ================= INSCRITOS =================

    html += '<div>'
    html += '<h2>INSCRITOS</h2>'
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">'

    for tee in ["1", "2"]:

        html += '<div>'
        html += f'<h3>{"7h" if tee=="1" else "8h"}</h3>'
        html += '<div style="border:1px solid #ccc;padding:8px;min-height:150px;">'

        for r in inscricoes:
            if r["tee"] == tee:
                html += f'<div>{r["name"]}</div>'

        html += '</div></div>'

    html += '</div></div>'

    # ================= SAIDAS =================

    html += '<div>'
    html += '<h2>Saídas</h2>'

    for tee in ["1", "2"]:

        html += f'<h3>{"7h" if tee=="1" else "8h"}</h3>'

        if not saidas_geradas.get(tee):
            html += "Aucun groupe généré.<br><br>"
            continue

        for i, grupo in enumerate(saidas_geradas[tee]):

            hora = horarios[tee][i] if i < len(horarios[tee]) else ""
            html += f"<b>{hora}</b><br>"

            total = 0

            for r in grupo:

                if r["name"].startswith("conv. "):
                    html += f'{r["name"]} (hcp 0)<br>'
                else:
                    for j in jogadores:
                        if j["name"] == r["name"]:
                            total += j["handicap"]
                            html += f'{j["name"]} ({j["handicap"]})<br>'
                            break

            html += f"<b>Total: {round(total,1)}</b><br><br>"

    html += '</div>'
    html += '</div>'  # ferme container principal

    return html

    # ================= ACTIONS =================

@app.post("/add_jogador")
def add_jogador(name: str = Form(...), handicap: float = Form(...)):

    conn = get_connection()
    conn.execute(
        "INSERT INTO jogadores (name, handicap, souhait) VALUES (?, ?, ?)",
        (name, handicap, "")
    )
    conn.commit()
    conn.close()

    return RedirectResponse("/admin", status_code=303)

@app.post("/registrar")
def registrar(name: str = Form(...), tee: str = Form(...)):
    global inscricoes

    # supprimer ancienne inscription du joueur + invité
    inscricoes = [
        i for i in inscricoes
        if i["name"] != name and i["name"] != f"conv. {name}"
    ]

    # ajouter joueur principal
    inscricoes.append({
        "name": name,
        "tee": tee
    })

    # vérifier si invité actif
    conn = get_connection()
    jogador = conn.execute(
        "SELECT convidado FROM jogadores WHERE name = ?",
        (name,)
    ).fetchone()
    conn.close()

    if jogador and jogador["convidado"] == 1:
        inscricoes.append({
            "name": f"conv. {name}",
            "tee": tee
        })

    return RedirectResponse("/", status_code=303)


@app.post("/nao_jogar")
def nao_jogar(name: str = Form(...)):
    global inscricoes
    inscricoes = [i for i in inscricoes if i["name"] != name]
    return RedirectResponse("/", status_code=303)


@app.post("/cancelar_todas")
def cancelar_todas():

    global inscricoes
    global saidas_geradas
    global horarios
    global message_erreur

    # 🔹 Reset variables en mémoire
    inscricoes = []
    saidas_geradas = {"1": [], "2": []}
    horarios = {"1": [], "2": []}
    message_erreur = ""

    # 🔹 Reset base de données
    conn = get_connection()
    conn.execute("""
        UPDATE jogadores
        SET convidado = 0,
            souhait = '',
            prioridade = ''
    """)
    conn.commit()
    conn.close()

    # 🔹 Remettre tous les convidados à False en base
    conn = get_connection()
    conn.execute("UPDATE jogadores SET convidado = 0")
    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)


@app.post("/reset_saidas")
def reset_saidas():
    global saidas_geradas, horarios
    saidas_geradas = {"1": [], "2": []}
    horarios = {"1": [], "2": []}
    return RedirectResponse("/", status_code=303)


@app.post("/configurar_jogo")
def configurar_jogo(
    data: str = Form(""),
    ranking_check: str = Form(None),
    hcp3: float = Form(None),
    hcp4: float = Form(None),
):
    global data_jogo, ranking, hcp_max_3, hcp_max_4

    data_jogo = data
    ranking = ranking_check is not None
    hcp_max_3 = hcp3
    hcp_max_4 = hcp4

    return RedirectResponse("/", status_code=303)

@app.post("/souhait")
def definir_souhait(name: str = Form(...), souhait: str = Form("")):

    conn = get_connection()
    conn.execute(
        "UPDATE jogadores SET souhait = ? WHERE name = ?",
        (souhait.strip(), name)
    )
    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)

@app.post("/delete_jogador")
def delete_jogador(name: str = Form(...)):
    conn = get_connection()
    conn.execute("DELETE FROM jogadores WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return RedirectResponse("/admin", status_code=303)

@app.post("/prioridade")
def definir_prioridade(name: str = Form(...), prioridade: str = Form("")):

    conn = get_connection()
    conn.execute(
        "UPDATE jogadores SET prioridade = ? WHERE name = ?",
        (prioridade, name)
    )
    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)

@app.post("/toggle_convidado")
def toggle_convidado(name: str = Form(...)):
    global inscricoes

    conn = get_connection()

    jogador = conn.execute(
        "SELECT convidado FROM jogadores WHERE name = ?",
        (name,)
    ).fetchone()

    novo_valor = 0 if jogador["convidado"] else 1

    conn.execute(
        "UPDATE jogadores SET convidado = ? WHERE name = ?",
        (novo_valor, name)
    )

    conn.commit()
    conn.close()

    # ✅ Si on désactive l’invité → le retirer des inscrits
    if novo_valor == 0:
        inscricoes = [
            i for i in inscricoes
            if i["name"] != f"conv. {name}"
        ]

    # ✅ Si on active et joueur déjà inscrit → ajouter invité
    else:
        for i in inscricoes:
            if i["name"] == name:
                inscricoes.append({
                    "name": f"conv. {name}",
                    "tee": i["tee"]
                })
                break

    return RedirectResponse("/", status_code=303)



    # ================= GERAR =================

    jogadores = get_jogadores()

def regrouper_souhaits(joueurs):
    """
    Version 100% sûre.
    Aucun joueur ne peut disparaître.
    """

    # Initialisation : chaque joueur dans son bloc
    blocs = [[j] for j in joueurs]

    # Helper pour trouver bloc d'un joueur
    def trouver_bloc(nom):
        for bloc in blocs:
            for j in bloc:
                if j["name"] == nom:
                    return bloc
        return None

    # Fusion selon souhaits
    for j in joueurs:

        souhait = j.get("souhait", "").strip()
        if not souhait:
            continue

        bloc1 = trouver_bloc(j["name"])
        bloc2 = trouver_bloc(souhait)

        if bloc1 and bloc2 and bloc1 is not bloc2:

            # Fusion propre
            bloc1.extend(bloc2)
            blocs.remove(bloc2)

    return blocs


def criar_grupos(lista):
    n = len(lista)

    if n == 0:
        return []

    # 🔥 SEUL CAS AUTORISÉ POUR 5
    if n == 5:
        return [lista]

    # Interdit d'avoir groupe de 5 sinon
    # On ne cherche QUE combinaisons 3 et 4

    melhor = None

    for num4 in range(n // 4, -1, -1):
        reste = n - (num4 * 4)

        if reste % 3 == 0:
            num3 = reste // 3
            melhor = (num4, num3)
            break

    if not melhor:
        # sécurité : tout en un seul groupe (ne devrait jamais arriver)
        return [lista]

    num4, num3 = melhor
    grupos = []
    i = 0

    # Groupes de 3 d'abord (partent avant)
    for _ in range(num3):
        grupos.append(lista[i:i+3])
        i += 3

    # Puis groupes de 4
    for _ in range(num4):
        grupos.append(lista[i:i+4])
        i += 4

    return grupos


@app.get("/gerar")
def gerar():
    global saidas_geradas
    global horarios
    global message_erreur

    jogadores = get_jogadores()
    message_erreur = ""

    for tee in ["1", "2"]:

        print("\n======================")
        print("TEE:", tee)

        # ===============================
        # 1️⃣ Récupérer joueurs du tee
        # ===============================
        lista = [r for r in inscricoes if r["tee"] == tee]
        print("INSCRITS:", len(lista))

        jogadores_com_hcp = []

        for r in lista:
            if r["name"].startswith("conv. "):
                jogadores_com_hcp.append({
                    "name": r["name"],
                    "handicap": 0,
                    "souhait": "",
                    "prioridade": ""
                })
            else:
                for j in jogadores:
                    if j["name"] == r["name"]:
                        jogadores_com_hcp.append(j)
                        break

        print("JOGADORES_COM_HCP:", len(jogadores_com_hcp))

        if not jogadores_com_hcp:
            saidas_geradas[tee] = []
            horarios[tee] = []
            continue

        # ===============================
        # 2️⃣ Regrouper souhaits
        # ===============================
        blocs = regrouper_souhaits(jogadores_com_hcp)

        print("NB BLOCS:", len(blocs))
        print("SOMME BLOCS:", sum(len(b) for b in blocs))

        # 🔥 Vérification sécurité
        if sum(len(b) for b in blocs) != len(jogadores_com_hcp):
            message_erreur = "ERREUR: Tous les joueurs ne sont pas dans les blocs."
            print("⚠️ PROBLÈME BLOCS")
            return RedirectResponse("/", status_code=303)

        # ===============================
        # 3️⃣ Trier joueurs par HCP décroissant
        # ===============================
        jogadores_com_hcp.sort(key=lambda j: j["handicap"], reverse=True)

        # ===============================
        # 4️⃣ Déterminer tailles optimales
        # ===============================
        grupos_brutos = criar_grupos(jogadores_com_hcp)
        tailles = [len(g) for g in grupos_brutos]
        grupos = [[] for _ in tailles]

        # ===============================
        # 5️⃣ Distribution par bloc
        # ===============================
        for bloco in blocs:

            placed = False

            for i in range(len(grupos)):
                if len(grupos[i]) + len(bloco) <= tailles[i]:
                    grupos[i].extend(bloco)
                    placed = True
                    break

            if not placed:
                message_erreur = "Impossible de placer les souhaits."
                print("⚠️ IMPOSSIBLE DE PLACER BLOC")
                return RedirectResponse("/", status_code=303)

        print("JOUEURS PLACÉS:", sum(len(g) for g in grupos))

        # 🔥 Vérification finale
        if sum(len(g) for g in grupos) != len(jogadores_com_hcp):
            message_erreur = "ERREUR: Tous les joueurs ne sont pas placés."
            print("⚠️ JOUEURS PERDUS")
            return RedirectResponse("/", status_code=303)

        # ===============================
        # 6️⃣ Séparer 3 et 4
        # ===============================
        grupos_3 = [g for g in grupos if len(g) == 3]
        grupos_4 = [g for g in grupos if len(g) == 4]

        grupos_3.sort(key=lambda g: sum(j["handicap"] for j in g))
        grupos_4.sort(key=lambda g: sum(j["handicap"] for j in g))

        grupos_ordenados = grupos_3 + grupos_4

        # ===============================
        # 7️⃣ Gestion priorité
        # ===============================
        def contient_primeira(grupo):
            return any(j.get("prioridade") == "primeira" for j in grupo)

        def contient_ultima(grupo):
            return any(j.get("prioridade") == "ultima" for j in grupo)

        grupos_primeira = [g for g in grupos_ordenados if contient_primeira(g)]
        grupos_normaux = [g for g in grupos_ordenados if not contient_primeira(g) and not contient_ultima(g)]
        grupos_ultima = [g for g in grupos_ordenados if contient_ultima(g)]

        grupos = grupos_primeira + grupos_normaux + grupos_ultima

        # ===============================
        # 8️⃣ Sauvegarde résultat
        # ===============================
        saidas_geradas[tee] = [
            [{"name": j["name"]} for j in grupo]
            for grupo in grupos
        ]

        inicio = "07:00" if tee == "1" else "08:00"
        base = datetime.strptime(inicio, "%H:%M")

        horarios[tee] = [
            (base + timedelta(minutes=7 * i)).strftime("%H:%M")
            for i in range(len(grupos))
        ]

    return RedirectResponse("/", status_code=303)

@app.get("/pdf")
def pdf():

    file_path = "JOGO.pdf"
    doc = SimpleDocTemplate(file_path)
    elements = []
    styles = getSampleStyleSheet()

    # Titre
    titre = f"JOGO {data_jogo}" if data_jogo else "JOGO"
    if ranking:
        titre += " - RANKING"

    elements.append(Paragraph(titre, styles["Title"]))
    elements.append(Spacer(1, 20))

    for tee in ["1", "2"]:

        elements.append(
            Paragraph(f"Tee {'7h' if tee == '1' else '8h'}", styles["Heading2"])
        )
        elements.append(Spacer(1, 10))

        if not saidas_geradas.get(tee):
            elements.append(Paragraph("Aucun groupe généré.", styles["Normal"]))
            elements.append(Spacer(1, 20))
            continue

        for i, grupo in enumerate(saidas_geradas[tee]):

            hora = horarios[tee][i] if i < len(horarios[tee]) else ""

            data_table = [[hora, "", "HCP"]]
            total = 0

            for r in grupo:
                joueur = next((j for j in jogadores if j["name"] == r["name"]), None)
                if joueur:
                    total += joueur["handicap"]
                    data_table.append(
                        [joueur["name"], "", str(joueur["handicap"])]
                    )

            data_table.append(["TOTAL", "", str(round(total, 1))])

            table = Table(data_table, colWidths=[200, 30, 50])
            table.setStyle(
                TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ])
            )

            elements.append(table)
            elements.append(Spacer(1, 20))

    doc.build(elements)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="JOGO.pdf"
    )

from fastapi.responses import FileResponse
from datetime import datetime, timedelta

@app.get("/export_whatsapp")
def export_whatsapp():

    print("DEBUG SAIDAS:", saidas_geradas)
    print("DEBUG HORARIOS:", horarios)

    jogadores = get_jogadores()

    texto = f"SAÍDAS DO DIA {data_jogo}\n"

    ranking_txt = "SIM" if ranking else "NÃO"
    texto += f"🏆 RANKING: {ranking_txt}\n"

    texto += "=" * 30 + "\n\n"

    for tee in ["1", "2"]:

        grupos = saidas_geradas.get(tee, [])

        if not grupos:
            continue

        titulo = "7h" if tee == "1" else "8h"
        texto += f"{titulo}\n"
        texto += "-" * 20 + "\n"

        # 🔥 Recalcul horaire de manière sûre
        inicio = "07:00" if tee == "1" else "08:00"
        base = datetime.strptime(inicio, "%H:%M")

        for i, grupo in enumerate(grupos):

            hora = (base + timedelta(minutes=7 * i)).strftime("%H:%M")
            texto += f"{hora}\n"

            total = 0

            for r in grupo:

                # 🎟️ Convidado
                if r["name"].startswith("conv. "):
                    texto += f"  - {r['name']} (hcp 0)\n"
                    continue

                # 👤 Joueur normal
                jogador = next((j for j in jogadores if j["name"] == r["name"]), None)

                if jogador:
                    total += jogador["handicap"]
                    texto += f"  - {jogador['name']} ({jogador['handicap']})\n"

            texto += f"  TOTAL: {round(total,1)}\n\n"

        texto += "\n"

    # 🔥 Sécurité : si aucun groupe
    if texto.strip() == "":
        texto = "Aucune saída générée."

    file_path = "saidas.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(texto)

    return FileResponse(
        file_path,
        media_type="text/plain",
        filename="saidas.txt"
    )

@app.post("/import_whatsapp")
def import_whatsapp(texto: str = Form(...)):

    global inscricoes

    # 🔄 Reset propre
    inscricoes = []

    linhas = texto.splitlines()
    tee_atual = None

    jogadores = get_jogadores()

    for linha in linhas:

        linha_original = linha.strip()

        if not linha_original:
            continue

        linha_lower = linha_original.lower().strip()

        # ==========================
        # 1️⃣ Détection horaire
        # ==========================

        if linha_lower.startswith("7:00"):
            tee_atual = "1"
            continue

        if linha_lower.startswith("8:00"):
            tee_atual = "2"
            continue

        # Si aucun tee défini → ignorer
        if not tee_atual:
            continue

        # Ignorer lignes décoratives
        if any(x in linha_lower for x in [
            "sabado", "sábado", "domingo", "ranking",
            "sexta", "jogos", "final"
        ]):
            continue

        # ==========================
        # 2️⃣ CAS CONVIDADO
        # ==========================

        if "amigo do" in linha_lower:

            parte = linha_lower.split("amigo do")[-1].strip()
            nome_responsavel = normalizar_nome(parte)

            if nome_responsavel:

                # Activer convidado en base
                conn = get_connection()
                conn.execute(
                    "UPDATE jogadores SET convidado = 1 WHERE name = ?",
                    (nome_responsavel,)
                )
                conn.commit()
                conn.close()

                # Ajouter conv. NOM
                inscricoes.append({
                    "name": f"conv. {nome_responsavel}",
                    "tee": tee_atual
                })

            continue

        # ==========================
        # 3️⃣ Nettoyage ligne joueur
        # ==========================

        # Supprimer contenu parenthèses
        if "(" in linha_original:
            linha_original = linha_original.split("(")[0]

        # Supprimer tirets
        if "-" in linha_original:
            linha_original = linha_original.split("-")[0]

        linha_original = linha_original.strip()

        # ==========================
        # 4️⃣ Normalisation nom
        # ==========================

        nome_oficial = normalizar_nome(linha_original)

        if not nome_oficial:
            print("NON MATCHÉ:", linha_original)
            continue

        # Ajouter inscription joueur
        inscricoes.append({
            "name": nome_oficial,
            "tee": tee_atual
        })

        # ==========================
        # 5️⃣ Détection priorité
        # ==========================

        prioridade_detectada = detectar_prioridade(linha)

        conn = get_connection()

        if prioridade_detectada:
            conn.execute(
                "UPDATE jogadores SET prioridade = ? WHERE name = ?",
                (prioridade_detectada, nome_oficial)
            )
        else:
            conn.execute(
                "UPDATE jogadores SET prioridade = '' WHERE name = ?",
                (nome_oficial,)
            )

        conn.commit()
        conn.close()

    # ==========================
    # 🔍 DEBUG FINAL
    # ==========================

    print("------ DEBUG IMPORT ------")
    print("TOTAL INSCRICOES:", len(inscricoes))
    print("7H:", len([i for i in inscricoes if i["tee"] == "1"]))
    print("8H:", len([i for i in inscricoes if i["tee"] == "2"]))
    print("--------------------------")

    return RedirectResponse("/", status_code=303)