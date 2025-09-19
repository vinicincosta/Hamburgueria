from tkinter.constants import CENTER

import flet as ft
from flet import AppBar, Text, View
from flet.core.alignment import top_left, bottom_center
from flet.core.border_radius import horizontal
from flet.core.box import BoxDecoration
from flet.core.buttons import ButtonStyle, RoundedRectangleBorder
from flet.core.colors import Colors
from flet.core.dropdown import Option
from flet.core.elevated_button import ElevatedButton
from flet.core.icons import Icons
from flet.core.text_style import TextStyle, TextThemeStyle
from flet.core.theme import TextTheme
from flet.core.types import FontWeight, MainAxisAlignment, CrossAxisAlignment
from sqlalchemy import Column
from sqlalchemy.dialects.oracle import NUMBER

from routes import *


def main(page: ft.Page):
    # Configurações
    page.title = "Exemplo de Login"
    page.theme_mode = ft.ThemeMode.LIGHT  # ou ft.ThemeMode.DARK
    page.window.width = 375
    page.window.height = 667
    page.fonts = {
        "Playfair Display": "https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap"
    }
    # Funções
    def click_login(e):
        loading_indicator.visible = True
        page.update()

        resultado_pessoas = listar_pessoas()
        print(f'Resultado: {resultado_pessoas}')

        # Verifica se os campos estão preenchidos
        if not input_email.value or not input_senha.value:
            snack_error('Email e senha são obrigatórios.')
            page.update()
            return
        page.update()

        # Chama a função de login
        token, papel, nome, error = post_login(input_email.value, input_senha.value)

        print(f"Token: {token}, Papel: {papel}, Nome: {nome}, Erro: {error}")
        print(token)
        # Verifica se o usuário está inativo
        for pessoa in resultado_pessoas:
            if pessoa['email'] == input_email.value:  # Verifica se o CPF corresponde
                if pessoa['status_pessoa'] == "Inativo":
                    snack_error('Erro: usuário inativo.')
                    page.update()
                    return  # Sai da função se o usuário estiver inativo

        # Se o login foi bem-sucedido e o usuário está ativo
        if token:
            snack_sucesso(f'Login bem-sucedido, {nome} ({papel})!')
            print(f"Papel do usuário: {papel}, Nome: {nome}")
            page.client_storage.set('token', token)
            page.client_storage.set('papel', papel)
            input_email.value = ''
            input_senha.value = ''

            if papel == "cliente":
                page.go("/presencial_delivery")  # Redireciona para a rota do usuário
            elif papel == "garcom":
                page.go("/mesa")  # Redireciona para a rota garçom
            else:
                snack_error('Erro: Papel do usuário desconhecido.')
        else:
            snack_error(f'Erro: {error}')

        page.update()

    def cadastro_click_user(e):
        try:
            # Se não for admin, define como cliente
            papel = input_papel.value
            if papel != "admin":
                papel = "cliente"

            pessoa, error = post_pessoas(
                input_nome.value,
                input_cpf.value,
                papel,  # papel já validado
                input_senha_cadastro.value,
                float(slider_salario.value or 0),  # garante valor numérico
                input_email_cadastrado.value,
                input_status_user.value,
            )

            if pessoa:
                snack_sucesso(f'Usuário criado com sucesso! ID: {pessoa["user_id"]}')
                # Resetar os campos
                input_nome.value = ""
                input_cpf.value = ""
                input_email_cadastrado.value = ""
                input_senha_cadastro.value = ""
                input_status_user.value = None
                input_papel.value = None
                slider_salario.value = 0  # volta para o mínimo
                txt_salario.value = "SALÁRIO: 0"
            else:
                snack_error(f'Erro: {error}')

        except Exception as ex:
            snack_error(f"Erro inesperado: {ex}")

        page.update()

    def click_logout(e):
        page.client_storage.remove("access_token")
        snack_sucesso("logout realizado com sucesso")
        page.go("/")

    def snack_sucesso(texto: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=Colors.ORANGE_800
        )
        page.snack_bar.open = True
        page.overlay.append(page.snack_bar)

    def snack_error(texto: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=Colors.ORANGE_900
        )
        page.snack_bar.open = True
        page.overlay.append(page.snack_bar)

    def cardapio(e):
        lv_lanches.controls.clear()  # limpa antes de carregar
        token = page.client_storage.get('token')
        resultado_lanches = listar_lanche(token)
        print(f'Resultado dos lanches: {resultado_lanches}')

        for lanche in resultado_lanches:
            lv_lanches.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Image(src="imagemdolanche.png", height=100),
                                ft.Column(
                                    [
                                        ft.Text(f'{lanche["nome_lanche"]}', color=Colors.ORANGE_900),
                                        ft.Text(f'R$ {lanche["valor_lanche"]:.2f}', color=Colors.YELLOW_900),
                                        ft.Text(f'{lanche["descricao_lanche"]}',
                                                color=Colors.YELLOW_800, width=200),

                                        # Botão Finalizar Pedido
                                        ft.ElevatedButton(
                                            "Finalizar Pedido",
                                            on_click=lambda e: page.open(dlg_modal),
                                            style=ft.ButtonStyle(
                                                bgcolor=Colors.ORANGE_700,
                                                color=Colors.BLACK,
                                                padding=15,
                                                shape={"": ft.RoundedRectangleBorder(radius=10)}
                                            )
                                        )
                                    ]
                                ),
                            ]
                        ),
                        bgcolor=Colors.BLACK,
                        height=180,
                        border_radius=10,
                        border=ft.Border(
                            top=ft.BorderSide(2, color=Colors.WHITE),
                            bottom=ft.BorderSide(2, color=Colors.WHITE)
                        ),
                    ),
                    shadow_color=Colors.YELLOW_900
                )
            )

        page.update()


    def cardapio_delivery(e):
        lv_lanches.controls.clear()  # limpa antes de carregar
        token = page.client_storage.get('token')
        resultado_lanches = listar_lanche(token)
        print(f'Resultado dos lanches: {resultado_lanches}')



        for lanche in resultado_lanches:
            lv_lanches.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Image(src="imagemdolanche.png", height=100),
                                ft.Column(
                                    [
                                        ft.Text(f'{lanche["nome_lanche"]}', color=Colors.ORANGE_900),
                                        ft.Text(f'R$ {lanche["valor_lanche"]:.2f}', color=Colors.YELLOW_900),
                                        ft.Text(f'{lanche["descricao_lanche"]}',
                                                color=Colors.YELLOW_800, width=200),

                                        # Botão Finalizar Pedido
                                        ft.ElevatedButton(
                                            "Finalizar Pedido",
                                            on_click=lambda e: page.open(dlg_modal),
                                            style=ft.ButtonStyle(
                                                bgcolor=Colors.ORANGE_700,
                                                color=Colors.BLACK,
                                                padding=15,
                                                shape={"": ft.RoundedRectangleBorder(radius=10)}
                                            )
                                        ),
                                        ft.ElevatedButton()
                                    ]
                                ),
                            ]
                        ),
                        bgcolor=Colors.BLACK,
                        height=180,
                        border_radius=10,
                        border=ft.Border(
                            top=ft.BorderSide(2, color=Colors.WHITE),
                            bottom=ft.BorderSide(2, color=Colors.WHITE)
                        ),
                    ),
                    shadow_color=Colors.YELLOW_900
                )
            )

        page.update()

    # 🔔 Modal de Confirmação
    def fechar_dialogo(e):
        dlg_modal.open = False
        page.update()
        print("✅ Pedido confirmado!")  # Aqui pode chamar cadastrar_vendas()

    dlg_modal = ft.AlertDialog(
        title=ft.Text("ALERTA‼️", color=Colors.BLACK),
        content=ft.Text(
            "Você realmente confirma esse pedido?\n"
            "Após cadastrado não terá como editar.\n"
            "Então chame o garçom mais próximo\n"
            "e se quiser alguma mudança já faça suas observações.",
            color=Colors.WHITE,
            font_family='Arial',
            size=18
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo(e)),
            ft.TextButton("OK ✅", on_click=lambda e: fechar_dialogo(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=Colors.ORANGE_800,
    )


    def exibir_detalhes_lanches(lanche):
        txt_resultado_lanche.value = (f'Nome - {lanche['nome_lanche']}\n'
                                        f'Valor - {lanche['valor_lanche']}\n'
                                        f'Descrição - {lanche['descricao_lanche']}\n'

                                        )

        page.go('/exibir_detalhes_lanches')



    # Rotas
    def gerencia_rotas(e):
        page.views.clear()
        # page.padding = 0
        page.views.append(
            View(
                "/",
                [

                    ft.Container(
                        width=page.window.width,
                        height=page.window.height,
                        image=ft.DecorationImage(
                            src="imagem1.png",fit=ft.ImageFit.COVER
                        )
                    ),

                    # ft.Column(
                    #     [
                    #         ft.Text("Bem-vindo à Biblioteca", size=24, weight=ft.FontWeight.BOLD),
                    #         ft.Container(height=10),  # Espaçamento
                    #         input_email,
                    #         input_senha,
                    #         ft.Container(height=10),  # Espaçamento
                    #         loading_indicator,
                    #         spacing,
                    #         btn_login,
                    #     ],
                    #     # Alinha a coluna de login no centro horizontal da página
                    #     horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    #     height=page.window.height,
                    #     alignment=ft.MainAxisAlignment.CENTER,
                    # )
                ], bgcolor=Colors.BLACK, floating_action_button=usuario,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, vertical_alignment=ft.MainAxisAlignment.CENTER
            )
        )

        if page.route == "/login":
            page.views.append(
                View(
                    "/login",
                    [
                        AppBar(title=logo, center_title=True, bgcolor=Colors.BLACK, color=Colors.PURPLE, title_spacing=5
                               ),
                        ft.Container(
                            width=page.window.width,
                            height=page.window.height,
                            image=ft.DecorationImage(
                                src="fundo.jpg", opacity=0.8
                            ),
                            content=ft.Column([
                                input_email,
                                input_senha,
                                btn_login,
                                btn_cadastro_login,
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=5)
                        ),
                    ], bgcolor=Colors.BLACK, horizontal_alignment=ft.CrossAxisAlignment.CENTER, padding=11,
                    vertical_alignment=ft.MainAxisAlignment.CENTER
                )
            )

        if page.route == "/cadastrar_pessoa":
            input_email.value = ""
            input_senha.value = ""
            page.views.append(
                View(
                    "/cadastrar_pessoa",
                    [
                        AppBar(title=Text('Cadastro',color=Colors.YELLOW_900),title_text_style=TextStyle(weight=ft.FontWeight.BOLD,font_family="Playfair Display",size=18), leading=fundo, bgcolor=Colors.BLACK,center_title=True),
                        input_nome,
                        input_email_cadastrado,
                        input_senha_cadastro,
                        # input_cpf,
                        # input_papel_user,
                        # input_status_user_usuario,

                        # slider_salario,

                        # txt_salario,


                        ElevatedButton(
                            "Cadastrar",
                            on_click=lambda e: cadastro_click_user(e),
                            bgcolor=Colors.ORANGE_800,
                            color=Colors.BLACK,
                        ),
                        ElevatedButton(
                            "Voltar",
                            on_click=lambda e: page.go("/login"),
                            bgcolor=Colors.ORANGE_800,
                            color=Colors.BLACK,
                        ),
                    ],bgcolor=Colors.BLACK

                )
            )

        if page.route == "/mesa":
            page.views.append(
                View(
                    "/mesa",
                    [
                        AppBar(title=ft.Image(src="imgdois.png",width=90), center_title=True, bgcolor=Colors.BLACK, color=Colors.PURPLE,
                               title_spacing=5,leading=logo, actions=[btn_logout]
                               ),
                                ft.Row([
                                    icone_mesa,
                                    mesa,

                                ]),
                                ft.Row([
                                    icone_pedido,
                                    item,
                                ]),
                                ft.Row([
                                    inserir_mesa,btn_pedidos,btn_limpar_tela
                                ])






                    ], bgcolor=Colors.BLACK,
                )
            )

        if page.route == "/presencial_delivery":

            page.views.append(
                View(
                    "/presencial_delivery",
                    [
                        AppBar(
                            title=ft.Image(src="imgdois.png", width=90),
                            center_title=True,
                            bgcolor=Colors.BLACK,
                            color=Colors.ORANGE_500,
                            title_spacing=5,
                            leading=logo,
                            actions=[btn_logout]
                        ),

                        ElevatedButton(
                            "Presencial",
                            on_click=lambda _: page.go("/cardapio_presencial"),
                            style=ButtonStyle(
                                shape={"": RoundedRectangleBorder(radius=15)},
                                padding=20,
                                bgcolor=Colors.ORANGE_600,
                                color=Colors.BLACK
                            )
                        ),
                        ElevatedButton(
                            "Delivery",
                            on_click=lambda _: page.go("/cardapio_delivery"),
                            style=ButtonStyle(
                                shape={"": RoundedRectangleBorder(radius=15)},
                                padding=20,
                                bgcolor=Colors.BLACK,
                                color=Colors.ORANGE_400
                            )
                        ),

                    ],
                    bgcolor=Colors.ORANGE_800,
                    spacing=20  # só define o espaçamento entre eles
                )
            )

        if page.route == "/cardapio_presencial":
            cardapio(e)
            page.views.append(
                View(
                    "/cardapio",
                    [
                        AppBar(title=ft.Image(src="imgdois.png", width=90), center_title=True, bgcolor=Colors.BLACK,
                               color=Colors.PURPLE, title_spacing=5, leading=logo, actions=[btn_logout]),

                        lv_lanches

                    ],
                    bgcolor=Colors.BLACK,
                )
            )

        if page.route == "/cardapio_delivery":
            cardapio(e)
            page.views.append(
                View(
                    "/cardapio",
                    [
                        AppBar(title=ft.Image(src="imgdois.png", width=90), center_title=True, bgcolor=Colors.BLACK,
                               color=Colors.PURPLE, title_spacing=5, leading=logo, actions=[btn_logout]),

                        lv_lanches

                    ],
                    bgcolor=Colors.BLACK,
                )
            )



        page.update()

    # Componentes
    loading_indicator = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

    fab_add_usuario = ft.FloatingActionButton(
        icon=Icons.ADD,
        on_click=lambda _: page.go("/add_usuario")
    )

    lv_lanches = ft.ListView(expand=True)

    icone_mesa = ft.Icon(Icons.TABLE_BAR,color=Colors.ORANGE_800)
    icone_pedido = ft.Icon(Icons.CHECKLIST)

    input_email = ft.TextField(
        label="Email",
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800,border_radius=5,
    )

    input_senha = ft.TextField(
        label="Senha",
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        password=True,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800,border_radius=5,
        can_reveal_password=True
    )
    inserir_mesa = ft.ElevatedButton(text='Ver pedidos',
                                     icon=Icons.CHECK,
                                     icon_color=Colors.BLACK,
                                     color=Colors.BLACK,
                                     bgcolor=Colors.YELLOW_900,
                                     )
    btn_pedidos = ft.ElevatedButton(text='Ver pedidos',icon=Icons.CHECK,icon_color=Colors.BLACK,color=Colors.BLACK,bgcolor=Colors.YELLOW_900)
    btn_limpar_tela = ft.ElevatedButton(text='Limpar tela',icon=Icons.CHECK,icon_color=Colors.BLACK,color=Colors.BLACK,bgcolor=Colors.YELLOW_900)

    input_nome = ft.TextField(
        label="Insira seu nome",
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800
    )

    input_email_cadastrado = ft.TextField(
        hint_text='Insira seu email',
        col=4,
        width=300,
        label="Email",
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800
    )

    input_senha_cadastro = ft.TextField(
        hint_text='Insira sua senha',
        col=4,
        width=300,
        label="Senha",
        password=True,
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800
    )

    input_status_user = ft.Dropdown(
        label="Status",
        width=300, bgcolor=Colors.ORANGE_800,
        fill_color=Colors.ORANGE_800, color=Colors.ORANGE_800, text_style=TextStyle(color=Colors.WHITE),
        options=[
            Option(key="Ativo", text="Ativo"),
            Option(key="Inativo", text="Inativo"),

        ]
    )




    # Indicador de carregamento
    loading_indicator = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

    spacing = ft.Container(visible=False, height=10)

    # Botões
    btn_cadastro_login = ft.ElevatedButton(
        text="Cadastrar",
        icon=Icons.LOGIN,
        bgcolor=Colors.ORANGE_800,
        color=Colors.BLACK,
        width=page.window.width,
        height=30,
        icon_color=Colors.WHITE,
        on_click=lambda _: page.go('/cadastrar_pessoa'),

    )
    ir_para_mesa = ft.ElevatedButton(
        text="mesa",
        icon=Icons.LOGIN,
        bgcolor=Colors.ORANGE_800,
        color=Colors.BLACK,
        width=page.window.width,
        height=30,
        icon_color=Colors.WHITE,
        on_click=lambda _: page.go('/mesa'),

    )


    btn_login = ft.ElevatedButton(
        text="Logar",
        icon=Icons.VERIFIED_USER,
        bgcolor=Colors.ORANGE_800,
        color=Colors.BLACK,
        width=page.window.width,
        height=30,
        icon_color=Colors.WHITE,
        on_click=click_login,

    )

    btn_cancelar = ft.OutlinedButton(
        text="Cancelar",
        style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
        width=page.window.width,
        on_click=lambda _: page.go("/usuarios"),
        height=45,
    )



    logo = ft.Image(
        src="fundo.jpg",  # troque para o caminho da sua imagem local ou URL
        fit=ft.ImageFit.CONTAIN,
        width=80, opacity=0.7,

    )

    fundo = ft.GestureDetector(
        on_tap=lambda e: page.go("/"),  # substitua "/inicio" pela rota que quiser
        content=ft.Image(
            src="fundo.jpg",  # troque para o caminho da sua imagem local ou URL
            fit=ft.ImageFit.CONTAIN
        )
    )

    usuario = ft.TextButton(icon=Icons.LOGIN, text="Entrar", icon_color=Colors.RED_700,
                            on_click=lambda _: page.go('/login'))
    btn_logout = ft.TextButton(
        icon=Icons.LOGOUT,
        scale=1.5,
        icon_color=Colors.RED_700,
        on_click=click_logout
    )


    btn_salvar = ft.FilledButton(
        text="Salvar",
        style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
        width=page.window.width,
        height=45,
    )


    btn_cancelar = ft.OutlinedButton(
        text="Cancelar",
        style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
        width=page.window.width,
        on_click=lambda _: page.go("/usuarios"),
        height=45,
    )

    # Pessoas
    input_cpf = ft.TextField(
        label='Cpf',
        hint_text='insira cpf',
        col=4,
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800

    )



    mesa = ft.TextField(keyboard_type=ft.Number,color=Colors.ORANGE_800,
                        bgcolor=Colors.RED_900,fill_color=Colors.ORANGE_800,label="Numero da mesa",
                        border_color=Colors.DEEP_PURPLE_800,label_style=TextStyle(color=Colors.WHITE))

    item = ft.TextField(keyboard_type=ft.Number, color=Colors.ORANGE_800,
                        bgcolor=Colors.RED_900, fill_color=Colors.ORANGE_800, label="Pedido",
                        border_color=Colors.DEEP_PURPLE_800, label_style=TextStyle(color=Colors.WHITE))

    input_papel = ft.Dropdown(

        label = "Papel",
        width = 300,bgcolor=Colors.ORANGE_800,
        fill_color = Colors.ORANGE_800,color=Colors.ORANGE_800,text_style=TextStyle(color=Colors.WHITE),
        options = [
            Option(key="Cliente", text="Cliente"),
            Option(key= "garcom", text="Garçom"),

        ]
    )

    def display_slider_salario(e):
        txt_salario.value = f'SALÁRIO: {int(e.control.value)}'
        page.update()



    slider_salario = ft.Slider(min=0, max=50000, divisions=485, label="{value}",
                               active_color=Colors.ORANGE_800,
                               inactive_color=Colors.ORANGE_900, on_change=display_slider_salario,thumb_color=Colors.RED
                               )

    txt_salario = ft.Text(value='SALÁRIO: 0', font_family="Consolas", size=18, color=Colors.WHITE, animate_size=20,weight=FontWeight.BOLD,theme_style=TextThemeStyle.HEADLINE_SMALL)

    txt_resultado_lanche = ft.Text("", font_family="Arial", color=Colors.BLACK, size=18)
    # Eventos
    page.on_route_change = gerencia_rotas
    page.on_close = page.client_storage.remove("auth_token")
    page.go(page.route)


# Comando que executa o aplicativo
# Deve estar sempre colado na linha
ft.app(main)
