import flet as ft
from flet import AppBar, Text, View
from flet.core.alignment import top_left
from flet.core.border_radius import horizontal
from flet.core.colors import Colors
from flet.core.icons import Icons



def main(page: ft.Page):
    # Configurações
    page.title = "Exemplo de Login"
    page.theme_mode = ft.ThemeMode.LIGHT  # ou ft.ThemeMode.DARK
    page.window.width = 375
    page.window.height = 667

    # Funções


    def clicklogout(e):
        page.client_storage.remove("access_token")
        snack_sucesso("logout efetuado!")
        page.go('/login')



    def snack_sucesso(texto: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=Colors.GREEN_700
        )
        page.snack_bar.open = True
        page.overlay.append(page.snack_bar)

    def snack_error(texto: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=Colors.RED_700
        )
        page.snack_bar.open = True
        page.overlay.append(page.snack_bar)



    def gerencia_rotas(e):
        page.views.clear()
        # page.padding = 0
        page.views.append(
            View(
                "/login",
                [

                    ft.Container(
                        width=page.window.width,
                        height=page.window.height,
                        image=ft.DecorationImage(
                            src="assets/fundo.jpg",
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
                ],bgcolor=Colors.BLACK,floating_action_button=usuario,
            )
        )

        if page.route == "/usuarios":
            fab_add_usuario.visible = page.client_storage.get("papel") == "admin"


            page.views.append(
                View(
                    "/",
                    [
                        AppBar(title=Text("Usuarios"), center_title=True, bgcolor=Colors.PRIMARY_CONTAINER,
                               leading=ft.Icon(), actions=[btn_logout]),
                        lv_usuarios
                    ],
                    floating_action_button=fab_add_usuario,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    scroll=ft.ScrollMode.HIDDEN,
                )
            )

        if page.route == "/add_usuario":
            page.views.append(
                View(
                    "/add_usuario",
                    [
                        AppBar(title=Text("Novo Usuario"), center_title=True, bgcolor=Colors.PRIMARY_CONTAINER,
                               leading=ft.Icon(), actions=[btn_logout]),
                        input_nome,
                        input_email,
                        input_senha,
                        input_papel,
                        btn_salvar,
                        btn_cancelar,
                        loading_indicator
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        page.update()

    # Componentes

    fab_add_usuario = ft.FloatingActionButton(
        icon=Icons.ADD,
        on_click= lambda _: page.go("/add_usuario")
    )

    lv_usuarios = ft.ListView(expand=True)

    # Campos
    input_email = ft.TextField(
        label="E-mail",
        width=300,
        prefix_icon=Icons.EMAIL_OUTLINED,
        keyboard_type=ft.KeyboardType.EMAIL,
        autofocus=True,
    )

    input_senha = ft.TextField(
        label="Senha",
        width=300,
        password=True,
        can_reveal_password=True,  # Ícone para mostrar/ocultar senha
        prefix_icon=Icons.LOCK_OUTLINE,
    )

    input_nome = ft.TextField(
        label="Nome",
        width=300,
        prefix_icon=Icons.PERSON,
    )

    input_papel = ft.TextField(
        label="Papel",
        width=300,
        prefix_icon=Icons.SECURITY,
    )

    # Indicador de carregamento
    loading_indicator = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

    spacing = ft.Container(visible=False, height=10)

    # Botões
    btn_login = ft.ElevatedButton(
        text="Login",
        icon=Icons.LOGIN,
        width=300,
        height=45,
    )
    usuario = ft.TextButton(icon=Icons.LOGIN, text="cadastrar", icon_color=Colors.RED_700,
                                              on_click=lambda _: page.go('/usuarios'))
    btn_logout = ft.TextButton(
        icon=Icons.LOGOUT,
        scale=1.5,
        icon_color=Colors.RED_700,
    )

    btn_salvar = ft.FilledButton(
        text="Salvar",
        style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
        width=page.window.width,
        height=45,
    )

    # container = ft.Container(
    #     width=800,
    #     height=600,
    #     image_src="assets/fundo.jpg",  # URL ou caminho local
    #     image_fit=ft.ImageFit.COVER,  # Ajusta a imagem para cobrir o fundo
    #     content=ft.Text("Texto sobre a imagem", size=30, color="white"),
    #     alignment=ft.alignment.center
    # )

    btn_cancelar = ft.OutlinedButton(
        text="Cancelar",
        style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
        width=page.window.width,
        on_click= lambda _: page.go("/usuarios"),
        height=45,
    )

    # Eventos
    page.on_route_change = gerencia_rotas
    page.on_close = page.client_storage.remove("auth_token")
    page.go(page.route)


# Comando que executa o aplicativo
# Deve estar sempre colado na linha
ft.app(main)
