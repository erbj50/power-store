import pandas as pd
import requests
from supabase import create_client, Client
import io
import uuid

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
URL_FEED_SHOPEE = "https://affiliate.shopee.com.br/api/v1/datafeed/download?id=YWJjZGVmZ2hpamtsbW5vcFMjz35zY_7hscVJ_4QLIFiIR3DQ9hsrLcX6rgIVVFkb"
SUPABASE_URL = "https://vzpzbjnakzbnkksfpatl.supabase.co"
SUPABASE_KEY = "sb_publishable_MezbGHiL8dv5qGqWX-ZikQ_GNmJ7TAk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

LIMITE_POR_CATEGORIA = 110

# ==============================================================================
# ✅ PRODUTOS QUE VENDEM RÁPIDO — ALTO GIRO, PREÇO ACESSÍVEL
# ==============================================================================
CATEGORIAS_ALVO = {
    "Bíblia e Harpa": [
        "biblia", "bíblia", "harpa", "harpa cristã", "nova almeida", "ntlh",
        "nvt", "livro sagrado", "salmos", "devocional", "hinario"
    ],
    "Lingerie e Moda Íntima": [
        "lingerie", "calcinha", "sutiã", "soutien", "camisola", "body feminino",
        "conjunto intimo", "renda feminina", "calça intima", "tanga"
    ],
    "Cuecas e Meias": [
        "cueca", "meia masculina", "meia feminina", "meia infantil", "meia esportiva",
        "kit cueca", "kit meia", "meia antiderrapante", "boxer", "slip"
    ],
    "Pendrives e Carregadores": [
        "pendrive", "pen drive", "flash drive", "carregador celular", "carregador rapido",
        "cabo usb", "cabo type-c", "cabo lightning", "adaptador usb", "hub usb",
        "carregador turbo", "power bank"
    ],
    "Pets": [
        "pet", "cachorro", "gato", "ração", "coleira", "guia para pet",
        "brinquedo pet", "arranhador", "cama pet", "comedouro", "bebedouro pet",
        "higiene pet", "banho pet", "aquario", "peixe"
    ],
    "Cozinha Express": [
        "panela", "frigideira", "copo", "caneca", "faca", "kit facas",
        "conjunto panelas", "wok", "grelha", "escorredor", "forma bolo",
        "talheres", "concha", "espatula", "abridor", "garrafa termica",
        "porta tempero", "pote hermetico", "tigela"
    ],
    "Eletrônicos Acessíveis": [
        "fone de ouvido", "earphone", "earbuds", "fone bluetooth",
        "caixa de som", "speaker bluetooth", "mouse", "teclado",
        "suporte celular", "webcam", "leitor cartao", "cabo hdmi",
        "adaptador hdmi", "smart watch", "relogio inteligente"
    ],
    "Moda Feminina": [
        "vestido", "blusa feminina", "calca feminina", "short feminino",
        "mini saia", "cropped", "conjunto feminino", "macacao", "regata feminina",
        "camisa feminina", "moletom feminino"
    ],
    "Moda Masculina": [
        "camiseta masculina", "camisa masculina", "bermuda masculina",
        "calca masculina", "polo masculina", "óculos de grau masculino"
        "conjunto masculino", "moletom masculino", "jaqueta masculina"
    ],
    "Beleza e Cuidado Pessoal": [
        "shampoo", "condicionador", "mascara capilar", "creme hidratante",
        "protetor solar", "perfume", "desodorante", "maquiagem", "base",
        "batom", "rimel", "sombra", "pincel maquiagem", "kit skincare",
        "sabonete", "esfoliante", "oleo capilar"


 ],
"Saúde e bem-estar": [
    "vitaminas",
    "suplementos",
    "suplementos alimentares",
    "antioxidantes",
    "suplementos para imunidade",
    "suplementos para energia",
    "suplementos para saúde respiratória",
    "suplementos para saúde mental",
    "suplementos detox",
    "suplementos esportivos",
    "mascara capilar",
    "creme hidratante",


    ],
}

# ==============================================================================
# ❌ BLACKLIST — descarte silencioso imediato
# ==============================================================================
BLACKLIST = [
    # Veículos
    "carro", "moto", "veiculo", "veículo", "automovel", "automóvel",
    "caminhao", "caminhão", "pneu", "escapamento", "retrovisor",
    # Cama e Banho
    "tapete", "lencol", "lençol", "fronha", "edredom", "cobertor",
    "toalha", "colchao", "colchão", "travesseiro", "mosquiteiro",
    # Jardim e Campo
    "jardinagem", "mangueira", "regador", "vaso planta", "adubo",
    "fertilizante", "roçadeira", "motosserra", "enxada", "pá",
    # Limpeza
    "detergente", "desinfetante", "sabão em pó", "amaciante",
    "vassoura", "rodo", "esfregao", "esponja limpeza", "multiuso",
    # Alimentos / Supermercado
    "alimento", "comida", "biscoito", "bolacha", "arroz", "feijao",
    "feijão", "macarrao", "macarrão", "cafe", "café", "cha ", "chá ",
    "oleo de cozinha", "açucar", "acucar", "farinha", "suplemento alimentar",
    "proteina", "whey", "creatina","capacete","cortina","pneu","sacola",
    "bamba d'agua","mangueira", "cabo de aço", "corda", "cordão", "cinto de segurança", "extintor",
]


def na_blacklist(titulo: str) -> bool:
    t = titulo.lower()
    return any(b in t for b in BLACKLIST)


def classificar_categoria(titulo: str) -> str | None:
    t = titulo.lower()
    for cat, palavras in CATEGORIAS_ALVO.items():
        if any(p in t for p in palavras):
            return cat
    return None  # Não se encaixa em nenhuma categoria de alto giro → descarta


def url_valida(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    u = url.strip()
    return u.startswith("http") and len(u) > 20


def atualizar_vitrine():
    print("📥 Baixando feed da Shopee...")
    try:
        response = requests.get(URL_FEED_SHOPEE, stream=True, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Erro ao conectar na Shopee: {e}")
        return

    print("📊 Lendo CSV...")
    try:
        conteudo = io.StringIO(response.content.decode('utf-8', errors='ignore'))
        df = pd.read_csv(conteudo, sep=',')
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return

    df.columns = [str(c).lower().strip() for c in df.columns]
    print(f"📋 Colunas: {list(df.columns)}")

    # ------------------------------------------------------------------
    # Mapeamento de colunas — DEBUG: mostra o que foi encontrado
    # ------------------------------------------------------------------
    col_titulo    = next((c for c in df.columns if 'product_name' in c or 'title' in c or 'nome' in c or 'titulo' in c), df.columns[0])
    col_preco     = next((c for c in df.columns if 'price' in c or 'preco' in c or 'valor' in c), df.columns[1])
    col_comissao  = next((c for c in df.columns if 'commission' in c or 'comissao' in c or 'rate' in c), None)
    col_imagem    = next((c for c in df.columns if 'image' in c or 'imagem' in c or 'foto' in c), None)
    col_vendas    = next((c for c in df.columns if 'sold' in c or 'sales' in c or 'vendas' in c or 'historico' in c), None)

    # ✅ LINK AFILIADO — prioriza coluna com "affiliate" ou "offer_link" ou "deep_link"
    col_link = next((c for c in df.columns if 'affiliate' in c and 'link' in c), None)
    if not col_link:
        col_link = next((c for c in df.columns if 'offer_link' in c or 'deep_link' in c or 'product_link' in c), None)
    if not col_link:
        col_link = next((c for c in df.columns if 'link' in c or 'url' in c), None)

    print(f"🎯 Título: {col_titulo} | Preço: {col_preco} | Link: {col_link} | Imagem: {col_imagem} | Vendas: {col_vendas}")

    # ------------------------------------------------------------------
    # Limpeza numérica
    # ------------------------------------------------------------------
    df['preco_limpo'] = pd.to_numeric(
        df[col_preco].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce'
    ).fillna(0)

    if col_comissao and col_comissao in df.columns:
        df['comissao_limpa'] = pd.to_numeric(
            df[col_comissao].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce'
        ).fillna(0)
        df['comissao_limpa'] = df['comissao_limpa'].apply(lambda x: x / 100 if x > 1.0 else x)
    else:
        df['comissao_limpa'] = 0.13

    # Quantidade vendida para priorizar alto giro
    if col_vendas and col_vendas in df.columns:
        df['vendas'] = pd.to_numeric(
            df[col_vendas].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce'
        ).fillna(0)
    else:
        df['vendas'] = 0

    # Score = vendas × comissão × preço (prioriza volume de vendas real)
    df['score'] = df['vendas'] * df['comissao_limpa'] * df['preco_limpo']
    # Fallback: se não houver dado de vendas, usa comissão × preço
    df.loc[df['vendas'] == 0, 'score'] = df['comissao_limpa'] * df['preco_limpo']

    # ------------------------------------------------------------------
    # ✅ FILTRO DE PREÇO E COMISSÃO
    # ------------------------------------------------------------------
    df_filtrado = df[
        (df['preco_limpo'] >= 25.0) &   # Kit/unidade mínima a partir de R$25
        (df['preco_limpo'] <= 120.0) &
        (df['comissao_limpa'] >= 0.13) &
        (df['comissao_limpa'] <= 0.55)
    ].sort_values(by=['score', 'preco_limpo'], ascending=[False, True])
    # Ordenação: maior giro primeiro, desempate pelo menor preço (mais acessível)

    print(f"⚡ {len(df_filtrado)} produtos passaram no filtro de preço/comissão.")

    # ------------------------------------------------------------------
    # Loop de seleção com descarte silencioso
    # ------------------------------------------------------------------
    contadores = {cat: 0 for cat in CATEGORIAS_ALVO}
    produtos_para_enviar = []

    for _, row in df_filtrado.iterrows():
        if len(produtos_para_enviar) >= 1000:
            break

        titulo = str(row.get(col_titulo, '')).strip()
        link   = str(row.get(col_link, '')) if col_link else ''
        imagem = str(row.get(col_imagem, '')) if col_imagem else ''

        # Descarte silencioso
        if not titulo:
            continue
        if not url_valida(link):
            continue
        if not url_valida(imagem):
            continue
        if na_blacklist(titulo):
            continue

        cat = classificar_categoria(titulo)
        if cat is None:
            continue  # Não pertence a nenhuma categoria de alto giro

        if contadores[cat] >= LIMITE_POR_CATEGORIA:
            continue

        produtos_para_enviar.append({
            "id":            str(uuid.uuid4()),
            "titulo":        titulo[:150],
            "preco":         float(row['preco_limpo']),
            "link_afiliado": link.strip(),
            "imagem_url":    imagem.strip(),
            "categoria":     cat,
            "score":         float(row['score'])
        })
        contadores[cat] += 1

    # ------------------------------------------------------------------
    # Resultado
    # ------------------------------------------------------------------
    print(f"\n✅ {len(produtos_para_enviar)} produtos aprovados:")
    for cat, qtd in contadores.items():
        if qtd > 0:
            print(f"   {cat}: {qtd}")

    if not produtos_para_enviar:
        print("⚠️ Nenhum produto aprovado. Verifique as colunas acima.")
        return

    print("\n📤 Atualizando Supabase...")
    try:
        supabase.table('produtos').delete().neq('titulo', '').execute()
        supabase.table('produtos').insert(produtos_para_enviar).execute()
        print("🎉 Vitrine atualizada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar no Supabase: {e}")


if __name__ == "__main__":
    atualizar_vitrine()