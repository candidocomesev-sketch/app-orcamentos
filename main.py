import flet as ft
import datetime
import os
from fpdf import FPDF

def main(page: ft.Page):
    servicos_adicionados = []
    valor_total_orcamento = 0.0

    page.title = "Candido Serviços Elétricos"
    page.bgcolor = "#F6F5F0"
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    cor_texto_principal = "#1E293B"
    cor_destaque = "#2563EB"
    cor_card = ft.Colors.WHITE

    hoje = datetime.datetime.now().strftime("%d/%m/%Y")

    # --- TABELA DE PREÇOS (Sua "Planilha" Interna) ---
    tabela_precos = {
        "Passagem de cabo de alimentação": 150.00,
        "Troca do chuveiro": 80.00,
        "Instalação do chuveiro": 120.00,
        "Instalação de ventilador": 180.00,
        "Troca de Ventilador": 150.00,
        "Instalação de tomada": 45.00,
        "Instalação de interruptores": 45.00,
        "Montagem do quadro de distribuição": 350.00,
        "Troca do quadro de distribuição": 400.00,
        "Troca de lâmpada": 20.00,
        "Troca de luminária": 60.00,
        "Instalação do lustre": 150.00,
        "Limpeza do lustre": 100.00,
        "Instalação de luminária": 70.00,
        "Instalação de balizadores": 55.00,
        "Instalação de luminárias jardim": 85.00,
        "Instalação de interruptores automatizados": 120.00,
        "Instalação de câmera": 150.00,
        "Configurações de automação": 200.00,
        "Configurações de CFTV": 250.00,
        "Teste e entrega": 100.00
    }

    # --- 1. CABEÇALHO ---
    caminho_logo = "logo.png"
    tem_logo = os.path.exists(caminho_logo)

    icone_ou_logo = (
        ft.Image(src=caminho_logo, width=45, height=45, fit=ft.ImageFit.CONTAIN)
        if tem_logo
        else ft.Icon(ft.Icons.BOLT, color=cor_destaque, size=24)
    )

    cabecalho = ft.Row([
        ft.Container(
            content=icone_ou_logo,
            bgcolor=ft.Colors.TRANSPARENT if tem_logo else cor_texto_principal,
            padding=5 if tem_logo else 10,
            border_radius=10
        ),
        ft.Column([
            ft.Text("Cândido", size=18, weight=ft.FontWeight.W_800, color=cor_texto_principal),
            ft.Text("SERVIÇOS ELÉTRICOS", size=10, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_500),
        ], spacing=0)
    ], alignment=ft.MainAxisAlignment.START)

    # --- 2. HERO SECTION ---
    textos_destaque = ft.Column([
        ft.Row([
            ft.Container(width=30, height=2, bgcolor=cor_destaque),
            ft.Text("ORÇAMENTO DE CAMPO", size=11, weight=ft.FontWeight.BOLD, color=cor_destaque)
        ]),
        ft.Text("Monte um", size=32, weight=ft.FontWeight.W_900, color=cor_texto_principal, height=1.1),
        ft.Text("orçamento", size=32, weight=ft.FontWeight.W_900, color=cor_texto_principal, height=1.1),
        ft.Text("sem complicar.", size=32, weight=ft.FontWeight.W_900, color=cor_destaque, height=1.1),
    ], spacing=2)

    # CORREÇÃO AQUI: span -> spans e passando uma lista [ ]
    dica_rapida = ft.Container(
        content=ft.Text(
            spans=[
                ft.TextSpan("Dica: ", ft.TextStyle(weight=ft.FontWeight.BOLD, color=cor_texto_principal)),
                ft.TextSpan("selecione o serviço para puxar o preço. Você pode editar o valor livremente.", ft.TextStyle(color=ft.Colors.GREY_700))
            ],
            size=12
        ),
        bgcolor="#EAE8E1",
        padding=12,
        border_radius=5,
        border=ft.Border(left=ft.BorderSide(4, cor_destaque))
    )

    # --- 3. FORMULÁRIO ---
    estilo_campo = {
        "border_color": ft.Colors.GREY_300,
        "border_radius": 8,
        "content_padding": 12,
        "text_size": 14,
        "cursor_color": cor_destaque,
        "focused_border_color": cor_destaque
    }

    input_cliente = ft.TextField(label="Nome do cliente", prefix_icon=ft.Icons.PERSON_OUTLINE, **estilo_campo)
    input_endereco = ft.TextField(label="Endereço completo", prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, **estilo_campo)

    opcoes_padrao = list(tabela_precos.keys()) + ["Outro (Digitar manualmente)..."]

    dropdown_servico = ft.Dropdown(
        label="Selecione o Serviço/Material",
        options=[ft.dropdown.Option(texto) for texto in opcoes_padrao],
        expand=True,
        **estilo_campo
    )
    input_servico_manual = ft.TextField(label="Qual o novo serviço?", visible=False, expand=True, **estilo_campo)
    
    input_qtd = ft.TextField(label="Qtd", width=75, value="1", keyboard_type=ft.KeyboardType.NUMBER, **estilo_campo)
    input_valor_un = ft.TextField(label="Valor Un. (R$)", width=120, keyboard_type=ft.KeyboardType.NUMBER, **estilo_campo)

    def ao_mudar_servico(e):
        servico_selecionado = dropdown_servico.value
        
        if servico_selecionado == "Outro (Digitar manualmente)...":
            input_servico_manual.visible = True
            input_valor_un.value = ""
        else:
            input_servico_manual.visible = False
            input_servico_manual.value = ""
            if servico_selecionado in tabela_precos:
                preco = tabela_precos[servico_selecionado]
                input_valor_un.value = f"{preco:.2f}".replace(".", ",")
                
        page.update()

    dropdown_servico.on_change = ao_mudar_servico

    txt_valor_total = ft.Text("R$ 0,00", size=24, weight=ft.FontWeight.W_800, color=cor_texto_principal)
    lista_servicos = ft.ListView(height=160, spacing=5)

    def atualizar_total():
        nonlocal valor_total_orcamento
        valor_total_orcamento = sum(item['total_item'] for item in servicos_adicionados)
        txt_valor_total.value = f"R$ {valor_total_orcamento:.2f}"

    def remover_servico(item_dict, container_linha):
        servicos_adicionados.remove(item_dict)
        lista_servicos.controls.remove(container_linha)
        atualizar_total()
        page.update()

    def adicionar_servico_click(e):
        descricao_final = input_servico_manual.value if input_servico_manual.visible else dropdown_servico.value

        if not descricao_final:
            snack = ft.SnackBar(ft.Text("Selecione ou digite um serviço!"), bgcolor=ft.Colors.RED_600)
            page.open(snack)
            return

        try:
            qtd = int(input_qtd.value)
            valor_un = float(input_valor_un.value.replace(",", "."))
            total_item = qtd * valor_un

            item_dict = {
                'descricao': descricao_final,
                'qtd': qtd,
                'valor_un': valor_un,
                'total_item': total_item
            }

            container_linha = ft.Container(padding=8, bgcolor="#F8FAFC", border_radius=8)

            btn_remover = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=ft.Colors.RED_400,
                tooltip="Remover Item",
                on_click=lambda _: remover_servico(item_dict, container_linha)
            )

            container_linha.content = ft.Row([
                ft.Text(descricao_final, expand=True, size=12, color=cor_texto_principal),
                ft.Text(f"{qtd}x", size=12, color=ft.Colors.GREY_600),
                ft.Text(f"R$ {total_item:.2f}", size=13, weight=ft.FontWeight.BOLD, color=cor_destaque),
                btn_remover
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

            lista_servicos.controls.append(container_linha)
            servicos_adicionados.append(item_dict)

            atualizar_total()

            dropdown_servico.value = None
            input_servico_manual.visible = False
            input_servico_manual.value = ""
            input_qtd.value = "1"
            input_valor_un.value = ""
            page.update()
        except ValueError:
            snack = ft.SnackBar(ft.Text("Verifique a quantidade e o valor!"), bgcolor=ft.Colors.RED_600)
            page.open(snack)

    btn_adicionar = ft.ElevatedButton(
        "Adicionar",
        on_click=adicionar_servico_click,
        bgcolor=cor_texto_principal,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12)
    )

    # --- 4. GERAÇÃO DO PDF ---
    def sanitizar_texto(texto):
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

    def gerar_pdf_click(e):
        if not servicos_adicionados:
            snack = ft.SnackBar(ft.Text("Adicione pelo menos um serviço!"), bgcolor=ft.Colors.RED_600)
            page.open(snack)
            return

        pdf = FPDF()
        pdf.add_page()

        if tem_logo:
            pdf.image(caminho_logo, x=10, y=8, w=30)

        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, sanitizar_texto("CANDIDO SERVIÇOS ELÉTRICOS"), ln=True, align="R")
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, "CNPJ - 44.734.575/0001/03", ln=True, align="R")
        pdf.ln(12)

        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(100, 10, sanitizar_texto("ORÇAMENTO DE SERVIÇOS"), ln=False)
        pdf.set_font("helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(90, 10, f"Data: {hoje}", ln=True, align="R")
        pdf.ln(5)

        nome_cliente = input_cliente.value if input_cliente.value else "Não informado"
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 7, sanitizar_texto(f"Cliente: {nome_cliente}"), ln=True)
        pdf.set_font("helvetica", "", 11)
        pdf.cell(0, 7, sanitizar_texto(f"Endereço: {input_endereco.value}"), ln=True)
        pdf.ln(8)

        pdf.set_fill_color(37, 99, 235)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(90, 8, sanitizar_texto("DESCRIÇÃO"), border=1, fill=True)
        pdf.cell(20, 8, "QTD", border=1, align="C", fill=True)
        pdf.cell(40, 8, "VALOR UN.", border=1, align="R", fill=True)
        pdf.cell(40, 8, "TOTAL", border=1, ln=True, align="R", fill=True)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "", 10)
        for item in servicos_adicionados:
            pdf.cell(90, 8, sanitizar_texto(item['descricao'])[:45], border=1)
            pdf.cell(20, 8, str(item['qtd']), border=1, align="C")
            pdf.cell(40, 8, f"R$ {item['valor_un']:.2f}", border=1, align="R")
            pdf.cell(40, 8, f"R$ {item['total_item']:.2f}", border=1, ln=True, align="R")

        pdf.ln(5)
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 10, f"VALOR TOTAL: R$ {valor_total_orcamento:.2f}", ln=True, align="R")

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "", 10)
        pdf.ln(8)
        pdf.cell(0, 6, sanitizar_texto("Garantia de 3 meses. Padrões NBR 5410, NR10 e NR 35."), ln=True)

        nome_arquivo = f"Orcamento_{nome_cliente.replace(' ', '_')}.pdf"
        
        caminho_salvar = os.path.join(os.path.expanduser("~"), nome_arquivo) if os.name != 'nt' else nome_arquivo
        pdf.output(caminho_salvar)

        snack = ft.SnackBar(ft.Text(f"PDF gerado com sucesso!"), bgcolor=ft.Colors.GREEN_700)
        page.open(snack)

    btn_gerar_pdf = ft.ElevatedButton(
        "Finalizar e Gerar PDF",
        icon=ft.Icons.PICTURE_AS_PDF,
        on_click=gerar_pdf_click,
        bgcolor=cor_destaque,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=15)
    )

    card_formulario = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("ORÇAMENTO", size=18, weight=ft.FontWeight.W_700, color=cor_texto_principal)
                ], spacing=2),
                ft.Column([
                    ft.Text(f"Data: {hoje}", size=11, color=ft.Colors.GREY_600)
                ], spacing=2, alignment=ft.MainAxisAlignment.END)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=20, color=ft.Colors.GREY_200),

            ft.Text("DADOS DO CLIENTE", size=11, weight=ft.FontWeight.BOLD, color=cor_texto_principal),
            input_cliente, input_endereco,
            ft.Divider(height=20, color=ft.Colors.GREY_200),

            ft.Text("ITENS DO ORÇAMENTO", size=11, weight=ft.FontWeight.BOLD, color=cor_texto_principal),
            ft.Row([dropdown_servico]),
            ft.Row([input_servico_manual]),
            ft.Row([input_qtd, input_valor_un, btn_adicionar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            ft.Container(height=5),
            lista_servicos,
            ft.Divider(height=20, color=ft.Colors.GREY_200),

            ft.Row([
                ft.Text("TOTAL PARCIAL", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_500),
                txt_valor_total
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            ft.Row([btn_gerar_pdf], alignment=ft.MainAxisAlignment.CENTER)

        ], spacing=8),
        bgcolor=cor_card,
        padding=18,
        border_radius=16,
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.Colors.BLACK12)
    )

    page.add(
        cabecalho,
        ft.Container(height=5),
        textos_destaque,
        ft.Container(height=5),
        dica_rapida,
        ft.Container(height=10),
        card_formulario
    )

ft.run(main)
